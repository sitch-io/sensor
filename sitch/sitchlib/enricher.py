from datetime import datetime
from feed_manager import FeedManager
from location_tool import LocationTool
import haversine
import json


class Enricher:
    def __init__(self, config):
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
        return

    @classmethod
    def get_distance_between_geo(cls, lat_1, lon_1, lat_2, lon_2):
        """ Determines distance in km """
        point_1 = (lat_1, lon_1)
        point_2 = (lat_2, lon_2)
        distance = haversine(point_1, point_2)
        return distance

    def get_bts_from_feed(self, mcc, mnc, cellid):
        feed_file = self.feed_obj.get_destination_file_name(self.feed_dir, mnc)
        with gzip.open(feed_file, 'r') as bolus:
            consumer = csv.DictReader(bolus)
            for row in consumer:
                if row["mnc"] == mnc and row["cellid"] == cellid:
                    return row
        return False

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
        platform_name = scan_document["scanner_name"]
        if scan_document["scan_results"] == []:
            print "No results found in scan document..."
            return
        else:
            try:
                for result in scan_document["scan_results"]:
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
                    results_set.append(("kal_channel", json.dumps(msg)))
            except:
                print "Failed to enrich KAL message: "
                print msg
        return results_set

    def enrich_sim808_scan(self, scan_document):
        chan = {}
        here = {}
        results_set = [("cell", scan_document)]
        results_channels = []
        platform_name = scan_document["scan_location"]["name"]
        scan_items = scan_document["scan_results"]
        for channel in scan_items:
            channel["band"] = scan_document["band"]
            channel["scan_finish"] = scan_document["scan_finish"]
            channel["site_name"] = scan_document["scan_location"]["name"]
            channel["scanner_public_ip"] = scan_document["scanner_public_ip"]
            channel["feed_info"] = self.get_feed_info(channel["mcc"],
                                                      channel["mnc"],
                                                      channel["lac"],
                                                      channel["cellid"])
            try:
                chan["lat"] = channel["feed_info"]["lat"]
                chan["lon"] = channel["feed_info"]["lon"]
                here["lat"] = gps_location["lat"]
                here["lon"] = gps_location["lon"]
            except TypeError:
                chan["lat"] = None
                chan["lon"] = None
                here["lat"] = None
                here["lon"] = None
            channel["distance"] = Enricher.calculate_distance(chan["lon"],
                                                              chan["lat"],
                                                              here["lon"],
                                                              here["lat"])
            channel = self.convert_hex_targets(channel)
            chan_enriched = ('sim808_channel', channel)
            try:
                _tester == channel["feed_info"]["range"]
            except:
                channel["feed_info"] = {'range': 0}
            if int(channel["distance"]) > channel["feed_info"]["range"]:
                message = "Cell tower distance greater than expected range!!"
                channel["alarm_msg"] = message
                results_set.append('sim808_alarm', channel)
            results_set.append(chan_enriched)
        print "Enriched SIM808 scan:"
        print results_set
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
            return 0
        pos_1 = (lon_1, lat_1)
        pos_2 = (lon_2, lat_2)
        dist_in_km = LocationTool.get_distance_between_points(pos_1, pos_2)
        dist_in_m = dist_in_km * 1000
        return dist_in_m
