cells.log
---------

::

    {"scan_results": [
      {"cgi_str": "310:260:275:20000",
       "site_name": "sitch-site-testing",
       "bsic": "16",
       "mcc": "310",
       "rla": 0,
       "lac": "275",
       "band": "ALL_BAND",
       "feed_info": {
         "mcc": "310",
         "lon": "-122.464146",
         "lac": "275",
         "range": 325,
         "lat": "37.776641",
         "mnc": "260",
         "cellid": "20082"},
       "scan_location": "sitch-site-testing",
       "mnc": "260",
       "txp": 03,
       "distance": 534.3820159387475,
       "scan_finish": "2017-05-06T06:25:49.837957",
       "rxl": 20.0,
       "cell": 0,
       "scanner_public_ip": "1.1.1.1",
       "rxq": 0.0,
       "ta": 255,
       "cellid": "20082",
       "cgi_int": 31026027520082,
       "arfcn": 684}
       ...],
      "band": "ALL_BAND",
      "site_name": "sitch-site-testing",
      "platform": "Unspecified",
      "scan_start": "",
      "scan_location": "sitch-site-testing",
      "scanner_public_ip": "1.1.1.1",
      "scan_finish": "2017-05-06T06:25:49.837957",
      "scan_program": "gsm_modem"
      "event_timestamp": "2017-05-06T06:25:49.837957"}

<cell>
======

+-----------------+----------------------------------------+
| possible values | description                            |
+=================+========================================+
| 0               | The serving cell                       |
+-----------------+----------------------------------------+
| 1-6             | The index of the neighboring cell      |
+-----------------+----------------------------------------+


<arfcn>
=======

[Absolute radio frequency channel number](https://en.wikipedia.org/wiki/Absolute_radio-frequency_channel_number)

<rxl>
=====

Receive level

The measured signal level shall be mapped to an RXLEV value between 0 and 63, as follows:

+-----------------+-----------------------+
| possible values | description           |
+=================+=======================+
| 0               | less than -110 dBm.   |
+-----------------+-----------------------+
| 1               | -110 dBm to -109 dBm. |
+-----------------+-----------------------+
| 2               | -109 dBm to -108 dBm. |
+-----------------+-----------------------+
| ...             |                       |
+-----------------+-----------------------+
| ...             |                       |
+-----------------+-----------------------+
| 62              | -49 dBm to -48 dBm.   |
+-----------------+-----------------------+
| 63              | greater than -48 dBm. |
+-----------------+-----------------------+


<rxq>
=====

Receive quality

+-----------------+------------------------------------------------------------+
| possible values | description                                                |
+=================+============================================================+
| 0...7           | as [RXQUAL](https://en.wikipedia.org/wiki/Rxqual) values   |
+-----------------+------------------------------------------------------------+
| 99              | not known or not detectable                                |
+-----------------+------------------------------------------------------------+

<mcc>
=====

[Mobile country code](https://en.wikipedia.org/wiki/Mobile_country_code)

<mnc>
=====

[Mobile network code](https://en.wikipedia.org/wiki/Mobile_country_code)

<bsic>
======

[Base station identity code](https://en.wikipedia.org/wiki/Base_station_identity_code)

<cellid>
========

[Cell id](https://en.wikipedia.org/wiki/Cell_ID)

*NOTE: In a 7-item line, cellid is not provided.  We set it to 0 to prevent barfing elsewhere.*

<lac>
=====

[Location area code](http://www.telecomabc.com/l/lac.html)

<rla>
=====

Receive level access minimum

GUESS: Minimum receiving level permitted to access the system Per: similar AT engineering mode (AT+QENG) command in [M95 AT commands manual](http://eddywireless.com/yahoo_site_admin/assets/docs/M95_AT_Commands_Manual_V12.196112248.pdf)

<txp>
=====

Transmit power maximum CCCH

<TA>
====

[Timing Advance](https://en.wikipedia.org/wiki/Timing_advance)
