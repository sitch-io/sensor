from datetime import datetime
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

geo_state = {"gps":
             {"geometry":
              {"coordinates":
                  [-122.431297, 37.773972]}}}
bad_geo_state = {"gps":
                 {"geometry":
                  {"coordinates":
                      [0, 0]}}}

states = ["CA"]


class TestIntegrationEnrichArfcn:
    def instantiate_arfcn(self):
        arfcn_enricher = sitchlib.EnrichArfcn(geo_state, states, feedpath)
        return arfcn_enricher

    def build_scan_doc(self, arfcn):
        scan_job = {"platform": "resin_your_mom",
                    "scan_results": [{"arfcn": arfcn}],
                    "scan_start": datetime.now(),
                    "scan_finish": datetime.now(),
                    "scan_program": "ARFCN_ENRICHER",
                    "scan_location": {"name": "fake_device_name"},
                    "scanner_public_ip": "1.1.1.1"}
        return scan_job

    def instantiate_arfcn_bad_geo_state(self):
        arfcn_enricher = sitchlib.EnrichArfcn(bad_geo_state, states, feedpath)
        return arfcn_enricher

    def test_instantiate_arfcn(self):
        arfcn = self.instantiate_arfcn()
        assert arfcn

    def test_arfcn_good(self):
        arfcn = self.instantiate_arfcn()
        test_arfcn = self.build_scan_doc("239")
        result = arfcn.compare_arfcn_to_feed(test_arfcn)
        assert len(result) == 1

    def test_arfcn_bad(self):
        arfcn = self.instantiate_arfcn()
        test_arfcn = self.build_scan_doc("99")
        result = arfcn.compare_arfcn_to_feed(test_arfcn)
        assert len(result) == 2

    def test_arfcn_gps_bad(self):
        arfcn = self.instantiate_arfcn_bad_geo_state()
        test_arfcn = self.build_scan_doc("99")
        result = arfcn.compare_arfcn_to_feed(test_arfcn)
        assert len(result) == 2
