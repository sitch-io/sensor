from gps_decomposer import GpsDecomposer
from gsm_decomposer import GsmDecomposer
from kal_decomposer import KalDecomposer
from geoip_decomposer import GeoipDecomposer


class Decomposer(object):
    decomp_ref = {"Kalibrate": KalDecomposer(),
                  "GSM_MODEM": GsmDecomposer(),
                  "gpsd": GpsDecomposer(),
                  "geo_ip": GeoipDecomposer()}

    @classmethod
    def decompose(cls, scan):
        result = []
        try:
            decomposer = Decomposer.decomp_ref[scan["scan_program"]]
            result = decomposer.decompose(scan)
        except Exception as e:
            print("Decomposition error for scan: %s" % (str(scan)))
            print(e)

        return result
