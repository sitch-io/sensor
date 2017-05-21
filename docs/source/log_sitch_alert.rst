sitch_alert.log
---------------

::

  {"details": "Primary BTS was 310:260:275:20082 now 310:260:275:42302. Site: sitch-site-testing",
   "type": "Primary BTS metadata change.",
   "id": 110,
   "device_id": "sitch-site-testing"
   "event_timestamp": "2017-05-07T06:28:38.545421"}

* ``details`` is a human-readable representation of the event, with details.
* ``type`` is a human-readable description of the alert type.  For a list of
  supported event types, look in the ``__init__`` section of
  http://sensor.readthedocs.io/en/test/_modules/sitchlib/alert_manager.html#AlertManager
* ``id`` is an ID that maps to a specific event type.  This is meant to simplify
  integration with SIEM and log management systems.
* ``device_id`` is the device ID (see device configuration environment vars)
* ``event_timestamp`` is generated when the alert is detected.
