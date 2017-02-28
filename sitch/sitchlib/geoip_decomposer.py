class GeoipDecomposer(object):
    @classmethod
    def decompose(cls, scan_document):
        results_set = [("geo_ip", scan_document)]
        if not GeoipDecomposer.scan_document_is_valid(scan_document):
            return []
        else:
            return results_set

    @classmethod
    def scan_document_is_valid(cls, scan_document):
        is_valid = False
        if "geometry" in scan_document:
            if "coordinates" in scan_document["geometry"]:
                if scan_document["geometry"]["coordinates"] != [0, 0]:
                    is_valid = True
        return is_valid
