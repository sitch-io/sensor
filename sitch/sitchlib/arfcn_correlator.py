"""ARFCN Correlator."""

import alert_manager
import os
import sqlite3
from utility import Utility


class ArfcnCorrelator(object):
    """The ArfcnCorrelator compares ARFCN metadata against feeds and threshold.

    The feed data is put in place by the FeedManager class, prior to
    instantiating the ArfcnCorrelator.
    """

    def __init__(self, feed_dir, whitelist, power_threshold, device_id):
        """Initializing the ArfcnCorrelator.

        Args:
            arfcn_db (str): Full path to the ARFCN database.
            whitelist (list): This is a list of ARFCNs that should be
                considered trustworthy enough to skip feed comparison.
                This does not override comparison against threshold.
            power_threshold (str): No matter the type, it will be coerced,
                if possible, to float.  This is the value that Kalibrate-
                reported channel power will be compared against to make a
                determination on whether or not to fire an alarm.
        """
        self.alerts = alert_manager.AlertManager(device_id)
        self.geo_state = {"type": "Point", "coordinates": [0, 0]}
        self.feed_dir = feed_dir
        self.arfcn_db = os.path.join(feed_dir, "arfcn.db")
        self.power_threshold = float(power_threshold)
        self.observed_arfcn = whitelist
        self.arfcn_threshold = []
        self.arfcn_range = []
        return

    def correlate(self, scan_bolus):
        """Entrypoint for correlation, wraps individual checks.

        Args:
            scan_bolus (tuple): Position 0 contains a string defining scan
                type.  If it's type 'gps', the geo_state instance variable
                will be updated with Position 1's contents.  If the scan type
                is 'kal_channel', we perform feed and threshold comparison.
                any other scan type will be compared against the feed only.

        Returns:
            list: Returns a list of alerts.  If no alerts are generated, an
                empty list is returned.
        """
        retval = []
        scan_type = scan_bolus[0]
        scan = scan_bolus[1]
        if scan_type == "gps":
            self.geo_state = scan["location"]
        arfcn = ArfcnCorrelator.arfcn_from_scan(scan_type, scan)
        if scan_type == "kal_channel":
            retval.append(scan_bolus)
            if self.arfcn_over_threshold(scan["power"]):
                message = "ARFCN %s over threshold at %s.  Observed: %s" % (
                          scan["channel"],
                          scan["site_name"],
                          scan["power"])
                alert = self.alerts.build_alert(200, message, self.geo_state)
                alert[1]["site_name"] = scan["site_name"]
                alert[1]["sensor_name"] = scan["sensor_name"]
                alert[1]["sensor_id"] = scan["sensor_id"]
                retval.append(alert)
                self.manage_arfcn_lists("in", arfcn, "threshold")
            else:
                self.manage_arfcn_lists("out", arfcn, "threshold")
        feed_alerts = self.compare_arfcn_to_feed(arfcn)
        for feed_alert in feed_alerts:
            feed_alert[1]["site_name"] = scan["site_name"]
            feed_alert[1]["sensor_name"] = scan["sensor_name"]
            feed_alert[1]["sensor_id"] = scan["sensor_id"]
            retval.append(feed_alert)
        self.observed_arfcn.append(arfcn)
        return retval

    def manage_arfcn_lists(self, direction, arfcn, aspect):
        """Manage the instance variable lists of ARFCNs.

        This is necessary to maintain an accurate state over time, and reduce
        unnecessary noise.

        Args:
          direction (str): Only will take action if this is "in" or "out"
          arfcn (str): This is the ARFCN that will be moved in or our of
              the list
          aspect (str): This is used to match the ARFCN with the list it
              should be moved in or out of.  This should be either
              "threshold" or "not_in_range".

        """
        reference = {"threshold": self.arfcn_threshold,
                     "not_in_range": self.arfcn_range}
        if direction == "in":
            if reference[aspect].count(arfcn) > 0:
                pass
            else:
                reference[aspect].append(arfcn)
        elif direction == "out":
            if reference[aspect].count(arfcn) == 0:
                pass
            else:
                while arfcn in reference[aspect]:
                    reference[aspect].remove(arfcn)
        return

    def arfcn_over_threshold(self, arfcn_power):
        """Compare the ARFCN power against the thresholdset on instantiation.

        Args:
            arfcn_power (float): If this isn't a float already, it will be
                coerced to float.

        Returns:
            bool:  True if arfcn_power is over threshold, False if not.
        """
        if float(arfcn_power) > self.power_threshold:
            return True
        else:
            return False

    def compare_arfcn_to_feed(self, arfcn):
        """Wrap other functions that dig into the FCC license DB.

        This relies on the observed_arfcn instance variable for caching, to
        skip DB comparison, that way we (probably) won't end up with a
        forever-increasing queue size.

        Args:
            arfcn (str):  This is the text representation of the ARFCN we want
                to compare against the FCC license database.

        Returns:
            list: You get back a list of alerts as tuples, where position 0 is
                'sitch_alert' and position 1 is the actual alert.
        """
        results = []
        # If we can't compare geo, have ARFCN 0 or already been found in feed:
        if (str(arfcn) in ["0", None] or
                arfcn in self.observed_arfcn or
                self.geo_state["coordinates"] == [0, 0]):
            return results
        else:
            msg = "ArfcnCorrelator: Cache miss on ARFCN %s" % str(arfcn)
            print(msg)
        results.extend(self.feed_alert_generator(arfcn))
        return results

    def feed_alert_generator(self, arfcn):
        """Wrap the yield_arfcn_from_feed function, and generates alerts.

        Args:
            arfcn (str): This is the string representation of the ARFCN to be
                correlated.

        Returns:
            list: This returns a list of alert tuples.
        """
        results = []
        if arfcn is None:
            return results
        if not self.match_arfcn_against_feed(arfcn, self.geo_state):
            msg = "Unable to locate a license for ARFCN %s" % str(arfcn)
            self.manage_arfcn_lists("in", arfcn, "not_in_range")
            alert = self.alerts.build_alert(400, msg, self.geo_state)
            results.append(alert)
        return results

    @classmethod
    def arfcn_from_scan(cls, scan_type, scan_doc):
        """Pull the ARFCN from different scan types.

        Args:
            scan_type (str): "kal_channel", "gsm_modem_channel", or "gps".
            scan_doc (dict): Scan document

        Returns:
            str: ARFCN from scan, or None if scan is unrecognized or
                unsupported.
        """
        if scan_type == "kal_channel":
            return scan_doc["arfcn_int"]
        elif scan_type == "gsm_modem_channel":
            return scan_doc["arfcn"]
        elif scan_type == "cell":
            return None
        elif scan_type == "scan":
            return None
        elif scan_type == "gps":
            return None
        else:
            print("ArfcnCorrelator: Unknown scan type: %s" % str(scan_type))
            return None

    def match_arfcn_against_feed(self, arfcn, state_gps):
        """Get a match for the ARFCN within range of the sensor.

        Args:
            arfcn (str): Absolute Radio Frequency Channel Number

        Returns:
            bool: True if there is an ARFCN in range, False if not.
        """
        result = False
        conn = sqlite3.connect(self.arfcn_db)
        c = conn.cursor()
        clean_arfcn = str(arfcn)
        c.execute("SELECT arfcn, carrier, lon, lat FROM arfcn WHERE arfcn=?", (clean_arfcn, ))  # NOQA
        for result in c.fetchall():
            test_set = {"arfcn": result[0], "carrier": result[1],
                        "lon": result[2], "lat": result[3]}
            if self.is_in_range(test_set, state_gps):
                result = True
                conn.close()
                break
        return result

    @classmethod
    def is_in_range(cls, item_gps, state_gps):
        """Return True if items are within 40km."""
        state_gps_lat = state_gps["coordinates"][1]
        state_gps_lon = state_gps["coordinates"][0]
        max_range = 40000  # 40km
        state_lon = state_gps_lon
        state_lat = state_gps_lat
        item_lon = item_gps["lon"]
        item_lat = item_gps["lat"]
        distance = Utility.calculate_distance(state_lon, state_lat,
                                              item_lon, item_lat)
        if distance > max_range:
            return False
        else:
            return True
