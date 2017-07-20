---------------
Event Lifecycle
---------------

The lifecycle of an event in SITCH begins in the Sensor, and ends with the
user's (or alert management system's) consumption.  We'll follow the most
frequent event, the GSM modem scan event.

Ingestion
---------

The Sensor runs the gsm_modem_consumer() function as a thread in runner.py.
This thread produces events from the output of the GSM modem being in
engineering mode.  gsm_modem_consumer() wraps the GsmModem class (found in
gsm_modem.py), takes the output from the __iter__() in GsmModem, and places it
into the ``scan_results_queue`` FIFO buffer.

Decomposition
-------------

The decomposer() function in runner.py is also run in a thread, and as scan
results are placed into the ``scan_results_queue`` FIFO, it pulls them out and
decomposes them into individual events, one for each cell.  Copies of these
decomposed events (labeled ``gsm_modem_channel``) are placed into the
``cgi_correlator_queue``, ``arfcn_correlator_queue``, and
``message_write_queue`` FIFO buffers.

Correlation
-----------

The cgi_correlator() and arfcn_correlator() functions are run in threads and
consume events from the ``cgi_correlator_queue`` and ``arfcn_correlator_queue``
FIFO buffers, respectively.  The cgi_correlator() correlates the information
contained in the event with the feed information based on the OpenCellID
database, taking the geolocation of the sensor into account.
If any alarms are produced, they are placed in the ``message_write_queue``.
The arfcn_correlator() function compares the ARFCN in the event metadata with
information contained in the feed based on the FCC license database, taking
into account the geolocation of the sensor.

Transmission
------------

The output() function is run in a thread and listens for events being placed
into the ``message_write_queue`` FIFO.  It takes the events it finds there and
writes them to disk, appending them to files by event type.

At this point, you have the original scan event, each decomposed channel event,
and any alerts produced, logged on disk in specific files, based on event type.

These events are picked up from disk by filebeat, and transmitted to Logstash,
which runs in the service side of SITCH.

Reception
---------

Logstash splits the information between two data stores.  The events themselves
get sent to Elasticsearch, and you can query them with Kibana.  Some of the
measurement metadata is sent to influxDB, and can be viewed with Chronograf.

Events with type ``sitch_alert`` are sent to Slack by Logstash.
