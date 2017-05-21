scanner.log
-----------

::

  {"site_name": "sitch-site-testing",
   "scan_results": [
   {"channel_detect_threshold": "105949.217083",
    "power": "854930.16",
    "final_freq": "874979084",
    "mod_freq": 20916.0,
    "band": "GSM-850",
    "sample_rate": "270833.002142",
    "gain": "80.0",
    "base_freq": 875000000.0,
    "device": "0: Generic RTL2832U OEM",
    "modifier": "-",
    "channel": "157"}
    ],
   "platform": "Unspecified",
   "scan_start": "2017-05-07T06:23:39.482440",
   "scan_location": "sitch-site-testing",
   "scanner_public_ip": "1.1.1.1",
   "scan_finish": "2017-05-07T06:28:38.545421",
   "event_timestamp": "2017-05-07T06:28:38.545421",
   "scan_program": "kalibrate",
   "scanner_name": "sitch-site-testing"}


The list of items under scan_results is used by the Decomposer to produce
messages that end up in the kal_channel log file.
