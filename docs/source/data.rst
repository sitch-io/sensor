---------------------------------------------
Understanding the Log Data Collected by Sitch
---------------------------------------------

The following sections describe the data for the files found in '/data/sitch/log/'.

cells.log
---------


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
