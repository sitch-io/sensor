import json


class Enricher:
    def __init__(self, config):
        self.device_id = config.device_id
        return

    @classmethod
    def determine_scan_type(cls, scan):
        scan_type = None
        try:
            if scan is str:
                scan = json.loads(str)
            if scan["scan_program"] == 'Kalibrate':
                scan_type = 'Kalibrate'
            if scan["scan_program"] == 'SIM808':
                scan_type = 'SIM808'
            if scan["scan_program"] == 'GPS':
                scan_type = 'GPS'
        except:
            print "Failure to determine scan type"
            print scan
        return scan_type

    def enrich_kal_scan(self, scan_document):
        results_set = [("scan", scan_document)]
        platform_name = scan_document["scanner_name"]
        if scan_document["scan_results"] == []:
            print "No results found in scan document..."
            return
        else:
            try:
                for result in scan_document["scan_results"]:
                    msg = {}
                    msg["band"] = result["band"]
                    msg["power"] = result["power"]
                    msg["sample_rate"] = result["sample_rate"]
                    msg["final_freq"] = result["final_freq"]
                    msg["channel"] = result["channel"]
                    msg["gain"] = result["gain"]
                    msg["location"] = scan_document["scan_location"]
                    msg["scan_start"] = scan_document["scan_start"]
                    msg["scan_finish"] = scan_document["scan_finish"]
                    msg["scan_program"] = scan_document["scan_program"]
                    results_set.append(("arfcn_power", json.dumps(msg)))
            except:
                print "Failed to enrich KAL message: "
                print msg
        return results_set

    def enrich_sim808_scan(self, scan_document):
        results_set = [("cell", scan_document)]
        platform_name = scan_document["scan_location"]
        # Field and logtype association...
        fields_of_interest = {"cell": "arfcn_prio",
                              "rxl": "arfcn_rxl",
                              "rxq": "arfcn_rxq",
                              "mcc": "arfcn_mcc",
                              "mnc": "arfcn_mnc",
                              "bsic": "arfcn_bsic",
                              "cellid": "arfcn_cellid",
                              "rla": "arfcn_rla",
                              "txp": "arfcn_txp",
                              "lac": "arfcn_lac",
                              "ta": "arfcn_ta"}
        scan_items = scan_document["scan_results"]
        cleaned = []
        # for item in scan_items:
        #    if "cellid" in item:
        #        item["cellid"] = int(item["cellid"], 16)
        #    item["lac"] = int(item["lac"], 16)
        #    cleaned.append(item)
        # results_set[1]["scan_results"] = cleaned
        return results_set

    def enrich_gps_scan(self, scan_document):
        retval = ("gps", scan_document)
        return retval
