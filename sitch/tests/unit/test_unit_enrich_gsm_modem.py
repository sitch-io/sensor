from mock import Mock
import imp
import os
import sys

sys.modules['pyudev'] = Mock()
modulename = 'sitchlib'
modulepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")
file, pathname, description = imp.find_module(modulename, [modulepath])
fixturepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "../fixture/ceng.txt")
feedpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "../fixture/feed/")
sitchlib = imp.load_module(modulename, file, pathname, description)
sitch_feed_base = os.getenv('SITCH_FEED_BASE')
samp_sim = {'platform': u'AMLOGIC',
            'band': 'GSM850_MODE',
            'scan_finish': '2016-05-07 02:36:50',
            'scan_location': {'name': 'test_site'},
            'scanner_public_ip': '0.0.0.0',
            'scan_results': [
                {'bsic': '12', 'mcc': '310', 'rla': '00', 'lac': '178d',
                 'mnc': '411', 'txp': '05', 'rxl': '33',
                    'cell': '0', 'rxq': '00', 'ta': '255', 'cellid': '000f',
                    'arfcn': '0154'},
                {'cell': '1', 'rxl': '20', 'lac': '178d', 'bsic': '30',
                 'mnc': '411', 'mcc': '310', 'cellid': '0010',
                 'arfcn': '0128'},
                {'cell': '2', 'rxl': '10', 'lac': '178d', 'bsic': '00',
                 'mnc': '411', 'mcc': '310', 'cellid': '76e2',
                 'arfcn': '0179'},
                {'cell': '3', 'rxl': '10', 'lac': '178d', 'bsic': '51',
                 'mnc': '411', 'mcc': '310', 'cellid': '1208',
                 'arfcn': '0181'},
                {'cell': '4', 'rxl': '31', 'lac': '0000', 'bsic': '00',
                 'mnc': '', 'mcc': '', 'cellid': 'ffff',
                 'arfcn': '0237'},
                {'cell': '5', 'rxl': '23', 'lac': '0000', 'bsic': '00',
                 'mnc': '', 'mcc': '', 'cellid': 'ffff',
                    'arfcn': '0238'},
                {'cell': '6', 'rxl': '23', 'lac': '0000', 'bsic': '00',
                 'mnc': '', 'mcc': '', 'cellid': 'ffff',
                 'arfcn': '0236'}],
            'scan_start': '',
            'scan_program': 'GSM_MODEM'}


class TestGsmModemEnricher:
    def create_empty_state(self):
        state = {"gps": {},
                 "geoip": {},
                 "geo_distance_meters": 0,
                 "primary_cell": {"arfcn": "",
                                  "mcc": "",
                                  "mnc": "",
                                  "lac": "",
                                  "cid": ""}}
        return state

    def create_config(self):
        config = sitchlib.ConfigHelper(feedpath=feedpath)
        return config

    def create_modem_enricher(self):
        config = self.create_config()
        state = self.create_empty_state()
        enricher = sitchlib.GsmModemEnricher(state, config.feed_dir)
        enricher.alerts = sitchlib.AlertManager()
        return enricher

    def test_convert_hex_targets(self):
        target_channel = samp_sim["scan_results"][0]
        result = sitchlib.Enricher.gsm_modem_enricher.convert_hex_targets(target_channel)
        assert result["lac"] == "6029"
        assert result["cellid"] == "15"

    def test_determine_scan_type(self):
        enricher = self.create_enricher()
        scantype = enricher.determine_scan_type(samp_sim)
        assert scantype == 'GSM_MODEM'

    def test_hex_to_dec(self):
        testval = 'ffff'
        desired_result = '65535'
        enricher = self.create_enricher()
        result = enricher.gsm_modem_enricher.hex_to_dec(testval)
        assert result == desired_result

    def test_enrich_kal(self):
        enricher = self.create_enricher()
        result = enricher.enrich_kal_scan(samp_kal)
        for entry in result:
            print entry
        desired_item_count = 5
        assert len(result) == desired_item_count
        for item in result:
            assert type(item) is tuple

    def test_calculate_distance(self):
        madrid = (40.24, 3.41)
        chattanooga = (35.244, 85.1835)
        result = sitchlib.Enricher.calculate_distance(madrid[0], madrid[1],
                                                      chattanooga[0],
                                                      chattanooga[1])
        assert result != 0

    def test_str_to_float_badval(self):
        testval = "I AINT"
        result = sitchlib.Enricher.str_to_float(testval)
        assert result is None

    def test_str_to_float_integer(self):
        testval = "12345"
        result = sitchlib.Enricher.str_to_float(testval)
        assert result == 12345.0

    def test_str_to_float_float(self):
        testval = "12345.0010234"
        result = sitchlib.Enricher.str_to_float(testval)
        assert result == 12345.0010234

    def test_geo_drift_check_suppress(self):
        """ We don't want to alarm if the starting value is zero """
        prior = 0
        threshold = 1
        current_gps = {"type": "Feature",
                       "geometry": {
                          "type": "Point",
                          "coordinates": [
                             3.41,
                             40.24]}}
        current_geoip = {"type": "Feature",
                         "geometry": {
                             "type": "Point",
                             "coordinates": [
                                 85.1835,
                                 35.244]}}
        result = sitchlib.Enricher.geo_drift_check(prior,
                                                   current_geoip,
                                                   current_gps,
                                                   threshold)
        assert not result

    def test_geo_drift_check_alarm(self):
        """ Make sure we throw alarms """
        prior = 1
        threshold = 1
        current_gps = {"type": "Feature",
                       "geometry": {
                          "type": "Point",
                          "coordinates": [
                             3.41,
                             40.24]}}
        current_geoip = {"type": "Feature",
                         "geometry": {
                             "type": "Point",
                             "coordinates": [
                                 85.1835,
                                 35.244]}}
        result = sitchlib.Enricher.geo_drift_check(prior,
                                                   current_geoip,
                                                   current_gps,
                                                   threshold)
        assert result

    def test_geo_drift_check_ok(self):
        """ If all is well, we return None """
        """ Make sure we throw alarms """
        prior = 1
        threshold = 6955000
        current_gps = {"type": "Feature",
                       "geometry": {
                          "type": "Point",
                          "coordinates": [
                             3.41,
                             40.24]}}
        current_geoip = {"type": "Feature",
                         "geometry": {
                             "type": "Point",
                             "coordinates": [
                                 85.1835,
                                 35.244]}}
        result = sitchlib.Enricher.geo_drift_check(prior,
                                                   current_geoip,
                                                   current_gps,
                                                   threshold)
        assert not result