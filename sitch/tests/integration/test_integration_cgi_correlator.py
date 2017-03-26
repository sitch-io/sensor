import imp
import os


modulename = 'sitchlib'
modulepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "../../")
feedpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "../fixture/feed/")
file, pathname, description = imp.find_module(modulename, [modulepath])
sitchlib = imp.load_module(modulename, file, pathname, description)

geo_state = {"geometry":
             {"coordinates":
              [-122.431297, 37.773972]}}

bad_geo_state = {"geometry":
                 {"coordinates":
                  [0, 0]}}

states = ["CA"]

gsm_modem_channel = {"cgi_str": "310:266:253:21553",
                     "site_name": "sitch_testing",
                     "mcc": "310",
                     "lac": "253",
                     "band": "ALL_BAND",
                     "mnc": "266",
                     "bsic": "00",
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
        cgi_correlator = sitchlib.CgiCorrelator(feedpath, [], ["310", "311"],
                                                "SENSOR_ID")
        return cgi_correlator

    def test_correlate_cgi_1(self):
        correlator = self.instantiate_cgi()
        scan_1 = ("gsm_modem_channel", gsm_modem_channel.copy())
        scan_body_2 = gsm_modem_channel.copy()
        scan_body_3 = gsm_modem_channel.copy()
        scan_body_4 = gsm_modem_channel.copy()
        scan_body_2["mcc"] = "999"
        scan_body_2["cell"] = 0
        scan_body_2["cgi_str"] = "999:410:17304:32381"
        scan_body_2["cgi_int"] = 9994101730432381
        scan_body_3["mcc"] = "310"
        scan_body_3["mnc"] = "410"
        scan_body_3["lac"] = "17304"
        scan_body_3["cellid"] = "32381"
        scan_body_3["cgi_str"] = "310:410:17304:32381"
        scan_body_3["cgi_int"] = 3104101730432381
        scan_body_3["cell"] = "0"
        scan_body_4["cell"] = "0"
        zero_one = ("gsm_modem_channel", scan_body_3)
        zero_two = ("gsm_modem_channel", scan_body_4)
        scan_2 = ("gsm_modem_channel", scan_body_2)
        result_0 = correlator.correlate(("gps", geo_state))
        result_1 = correlator.correlate(scan_1)
        result_2 = correlator.correlate(scan_2)
        result_3 = correlator.correlate(zero_one)  # BTS out of range
        result_4 = correlator.correlate(zero_two)
        print result_0
        assert len(result_0) == 0
        print result_1
        assert result_1[0][1]["id"] == 120
        print result_2
        assert result_2[0][1]["id"] == 130
        print result_3
        assert result_3[0][1]["id"] == 100
        print result_4
        assert result_4[0][1]["id"] == 110
