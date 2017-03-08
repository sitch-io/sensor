from utility import Utility


class GsmDecomposer(object):
    @classmethod
    def decompose(cls, scan_document):
        results_set = [("cell", scan_document)]
        scan_items = scan_document["scan_results"]
        for channel in scan_items:
            try:
                channel = GsmDecomposer.enrich_channel_with_scan(channel,
                                                                 scan_document)
                channel["arfcn_int"] = GsmDecomposer.arfcn_int(channel["arfcn"])
                # Now we bring the hex values to decimal...
                channel = GsmDecomposer.convert_hex_targets(channel)
                channel = GsmDecomposer.convert_float_targets(channel)
                # Setting CGI identifiers
                channel["cgi_str"] = GsmDecomposer.make_bts_friendly(channel)
                channel["cgi_int"] = GsmDecomposer.get_cgi_int(channel)
                chan_enriched = ('gsm_modem_channel', channel)
                results_set.append(chan_enriched)
            except Exception as e:
                print("Exception caught in GsmDecomposer: %s for message %s" % (e, str(channel)))

        return results_set

    @classmethod
    def enrich_channel_with_scan(cls, channel, scan_document):
        """ Enriches channel with scan document metadata """
        channel["band"] = scan_document["band"]
        channel["scan_finish"] = scan_document["scan_finish"]
        channel["site_name"] = scan_document["site_name"]
        channel["scan_location"] = scan_document["scan_location"]
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
    def bts_from_channel(cls, channel):
        bts = {"mcc": channel["mcc"],
               "mnc": channel["mnc"],
               "lac": channel["lac"],
               "cellid": channel["cellid"]}
        return bts

    @classmethod
    def make_bts_friendly(cls, bts_struct):
        """ Expecting a dict with keys for mcc, mnc, lac, cellid"""
        retval = "%s:%s:%s:%s" % (str(bts_struct["mcc"]),
                                  str(bts_struct["mnc"]),
                                  str(bts_struct["lac"]),
                                  str(bts_struct["cellid"]))
        return retval

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
