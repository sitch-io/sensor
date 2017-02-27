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

samp_sim = {'platform': u'AMLOGIC',
            'band': 'GSM850_MODE',
            'scan_finish': '2016-05-07 02:36:50',
            'scan_location': {'name': 'test_site'},
            'scanner_public_ip': '71.202.120.242',
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


class TestIntegrationEnrichGsmModem:
    def test_gsm(self):
        results = sitchlib.Decomposer.decompose(samp_sim)
        assert len(results) == 8

    def test_gsm_structure(self):
        results = sitchlib.Decomposer.decompose(samp_sim)
        for result in results:
            assert len(result) == 2
            assert type(result[0]) is str
            assert type(result[1]) is dict
