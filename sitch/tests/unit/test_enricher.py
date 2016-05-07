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
            'scan_location': 'test_site',
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
