import LatLon
import alert_manager
from fcc_feed import FccFeed
from string import Template
from utility import Utility


class ArfcnCorrelator(object):
    """ARFCN Enricher:

    Confirms license for ARFCN

    Checks ARFCN power measurement (if available) against threshold

    """
    def __init__(self, geo_state, states, feed_dir, whitelist,
                 power_threshold):
        """ geo_state looks like this:
        {"lat": 123, "lon": 124}
        """
        self.alerts = alert_manager.AlertManager()
        self.geo_state = geo_state
        self.feed_dir = feed_dir
        self.states = states
        self.power_threshold = float(power_threshold)
        self.fcc_feed = FccFeed(states, feed_dir)
        # Whitelist goes into observed_arfcn, and bypasses feed comparison (still threshold alert though)
        self.observed_arfcn = whitelist
        self.arfcn_over_threshold = []
        self.arfcn_not_in_feed = []
        self.arfcn_out_of_range = []
        return

    def correlate(self, scan_document):
        """Entrypoint, so to speak"""
        retval = []
        scan_type = scan_document[0]
        scan = scan_document[1]
        arfcn = ArfcnCorrelator.arfcn_from_scan(scan_type, scan)
        if scan_type == "kal_channel":
            if self.arfcn_over_threshold(arfcn):
                message = "ARFCN %s over threshold at %s.  Observed: %s" % (
                          scan["channel"],
                          scan["site_name"],
                          scan["power"])
                alert = self.alerts.build_alert(200, message)
                retval.append(alert)
                self.manage_arfcn_lists("in", arfcn, "threshold")
            else:
                self.manage_arfcn_lists("out", arfcn, "threshold")
        feed_alerts = self.compare_arfcn_to_feed(arfcn)
        for feed_alert in feed_alerts:
            retval.append(feed_alert)
        self.observed_arfcn.append(arfcn)
        return retval

    def manage_arfcn_lists(self, direction, arfcn, aspect):
        reference = {"threshold": self.arfcn_over_threshold,
                     "not_in_feed": self.arfcn_not_in_feed,
                     "not_in_range": self.arfcn_out_of_range}
        if direction == "in":
            if reference["aspect"].count(arfcn) > 0:
                pass
            else:
                reference["aspect"].append(arfcn)
        elif direction == "out":
            if reference["aspect"].count(arfcn) == 0:
                pass
            else:
                while arfcn in reference["aspect"]  :
                    reference["aspect"].remove(arfcn)
        return

    def arfcn_over_threshold(self, arfcn):
        """Returns bool"""
        if float(arfcn) > self.power_threshold:
            return True
        else:
            return False


    def compare_arfcn_to_feed(self, arfcn):
        """Returns a list of tuples, and only alarms.

        """
        results = []
        # If we can't compare geo, have ARFCN 0 or already been found in feed:
        if (str(arfcn) == "0" or
            arfcn in self.observed_arfcn or
            self.geo_state["gps"] == {}):
            return results
        else:
            msg = "ArfcnCorrelator: Cache miss on ARFCN %s" % str(arfcn)
            print(msg)
        feed_alerts = self.compare_arfcn_to_feed(arfcn)
        if feed_alerts:
            for feed_alert in feed_alerts:
                results.append(feed_alert)
        return results


    def feed_alert_generator(self, arfcn):
        results = []
        for item in ArfcnCorrelator.yield_arfcn_from_feed(arfcn, self.states,
                                                          self.feed_dir):
            item_gps = self.assemble_gps(item)
            if self.is_in_range(item_gps, self.geo_state["gps"]):
                return results
        msg = "Unable to locate a license for ARFCN %s" % str(arfcn)
        alert = self.alerts.build_alert(400, msg)
        results.append(alert)

    @classmethod
    def arfcn_from_scan(cls, scan_type, scan_doc):
        if scan_type == "kal_channel":
            return scan_doc["arfcn_int"]
        elif scan_type == "cell":
            return scan_doc["arfcn_int"]
        else:
            print("ArfcnCorrelator: Unrecognized scan type: %s" % str(scan_type))
            return None

    @classmethod
    def yield_arfcn_from_feed(cls, arfcn, states, feed_dir):
        fcc_feed = FccFeed(states, feed_dir)
        for item in fcc_feed:
            if str(item["ARFCN"]) != str(arfcn):
                continue
            else:
                yield item
        return

    @classmethod
    def is_in_range(cls, item_gps, state_gps):
        max_range = 40000  # 40km
        state_lon = state_gps["lon"][0]
        state_lat = state_gps["lat"][1]
        item_lon = item_gps["lon"]
        item_lat = item_gps["lat"]
        distance = Utility.calculate_distance(state_lon, state_lat,
                                              item_lon, item_lat)
        if distance > max_range:
            return False
        else:
            return True

    @classmethod
    def assemble_latlon(cls, item):
        lat_tmpl = Template('$LOC_LAT_DEG $LOC_LAT_MIN $LOC_LAT_SEC $LOC_LAT_DIR')
        long_tmpl = Template('$LOC_LONG_DEG $LOC_LONG_MIN $LOC_LONG_SEC $LOC_LONG_DIR')
        return(lat_tmpl.substitute(item), long_tmpl.substitute(item))

    @classmethod
    def assemble_gps(cls, item):
        latlon = {}
        try:
            lat, lon = ArfcnCorrelator.assemble_latlon(item)
            ll = LatLon.string2latlon(lat, lon, "d% %m% %S% %H")
            latlon["lat"] = ll.to_string('D%')[0]
            latlon["lon"] = ll.to_string('D%')[1]
        except:
            print("ArfcnCorrelator: Unable to compose lat/lon from:")
            print(item)
        return latlon
