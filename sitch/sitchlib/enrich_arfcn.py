import LatLon
import alert_manager
from fcc_feed import FccFeed
from string import Template
from utility import Utility


class EnrichArfcn(object):
    """ARFCN Enricher:

    Confirms license for ARFCN

    Checks ARFCN power measurement (if available) against threshold

    """
    def __init__(self, geo_state, states, feed_dir, whitelist,
                 power_threshold):
        """ geo_state looks like this:
        {"gps": {},
         "geoip": {},
         "geo_distance_meters": 0}
        """
        self.alerts = alert_manager.AlertManager()
        self.geo_state = geo_state
        self.feed_dir = feed_dir
        self.states = states
        self.power_threshold = float(power_threshold)
        self.fcc_feed = FccFeed(states, feed_dir)
        self.observed_arfcn = []
        return

    def compare_arfcn_to_feed(self, scan_document):
        """Returns a list of tuples.

        If the comparison was OK, you'll only get a single tuple of
        ("scan", SCAN_DOCUMENT) where tuple[0] represents the item type, and
        SCAN_DOCUMENT is the original scan document passed into the method.

        """

        arfcn = scan_document["scan_results"][0]["arfcn"]
        results_set = [("scan", scan_document)]
        if str(arfcn) == "0":
            return results_set
        if arfcn in self.observed_arfcn:
            return results_set
        if self.geo_state["gps"] == {}:
            msg = "EnrichARFCN: No gps state for comparison.  ARFCN: %s" % arfcn
            print(msg)
        msg = "EnrichARFCN: Cache miss.  Attempt to get %s from feed files..." % str(arfcn)
        print(msg)
        for item in EnrichArfcn.yield_arfcn_from_feed(arfcn, self.states,
                                                      self.feed_dir):
            item_gps = self.assemble_gps(item)
            if self.is_in_range(item_gps, self.geo_state["gps"]):
                self.observed_arfcn.append(arfcn)
                return results_set
        results_set[0][1]["scan_finish"] = Utility.get_now_string()
        msg = "Unable to locate a license for ARFCN %s" % str(arfcn)
        alert = self.alerts.build_alert(400, msg)
        results_set.append(alert)
        self.observed_arfcn.append(arfcn)
        if results_set[0][1]["type"] == "kal_channel":
            if float(results_set[0][1]["power"]) > self.power_threshold:
                message = "ARFCN %s over threshold at %s.  Observed: %s" % (
                          results_set[0][1]["channel"],
                          results_set[0][1]["site_name"],
                          results_set[0][1]["power"])
                alert = self.alerts.build_alert(200, message)
                results_set.append(alert)
        return results_set

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
        state_lon = state_gps["geometry"]["coordinates"][0]
        state_lat = state_gps["geometry"]["coordinates"][1]
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
            lat, lon = EnrichArfcn.assemble_latlon(item)
            ll = LatLon.string2latlon(lat, lon, "d% %m% %S% %H")
            latlon["lat"] = ll.to_string('D%')[0]
            latlon["lon"] = ll.to_string('D%')[1]
        except:
            print("EnrichARFCN: Unable to compose lat/lon from:")
            print(item)
        return latlon
