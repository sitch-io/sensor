from mock import MagicMock
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
sitchlib = imp.load_module(modulename, file, pathname, description)
sitch_feed_base = os.getenv('SITCH_FEED_BASE')
samp_sim = {'platform': u'AMLOGIC',
            'band': 'GSM850_MODE',
            'scan_finish': '2016-05-07 02:36:50',
            'scan_location': {'name': 'test_site'},
            'scanner_public_ip': '0.0.0.0',
            'scan_results': [
                {'bsic': '12', 'mcc': '310', 'rla': '00', 'lac': '178d',
                 'mnc': '411', 'txp': '05', 'rxl': '33', 'cell': '0',
                 'rxq': '00', 'ta': '255', 'cellid': '000f', 'arfcn': '0154'},
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
                 'mnc': '', 'mcc': '', 'cellid': 'ffff', 'arfcn': '0237'},
                {'cell': '5', 'rxl': '23', 'lac': '0000', 'bsic': '00',
                 'mnc': '', 'mcc': '', 'cellid': 'ffff', 'arfcn': '0238'},
                {'cell': '6', 'rxl': '23', 'lac': '0000', 'bsic': '00',
                 'mnc': '', 'mcc': '', 'cellid': 'ffff', 'arfcn': '0236'}],
            'scan_start': '',
            'scan_program': 'GSM_MODEM'}

samp_kal = {'platform': u'AMLOGIC',
            'scan_finish': '2016-05-07 04:14:30',
            'scan_location': {'name': 'test_site'},
            'scanner_public_ip': '0.0.0.0',
            'scan_results': [
                {'channel_detect_threshold': '279392.605625',
                 'power': '599624.47', 'final_freq': '869176168',
                 'mod_freq': 23832.0, 'band': 'GSM-850',
                 'sample_rate': '270833.002142', 'gain': '80.0',
                 'base_freq': 869200000.0, 'device': '0: Generic RTL2832U OEM',
                 'modifier': '-', 'channel': '128'},
                {'channel_detect_threshold': '279392.605625',
                 'power': '400160.02', 'final_freq': '874376406',
                 'mod_freq': 23594.0, 'band': 'GSM-850',
                 'sample_rate': '270833.002142', 'gain': '80.0',
                 'base_freq': 874400000.0, 'device': '0: Generic RTL2832U OEM',
                 'modifier': '-', 'channel': '154'},
                {'channel_detect_threshold': '279392.605625',
                 'power': '401880.05', 'final_freq': '889829992',
                 'mod_freq': 29992.0, 'band': 'GSM-850',
                 'sample_rate': '270833.002142', 'gain': '80.0',
                 'base_freq': 889800000.0, 'device': '0: Generic RTL2832U OEM',
                 'modifier': '+', 'channel': '231'},
                {'channel_detect_threshold': '279392.605625',
                 'power': '397347.54', 'final_freq': '891996814',
                 'mod_freq': 3186.0, 'band': 'GSM-850',
                 'sample_rate': '270833.002142', 'gain': '80.0',
                 'base_freq': 892000000.0, 'device': '0: Generic RTL2832U OEM',
                 'modifier': '-', 'channel': '242'}],
            'scan_start': '2016-05-07 04:10:35',
            'scan_program': 'Kalibrate',
            'scanner_name': 'test_site'}


class TestEnricher:
    def create_config(self):
        config = sitchlib.ConfigHelper
        config.__init__ = (MagicMock(return_value=None))
        config.device_id = "12345"
        config.feed_dir = "/tmp/"
        config.kal_threshold = "1000000"
        config.mcc_list = []
        config.state_list = []
        config.feed_url_base = sitch_feed_base
        return config

    def create_enricher(self):
        config = self.create_config()
        gps_location = {"lon": 0, "lat": 0}
        enricher = sitchlib.Enricher(config, gps_location)
        enricher.alerts = sitchlib.AlertManager()
        return enricher

    def test_convert_hex_targets(self):
        target_channel = samp_sim["scan_results"][0]
        enr = self.create_enricher()
        result = enr.gsm_modem_enricher.convert_hex_targets(target_channel)
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

    def test_str_to_float_badval(self):
        testval = "I AINT"
        result = sitchlib.Utility.str_to_float(testval)
        assert result is None

    def test_str_to_float_integer(self):
        testval = "12345"
        result = sitchlib.Utility.str_to_float(testval)
        assert result == 12345.0

    def test_str_to_float_float(self):
        testval = "12345.0010234"
        result = sitchlib.Utility.str_to_float(testval)
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
