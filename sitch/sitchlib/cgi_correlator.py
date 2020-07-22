"""CGI Correlator module."""

import os
import sqlite3
from . import alert_manager
from .utility import Utility


class CgiCorrelator:
    """The CgiCorrelator compares CGI addressing against the OpenCellID DB.

    The feed data is put in place by the FeedManager class, prior to
    instantiating the CgiCorrelator.
    """

    def __init__(self, feed_dir, cgi_whitelist, mcc_list, device_id):
        """Initializing CgiCorrelator.

        Args:
            feed_dir (str): Directory where feed files can be found
            cgi_whitelist (list): List of CGIs to not alert on

        """
        self.feed_dir = feed_dir
        self.alerts = alert_manager.AlertManager(device_id)
        self.prior_bts = {}
        self.state = {"type": "Point", "coordinates": [0, 0]}
        self.feed_cache = []
        self.good_cgis = []
        self.bad_cgis = []
        self.mcc_list = mcc_list
        self.cgi_whitelist = cgi_whitelist
        self.cgi_db = os.path.join(feed_dir, "cgi.db")
        self.alarm_140_cache = ""
        print(CgiCorrelator.cgi_whitelist_message(self.cgi_whitelist))

    def correlate(self, scan_bolus):
        """Entrypoint for the CGI correlation component.

        Args:
            scan_bolus (tuple):  scan_bolus[0] contains the scan type.  If
                the type is 'gps', it will set the correlator's geo location.
                For other scan types, we expect them to look like
                gsm_modem_channel events, and they are compared against the
                feed database as well as state history, tracking things
                like the current active cell's CGI.

        Returns:
            list: Returns a list of tuples, representing alerts.  If no alerts
                fire, the list will be empty.
        """
        retval = []
        if scan_bolus[0] == "gps":
            self.state = scan_bolus[1]["location"]
        elif scan_bolus[0] == "cell":
            retval = self.check_scan_document(scan_bolus[1])
            scan_bolus[1]["location"] = self.state
            retval.append(scan_bolus)
        elif scan_bolus[0] != "gsm_modem_channel":
            print("CgiCorrelator: Unsupported scan type: %s" % str(scan_bolus[0]))  # NOQA
            pass
        else:
            channel = scan_bolus[1]
            if channel["mcc"] in ["", None]:
                return retval  # We don't correlate incomplete CGIs...
            # Here's the feed comparison part:
            channel["feed_info"] = self.get_feed_info(channel["mcc"],
                                                      channel["mnc"],
                                                      channel["lac"],
                                                      channel["cellid"])
            chan, here = CgiCorrelator.build_chan_here(channel, self.state)
            channel["distance"] = Utility.calculate_distance(chan["lon"],
                                                             chan["lat"],
                                                             here["lon"],
                                                             here["lat"])
            channel["location"] = self.state
            # In the event we have incomplete information, bypass comparison.
            skip_feed_comparison = CgiCorrelator.should_skip_feed(channel)
            if skip_feed_comparison is False:
                if channel["mcc"] not in self.mcc_list:
                    msg = ("MCC %s should not be observed by sensor at %s / %s. ARFCN: %s CGI: %s Cell Priority: %s" %  # NOQA
                           (channel["mcc"], channel["site_name"],
                            channel["sensor_name"], channel["arfcn"],
                            channel["cgi_str"], channel["cell"]))
                    alert = self.alerts.build_alert(130, msg, self.state)
                    alert[1]["site_name"] = channel["site_name"]
                    alert[1]["sensor_name"] = channel["sensor_name"]
                    alert[1]["sensor_id"] = channel["sensor_id"]
                    retval.append(alert)
                feed_comparison_results = self.feed_comparison(channel)
                for feed_alert in feed_comparison_results:
                    retval.append(feed_alert)
            retval.append(scan_bolus)
        return retval

    def check_scan_document(self, scan_document):
        """Check to see if there are no in-LAI neighbors for channel 0

        """
        results = []
        chan_0 = self.get_cell_by_id(scan_document, 0)
        chan_1 = self.get_cell_by_id(scan_document, 1)
        chan_0_lai = self.get_lai_for_channel(chan_0)
        chan_1_lai = self.get_lai_for_channel(chan_1)
        chan_0_cgi = self.make_bts_friendly(self.get_cell_by_id(scan_document,
                                                                0))
        chan_1_cgi = self.make_bts_friendly(self.get_cell_by_id(scan_document,
                                                                1))
        cache_compare = "%s  %s" % (chan_0_lai, chan_1_lai)
        if cache_compare == self.alarm_140_cache:
            # We've already flagged this, no need to alert every 2s
            return results
        if "::" in chan_1_lai:
            message = "Serving cell has no neighbor at %s / %s!  Serving cell: %s" % (scan_document["site_name"], scan_document["sensor_name"], chan_0_cgi)  # NOQA
            alert = self.alerts.build_alert(141, message, self.state)
            alert[1]["site_name"] = scan_document["site_name"]
            alert[1]["sensor_name"] = scan_document["sensor_name"]
            alert[1]["sensor_id"] = scan_document["sensor_id"]
            results.append(alert)
            self.alarm_141_cache = cache_compare
        elif chan_0_lai != chan_1_lai:
            message = "Preferred neighbor outside of LAI at %s / %s! Serving cell CGI: %s Next neighbor CGI: %s" % (scan_document["site_name"], scan_document["sensor_name"], chan_0_cgi, chan_1_cgi)  # NOQA
            alert = self.alerts.build_alert(140, message, self.state)
            alert[1]["site_name"] = scan_document["site_name"]
            alert[1]["sensor_name"] = scan_document["sensor_name"]
            alert[1]["sensor_id"] = scan_document["sensor_id"]
            results.append(alert)
            self.alarm_140_cache = cache_compare
        else:
            # If we've gotten this far, we've established that we're not still
            # in an identical alarm state (cache compare), and the LAIs
            # of the primary and secondary cells are the same.  So we
            # reset the alarm cache for this alert.
            self.alarm_140_cache = ""
            self.alarm_141_cache = ""
        return results

    @classmethod
    def get_lai_for_channel(cls, channel):
        chan_clean = cls.convert_hex_targets(channel)
        lai = ":".join([chan_clean["mcc"], chan_clean["mnc"],
                        chan_clean["lac"]])
        return lai

    @classmethod
    def get_cell_by_id(cls, scan_document, cell_no):
        """Get cell from doc by ID"""
        for cell in scan_document["scan_results"]:
            if cell["cell"] == cell_no:
                return cell
        raise ValueError("CgiCorrelator: No cell by ID for %s in %s" % (cell_no, scan_document))  # NOQA

    @classmethod
    def cgi_whitelist_message(cls, cgi_wl):
        """Format and return the CGI whitelist initialization message.

        Args:
            cgi_wl (list): CGI whitelist

        Returns:
            str: Formatted message
        """
        wl_string = ",".join(cgi_wl)
        message = "CgiCorrelator: Initializing with CGI whitelist: %s" % wl_string  # NOQA
        return message

    @classmethod
    def should_skip_feed(cls, channel):
        """Examine channel info to determine if feed comparison should happen.

        Args:
            channel (dict): Channel information.

        Returns:
            bool: True if channel information is complete, False if not.
        """
        skip_feed_comparison = False
        skip_feed_trigger_values = ['000', '0000', '00', '0', None]
        for x in ["mcc", "mnc", "lac", "cellid"]:
            if channel[x] in skip_feed_trigger_values:
                skip_feed_comparison = True
        return skip_feed_comparison

    @classmethod
    def get_cgi_int(cls, channel):
        """Attempt to create an integer representation of CGI."""
        try:
            cgi_int = int(channel["cgi_str"].replace(':', ''))
        except:
            print("CgiCorrelator: Unable to convert CGI to int")
            print(channel["cgi_str"])
            cgi_int = 0
        return cgi_int

    @classmethod
    def build_chan_here(cls, channel, state):
        """Build geo information for channel, to aid in geo correlation.

        Args:
            channel (dict): Channel metadata
            state (dict): Geo-json representing the current location of the
                sensor

        Returns:
            dict: Original channel structure, with the current sensor location
                embedded.
        """
        chan = {}
        here = {}
        try:
            chan["lat"] = float(channel["feed_info"]["lat"])
            chan["lon"] = float(channel["feed_info"]["lon"])
            here["lat"] = state["coordinates"][1]
            here["lon"] = state["coordinates"][0]
        except (TypeError, ValueError, KeyError) as e:
            print("CgiCorrelator: Incomplete geo info...")
            print("CgiCorrelator: Error: %s" % str(e))
            chan["lat"] = 0
            chan["lon"] = 0
            here["lat"] = 0
            here["lon"] = 0
        return(chan, here)

    @classmethod
    def channel_in_feed_db(cls, channel):
        """Return True if channel geo metadata is complete."""
        result = True
        if (channel["feed_info"]["range"] == 0 and
                channel["feed_info"]["lon"] == 0 and
                channel["feed_info"]["lat"] == 0):
            result = False
        return result

    @classmethod
    def channel_out_of_range(cls, channel):
        """Check to see if sensor is out of range for CGI.

        Args:
            channel (dict): Channel metadata

        Returns:
            bool: True if the sensor is in range of the detected CGI
        """
        result = False
        if int(channel["distance"]) > int(channel["feed_info"]["range"]):
            result = True
        return result

    @classmethod
    def bts_from_channel(cls, channel):
        """Create a simplified representation of BTS metadata.

        Args:
            channel (dict):

        Returns:
            dict: Contains MCC, MNC, LAC, and cellid

        """
        bts = {"mcc": channel["mcc"],
               "mnc": channel["mnc"],
               "lac": channel["lac"],
               "cellid": channel["cellid"]}
        return bts

    @classmethod
    def primary_bts_changed(cls, prior_bts, channel, cgi_whitelist):
        """Create alarms if primary BTS metadats changed.

        Args:
            prior_bts (str): Current primary BTS
            channel (dict): Channel metadata
            cgi_whitelist: Whitelist of CGIs to NOT alert on

        Returns:
            bool: True if the primary BTS has changed and the new BTS in not
                on the whitelist. False otherwise.

        """
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
        """Compare channel metadata against the feed DB.

        This function wraps a few checks against the feed DB.  It first checks
            if the bts is in the feed DB.  Next, it checks that the sensor is
            within range of the BTS in the feed DB.  Finally, if it's the
            primary channel, it checks to see if the primary BTS has changed.

        Args:
            channel (dict): Channel, enriched with geo information

        Returns:
            list: If alarms are generated, they'll be returned in a list of
                tuples.  Otherwise, an empty list comes back.

        """
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
        if channel["cell"] == 0:
            comparison_results.append(self.process_cell_zero(channel))
        for result in comparison_results:
            if result != ():
                result[1]["site_name"] = channel["site_name"]
                result[1]["sensor_name"] = channel["sensor_name"]
                result[1]["sensor_id"] = channel["sensor_id"]
                retval.append(result)
        if len(retval) == 0:
            if channel["cgi_str"] not in self.good_cgis:
                self.good_cgis.append(channel["cgi_str"])
        return retval

    def check_channel_against_feed(self, channel):
        """Determine whether or not to fire an alert for CGI presence in feed.

        Args:
            channel (dict): Channel metadata

        Returns:
            tuple: Empty if there is no alert, a two-item tuple if an alert
                is generated.

        """
        alert = ()
        if CgiCorrelator.channel_in_feed_db(channel) is False:
            bts_info = "ARFCN: %s CGI: %s" % (channel["arfcn"],
                                              channel["cgi_str"])
            message = "BTS not in feed database! Info: %s Sensor: %s / %s" % (
                bts_info, str(channel["site_name"]),
                str(channel["sensor_name"]))
            if channel["cgi_str"] not in self.bad_cgis:
                self.bad_cgis.append(channel["cgi_str"])
            alert = self.alerts.build_alert(120, message, self.state)
        return alert

    def check_channel_range(self, channel):
        """Check to see if the detected CGI is in range.

        Args:
            channel (dict): Channel metadata, enriched with feed info.

        Returns:
            tuple: Empry if no alert is generated.  A two-item tuple if an
                alert condition is detected.

        """
        alert = ()
        if CgiCorrelator.channel_out_of_range(channel):
            message = ("ARFCN: %s Expected range: %s Actual distance:" +
                       " %s CGI: %s Sensor: %s / %s") % (
                           channel["arfcn"],
                           str(channel["feed_info"]["range"]),  # NOQA
                           str(channel["distance"]),
                           channel["cgi_str"],
                           channel["site_name"],
                           channel["sensor_name"])
            if channel["cgi_str"] not in self.bad_cgis:
                self.bad_cgis.append(channel["cgi_str"])
            alert = self.alerts.build_alert(100, message, self.state)
        return alert

    def process_cell_zero(self, channel):
        """Process channel zero.

        Args:
            channel (dict): Channel metadata.

        Returns:
            tuple: Empry if there is no alert, a two-item tuple if an alert
                condition is detected.
        """
        alert = ()
        current_bts = CgiCorrelator.bts_from_channel(channel)
        if CgiCorrelator.primary_bts_changed(self.prior_bts, channel,
                                             self.cgi_whitelist):
            msg = ("Primary BTS was %s " +
                   "now %s. Sensor: %s / %s") % (
                    CgiCorrelator.make_bts_friendly(self.prior_bts),
                    CgiCorrelator.make_bts_friendly(current_bts),
                    channel["site_name"],
                    channel["sensor_name"])
            alert = self.alerts.build_alert(110, msg, self.state)
        self.prior_bts = dict(current_bts)
        return alert

    @classmethod
    def make_bts_friendly(cls, bts_struct):
        """Create a human-friendly representation of CGI.

        Args:
            bts_struct (dict): Simple structure containing CGI components.

        Returns:
            str: String reperesentation of CGI, with items being
                colon-separated.
        """
        retval = "%s:%s:%s:%s" % (str(bts_struct["mcc"]),
                                  str(bts_struct["mnc"]),
                                  str(bts_struct["lac"]),
                                  str(bts_struct["cellid"]))
        return retval

    def get_feed_info(self, mcc, mnc, lac, cellid):
        """Check CGI against cache, then against the feed DB.

        Args:
            mcc (str): Mobile Country Code
            mnc (str): Mobile Network Code
            lac (str): Location Area Code
            cellid (str): Cell ID

        Returns:
            dict: Dictionary containing feed information for CGI
        """
        if self.feed_cache != []:
            for x in self.feed_cache:
                if CgiCorrelator.cell_matches(x, mcc, mnc,
                                              lac, cellid):
                    return x
            feed_string = "%s:%s:%s:%s" % (mcc, mnc, lac, cellid)
            msg = "CgiCorrelator: Cache miss: %s" % feed_string
            print(msg)
        normalized = self.get_feed_info_from_db(mcc, mnc, lac, cellid)
        self.feed_cache.append(normalized)
        return normalized

    def get_feed_info_from_db(self, mcc, mnc, lac, cellid):
        """Interrogate DB for CGI information.

        Args:
            (str): Mobile Country Code
            mnc (str): Mobile Network Code
            lac (str): Location Area Code
            cellid (str): Cell ID

        Returns:
            dict: Dictionary containing feed information for CGI.  If no
                information exists, the feed geo information will be zeroed
                out...
        """
        try:
            conn = sqlite3.connect(self.cgi_db)
            c = conn.cursor()
            c.execute("SELECT mcc, net, area, cell, lon, lat, range FROM cgi WHERE mcc=? AND net=? AND area=? AND cell=?",  # NOQA
                      (mcc, mnc, lac, cellid))
            result = c.fetchone()
            if result:
                cell = {"mcc": result[0], "net": result[1], "area": result[2],
                        "cell": result[3], "lon": result[4], "lat": result[5],
                        "range": int(result[6])}
            else:
                cell = {"mcc": mcc, "net": mnc, "area": lac, "cell": cellid,
                        "lon": 0, "lat": 0, "range": 0}
            conn.close()
        except sqlite3.OperationalError as e:
            print("CgiCorrelator: Unable to access CGI database! %s" % e)
            cell = {"mcc": mcc, "net": mnc, "area": lac, "cell": cellid,
                    "lon": 0, "lat": 0, "range": 0}
        normalized = self.normalize_feed_info_for_cache(cell)
        return normalized

    @classmethod
    def cell_matches(cls, cell, mcc, mnc, lac, cellid):
        """Compare cell metadata against mcc, mnc, lac, cellid."""
        result = False
        if (cell["mcc"] == mcc and
                cell["mnc"] == mnc and
                cell["lac"] == lac and
                cell["cellid"] == cellid):
            result = True
        return result

    @classmethod
    def normalize_feed_info_for_cache(cls, feed_item):
        """Normalize field keys for the feed cache."""
        cache_item = {}
        cache_item["mcc"] = feed_item["mcc"]
        cache_item["mnc"] = feed_item["net"]
        cache_item["lac"] = feed_item["area"]
        cache_item["cellid"] = feed_item["cell"]
        cache_item["lon"] = float(feed_item["lon"])
        cache_item["lat"] = float(feed_item["lat"])
        cache_item["range"] = feed_item["range"]
        return cache_item

    @classmethod
    def convert_hex_targets(cls, channel):
        """Convert lac and cellid from hex to decimal."""
        for target in ['lac', 'cellid']:
            if target in channel:
                channel[target] = Utility.hex_to_dec(channel[target])
        return channel

    @classmethod
    def convert_float_targets(cls, channel):
        """Convert string values for rxq and rxl to floating point."""
        for target in ['rxq', 'rxl']:
            if target in channel:
                channel[target] = Utility.str_to_float(channel[target])
        return channel
