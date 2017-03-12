"""Decompose GPS Events."""


class GpsDecomposer(object):
    """GPS Decomposer."""

    @classmethod
    def decompose(cls, scan_document):
        """Decompose a GPS event.

        Args:
            scan_document (dict): Geo json from GPS device.

        Returns:
            list: One two-item tuple in list.  Position 0 is `gps`, position 1
                is the validated geo scan.  If the scan doesn't validate, an
                empty list is returned.
        """
        results_set = [("gps", scan_document)]
        if not GpsDecomposer.scan_document_is_valid(scan_document):
            return []
        else:
            return results_set

    @classmethod
    def scan_document_is_valid(cls, scan_document):
        """Validate the scan document."""
        is_valid = False
        if "geometry" in scan_document:
            if "coordinates" in scan_document["geometry"]:
                if scan_document["geometry"]["coordinates"] != [0, 0]:
                    is_valid = True
        return is_valid
