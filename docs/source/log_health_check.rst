health_check.log
----------------

::

  {"cpu_times":
    {"iowait": 4694.23,
     "idle": 3089452.32,
     "user": 1786751.62,
     "system": 125489.34},
   "data_vol": 5.5,
   "root_vol": 5.5,
   "cpu_percent": [42.0, 53.0, 35.9, 38.0],
   "mem":
     {"swap_percent_used": 0.0,
      "free": 464707584},
   "queue_sizes": {
     "arfcn_correlator": 0,
     "geo_correlator": 0,
     "scan_results": 0,
     "cgi_correlator": 0},
   "application_uptime_seconds": 32461,
   "event_timestamp": "2017-05-07T06:32:09.816725",
   "scan_program": "health_check"}


The frequency with which these events are generated is determined by the
``HEALTH_CHECK_INTERVAL`` environment variable.

How is this information useful?

If you notice a trend where a metric under "queue_sizes" is always-increasing,
you may have a failed processing thread.  Correlate this with the events coming
from heartbeat.log.  Look for the absence of a heartbeat event for the
corresponding thread).  If you've confirmed that a thread has failed, the
fastest fix is to just restart the sensor.  If you can get a traceback for the
thread failure, please submit it as an issue at
https://github.com/sitch-io/sensor/issues/new.
