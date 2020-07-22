"""Decompose Kalibrate scans."""

from .utility import Utility


class KalDecomposer:
    """Decompose Kalibrate scans."""

    @classmethod
    def decompose(cls, scan_document):
        """Decompose Kalibrate scans into channels.

        The first item in each returned tuple indicates the scan doc type.
            This module produces: "scan" (Kalibrate scan doc) and "kal_channel"
            (Individual channel from Kalibrate scan)

        Args:
            scan_document (dict): Output from Kalibrate as interpreted by
                `kalibrate` Python module.
        """
        results_set = [("scan", scan_document)]
        if scan_document["scan_results"] == []:
            print("KalDecomposer: No results found in scan document...")
            return results_set
        else:
            for result in scan_document["scan_results"]:
                try:
                    msg = {}
                    msg["event_type"] = "kalibrate_channel"
                    msg["band"] = result["band"]
                    msg["power"] = Utility.str_to_float(result["power"])
                    msg["sample_rate"] = result["sample_rate"]
                    msg["final_freq"] = result["final_freq"]
                    msg["channel"] = result["channel"]
                    msg["gain"] = result["gain"]
                    msg["site_name"] = scan_document["site_name"]
                    msg["sensor_id"] = scan_document["sensor_id"]
                    msg["sensor_name"] = scan_document["sensor_name"]
                    msg["scan_start"] = scan_document["scan_start"]
                    msg["scan_finish"] = scan_document["scan_finish"]
                    msg["event_timestamp"] = scan_document["event_timestamp"]
                    msg["scan_program"] = scan_document["scan_program"]
                    msg["scanner_public_ip"] = scan_document["scanner_public_ip"]  # NOQA
                    try:
                        msg["arfcn_int"] = int(result["channel"])
                    except:
                        print("KalDecomposer: Unable to convert ARFCN to int")
                        print(result["channel"])
                        msg["arfcn_int"] = 0
                    chan_enriched = ('kal_channel', msg)
                    results_set.append(chan_enriched)
                except Exception as e:
                    print("KalDecomposer: Failed to parse Kalibrate message.")
                    print(e)
                    print(msg)
        return results_set
