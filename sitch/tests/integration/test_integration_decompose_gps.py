import imp
import os
import mock
import sys

sys.modules['pyudev'] = mock.Mock()
modulename = 'sitchlib'
modulepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "../../")
feedpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "../fixture/feed/")
file, pathname, description = imp.find_module(modulename, [modulepath])
sitchlib = imp.load_module(modulename, file, pathname, description)

def build_gps_scan(lon, lat):
    gps_scan = {"scan_program": "gpsd",
                "type": "Feature",
                "geometry":
                  {"type": "Point",
                   "coordinates": [lon,
                                   lat]}}
    return gps_scan

class TestIntegrationDecomposeGps:
    def test_gps_empty(self):
        # If it's 0,0 we don't let it past the decomposer
        result = sitchlib.GpsDecomposer.decompose(build_gps_scan(0,0))
        assert len(result) == 0

    def test_gsm_structure(self):
        results = sitchlib.Decomposer.decompose(build_gps_scan(1,1))
        assert len(results) == 1
        for result in results:
            assert len(result) == 2
            assert type(result[0]) is str
            assert type(result[1]) is dict
