"""Decompose GeoIP Events."""


class GeoipDecomposer(object):
    """GeoIP Decomposer."""

    @classmethod
    def decompose(cls, scan_document):
        """Validate and decompose GeoIP Events.

        Args:
            scan_document (dict): GeoIP scan document.

        Returns:
            list: one item in list: a two-item tuple.  Position 0 is `geo_ip`.
                Position 1 is the actual scan document.  If the scan fails
                validation, you'll only get an empty list back
        """
        results_set = [("geo_ip", scan_document)]
        if not GeoipDecomposer.scan_document_is_valid(scan_document):
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
