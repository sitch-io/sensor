heartbeat.log
-------------

::

  {"heartbeat_service_name": "MainThread", "event_timestamp": "2017-05-07T06:32:09.815061", "scan_program": "heartbeat"}
  {"heartbeat_service_name": "kalibrate_consumer", "event_timestamp": "2017-05-07T06:32:09.815243", "scan_program": "heartbeat"}
  {"heartbeat_service_name": "arfcn_correlator", "event_timestamp": "2017-05-07T06:32:09.815323", "scan_program": "heartbeat"}
  {"heartbeat_service_name": "decomposer", "event_timestamp": "2017-05-07T06:32:09.815391", "scan_program": "heartbeat"}
  {"heartbeat_service_name": "gsm_modem_consumer", "event_timestamp": "2017-05-07T06:32:09.815456", "scan_program": "heartbeat"}
  {"heartbeat_service_name": "geoip_consumer", "event_timestamp": "2017-05-07T06:32:09.815520", "scan_program": "heartbeat"}
  {"heartbeat_service_name": "writer", "event_timestamp": "2017-05-07T06:32:09.815584", "scan_program": "heartbeat"}
  {"heartbeat_service_name": "geo_correlator", "event_timestamp": "2017-05-07T06:32:09.815648", "scan_program": "heartbeat"}
  {"heartbeat_service_name": "gps_consumer", "event_timestamp": "2017-05-07T06:32:09.815711", "scan_program": "heartbeat"}
  {"heartbeat_service_name": "cgi_correlator", "event_timestamp": "2017-05-07T06:32:09.815780", "scan_program": "heartbeat"}

These events are most useful when chasing down thread failure.  It doesn't
happen often, but when it does, you can look at these events as a time-series
and see where one ceases to appear.  This is most useful when correlated with
queue sizes as reflected in health_check.log.
