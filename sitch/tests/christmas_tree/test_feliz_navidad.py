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
    def test_feliz_navidad(self):
        decomposer = sitchlib.Decomposer()
        gps_a_decomp = decomposer.decompose(samples.gps_device_loc_a)
        gps_b_decomp = decomposer.decompose(samples.gps_device_loc_b)
        # geoip_a_decomp = decomposer.decompose(samples.geoip_loc_a)
        # geoip_b_decomp = decomposer.decompose(samples.geoip_loc_b)
        gsm_decomp = decomposer.decompose(samples.gsm_modem_1)
        kal_decomp = decomposer.decompose(samples.kal_scan_1)
        # First we light up the ARFCN correlator...
        arfcn_correlator = sitchlib.ArfcnCorrelator(states, feedpath,
                                                    [], 1000000, "DEVICE_ID")
        # Now we light up the CGI correlator...
        cgi_correlator = sitchlib.CgiCorrelator(feedpath, [], ["310", "311"],
                                                "DEVICE_ID")
        # Lastly, the geo correlator...
        geo_correlator = sitchlib.GeoCorrelator("DEVICE_ID")
        # Run gps_a, Kalibrate, and GSM stuff through the ARFCN correlator
        arfcn_results = []
        for gps in gps_a_decomp:
            arfcn_correlator.correlate(gps)
        for k in kal_decomp:
            if k[0] == "kal_channel":
                arfcn_results.extend(arfcn_correlator.correlate(k))
        # arfcn_results.extend(arfcn_correlator.correlate("Kalibrate", kal_decomp))
        for g in gsm_decomp:
            arfcn_results.extend(arfcn_correlator.correlate(g))
        # Run GPS A then B through GPS correlator
        geo_results = []
        for geo in gps_a_decomp:
            geo_results.extend(geo_correlator.correlate(geo))
        for geo in gps_b_decomp:
            geo_results.extend(geo_correlator.correlate(geo))
        # Flush everything applicable through the CGI correlator now...
        cgi_results = []
        for g in gsm_decomp:
            cgi_results.extend(cgi_correlator.correlate(g))
        print("CGI Results")
        for c in cgi_results:
            print c
        assert len(cgi_results) == 4  # Four of six are correlated and not in DB
        print("GEO Results")
        for g in geo_results:
            print g
        assert len(geo_results) == 1  # One alert for delta being over threshold
        print("ARFCN Results")
        for a in arfcn_results:
            print a
        assert len(arfcn_results) == 3
