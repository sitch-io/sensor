import csv
import gzip
import json
import os
import alert_manager
from utility import Utility


class GsmModemEnricher(object):
    def __init__(self, state, feed_dir):
        """ State looks like this:
        {"gps": {},
         "geoip": {},
         "geo_distance_meters": 0}
        """
        self.state = state
        self.feed_dir = feed_dir
        self.alerts = alert_manager.AlertManager()
        self.prior_bts = {}
        self.feed_cache = []
        self.good_arfcns = []
        self.bad_arfcns = []
        return

    def enrich_gsm_modem_scan(self, scan_document):
        chan = {}
        here = {}
        state = self.state
        results_set = [("cell", scan_document)]
        # platform_name = scan_document["scan_location"]["name"]
        scan_items = scan_document["scan_results"]
        for channel in scan_items:
            channel["band"] = scan_document["band"]
            channel["scan_finish"] = scan_document["scan_finish"]
            channel["site_name"] = scan_document["scan_location"]["name"]
            channel["scanner_public_ip"] = scan_document["scanner_public_ip"]
            try:
                channel["arfcn_int"] = int(channel["arfcn"])
            except:
                print "EnrichGSM: Unable to convert ARFCN to int"
                print channel["arfcn"]
                channel["arfcn_int"] = 0
            """ In the event we have incomplete information, we need to bypass
            comparison.
            """
            skip_feed_comparison = False
            skip_feed_trigger_values = ['', '0000', '00', '0']
            for x in ["mcc", "mnc", "lac", "cellid"]:
                if channel[x] in skip_feed_trigger_values:
                    skip_feed_comparison = True

            """ Now we bring the hex values to decimal..."""
            channel = self.convert_hex_targets(channel)
            channel = self.convert_float_targets(channel)

            """ Setting CGI """
            cgi = "%s%s%s%s" % (str(channel["mcc"]), str(channel["mnc"]),
                                str(channel["lac"]), str(channel["cellid"]))
            channel["cgi_str"] = cgi
            try:
                channel["cgi_int"] = int(cgi)
            except:
                print "EnrichGSM: Unable to convert CGI to int"
                print cgi
                channel["cgi_int"] = 0

            """ Here's the feed comparison part """
            if skip_feed_comparison is False:
                channel["feed_info"] = self.get_feed_info(channel["mcc"],
                                                          channel["mnc"],
                                                          channel["lac"],
                                                          channel["cellid"])
                try:
                    chan["lat"] = channel["feed_info"]["lat"]
                    chan["lon"] = channel["feed_info"]["lon"]
                    here["lat"] = state["gps"]["geometry"]["coordinates"][0]
                    here["lon"] = state["gps"]["geometry"]["coordinates"][1]
                except TypeError:
                    print "EnrichGSM: Incomplete geo info..."
                    chan["lat"] = None
                    chan["lon"] = None
                    here["lat"] = None
                    here["lon"] = None
                channel["distance"] = Utility.calculate_distance(chan["lon"],
                                                                 chan["lat"],
                                                                 here["lon"],
                                                                 here["lat"])
            chan_enriched = ('gsm_modem_channel', channel)
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
                message = "BTS not in feed database! Info: %s Site: %s" % (
                    bts_info, channel["site_name"])
                alert = self.alerts.build_alert(120, message)
                results_set.append(alert)
            # Else, be willing to alert if channel is not in range
            elif int(channel["distance"]) > int(channel["feed_info"]["range"]):
                message = ("ARFCN: %s Expected range: %s  Actual distance:" +
                           " %s Channel info: %s Site: %s") % (
                           channel["arfcn"],
                           str(channel["feed_info"]["range"]),
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
                if self.prior_bts == {}:
                    self.prior_bts = dict(current_bts)
                elif self.prior_bts != current_bts:
                    message = ("Primary BTS was %s " +
                               "now %s. Site: %s") % (
                                   self.make_bts_friendly(self.prior_bts),
                                   self.make_bts_friendly(current_bts),
                                   channel["site_name"])
                    alert = self.alerts.build_alert(110, message)
                    results_set.append(alert)
                    self.prior_bts = dict(current_bts)
        return results_set

    def make_bts_friendly(self, bts_struct):
        """ Expecting a dict with keys for mcc, mnc, lac, cellid"""
        retval = "%s:%s:%s:%s" % (str(bts_struct["mcc"]),
                                  str(bts_struct["mnc"]),
                                  str(bts_struct["lac"]),
                                  str(bts_struct["cellid"]))
        return retval

    def get_feed_info(self, mcc, mnc, lac, cellid):
        if self.feed_cache != []:
            for x in self.feed_cache:
                if (x["mcc"] == mcc and
                        x["mnc"] == mnc and
                        x["lac"] == lac and
                        x["cellid"] == cellid):
                    return x
            feed_string = "%s:%s:%s:%s" % (mcc, mnc, lac, cellid)
            print "EnrichGSM: Cache miss!  Attempt to match %s from feed..." % feed_string
        normalized = self.get_feed_info_from_files(mcc, mnc, lac, cellid)
        self.feed_cache.append(normalized)
        return normalized

    def get_feed_info_from_files(self, mcc, mnc, lac, cellid):
        """ Field names get changed when loaded into the cache, to
        match field IDs used elsewhere. """
        feed_file = self.construct_feed_file_name(self.feed_dir, mcc)
        with gzip.open(feed_file, 'r') as feed_data:
            consumer = csv.DictReader(feed_data)
            for cell in consumer:
                if (cell["mcc"] == mcc and
                        cell["net"] == mnc and
                        cell["area"] == lac and
                        cell["cell"] == cellid):
                    normalzed = self.normalize_feed_info_for_cache(cell)
                    return normalzed
        """If unable to locate cell in file, we populate the
        cache with obviously fake values """
        cell = {"mcc": mcc, "net": mnc, "area": lac, "cell": cellid,
                "lon": 0, "lat": 0, "range": 0}
        normalized = self.normalize_feed_info_for_cache(cell)
        return normalized

    @classmethod
    def normalize_feed_info_for_cache(cls, feed_item):
        cache_item = {}
        cache_item["mcc"] = feed_item["mcc"]
        cache_item["mnc"] = feed_item["net"]
        cache_item["lac"] = feed_item["area"]
        cache_item["cellid"] = feed_item["cell"]
        cache_item["lon"] = feed_item["lon"]
        cache_item["lat"] = feed_item["lat"]
        cache_item["range"] = feed_item["range"]
        return cache_item

    @classmethod
    def construct_feed_file_name(cls, feed_dir, mcc):
        file_name = "%s.csv.gz" % mcc
        dest_file_name = os.path.join(feed_dir, file_name)
        return dest_file_name

    @classmethod
    def convert_hex_targets(cls, channel):
        for target in ['lac', 'cellid']:
            if target in channel:
                channel[target] = GsmModemEnricher.hex_to_dec(channel[target])
        return channel

    @classmethod
    def convert_float_targets(cls, channel):
        for target in ['rxq', 'rxl']:
            if target in channel:
                channel[target] = GsmModemEnricher.hex_to_dec(channel[target])
        return channel

    @classmethod
    def hex_to_dec(cls, hx):
        integer = int(hx, 16)
        return str(integer)
