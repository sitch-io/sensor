import imp
import os
import mock
import sys
from device_samples import DeviceSamples as samples


sys.modules['pyudev'] = mock.Mock()
modulename = 'sitchlib'
modulepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "../../")
feedpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "../fixture/feed/")
file, pathname, description = imp.find_module(modulename, [modulepath])
sitchlib = imp.load_module(modulename, file, pathname, description)


states = ["CA"]


class TestFelizNavidad:
    def message_has_base_attributes(self, message):
        assert message[1]["event_timestamp"]
        assert message[1]["site_name"]
        assert message[1]["sensor_id"]
        assert message[1]["sensor_name"]
        assert message[1]["event_type"] != "base_event"
        if message[1]["event_type"] == "sitch_alert":
            assert "coordinates" in message[1]["location"]

    def test_feliz_navidad(self):
        decomposer = sitchlib.Decomposer()
        gps_a_decomp = decomposer.decompose(samples.gps_device_loc_a)
        gps_b_decomp = decomposer.decompose(samples.gps_device_loc_b)
        gsm_decomp = decomposer.decompose(samples.gsm_modem_1)
        gsm_decomp.extend(decomposer.decompose(samples.gsm_modem_2))
        kal_decomp = decomposer.decompose(samples.kal_scan_1)
        # First we light up the ARFCN correlator...
        arfcn_correlator = sitchlib.ArfcnCorrelator(feedpath, [], 1000000,
                                                    "DEVICE_ID")
        # Now we light up the CGI correlator...
        cgi_correlator = sitchlib.CgiCorrelator(feedpath, [], ["310", "311"],
                                                "DEVICE_ID")
        # Lastly, the geo correlator...
        geo_correlator = sitchlib.GeoCorrelator("DEVICE_ID")
        # Run gps_a, Kalibrate, and GSM stuff through the ARFCN correlator
        arfcn_results = []
        for gps in gps_a_decomp:
            self.message_has_base_attributes(gps)
            arfcn_correlator.correlate(gps)
        for k in kal_decomp:
            if k[0] == "kal_channel":
                self.message_has_base_attributes(k)
                arfcn_results.extend(arfcn_correlator.correlate(k))
        for g in gsm_decomp:
            self.message_has_base_attributes(g)
            arfcn_results.extend(arfcn_correlator.correlate(g))
        # Run GPS A then B through GPS correlator
        geo_results = []
        for geo in gps_a_decomp:
            self.message_has_base_attributes(geo)
            geo_results.extend(geo_correlator.correlate(geo))
        for geo in gps_b_decomp:
            self.message_has_base_attributes(geo)
            geo_results.extend(geo_correlator.correlate(geo))
        # Flush everything applicable through the CGI correlator now...
        cgi_results = []
        for g in gsm_decomp:
            self.message_has_base_attributes(g)
            # print g
            cgi_results.extend(cgi_correlator.correlate(g))
        print("CGI Results")
        for c in cgi_results:
            self.message_has_base_attributes(c)
            print c
        assert len(cgi_results) == 5  # 4 of 6 are correlated and not in DB
        print("GEO Results")
        for g in geo_results:
            self.message_has_base_attributes(g)
            print g
        assert len(geo_results) == 1  # 1 alert for delta being over threshold
        print("ARFCN Results")
        for a in arfcn_results:
            self.message_has_base_attributes(a)
            print a
        assert len(arfcn_results) == 3
