class DeviceSamples(object):
    gps_device_loc_a = {"scan_program": "gpsd",
                        "site_name": "test_site",
                        "sensor_id": "test_sensor_id",
                        "sensor_name": "test_sensor",
                        "type": "Feature",
                        "sat_time": "2017-03-25T00:30:48.000Z",
                        "time_drift": 2,
                        "sys_time": "2017-03-25T00:32:48.416592",
                        "event_timestamp": "2016-05-07 04:10:35",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [-122.431297, 37.773972]}}

    gps_device_loc_b = {"scan_program": "gpsd",
                        "site_name": "test_site",
                        "sensor_id": "test_sensor_id",
                        "sensor_name": "test_sensor",
                        "type": "Feature",
                        "sat_time": "2017-03-25T00:30:48.000Z",
                        "time_drift": 2,
                        "sys_time": "2017-03-25T00:32:48.416592",
                        "event_timestamp": "2016-05-07 04:10:35",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [-100.431297, 32.773972]}}

    geoip_loc_a = {"scan_program": "geoip",
                   "event_timestamp": "2016-05-07 04:10:35",
                   "type": "Feature",
                   "geometry": {
                       "type": "Point",
                       "coordinates": [-122.431297, 37.773972]}}

    geoip_loc_b = {"scan_program": "geoip",
                   "event_timestamp": "2016-05-07 04:10:35",
                   "type": "Feature",
                   "geometry": {
                       "type": "Point",
                       "coordinates": [-100.431297, 32.773972]}}

    gsm_modem_1 = {"platform": "PLATFORM-NAME",
                   "scan_results": [
                    {'bsic': '12', 'mcc': '310', 'rla': 0, 'lac': '178d',
                     'mnc': '411', 'txp': 05, 'rxl': 33, 'cell': 0,
                     'rxq': 00, 'ta': 255, 'cellid': '000f', 'arfcn': 154},
                    {'cell': 1, 'rxl': 20, 'lac': '178d', 'bsic': '30',
                     'mnc': '411', 'mcc': '310', 'cellid': '0010',
                     'arfcn': 128},
                    {'cell': 2, 'rxl': 10, 'lac': '178d', 'bsic': '00',
                     'mnc': '411', 'mcc': '310', 'cellid': '76e2',
                     'arfcn': 179},
                    {'cell': 3, 'rxl': 10, 'lac': '178d', 'bsic': '51',
                     'mnc': '411', 'mcc': '310', 'cellid': '1208',
                     'arfcn': 181},
                    {'cell': 4, 'rxl': 31, 'lac': 0000, 'bsic': '00',
                     'mnc': '', 'mcc': '', 'cellid': 'ffff', 'arfcn': 237},
                    {'cell': 5, 'rxl': 23, 'lac': '0000', 'bsic': '00',
                     'mnc': '', 'mcc': '', 'cellid': 'ffff', 'arfcn': 238},
                    {'cell': 6, 'rxl': 23, 'lac': '0000', 'bsic': '00',
                     'mnc': '', 'mcc': '', 'cellid': 'ffff', 'arfcn': 236}
                          ],
                   "scan_start": "",
                   "scan_finish": "2016-05-07 02:36:50",
                   "event_timestamp": '2016-05-07 04:10:35',
                   "scan_program": "gsm_modem",
                   "site_name": "test_site",
                   "sensor_id": "test_sensor_id",
                   "sensor_name": "test_sensor",
                   "scanner_public_ip": "66.18.61.61",
                   "band": "GSM850_MODE"}

    kal_scan_1 = {'platform': 'PLATFORM-NAME',
                  'scan_finish': '2016-05-07 04:14:30',
                  'site_name': 'SITE_NAME',
                  "sensor_id": "test_sensor_id",
                  "sensor_name": "test_sensor",
                  'scanner_public_ip': '0.0.0.0',
                  'sensor_name': 'SENSOR_NAME',
                  'sensor_id': 'SENSOR_ID',
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
                  'event_timestamp': '2016-05-07 04:10:35',
                  'scan_program': 'kalibrate'}
