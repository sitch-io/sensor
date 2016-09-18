import imp
import os
import mock
import sys

sys.modules['pyudev'] = mock.Mock()
modulename = 'sitchlib'
modulepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "../../")
file, pathname, description = imp.find_module(modulename, [modulepath])
sitchlib = imp.load_module(modulename, file, pathname, description)


class TestIntegrationGeoIp:
    def instantiate_geoip(self):
        geoip = sitchlib.GeoIp(delay=2)
        return geoip

    def test_instantiate_geoip(self):
        geoip = self.instantiate_geoip()
        assert geoip

    def test_geoip_iterator(self):
        geoip = self.instantiate_geoip()
        results = []
        for x in geoip:
            results.append(x)
            print x
            if len(results) > 2:
                break
        for g in results:
            assert len(g["geometry"]["coordinates"]) == 2
