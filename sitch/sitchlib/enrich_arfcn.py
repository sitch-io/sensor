import LatLon
import alert_manager
from fcc_feed import FccFeed
from string import Template
from utility import Utility


class EnrichArfcn(object):
    def __init__(self, geo_state, states, feed_dir):
        """ geo_state looks like this:
        {"gps": {},
         "geoip": {},
         "geo_distance_meters": 0}
        """
        self.alerts = alert_manager.AlertManager()
        self.geo_state = geo_state
        self.feed_dir = feed_dir
        self.fcc_feed = FccFeed(states, feed_dir)
        self.observed_arfcn = []
        return

    def compare_arfcn_to_feed(self, scan_document):
        """ Returns a tuple of bool and string.
        Bool represents if the commparison was good, false if it failed."""
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
        for item in self.fcc_feed:
            if str(item["ARFCN"]) != str(arfcn):
                continue
            item_gps = self.assemble_gps(item)
            if self.is_in_range(item_gps, self.geo_state["gps"]):
                return results_set
        results_set[0][1]["scan_finish"] = Utility.get_now_string()
        msg = "Unable to locate a license for ARFCN %s" % str(arfcn)
        alert = self.alerts.build_alert(400, msg)
        results_set.append(alert)
        self.observed_arfcn.append(arfcn)
        return results_set

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
