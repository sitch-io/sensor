from mock import MagicMock
import imp
import os
modulename = 'sitchlib'
modulepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")
file, pathname, description = imp.find_module(modulename, [modulepath])
fixturepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "../fixture/ceng.txt")
sitchlib = imp.load_module(modulename, file, pathname, description)
samp_sim = {'platform': u'AMLOGIC',
            'scan_finish': '2016-05-07 02:36:50',
            'scan_location': {'name': 'test_site'},
            'scan_results': [
                {'bsic': '12', 'mcc': '310', 'rla': '00', 'lac': '178d', 'mnc': '411', 'txp': '05', 'rxl': '33',
                    'cell': '0', 'rxq': '00', 'ta': '255', 'cellid': '000f', 'arfcn': '0154'},
                {'cell': '1', 'rxl': '20', 'lac': '178d', 'bsic': '30', 'mnc': '411', 'mcc': '310', 'cellid': '0010',
                    'arfcn': '0128'},
                {'cell': '2', 'rxl': '10', 'lac': '178d', 'bsic': '00', 'mnc': '411', 'mcc': '310', 'cellid': '76e2',
                    'arfcn': '0179'},
                {'cell': '3', 'rxl': '10', 'lac': '178d', 'bsic': '51', 'mnc': '411', 'mcc': '310', 'cellid': '1208',
                    'arfcn': '0181'},
                {'cell': '4', 'rxl': '31', 'lac': '0000', 'bsic': '00', 'mnc': '', 'mcc': '', 'cellid': 'ffff',
                    'arfcn': '0237'},
                {'cell': '5', 'rxl': '23', 'lac': '0000', 'bsic': '00', 'mnc': '', 'mcc': '', 'cellid': 'ffff',
                    'arfcn': '0238'},
                {'cell': '6', 'rxl': '23', 'lac': '0000', 'bsic': '00', 'mnc': '', 'mcc': '', 'cellid': 'ffff',
                    'arfcn': '0236'}],
            'scan_start': '',
            'scan_program': 'SIM808'}

samp_kal = {'platform': u'AMLOGIC',
            'scan_finish': '2016-05-07 04:14:30',
            'scan_location': {'name': 'test_site'},
            'scan_results': [
                {'channel_detect_threshold': '279392.605625', 'power': '599624.47', 'final_freq': '869176168',
                    'mod_freq': 23832.0, 'band': 'GSM-850', 'sample_rate': '270833.002142', 'gain': '80.0',
                    'base_freq': 869200000.0, 'device': '0: Generic RTL2832U OEM', 'modifier': '-', 'channel': '128'},
                {'channel_detect_threshold': '279392.605625', 'power': '400160.02', 'final_freq': '874376406',
                    'mod_freq': 23594.0, 'band': 'GSM-850', 'sample_rate': '270833.002142', 'gain': '80.0',
                    'base_freq': 874400000.0, 'device': '0: Generic RTL2832U OEM', 'modifier': '-', 'channel': '154'},
                {'channel_detect_threshold': '279392.605625', 'power': '401880.05', 'final_freq': '889829992',
                    'mod_freq': 29992.0, 'band': 'GSM-850', 'sample_rate': '270833.002142', 'gain': '80.0',
                    'base_freq': 889800000.0, 'device': '0: Generic RTL2832U OEM', 'modifier': '+', 'channel': '231'},
                {'channel_detect_threshold': '279392.605625', 'power': '397347.54', 'final_freq': '891996814',
                    'mod_freq': 3186.0, 'band': 'GSM-850', 'sample_rate': '270833.002142', 'gain': '80.0',
                    'base_freq': 892000000.0, 'device': '0: Generic RTL2832U OEM', 'modifier': '-', 'channel': '242'}],
            'scan_start': '2016-05-07 04:10:35',
            'scan_program': 'Kalibrate',
            'scanner_name': 'test_site'}


class TestEnricher:
    def create_config(self):
        config = sitchlib.ConfigHelper
        config.__init__ = (MagicMock(return_value=None))
        config.device_id = "12345"
        return config

    def create_enricher(self):
        config = self.create_config()
        enricher = sitchlib.Enricher(config)
        return enricher

    def test_determine_scan_type(self):
        enricher = self.create_enricher()
        scantype = enricher.determine_scan_type(samp_sim)
        assert scantype == 'SIM808'

    def test_hex_to_dec(self):
        testval = 'ffff'
        desired_result = '65535'
        enricher = self.create_enricher()
        result = enricher.hex_to_dec(testval)
        assert result == desired_result

    def test_enrich_sim808(self):
        enricher = self.create_enricher()
        result = enricher.enrich_sim808_scan(samp_sim)
        desired_item_count = 8
        desired_cell6_cellid = '65535'
        assert len(result) == desired_item_count
        assert result[7][1]['cellid'] == desired_cell6_cellid
        for item in result:
            assert type(item) is tuple

    def test_enrich_kal(self):
        enricher = self.create_enricher()
        result = enricher.enrich_kal_scan(samp_kal)
        desired_item_count = 5
        assert len(result) == desired_item_count
        for item in result:
            assert type(item) is tuple
