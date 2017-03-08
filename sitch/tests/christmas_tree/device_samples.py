class DeviceSamples(object):
    gps_device_loc_a = {"scan_program": "gpsd",
                        "type": "Feature",
                        "geometry": {
                        "type": "Point",
                        "coordinates": [-122.431297, 37.773972]}}

    gps_device_loc_b = {"scan_program": "gpsd",
                        "type": "Feature",
                        "geometry": {
                        "type": "Point",
                        "coordinates": [-100.431297, 32.773972]}}

    geoip_loc_a = {"scan_program": "geoip",
                   "type": "Feature",
                   "geometry": {
                   "type": "Point",
                   "coordinates": [-122.431297, 37.773972]}}

    geoip_loc_b = {"scan_program": "geoip",
                   "type": "Feature",
                   "geometry": {
                   "type": "Point",
                   "coordinates": [-100.431297, 32.773972]}}

    gsm_modem_1 = {"platform": "PLATFORM-NAME",
                   "scan_results": [
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
                     'mnc': '', 'mcc': '', 'cellid': 'ffff', 'arfcn': '0236'}
                          ],
                   "scan_start": "",
                   "scan_finish": "2016-05-07 02:36:50",
                   "scan_program": "GSM_MODEM",
                   "scan_location": "SCAN_LOCATION",
                   "site_name": "SITE_NAME",
                   "scanner_public_ip": "66.18.61.61",
                   "band": "GSM850_MODE",
                   "scanner_name": "DEVICE-ID"}

    kal_scan_1 = {'platform': 'PLATFORM-NAME',
                  'scan_finish': '2016-05-07 04:14:30',
                  'scan_location': 'SCAN_LOCATION',
                  "site_name": "SITE_NAME",
                  'scanner_public_ip': '0.0.0.0',
                  'scan_results': [
                    {'channel_detect_threshold': '279392.605625',
                        'power': '5909624.47', 'final_freq': '869176168',
                        'mod_freq': 23832.0, 'band': 'GSM-850',
                        'sample_rate': '270833.002142', 'gain': '80.0',
                        'base_freq': 869200000.0, 'device':
                        '0: Generic RTL2832U OEM', 'modifier': '-',
                        'channel': '12'},  # This should not be in the feed DB
                    {'channel_detect_threshold': '279392.605625',
                        'power': '5909624.47', 'final_freq': '869176168',
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
                  'scanner_name': 'DEVICE-ID'}
