from mock import MagicMock
import imp
import os
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
            'scanner_public_ip': '71.202.120.242',
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
# alternate_cell = {"mcc": "310", "mnc": "410", "lac": "34011", "cellid": "45789",
#                  "cell": "7", "arfcn": "0988"}
# GSM,310,410,27305,63153,,-82.57584,29.969747,1102,2,1,1459815432,1461799588,
alternate_cell = {"mcc": "310", "mnc": "410", "lac": "6AA9", "cellid": "F6B1",
                  "cell": "7", "arfcn": "0988"}
samp_kal = {'platform': u'AMLOGIC',
            'scan_finish': '2016-05-07 04:14:30',
            'scan_location': {'name': 'test_site'},
            'scanner_public_ip': '0.0.0.0',
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


class TestIntegrationEnricher:
    def create_config(self):
        config = sitchlib.ConfigHelper
        config.__init__ = (MagicMock(return_value=None))
        config.device_id = "12345"
        config.feed_dir = "/tmp/"
        config.kal_threshold = "500000"
        config.mcc_list = [310]
        config.feed_url_base = sitch_feed_base
        return config

    def create_enricher(self):
        config = self.create_config()
        gps_location = {"lon": 40.24, "lat": 3.41}
        enricher = sitchlib.Enricher(config, gps_location)
        return enricher

    def test_generate_alert_100(self):
        # Tower not in DB
        scan = samp_sim
        enricher = self.create_enricher()
        scan["scan_results"].append(alternate_cell)
        results = enricher.enrich_sim808_scan(scan)
        alert_types = []
        for result in results:
            print result
            if result[0] == "sitch_alert":
                alert_types.append(result[1]["id"])
        assert 100 in alert_types

    def test_generate_alert_110(self):
        # Tower not in DB
        scan = samp_sim
        enricher = self.create_enricher()
        alt_cell = dict(alternate_cell)
        alt_cell["cell"] = '0'
        scan["scan_results"].append(alt_cell)
        results = enricher.enrich_sim808_scan(scan)
        alert_types = []
        for result in results:
            print result
            if result[0] == "sitch_alert":
                alert_types.append(result[1]["id"])
        assert 110 in alert_types

    def test_generate_alert_120(self):
        # Tower not in DB
        scan = samp_sim
        enricher = self.create_enricher()
        results = enricher.enrich_sim808_scan(scan)
        alert_types = []
        for result in results:
            print result
            if result[0] == "sitch_alert":
                alert_types.append(result[1]["id"])
        assert 120 in alert_types

    def test_generate_alert_200(self):
        # Tower not in DB
        scan = samp_kal
        enricher = self.create_enricher()
        results = enricher.enrich_kal_scan(scan)
        alert_types = []
        for result in results:
            print result
            if result[0] == "sitch_alert":
                alert_types.append(result[1]["id"])
        assert 200 in alert_types
