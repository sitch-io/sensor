Sensor Environment Variables
----------------------------

The SITCH Sensor requires some environment variables to be set in order to operate.


+---------------------------+-------------------------------------------------------+
| Environment Variable      | Purpose                                               |
+===========================+=======================================================+
| CGI_WHITELIST             | List of trusted CGIs.                                 |
+---------------------------+-------------------------------------------------------+
| FEED_RADIO_TARGETS        | (Optional) Radio types to target for feed ingestion.  |
|                           | Defaults to GSM.                                      |
+---------------------------+-------------------------------------------------------+
| FEED_URL_BASE             | Base URL for Sensor feed.                             |
+---------------------------+-------------------------------------------------------+
| GSM_MODEM_BAND            | Restrict GSM modem to this band.  Options:            |
|                           | (EGSM_MODE | PGSM_MODE | DCS_MODE | GSM850_MODE |     |
|                           | PCS_MODE | EGSM_DCS_MODE | GSM850_PCS_MODE |          |
|                           | EGSM_PCS_MODE | ALL_BAND)                             |
+---------------------------+-------------------------------------------------------+
| GSM_MODEM_PORT            | (Optional) Set the tty for the GSM modem              |
+---------------------------+-------------------------------------------------------+
| KAL_BAND                  | Band for Kalibrate to scan. (GSM850 | GSM-R |         |
|                           | GSM900 | EGSM | DCS | PCS)                            |
+---------------------------+-------------------------------------------------------+
| KAL_GAIN                  | Gain value for Kalibrate.  Try 60.                    |
+---------------------------+-------------------------------------------------------+
| KAL_THRESHOLD             | Alarm threshold for Kalibrate channel power level.    |
|                           | Try 1000000.                                          |
+---------------------------+-------------------------------------------------------+
| LOCATION_NAME             | Name of the location for this sensor.  No spaces.     |
+---------------------------+-------------------------------------------------------+
| LOG_HOST                  | Logstash endpoint.                                    |
|                           | Formatted like this: `hostname:port`                  |
+---------------------------+-------------------------------------------------------+
| MCC_LIST                  | List of Mobile Country Codes to ingest from feed.     |
|                           | USA is 310, 311, 312, 313, and 316                    |
|                           | List is comma-separated: "310,311,316"                |
+---------------------------+-------------------------------------------------------+
| MODE                      | Set to "clutch" to go into a wait loop during start.  |
|                           | Useful for troubleshooting.                           |
+---------------------------+-------------------------------------------------------+
| NO_FEED_UPDATE            | (Optional) If set, do not attempt to update the feed  |
|                           | on boot.                                              |
+---------------------------+-------------------------------------------------------+
| STATE_LIST                | Comma-separated list of states for feed ingestion.    |
|                           | California and Texas would be: "CA,TX"                |
+---------------------------+-------------------------------------------------------+
| VAULT_PATH                | Path to Logstash/Filebeat credentials in Vault.       |
|                           | In the demo environment, this is 'secret/client'      |
+---------------------------+-------------------------------------------------------+
| VAULT_TOKEN               | Client token used to retrieve credentials from Vault. |
+---------------------------+-------------------------------------------------------+
| VAULT_URL                 | URL for Vault instance containing Logstash/Filebeat   |
|                           | credentials.  Looks like: "https://ser.ver.com:8200"  |
+---------------------------+-------------------------------------------------------+
| NO_FEED_UPDATE            | If set, do not attempt to update the feed on boot.    |
+---------------------------+-------------------------------------------------------+
| GSM_MODEM_PORT            | (Optional) GSM modem USB-TTY port. This should        |
|                           | be autodetected and not need to be set.               |
|                           | Looks like: /dev/ttyUSB0                              |
|                           | See: "Found but undetected TTY " in the docs          |
+---------------------------+-------------------------------------------------------+
| GPS_DEVICE_PORT           | (Optional) GPS device USB-TTY port. This should       |
|                           | be autodetected and not need to be set.               |
|                           | Looks like: /dev/ttyUSB0                              |
|                           | See: "Found but undetected TTY " in the docs          |
+---------------------------+-------------------------------------------------------+
