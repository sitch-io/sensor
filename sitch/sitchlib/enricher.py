from alert_manager import AlertManager
from datetime import datetime
from feed_manager import FeedManager
from enrich_gsm_modem import GsmModemEnricher
from enrich_kal_scan import KalScanEnricher
from enrich_arfcn import EnrichArfcn
from utility import Utility
import json


class Enricher:
    def __init__(self, config, geo_state):
        self.device_id = config.device_id
        self.born_on_date = datetime.now()
        self.public_ip = config.public_ip
        self.platform_name = config.platform_name
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
        self.gsm_modem_enricher = GsmModemEnricher(geo_state, self.feed_dir)
        self.kal_enricher = KalScanEnricher(self.kal_threshold)
        self.arfcn_enricher = EnrichArfcn(geo_state, config.state_list,
                                          self.feed_dir)
        return

    @classmethod
    def determine_scan_type(cls, scan):
        scan_type = None
        try:
            if scan is str:
                scan = json.loads(str)
            if scan["scan_program"] == 'Kalibrate':
                scan_type = 'Kalibrate'
            elif scan["scan_program"] == 'GSM_MODEM':
                scan_type = 'GSM_MODEM'
            elif scan["scan_program"] == 'gps':
                scan_type = 'GPS'
            elif scan["scan_program"] == 'geo_ip':
                scan_type = 'GEOIP'
            elif scan["scan_program"] == 'heartbeat':
                scan_type = 'HEARTBEAT'
        except:
            print "Failure to determine scan type"
            print scan
        return scan_type

    def enrich_gsm_modem_scan(self, scan, state):
        self.gsm_modem_enricher.state = state
        retval = self.gsm_modem_enricher.enrich_gsm_modem_scan(scan)
        return retval

    def enrich_kal_scan(self, scan_document):
        results_set = self.kal_enricher.enrich_kal_scan(scan_document)
        return results_set

    def enrich_gps_scan(self, scan_document):
        retval = [("gps", scan_document)]
        return retval

    def enrich_geoip_scan(self, scan_document):
        retval = [("geoip", scan_document)]
        return retval

    def check_arfcn_in_range(self, arfcn):
        """ Checks to make sure ARFCN is licensed for this area """
        scan_job = {"platform": self.platform_name,
                    "scan_results": [{"arfcn": arfcn}],
                    "scan_start": datetime.now(),
                    "scan_finish": datetime.now(),
                    "scan_program": "ARFCN_ENRICHER",
                    "scan_location": {"name": self.device_id},
                    "scanner_public_ip": self.public_ip}
        retval = self.arfcn_enricher.compare_arfcn_to_feed(scan_job)
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
