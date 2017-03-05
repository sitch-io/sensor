from alert_manager import AlertManager
from utility import Utility


class GeoCorrelator(object):
    def __init__(self):
        self.geo_anchor = {}
        self.threshold = 10

    def correlate(self, scan_bolus):
        scan_body = scan_bolus[1]
        if self.geo_anchor == {}:
            self.geo_anchor = scan_body
            print("GeoCorrelator: Setting anchor to %s" % str(scan_body))
            alerts = []
        else:
            alerts = GeoCorrelator.geo_drift_check(self.geo_anchor, scan_body,
                                                   self.threshold)
        return alerts

    @classmethod
    def geo_drift_check(cls, geo_anchor, gps_scan, threshold):
        lat_1 = geo_anchor["geometry"]["coordinates"][1]
        lon_1 = geo_anchor["geometry"]["coordinates"][0]
        lat_2 = gps_scan["geometry"]["coordinates"][1]
        lon_2 = gps_scan["geometry"]["coordinates"][0]
        current_distance = Utility.calculate_distance(lon_1, lat_1,
                                                      lon_2, lat_2)
        if current_distance < threshold:
            return []
        else:
            message = "Possible GPS spoofing attack! %d delta from anchor" % (
                      current_distance)
            alert = AlertManager().build_alert(300, message)
            return[alert]
