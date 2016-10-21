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


class TestIntegrationEnrichKalScan:
    def instantiate_kal_enricher(self, threshold):
        kal_enricher = sitchlib.KalScanEnricher(threshold)
        return kal_enricher

    def build_scan_doc(self):
        samp_kal = {'platform': u'AMLOGIC',
                    'scan_finish': '2016-05-07 04:14:30',
                    'scan_location': {'name': 'test_site'},
                    'scanner_public_ip': '0.0.0.0',
                    'scan_results': [
                        {'channel_detect_threshold': '279392.605625',
                            'power': '599624.47', 'final_freq': '869176168',
                            'mod_freq': 23832.0, 'band': 'GSM-850',
                            'sample_rate': '270833.002142', 'gain': '80.0',
                            'base_freq': 869200000.0, 'device':
                            '0: Generic RTL2832U OEM', 'modifier': '-',
                            'channel': '128'},
                        {'channel_detect_threshold': '279392.605625',
                            'power': '400160.02', 'final_freq': '874376406',
                            'mod_freq': 23594.0, 'band': 'GSM-850',
                            'sample_rate': '270833.002142', 'gain': '80.0',
                            'base_freq': 874400000.0, 'device':
                            '0: Generic RTL2832U OEM', 'modifier': '-',
                            'channel': '154'},
                        {'channel_detect_threshold': '279392.605625',
                            'power': '401880.05', 'final_freq': '889829992',
                            'mod_freq': 29992.0, 'band': 'GSM-850',
                            'sample_rate': '270833.002142', 'gain': '80.0',
                            'base_freq': 889800000.0, 'device':
                            '0: Generic RTL2832U OEM', 'modifier': '+',
                            'channel': '231'},
                        {'channel_detect_threshold': '279392.605625',
                            'power': '397347.54', 'final_freq': '891996814',
                            'mod_freq': 3186.0, 'band': 'GSM-850',
                            'sample_rate': '270833.002142', 'gain': '80.0',
                            'base_freq': 892000000.0, 'device':
                            '0: Generic RTL2832U OEM', 'modifier': '-',
                            'channel': '242'}],
                    'scan_start': '2016-05-07 04:10:35',
                    'scan_program': 'Kalibrate',
                    'scanner_name': 'test_site'}
        return samp_kal

    def test_instantiate_kal_enricher(self):
        arfcn = self.instantiate_kal_enricher(100000)
        assert arfcn

    def test_kal_good(self):
        kal_enricher = self.instantiate_kal_enricher(10000000000)
        kal_scan = self.build_scan_doc()
        result = kal_enricher.enrich_kal_scan(kal_scan)
        assert len(result) == 5

    def test_kal_bad(self):
        kal_enricher = self.instantiate_kal_enricher(10000)
        kal_scan = self.build_scan_doc()
        result = kal_enricher.enrich_kal_scan(kal_scan)
        assert len(result) == 9

    def test_kal_response_structure(self):
        kal_enricher = self.instantiate_kal_enricher(10000)
        kal_scan = self.build_scan_doc()
        results = kal_enricher.enrich_kal_scan(kal_scan)
        assert len(results) == 9
        for result in results:
            assert len(result) == 2
            assert type(result[0]) is str
            assert type(result[1]) is dict
