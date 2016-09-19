from alert_manager import AlertManager
from datetime import datetime
from feed_manager import FeedManager
from enrich_gsm_modem import GsmModemEnricher
from utility import Utility
import json


class Enricher:
    def __init__(self, config, state):
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
        self.kal_threshold = config.kal_threshold
        self.suppressed_alerts = {}
        self.gsm_modem_enricher = GsmModemEnricher(state, self.feed_dir)
        return

    @classmethod
    def determine_scan_type(cls, scan):
        scan_type = None
        try:
            if scan is str:
                scan = json.loads(str)
            if scan["scan_program"] == 'Kalibrate':
                scan_type = 'Kalibrate'
            if scan["scan_program"] == 'GSM_MODEM':
                scan_type = 'GSM_MODEM'
            if scan["scan_program"] == 'gps':
                scan_type = 'GPS'
            if scan["scan_program"] == 'geo_ip':
                scan_type = 'GEOIP'
        except:
            print "Failure to determine scan type"
            print scan
        return scan_type

    def enrich_gsm_modem_scan(self, scan, state):
        self.gsm_modem_enricher.state = state
        retval = self.gsm_modem_enricher.enrich_gsm_modem_scan(scan)
        return retval

    def enrich_kal_scan(self, scan_document):
        results_set = [("scan", scan_document)]
        kal_threshold = float(self.kal_threshold)
        # platform_name = scan_document["scanner_name"]
        if scan_document["scan_results"] == []:
            print "No results found in scan document..."
            return results_set
        else:
            for result in scan_document["scan_results"]:
                try:
                    msg = {}
                    msg["band"] = result["band"]
                    msg["power"] = Enricher.str_to_float(result["power"])
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

    def enrich_gps_scan(self, scan_document):
        retval = ("gps", scan_document)
        return retval

    def enrich_geoip_scan(self, scan_document):
        retval = ("geoip", scan_document)
        return retval
    """
    @classmethod
    def hex_to_dec(cls, hx):
        integer = int(hx, 16)
        return str(integer)

    def get_feed_info(self, mcc, mnc, lac, cellid):
        feed_info = self.feed_obj.get_feed_info_for_tower(mcc, mnc,
                                                          lac, cellid)
        return feed_info
    """


    @classmethod
    def str_to_float(cls, s):
        retval = None
        try:
            retval = float(s)
        except:
            print "Unable to convert %s to float" % str(s)
        return retval

    @classmethod
    def geo_drift_check(cls, prior_distance, geoip_scan, gps_scan, threshold):
        """ We take the prior distance (in meters) and compare to the
        distance between the geoip_scan and gps_scan results.  If the
        difference is greater than the threshold value, we alarm on a potential
        GPS spoofing attack."""
        if prior_distance == 0:
            return
        lat_1 = geoip_scan["geometry"]["coordinates"][0]
        lon_1 = geoip_scan["geometry"]["coordinates"][1]
        lat_2 = gps_scan["geometry"]["coordinates"][0]
        lon_2 = gps_scan["geometry"]["coordinates"][1]
        current_distance = Utility.calculate_distance(lon_1, lat_1,
                                                      lon_2, lat_2)
        if abs(current_distance - prior_distance) < threshold:
            return
        else:
            message = "Possible GPS spoofing attack! Was %d Now %d" % (
                      prior_distance, current_distance)
            alert = AlertManager().build_alert(300, message)
            return alert
