import csv
import gzip
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

    @classmethod
    def enrich_channel_with_scan(cls, channel, scan_document):
        """ Enriches channel with scan document metadata """
        channel["band"] = scan_document["band"]
        channel["scan_finish"] = scan_document["scan_finish"]
        channel["site_name"] = scan_document["scan_location"]["name"]
        channel["scanner_public_ip"] = scan_document["scanner_public_ip"]
        return channel

    @classmethod
    def arfcn_int(cls, arfcn):
        """ Attempts to derive an integer representation of ARFCN, or return
        zero if unable to convert.
        """
        try:
            arfcn_int = int(arfcn)
        except:
            msg = "EnrichGSM: Unable to convert ARFCN to int"
            print(msg)
            print(arfcn)
            arfcn_int = 0
        return arfcn_int

    @classmethod
    def should_skip_feed(cls, channel):
        skip_feed_comparison = False
        skip_feed_trigger_values = ['', '0000', '00', '0']
        for x in ["mcc", "mnc", "lac", "cellid"]:
            if channel[x] in skip_feed_trigger_values:
                skip_feed_comparison = True
        return skip_feed_comparison

    @classmethod
    def get_cgi_int(cls, channel):
        """ Attempts to create an integer representation of CGI """
        try:
            cgi_int = int(channel["cgi_str"].replace(':', ''))
        except:
            print("EnrichGSM: Unable to convert CGI to int")
            print(channel["cgi_str"])
            cgi_int = 0
        return cgi_int

    @classmethod
    def build_chan_here(cls, channel, state):
        chan = {}
        here = {}
        try:
            chan["lat"] = channel["feed_info"]["lat"]
            chan["lon"] = channel["feed_info"]["lon"]
            here["lat"] = state["gps"]["geometry"]["coordinates"][0]
            here["lon"] = state["gps"]["geometry"]["coordinates"][1]
        except (TypeError, ValueError):
            print("EnrichGSM: Incomplete geo info...")
            chan["lat"] = None
            chan["lon"] = None
            here["lat"] = None
            here["lon"] = None
        return(chan, here)

    @classmethod
    def channel_in_feed_db(cls, channel):
        result = True
        if (channel["feed_info"]["range"] == 0 and
            channel["feed_info"]["lon"] == 0 and
            channel["feed_info"]["lat"] == 0):
           result = False
        return result

    @classmethod
    def channel_out_of_range(cls, channel):
        result = False
        if int(channel["distance"]) > int(channel["feed_info"]["range"]):
            result = True
        return result

    @classmethod
    def bts_from_channel(cls, channel):
        bts = {"mcc": channel["mcc"],
               "mnc": channel["mnc"],
               "lac": channel["lac"],
               "cellid": channel["cellid"]}
        return bts

    @classmethod
    def primary_bts_changed(cls, prior_bts, channel):
        result = False
        current_bts = GsmModemEnricher.bts_from_channel(channel)
        if prior_bts == {}:
            pass
        elif prior_bts != current_bts:
            result = True
        return result


    def enrich_gsm_modem_scan(self, scan_document):
        chan = {}
        here = {}
        state = self.state
        results_set = [("cell", scan_document)]
        scan_items = scan_document["scan_results"]
        for channel in scan_items:
            channel = GsmModemEnricher.enrich_channel_with_scan(channel,
                                                                scan_document)
            channel["arfcn_int"] = GsmModemEnricher.arfcn_int(channel["arfcn"])
            # In the event we have incomplete information, bypass comparison.
            skip_feed_comparison = GsmModemEnricher.should_skip_feed(channel)
            # Now we bring the hex values to decimal...
            channel = self.convert_hex_targets(channel)
            channel = self.convert_float_targets(channel)
            # Setting CGI identifiers
            channel["cgi_str"] = GsmModemEnricher.make_bts_friendly(channel)
            channel["cgi_int"] = GsmModemEnricher.get_cgi_int(channel)
            """ Here's the feed comparison part """
            if skip_feed_comparison is False:
                channel["feed_info"] = self.get_feed_info(channel["mcc"],
                                                          channel["mnc"],
                                                          channel["lac"],
                                                          channel["cellid"])
                chan, here = GsmModemEnricher.build_chan_here(channel, state)
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
            results_set.append(self.check_channel_against_feed(channel))
            # Else, be willing to alert if channel is not in range
            results_set.append(self.check_channel_range(channel))
            # Test for primary BTS change
            if channel["cell"] == '0':
                results_set.append(self.process_cell_zero(channel))
        return results_set

    def check_channel_against_feed(self, channel):
        alert = ("null", "channel_against_feed clean")
        if GsmModemEnricher.channel_in_feed_db(channel) is False:
            bts_info = "ARFCN: %s CGI: %s" % (channel["arfcn"],
                                              channel["cgi_str"])
            message = "BTS not in feed database! Info: %s Site: %s" % (
                bts_info, str(channel["site_name"]))
            alert = self.alerts.build_alert(120, message)
        return alert

    def check_channel_range(self, channel):
        alert = ("null", "channel_range clean")
        if GsmModemEnricher.channel_out_of_range(channel):
            message = ("ARFCN: %s Expected range: %s Actual distance:" +
                       " %s CGI: %s Site: %s") % ( channel["arfcn"],
                       str(channel["feed_info"]["range"]),
                       str(channel["distance"]),
                       channel["cgi_str"],
                       channel["site_name"])
            alert = self.alerts.build_alert(100, message)
        return alert

    def process_cell_zero(self, channel):
        """ Accepts channel (zero) as arg, returns a list which will
        be populated with any alerts we decide to fire """
        alert = ("null", "cell_zero clean")
        current_bts = GsmModemEnricher.bts_from_channel(channel)
        if GsmModemEnricher.primary_bts_changed(self.prior_bts, channel):
            msg = ("Primary BTS was %s " +
                   "now %s. Site: %s") % (
                    GsmModemEnricher.make_bts_friendly(self.prior_bts),
                    GsmModemEnricher.make_bts_friendly(current_bts),
                    channel["site_name"])
            alert = self.alerts.build_alert(110, msg)
            self.prior_bts = dict(current_bts)
        return alert


    @classmethod
    def make_bts_friendly(cls, bts_struct):
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
            msg = "EnrichGSM: Cache miss: %s" % feed_string
            print(msg)
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
