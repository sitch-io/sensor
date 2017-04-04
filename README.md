# SITCH Sensor

[![Join the chat at https://gitter.im/sitch-io/sensor](https://badges.gitter.im/sitch-io/sensor.svg)](https://gitter.im/sitch-io/sensor?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)


[![Build Status](https://travis-ci.org/sitch-io/sensor.svg?branch=master)](https://travis-ci.org/sitch-io/sensor)

[![Code Climate](https://codeclimate.com/github/sitch-io/sensor/badges/gpa.svg)](https://codeclimate.com/github/sitch-io/sensor)

[![Test Coverage](https://codeclimate.com/github/sitch-io/sensor/badges/coverage.svg)](https://codeclimate.com/github/sitch-io/sensor/coverage)



## Getting Started

## Prerequisites
* Accounts with the following providers:
  * Resin.io
  * Github
* Access to the following services (See Service configuration for more
  information)
  * Logstash
  * Vault
  * SITCH feed.  See https://github.com/sitch-io/feed_builder for more
  information.
* Hardware
  * Raspberry Pi 3
  * Simcom (SIM808 | SIM800L | SIM900) GSM modem with SIM
  * USB TTY cable (for GSM modem)
  * RTL-SDR device.  Tested with NooElec NESDR Mini and NooElec NESDR XTR
  * GlobalSat USB GPS dongle (any gpsd-compatible USB GPS shold work)

## Step by step...

1. Create an application in Resin.
1. Fork this project and clone it on your workstation.  Or clone it directly...
but forking makes modifications and PRs easier to deal with.
1. Add the Resin application as a remote repo (`git remote add resin myusername@git.resin.io/myusername/myapplicationname.git`)
1. Push to your Resin application: `git push resin master`

We expect the following environment variables to be set in Resin:


| Variable           | Purpose                                                 |
|--------------------|---------------------------------------------------------|
| FEED_URL_BASE      | Base URL for feed data retrieval                        |
| GSM_MODEM_BAND     | Band to scan with SIM808 (try GSM850_MODE)              |
| KAL_BAND           | Band to scan with Kalibrate (try GSM850)                |
| KAL_GAIN           | Gain setting for Kalibrate (try 60-80)                  |
| KAL_THRESHOLD      | Threshold for alerting on Kalibrate ARFCN power         |
| LOCATION_NAME      | Override the default device name (Resin UUID)           |
| LOG_HOST           |  hostname:port                                          |
| MCC_LIST           | Comma-separated list of MCCs to retrieve feed files for |
| MODE               | Set to 'clutch' to go into a wait loop (for debugging)  |
| STATE_LIST         | List of states (in caps) for FCC feed.  ex: "CA,TX"     |
| GSM_MODEM_PORT     | Override GSM modem autodetect                           |
| VAULT_PATH         | Path to logstash cert/keys in Vault                     |
| VAULT_TOKEN        | Token for accessing credentials in vault                |
| VAULT_URL          | URL for accessing Vault. ex: https://v.example.com:port |
| CGI_WHITELIST      | List of CGIs we trust (see below)                       |
| FEED_RADIO_TARGETS | List of radios for feed (optional, defaults to GSM)     |


The CGI_WHITELIST will suppress alert 110 (BTS metadata changed) if the CGI of
channel 0 in your GSM modem output matches an item in CGI_WHITELIST.  This is
the format you should use: `MCC:MNC:LAC:CELLID,MCC:MNC:LAC:CELLID`  This is
what the contents of that environment variable should look like:
`310:411:11:22,310:411:11:23`.  This environment variable is not required.


## Testing
Testing is done with pytest.  Coverage module optional.

Testing requirements (local testing possible only on Linux):
* lshw
* pip packages: pytest-cov pytest-pep8 pyserial hvac kalibrate haversine
python-geoip python-geoip-geolite2 pyudev gps3 LatLon python-dateutil


1. Navigate to the base directory of the repository.
1. Set the environment variable to reach your SITCH feed:
`export SITCH_FEED_BASE=https://MY.FEED.URL/base`
1. Run `py.test --cov sitchlib` .

* OR, offer a PR and let travis-ci build and run the tests for you.

## GSM modem device detection
If you're using a GSM modem that's not recognized by the device detector,
please add the output from running the `ATI` command against your GSM modem in
the variable named `positive_match` in the `is_a_gsm_modem()` method, in the
`sensor/sitch/sitchlib/device_detector.py` file.  Then send a pull request so
that everyone can get the benefit of your discovery.

## Contributing
* Please do PRs against the `test` branch.
* To add an ID string to the device detector for GSM modems, add part of the
ID string to the ```positive_match``` variable in the
```DeviceDetector.is_a_gsm_modem()``` function
