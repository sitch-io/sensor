from alert_manager import AlertManager
from datetime import datetime
from feed_manager import FeedManager
from location_tool import LocationTool
import json


class Enricher:
    def __init__(self, config, gps_location):
        self.device_id = config.device_id
        self.born_on_date = datetime.now()
        """ BTS reference looks like a list of these:
        {'radio': 'GSM',
         'mcc': '310',
         'net': '260',
         'area': '35873',
         'cell': '21421',
         'unit': None,
         'lon': '-122.753575',
         'lat': '45.12181',
         'range': '1102',
         'samples': '2',
         'changeable': '1',
         'created': '1459746499',
         'updated': '1459746499',
         'averageSignal': '-91'} """
        self.bts_reference = []
        self.feed_dir = config.feed_dir
        self.feed_obj = FeedManager(config)
        self.alerts = AlertManager()
        # VVV mcc, mnc, lac, cellid
        self.current_primary = {}
        self.gps_location = gps_location
        self.kal_threshold = config.kal_threshold
        self.suppressed_alerts = {}
        return

    @classmethod
    def convert_hex_targets(cls, channel):
        for target in ['lac', 'cellid']:
            if target in channel:
                channel[target] = Enricher.hex_to_dec(channel[target])
        return channel

    @classmethod
    def determine_scan_type(cls, scan):
        scan_type = None
        try:
            if scan is str:
                scan = json.loads(str)
            if scan["scan_program"] == 'Kalibrate':
                scan_type = 'Kalibrate'
            if scan["scan_program"] == 'SIM808':
                scan_type = 'SIM808'
            if scan["scan_program"] == 'GPS':
                scan_type = 'GPS'
        except:
            print "Failure to determine scan type"
            print scan
        return scan_type

    def enrich_kal_scan(self, scan_document):
        results_set = [("scan", scan_document)]
        kal_threshold = float(self.kal_threshold)
        platform_name = scan_document["scanner_name"]
        if scan_document["scan_results"] == []:
            print "No results found in scan document..."
            return
        else:
            for result in scan_document["scan_results"]:
                try:
                    msg = {}
                    msg["band"] = result["band"]
                    msg["power"] = result["power"]
                    msg["sample_rate"] = result["sample_rate"]
                    msg["final_freq"] = result["final_freq"]
                    msg["channel"] = result["channel"]
                    msg["gain"] = result["gain"]
                    msg["site_name"] = scan_document["scan_location"]["name"]
                    msg["scan_start"] = scan_document["scan_start"]
                    msg["scan_finish"] = scan_document["scan_finish"]
                    msg["scan_program"] = scan_document["scan_program"]
                    msg["scanner_public_ip"] = scan_document["scanner_public_ip"]
                    chan_enriched = ('kal_channel', msg)
                    results_set.append(chan_enriched)
                except Exception as e:
                    print "Failed to enrich Kalibrate message."
                    print e
                    print msg
                    # Now we look at alerting...
                try:
                    power = float(msg["power"])
                    if power > kal_threshold:
                        message = "ARFCN %s is over threshold at %s!" % (msg["channel"],
                                                                         msg["site_name"])
                        alert = self.alerts.build_alert(200, message)
                        results_set.append(alert)
                except Exception as e:
                    print "Failed to fire alert!"
                    print e
                    print msg

        return results_set

    def enrich_sim808_scan(self, scan_document):
        chan = {}
        here = {}
        results_set = [("cell", scan_document)]
        platform_name = scan_document["scan_location"]["name"]
        scan_items = scan_document["scan_results"]
        for channel in scan_items:
            channel["band"] = scan_document["band"]
            channel["scan_finish"] = scan_document["scan_finish"]
            channel["site_name"] = scan_document["scan_location"]["name"]
            channel["scanner_public_ip"] = scan_document["scanner_public_ip"]
            # We need to be able to bypass in the event of incomplete info
            skip_feed_comparison = False
            skip_feed_trigger_values = ['', '0000', '00', '0']
            for x in ["mcc", "mnc", "lac", "cellid"]:
                if channel[x] in skip_feed_trigger_values:
                    skip_feed_comparison = True
            channel = self.convert_hex_targets(channel)
            if skip_feed_comparison is False:
                channel["feed_info"] = self.get_feed_info(channel["mcc"],
                                                          channel["mnc"],
                                                          channel["lac"],
                                                          channel["cellid"])
                try:
                    chan["lat"] = channel["feed_info"]["lat"]
                    chan["lon"] = channel["feed_info"]["lon"]
                    here["lat"] = self.gps_location["lat"]
                    here["lon"] = self.gps_location["lon"]
                except TypeError:
                    print "Incomplete geo info..."
                    chan["lat"] = None
                    chan["lon"] = None
                    here["lat"] = None
                    here["lon"] = None
                channel["distance"] = Enricher.calculate_distance(chan["lon"],
                                                                  chan["lat"],
                                                                  here["lon"],
                                                                  here["lat"])
            chan_enriched = ('sim808_channel', channel)
            results_set.append(chan_enriched)
            # Stop here if we don't process against the feed...
            if skip_feed_comparison is True:
                continue
            # Alert if tower is not in feed DB
            if (channel["feed_info"]["range"] == 0 and
                    channel["feed_info"]["lon"] == 0 and
                    channel["feed_info"]["lat"] == 0):
                bts_info = "ARFCN: %s mcc: %s mnc: %s lac: %s cellid: %s" % (
                    channel["arfcn"], channel["mcc"], channel["mnc"],
                    channel["lac"], channel["cellid"])
                message = "BTS not in feed database! Info: %s Site: %s" % (bts_info, channel["site_name"])
                alert = self.alerts.build_alert(120, message)
                results_set.append(alert)
            # Else, be willing to alert if channel is not in range
            elif int(channel["distance"]) > int(channel["feed_info"]["range"]):
                message = ("ARFCN: %s, Expected range: %s  Actual distance: %s  Channel info: %s Site: %s") % (
                           channel["arfcn"], str(channel["feed_info"]["range"]),
                           str(channel["distance"]),
                           json.dumps(channel),
                           channel["site_name"])
                alert = self.alerts.build_alert(100, message)
                results_set.append(alert)
            # Test for primary BTS change
            if channel["cell"] == '0':
                current_bts = {"mcc": channel["mcc"],
                               "mnc": channel["mnc"],
                               "lac": channel["lac"],
                               "cellid": channel["cellid"]}
                if self.current_primary == {}:
                    self.current_primary = current_bts
                elif self.current_primary != current_bts:
                    message = "Primary BTS was %s now %s. Site: %s" % (json.dumps(self.current_primary),
                                                                       json.dumps(current_bts),
                                                                       channel["site_name"])
                    alert = self.alerts.build_alert(110, message)
                    results_set.append(alert)
        return results_set

    def enrich_gps_scan(self, scan_document):
        retval = ("gps", scan_document)
        return retval

    @classmethod
    def hex_to_dec(cls, hx):
        integer = int(hx, 16)
        return str(integer)

    def get_feed_info(self, mcc, mnc, lac, cellid):
        feed_info = self.feed_obj.get_feed_info_for_tower(mcc, mnc, lac, cellid)
        return feed_info

    @classmethod
    def calculate_distance(cls, lon_1, lat_1, lon_2, lat_2):
        if None in [lon_1, lat_1, lon_2, lat_2]:
            print "Zero geo coordinate detected, not resolving distance."
            return 0
        pos_1 = (lon_1, lat_1)
        pos_2 = (lon_2, lat_2)
        dist_in_km = LocationTool.get_distance_between_points(pos_1, pos_2)
        dist_in_m = dist_in_km * 1000
        return dist_in_m
