# SITCH Sensor

[![Build Status](https://travis-ci.org/sitch-io/sensor.svg?branch=master)](https://travis-ci.org/sitch-io/sensor)

## Getting Started

## Prerequisites
* Accounts with the following providers:
  * Resin.io
  * Github
* Access to the following services (See Service configuration for more information)
  * Logstash
  * Vault
  * SITCH feed.  If you follow the Service configuration process, it will be located in AWS S3.
* Hardware
  * Raspberry Pi 2
  * Fona SIM808 GSM modem w/ USB TTY cable
  * RTL-SDR device.  Tested with NooElec NESDR Mini and NooElec NESDR XTR

## Step by step...

1. Create an application in Resin.
1. Fork this project and clone it on your workstation.  Or clone it directly... but forking makes modifications and PRs easier to deal with.
1. Add the Resin application as a remote repo (`git remote add resin myusername@git.resin.io/myusername/myapplicationname.git`)
1. Push to your Resin application: `git push resin master`

We expect the following environment variables to be set in Resin:
```shell
FEED_URL_BASE       # Base URL for feed data retrieval
KAL_BAND            # Band to scan with Kalibrate (try GSM850)
KAL_GAIN            # Gain setting for Kalibrate (try 80)
KAL_THRESHOLD       # Threshold for creating alerts based on Kalibrate's signal strength metric
LOCATION_NAME       # Override the default device naming, which is Resin device ID
LOG_HOST            # host:port
LOG_METHOD          # local_file or direct.  Local file expects that the logstash-forwarder daemon is shipping logs.  Direct sends right from the output thread, no file or logstash-forwarder daemon.  Not thoroughly tested.  No intelligent queue management in the event it's unable to reach the server.
MCC_LIST            # Comma-separated list of MCCs to retrieve feed files for
MODE                # setting this to 'clutch' will cause it to loop before all the fun stuff starts.  Great for when you're troubleshooting in the Resin console.
GSM_MODEM_BAND         # Band to scan with SIM808 (try GSM850_MODE)
GSM_MODEM_PORT         # Device for tty (try /dev/ttyUSB0)
VAULT_LS_CERT_PATH  # Path to logstash cert (secret/logstash-fwd-crt)
VAULT_TOKEN         # token for accessing credentials in vault
VAULT_URL           # https://vault.mydomain.com:port
```

## Testing
Testing is done with pytest.  Coverage module optional.

1. Navigate to the base directory of the repository.
1. Set the environment variable to reach your SITCH feed: `export SITCH_FEED_BASE=https://MY.FEED.URL/base`
1. Run `py.test --cov sitchlib` .

## Contributing
Please do PRs against the `test` branch.
