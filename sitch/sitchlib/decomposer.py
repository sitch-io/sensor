from gps_decomposer import GpsDecomposer
from gsm_decomposer import GsmDecomposer
from kal_decomposer import KalDecomposer


class Decomposer(object):
    decomp_ref = {"Kalibrate": KalDecomposer(),
                  "GSM_MODEM": GsmDecomposer(),
                  "gpsd": GpsDecomposer()}

    def __init__(self):
        return

    @classmethod
    def decompose(cls, scan):
        result = []
        try:
            decomposer = Decomposer.decomp_ref[scan["scan_program"]]
            result = decomposer.decompose(scan)
        except KeyError:
            print("Unrecognized scan: %s" % str(scan))
        return result
