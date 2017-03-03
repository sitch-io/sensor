import csv
import gzip
import alert_manager
from utility import Utility


class CgiCorrelator(object):
    def __init__(self, feed_dir, cgi_whitelist):
        self.feed_dir = feed_dir
        self.alerts = alert_manager.AlertManager()
        self.prior_bts = {}
        self.state = {"geometry": {"coordinates": [0, 0]}}
        self.feed_cache = []
        self.good_cgis = []
        self.bad_cgis = []
        self.cgi_whitelist = cgi_whitelist
        print(CgiCorrelator.cgi_whitelist_message(self.cgi_whitelist))
        return

    def correlate(self, scan_bolus):
        retval = []
        if scan_bolus[0] == "gps":
            self.state = scan_bolus[1]
        elif scan_bolus[0] != "gsm_modem_channel":
            print("CgiCorrelator: Unsupported scan type: %s" % scan_bolus[0])
            pass
        else:
            channel = scan_bolus[1]
            if channel["mcc"] in ["", None]:
                return retval  # We don't correlate incomplete CGIs...
            channel["arfcn_int"] = CgiCorrelator.arfcn_int(channel["arfcn"])
            # Now we bring the hex values to decimal...
            channel = self.convert_hex_targets(channel)
            channel = self.convert_float_targets(channel)
            # Setting CGI identifiers
            channel["cgi_str"] = CgiCorrelator.make_bts_friendly(channel)
            channel["cgi_int"] = CgiCorrelator.get_cgi_int(channel)
            """ Here's the feed comparison part """
            channel["feed_info"] = self.get_feed_info(channel["mcc"],
                                                      channel["mnc"],
                                                      channel["lac"],
                                                      channel["cellid"])
            chan, here = CgiCorrelator.build_chan_here(channel, self.state)
            channel["distance"] = Utility.calculate_distance(chan["lon"],
                                                             chan["lat"],
                                                             here["lon"],
                                                             here["lat"])
            # In the event we have incomplete information, bypass comparison.
            skip_feed_comparison = CgiCorrelator.should_skip_feed(channel)
            if skip_feed_comparison is False:
                feed_comparison_results = self.feed_comparison(channel)
                for feed_alert in feed_comparison_results:
                    retval.append(feed_alert)
        return retval

    @classmethod
    def cgi_whitelist_message(cls, cgi_wl):
        wl_string = ",".join(cgi_wl)
        message = "CgiCorrelator: Initializing with CGI whitelist: %s" % wl_string
        return message

    @classmethod
    def arfcn_int(cls, arfcn):
        """ Attempts to derive an integer representation of ARFCN, or return
        zero if unable to convert.
        """
        try:
            arfcn_int = int(arfcn)
        except:
            msg = "CgiCorrelator: Unable to convert ARFCN to int"
            print(msg)
            print(arfcn)
            arfcn_int = 0
        return arfcn_int

    @classmethod
    def should_skip_feed(cls, channel):
        skip_feed_comparison = False
        skip_feed_trigger_values = ['', '0000', '00', '0', None]
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
            print("CgiCorrelator: Unable to convert CGI to int")
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
            here["lat"] = state["geometry"]["coordinates"][0]
            here["lon"] = state["geometry"]["coordinates"][1]
        except (TypeError, ValueError, KeyError) as e:
            print("CgiCorrelator: Incomplete geo info...")
            print("CgiCorrelator: Error: %s" % str(e))
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
    def primary_bts_changed(cls, prior_bts, channel, cgi_whitelist):
        result = False
        current_bts = CgiCorrelator.bts_from_channel(channel)
        cgi_string = channel["cgi_str"]
        if prior_bts == {}:
            pass
        elif cgi_string in cgi_whitelist:
            pass
        elif prior_bts != current_bts:
            result = True
        return result


    def feed_comparison(self, channel):
        comparison_results = []
        retval = []
        # Alert if tower is not in feed DB
        if (channel["cgi_str"] not in self.bad_cgis and
            channel["cgi_str"] not in self.cgi_whitelist and
            channel["cgi_str"] not in self.good_cgis):
            comparison_results.append(self.check_channel_against_feed(channel))
        # Else, be willing to alert if channel is not in range
        if (channel["cgi_str"] not in self.bad_cgis and
            channel["cgi_str"] not in self.cgi_whitelist and
            channel["cgi_str"] not in self.good_cgis):
            comparison_results.append(self.check_channel_range(channel))
        # Test for primary BTS change
        if channel["cell"] == '0':
            comparison_results.append(self.process_cell_zero(channel))
        for result in comparison_results:
            if result != ():
                retval.append(result)
        if len(retval) == 0:
            print("Clean CGI: %s" % channel["cgi_str"])
            if channel["cgi_str"] not in self.good_cgis:
                self.good_cgis.append(channel["cgi_str"])
        else:
            print("Dirty CGI: %s" % channel["cgi_str"])
            print(str(retval))
        return retval


    def check_channel_against_feed(self, channel):
        alert = ()
        if CgiCorrelator.channel_in_feed_db(channel) is False:
            bts_info = "ARFCN: %s CGI: %s" % (channel["arfcn"],
                                              channel["cgi_str"])
            message = "BTS not in feed database! Info: %s Site: %s" % (
                bts_info, str(channel["site_name"]))
            if channel["cgi_str"] not in self.bad_cgis:
                self.bad_cgis.append(channel["cgi_str"])
            alert = self.alerts.build_alert(120, message)
        return alert

    def check_channel_range(self, channel):
        alert = ()
        if CgiCorrelator.channel_out_of_range(channel):
            message = ("ARFCN: %s Expected range: %s Actual distance:" +
                       " %s CGI: %s Site: %s") % ( channel["arfcn"],
                       str(channel["feed_info"]["range"]),
                       str(channel["distance"]),
                       channel["cgi_str"],
                       channel["site_name"])
            if channel["cgi_str"] not in self.bad_cgis:
                self.bad_cgis.append(channel["cgi_str"])
            alert = self.alerts.build_alert(100, message)
        return alert

    def process_cell_zero(self, channel):
        """ Accepts channel (zero) as arg, returns a list which will
        be populated with any alerts we decide to fire """
        alert = ()
        current_bts = CgiCorrelator.bts_from_channel(channel)
        if CgiCorrelator.primary_bts_changed(self.prior_bts, channel,
                                                self.cgi_whitelist):
            msg = ("Primary BTS was %s " +
                   "now %s. Site: %s") % (
                    CgiCorrelator.make_bts_friendly(self.prior_bts),
                    CgiCorrelator.make_bts_friendly(current_bts),
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
                if CgiCorrelator.cell_matches(x, mcc, mnc,
                                                 lac, cellid):
                    return x
            feed_string = "%s:%s:%s:%s" % (mcc, mnc, lac, cellid)
            msg = "CgiCorrelator: Cache miss: %s" % feed_string
            print(msg)
        normalized = self.get_feed_info_from_files(mcc, mnc, lac, cellid)
        self.feed_cache.append(normalized)
        return normalized

    @classmethod
    def cell_matches(cls, cell, mcc, mnc, lac, cellid):
        result = False
        if (cell["mcc"] == mcc and
            cell["mnc"] == mnc and
            cell["lac"] == lac and
            cell["cellid"] == cellid):
            result = True
        return result

    def get_feed_info_from_files(self, mcc, mnc, lac, cellid):
        """ Field names get changed when loaded into the cache, to
        match field IDs used elsewhere. """
        feed_file = Utility.construct_feed_file_name(self.feed_dir, mcc)
        try:
            with gzip.open(feed_file, 'r') as feed_data:
                consumer = csv.DictReader(feed_data)
                for cell in consumer:
                    normalized = self.normalize_feed_info_for_cache(cell)
                    if CgiCorrelator.cell_matches(normalized, mcc, mnc,
                                                     lac, cellid):
                        return normalized
        except IOError as e:
            msg = "CgiCorrelator: Unable to open feed for %s!\n\t%s" % (str(mcc),  # NOQA
                                                                        str(e))
            print(msg)
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
    def convert_hex_targets(cls, channel):
        for target in ['lac', 'cellid']:
            if target in channel:
                channel[target] = Utility.hex_to_dec(channel[target])
        return channel

    @classmethod
    def convert_float_targets(cls, channel):
        for target in ['rxq', 'rxl']:
            if target in channel:
                channel[target] = Utility.str_to_float(channel[target])
        return channel
