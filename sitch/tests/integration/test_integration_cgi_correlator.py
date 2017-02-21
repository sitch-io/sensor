import imp
import os
# import mock
# import sys

# sys.modules['pyudev'] = mock.Mock()
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


class TestIntegrationCgiCorrelator:
    def instantiate_cgi(self):
        cgi_correlator = sitchlib.CgiCorrelator(feedpath, [], 100000)
        return cgi_correlator

    def test_correlate_cgi_1(self):
        correlator = self.instantiate_cgi()
        scan_1 = ("gsm_modem_channel", gsm_modem_channel)
        result_0 = correlator.correlate(("gps", geo_state))
        result_1 = correlator.correlate(scan_1)
        assert len(result_0) == 0
        assert len(result_1) == 1
