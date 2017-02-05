# from datetime import datetime
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

kal_channel = {"site_name": "sitch_testing",
               "power": 582752.95,
               "final_freq": "892019766",
               "band": "GSM-850",
               "scan_finish": "2017-01-30 01:19:35",
               "sample_rate": "270833.002142",
               "gain": "80.0",
               "scanner_public_ip": "71.204.189.222",
               "scan_start": "2017-01-30 01:13:20",
               "scan_program": "Kalibrate",
               "arfcn_int": 242,
               "channel": "242",
               "offset": 22042,
               "type": "kal_channel",
               "input_type": "log"}
gsm_modem_channel = {"cgi_str": "310:266:253:21553",
                     "site_name": "sitch_testing",
                     "mcc": "310",
                     "lac": "253",
                     "band": "ALL_BAND",
                     "feed_info": {
                          "mcc": "310",
                          "lon": 0,
                          "lac": "253",
                          "range": 0,
                          "lat": 0,
                          "mnc": "266",
                          "cellid": "21553"},
                     "mnc": "266",
                     "bsic": "00",
                     "distance": 12798576.615081305,
                     "scan_finish": "2017-01-30 01:33:48",
                     "rxl": 7,
                     "arfcn_int": 1692,
                     "cell": "4",
                     "scanner_public_ip": "71.204.189.222",
                     "cellid": "21553",
                     "cgi_int": 31026625321553,
                     "arfcn": "1692",
                     "source": "/var/log/sitch/gsm_modem_channel.log",
                     "offset": 42048460,
                     "type": "gsm_modem_channel",
                     "input_type": "log"}


class TestIntegrationECorrelateArfcn:
    def instantiate_arfcn(self):
        arfcn_correlator = sitchlib.CorrelateArfcn(geo_state, states, feedpath,
                                                   [], 100000)
        return arfcn_correlator

    def instantiate_arfcn_bad_geo_state(self):
        arfcn_enricher = sitchlib.EnrichArfcn(bad_geo_state, states, feedpath,
                                              [], 100000)
        return arfcn_enricher

    def test_instantiate_arfcn(self):
        arfcn = self.instantiate_arfcn()
        assert arfcn

    def test_arfcn_override_gps(self):
        arfcn = self.instantiate_arfcn()
        test_arfcn = self.build_scan_doc("239")
        result = arfcn.compare_arfcn_to_feed(test_arfcn)
        assert len(result) == 1

    def test_arfcn_good(self):
        arfcn = self.instantiate_arfcn()
        test_arfcn = self.build_scan_doc("239")
        result = arfcn.compare_arfcn_to_feed(test_arfcn)
        assert len(result) == 0

    def test_arfcn_bad(self):
        arfcn = self.instantiate_arfcn()
        test_arfcn = self.build_scan_doc("99")
        result = arfcn.compare_arfcn_to_feed(test_arfcn)
        assert len(result) == 1

    def test_arfcn_gps_bad(self):
        arfcn = self.instantiate_arfcn_bad_geo_state()
        test_arfcn = self.build_scan_doc("99")
        result = arfcn.compare_arfcn_to_feed(test_arfcn)
        print result
        assert len(result) == 1

    def test_kal_channel_over_threshold(self):
        arfcn = self.instantiate_arfcn()
        results = arfcn.compare_arfcn_to_feed(kal_channel)
        print results
        assert len(results) == 1

    def test_gsm_modem_channel_parse(self):
        arfcn = self.instantiate_arfcn()
        results = arfcn.compare_arfcn_to_feed(gsm_modem_channel)
        print results
        assert len(results) == 0
