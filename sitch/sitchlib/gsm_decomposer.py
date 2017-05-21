"""Decompose GSM scans."""

from utility import Utility


class GsmDecomposer(object):
    """Decomposes GSM scans."""

    @classmethod
    def decompose(cls, scan_document):
        """Turn one scan document into a list of channel scan documents.

        Args:
            scan_document (dict): GSM modem scan.

        Returns:
            list: List of tuples.  First position in tuple identifies scan
                type.  Second position is the actual scan data.
        """
        results_set = [("cell", scan_document)]
        scan_items = scan_document["scan_results"]
        for channel in scan_items:
            try:
                channel = GsmDecomposer.enrich_channel_with_scan(channel,
                                                                 scan_document)
                # channel["arfcn_int"] = GsmDecomposer.arfcn_int(channel["arfcn"])  # NOQA
                if channel["arfcn"] == 0 and channel["cell"] != 0:
                    continue  # If the data is incomplete, we don't forward
                # Now we bring the hex values to decimal...
                channel = GsmDecomposer.convert_hex_targets(channel)
                channel = GsmDecomposer.convert_float_targets(channel)
                # Setting CGI identifiers
                channel["cgi_str"] = GsmDecomposer.make_bts_friendly(channel)
                channel["cgi_int"] = GsmDecomposer.get_cgi_int(channel)
                chan_enriched = ('gsm_modem_channel', channel)
                results_set.append(chan_enriched)
            except Exception as e:
                print("Exception caught in GsmDecomposer: %s for channel %s in %s" % (e, str(channel), str(scan_document)))  # NOQA

        return results_set

    @classmethod
    def enrich_channel_with_scan(cls, channel, scan_document):
        """Enrich channel with scan document metadata."""
        channel["band"] = scan_document["band"]
        channel["scan_finish"] = scan_document["scan_finish"]
        channel["site_name"] = scan_document["site_name"]
        channel["sensor_id"] = scan_document["sensor_id"]
        channel["sensor_name"] = scan_document["sensor_name"]
        channel["scanner_public_ip"] = scan_document["scanner_public_ip"]
        channel["event_timestamp"] = scan_document["scan_finish"]
        return channel

    @classmethod
    def get_cgi_int(cls, channel):
        """Attempt to create an integer representation of CGI."""
        try:
            cgi_int = int(channel["cgi_str"].replace(':', ''))
        except:
            print("EnrichGSM: Unable to convert CGI to int")
            print(channel["cgi_str"])
            cgi_int = 0
        return cgi_int

    @classmethod
    def bts_from_channel(cls, channel):
        """Return clean BTS from channel."""
        bts = {"mcc": channel["mcc"],
               "mnc": channel["mnc"],
               "lac": channel["lac"],
               "cellid": channel["cellid"]}
        return bts

    @classmethod
    def make_bts_friendly(cls, bts_struct):
        """Expect a dict with keys for mcc, mnc, lac, cellid."""
        retval = "%s:%s:%s:%s" % (str(bts_struct["mcc"]),
                                  str(bts_struct["mnc"]),
                                  str(bts_struct["lac"]),
                                  str(bts_struct["cellid"]))
        return retval

    @classmethod
    def convert_hex_targets(cls, channel):
        """Convert LAC anc CellID from hex to decimal."""
        for target in ['lac', 'cellid']:
            if target in channel:
                channel[target] = Utility.hex_to_dec(channel[target])
        return channel

    @classmethod
    def convert_float_targets(cls, channel):
        """Convert rxq and rxl to float."""
        for target in ['rxq', 'rxl']:
            if target in channel:
                channel[target] = Utility.val_to_float(channel[target])
        return channel
