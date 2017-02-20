import imp
import os


modulename = 'sitchlib'
modulepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "../../")
feedpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "../fixture/feed/")
file, pathname, description = imp.find_module(modulename, [modulepath])
sitchlib = imp.load_module(modulename, file, pathname, description)


geo_state = {"lat": 37.773972, "lon": -122.431297}
geo_other_state = {"lat": 32.773972, "lon": -100.431297}


class TestIntegrationCorrelateGeo:
    def instantiate_geo(self):
        geo_correlator = sitchlib.GeoCorrelator()
        return geo_correlator

    def test_instantiate_measure_drift(self):
        correlator = self.instantiate_geo()
        result_1 = correlator.correlate(("gps", geo_state))
        result_2 = correlator.correlate(("gps", geo_other_state))
        assert len(result_1) == 0
        assert len(result_2) == 1
