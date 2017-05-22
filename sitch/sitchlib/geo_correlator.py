"""Correlate based on geograpgic information."""

from alert_manager import AlertManager
from utility import Utility


class GeoCorrelator(object):
    """Geographic correlator."""

    def __init__(self, device_id):
        """Initialize the Geographic Correlator."""
        self.geo_anchor = {}
        self.threshold = 10
        self.time_threshold = 10
        self.device_id = device_id

    def correlate(self, scan_bolus):
        """Correlate one geo event.

        The first time we get a geo event, we set the state and print a message
            to stdout to that effect.  Every subsequent message is compared
            against the geo_anchor.  Once the anchor is set, it does not
            change for the life of the instance.  Correlation of subsequent
            events causes the distance beween the anchor and current event
            to be determined and if the threshold of 10km is exceeded, an alert
            is returned.

        Args:
            scan_bolus (tuple): Two-item tuple.  Position 0 contains the scan
                type, which is not checked.  We should only ever have geo
                events coming through this method.  Position 1 is expected to
                contain geo json.

        Returns:
            list: List of alerts.  If no alerts are fired, the list returned is
                zero-length.
        """
        scan_body = scan_bolus[1]
        if self.geo_anchor == {}:
            self.geo_anchor = scan_body
            print("GeoCorrelator: Setting anchor to %s" % str(scan_body))
            alerts = []
        else:
            alerts = GeoCorrelator.geo_drift_check(self.geo_anchor, scan_body,
                                                   self.threshold,
                                                   self.device_id)
            for alert in GeoCorrelator.time_drift_check(scan_body,
                                                        self.time_threshold,
                                                        self.device_id):
                alert[1]["site_name"] = scan_body["site_name"]
                alert[1]["sensor_name"] = scan_body["sensor_name"]
                alert[1]["sensor_id"] = scan_body["sensor_id"]
                alerts.append(alert)
        return alerts

    @classmethod
    def geo_drift_check(cls, geo_anchor, gps_scan, threshold, device_id):
        """Fire alarm if distance between points exceeds threshold.

        Args:
            geo_anchor (dict): Geographic anchor point, usually stored in an
                instance variable and passed in via the `correlate()` method.
            gps_scan (dict): Same format as geo_anchor, expects the same format
                as `geo_anchor`.
            threshold (int): Alerting threshold in km.

        Returns:
            list: list of alerts (usually just one) or an empty list of there
                are no alerts.
        """
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
            alert = AlertManager(device_id).build_alert(300, message)
            return[alert]

    @classmethod
    def time_drift_check(cls, gps_scan, threshold_mins, device_id):
        """Checks drift value, alarms if beyond threshold."""
        current_delta = gps_scan["time_drift"]
        if current_delta < threshold_mins:
            return []
        else:
            message = "Possible GPS time spoofing attack! %d delta from system" % (current_delta)  # NOQA
            alert = AlertManager(device_id).build_alert(310, message)
            return[alert]
