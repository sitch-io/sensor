# Changelog

## v3.0

### Other

* Making log method and mode in ConfigHelper easier to deal with. [Ash Wilson]

* Updating README for v3. [Ash Wilson]

* Adding git changelog generator config. [Ash Wilson]

* Adding version and author attributes to init, using to help with changelog generation. [Ash Wilson]

* Adding codeclimate configs. [Ash Wilson]

* Is is not ==... [Ash Wilson]

* Noise maker for bad messages hitting write_log_message() [Ash Wilson]

* Cleaning out old comments, improving stdout messaging. [Ash Wilson]

* Minor edits. [Ash Wilson]

* Re-naming binaries, re-aligning as appropriate. [Ash Wilson]

* Removing some supporting code for logstash-forwarder, general cleanup. [Ash Wilson]

* That's not how you spell friendly... [Ash Wilson]

* Fixing json parse issues for primary BTS change alerts. [Ash Wilson]

* Correcting reference to sitch init events. [Ash Wilson]

* Adding instructions for expanding GSM device support. [Ash Wilson]

* Adding initialization log message generation points. [Ash Wilson]

* Removing unnecessary filebeat.yml file. [Ash Wilson]

* Adding support for initialization-related log messages. [Ash Wilson]

* Piping all CMD output to stdout. [Ash Wilson]

* Fixing enricher for integration tests. [Ash Wilson]

* Better placement for CGI processing. [Ash Wilson]

* Better placement for CGI processing. [Ash Wilson]

* Corrected bad variable name in kal enricher. [Ash Wilson]

* Adding integer fields for CGI and ARFCN. [Ash Wilson]

* Fixed filebeat config. [Ash Wilson]

* Catch SocketError from gpsd. [Ash Wilson]

* Messaging around cache behavior for ARFCN enricher. [Ash Wilson]

* Caching for arfcn enrichment. [Ash Wilson]

* Correcting issue with bad log file reference. [Ash Wilson]

* Cleaning up unnecessary print statements. [Ash Wilson]

* Better messaging around feed manager. [Ash Wilson]

* Better messaging around feed manager. [Ash Wilson]

* Better messaging around feed manager. [Ash Wilson]

* Aligining feed manager components. [Ash Wilson]

* Fixing reference to nonexistent method. [Ash Wilson]

* Wiring up the filebeat stuff. [Ash Wilson]

* Wiring up the filebeat stuff. [Ash Wilson]

* Wiring up feed retrieval for FCC and MCC. [Ash Wilson]

* Switching to filebeat. [Ash Wilson]

* Fixing bad order of args for GSM modem enrichment routine. [Ash Wilson]

* WIP: debugging GSM modem report parsing. [Ash Wilson]

* Removing GSM report debug output. [Ash Wilson]

* Letting key errors blow up for troubleshooting. [Ash Wilson]

* Doing a cleaner yaml dump for filebeat config file. [Ash Wilson]

* Adding pyyaml in build. [Ash Wilson]

* Adding initial support for filebeats. [Ash Wilson]

* Adding filebeat binaries. [Ash Wilson]

* Updating Dockerfile to add filebeat binary. [Ash Wilson]

* Testing logging. [Ash Wilson]

* Try formatting output differently. [Ash Wilson]

* Try dumping json. [Ash Wilson]

* Switching to LogstashFormatterV1. [Ash Wilson]

* Switching to LogstashFormatterV1. [Ash Wilson]

* Dropping Logstash CA into /etc/ssl/certs. [Ash Wilson]

* Switching back to LogstashHandler. [Ash Wilson]

* Switching back to LogstashHandler. [Ash Wilson]

* Switching back to LogstashHandler. [Ash Wilson]

* Switching back to LogstashHandler. [Ash Wilson]

* Fixing logger. [Ash Wilson]

* Fixing Dockerfile. [Ash Wilson]

* Fixing Dockerfile. [Ash Wilson]

* Fixing Dockerfile. [Ash Wilson]

* Fixing Dockerfile. [Ash Wilson]

* Tweaking Logstash client settings. [Ash Wilson]

* WIP: logstash in python. [Ash Wilson]

* WIP: moving to pure-python logstash delivery. [Ash Wilson]

* Converging logging methods to python module- cutting out logstash-forwarder. [Ash Wilson]

* Completed service-specific heartbeats.  Fixes #3. [Ash Wilson]

* WIP: heartbeat message generation. [Ash Wilson]

* WIP: heartbeat message generation. [Ash Wilson]

* Changing method for heartbeat message generation. [Ash Wilson]

* Wiring up the rest of the heartbeat messages. [Ash Wilson]

* Adding per-service heartbeat messages. [Ash Wilson]

* Adding GSM modem config dump. [Ash Wilson]

* Improving GSM startup process. [Ash Wilson]

* Getting registration information from GSM modem. [Ash Wilson]

* Adding waits and better logging for GSM modem initialization. [Ash Wilson]

* Setting GSM modem to auto-register, other minor cleanup. [Ash Wilson]

* Cleanup. [Ash Wilson]

* Moving all usbtty interaction to 4800. [Ash Wilson]

* Adding more verbose device detection output. [Ash Wilson]

* Adding waits to give usbtty ports a chance to sync. [Ash Wilson]

* Normalizing the handling of serial connection flushing/closing in device detector. [Ash Wilson]

* Adding verbose device detector output on device init. [Ash Wilson]

* Flushing serial port before closing, in device detector. [Ash Wilson]

* Improvements to device detector. [Ash Wilson]

* Improvements to device detector. [Ash Wilson]

* Improvements to device detector. [Ash Wilson]

* Adding a space into the ID string query. [Ash Wilson]

* Adding waits, change GSM detect to 9600. [Ash Wilson]

* Changing port speed and adding a short pre-init delay for GSM modem. [Ash Wilson]

* Improving formatting for GSM modem engineering mode init string. [Ash Wilson]

* Making noise for GSM modem. [Ash Wilson]

* Correcting reference to class method in config helper. [Ash Wilson]

* Improving interaction with device detector. [Ash Wilson]

* Aligning serial port speeds, all to 4800.  Added messaging to GPS initialization. [Ash Wilson]

* Adding messaging for otherwise unparseable GSM modem output. [Ash Wilson]

* Adding debug output, chasing down GSM modem stuff. [Ash Wilson]

* Improving test coverage, added kal enricher to __init__.py. [Ash Wilson]

* Fixing travis-ci config. [Ash Wilson]

* Commenting out unnecessary code, will clean up later. [Ash Wilson]

* Improving failure handling for log output. [Ash Wilson]

* Implementing deepcopy for geojson and gps info. [Ash Wilson]

* Now debugging GPS device. [Ash Wilson]

* Adding some debug statements to geoip listener. [Ash Wilson]

* Updating Dockerfile for LatLon python module. [Ash Wilson]

* Adding ARFCN enricher components. [Ash Wilson]

* Better handling for unconfigured GSM modem. [Ash Wilson]

* Improving messaging around caught exceptions. [Ash Wilson]

* Informative failure message when GSM modem is unconfigured. [Ash Wilson]

* Broader exception handling to catch JSON decode errors. [Ash Wilson]

* Fixes #19 by adding a limited iteration routine to open serial port for GSM modem. [Ash Wilson]

* Adding log type support for GeoIP. [Ash Wilson]

* Adding a wait to give serial device time to open. [Ash Wilson]

* Aligning pure python log shipping method. [Ash Wilson]

* Fixing data type issue (tuple to list) for some enriched scans. [Ash Wilson]

* Adding better error handling to runner/enricher. [Ash Wilson]

* Added note for improving device detection. [Ash Wilson]

* Caps, caps, caps. [Ash Wilson]

* Correcting old reference in routine that builds logstash config. [Ash Wilson]

* Correcting bad var type for inbound crypto material in ConfigHelper() [Ash Wilson]

* Correcting old varname for vault path. [Ash Wilson]

* Correcting lack of crypto ramdisk base path. [Ash Wilson]

* Correcting vars in config object. [Ash Wilson]

* Adding initialization message to device detector. [Ash Wilson]

* Fixing bad ordering in config initialization process. [Ash Wilson]

* Better filtering before GPS fix yield. [Ash Wilson]

* Less crap in the GPS feed, we hope. [Ash Wilson]

* Try to resolve a potential race condition and let gpsd have a few seconds to go live. [Ash Wilson]

* Revving to Ubuntu 16 for newer Python version. [Ash Wilson]

* Better wiring for the device autodetect feature. [Ash Wilson]

* Better wiring for the device autodetect feature. [Ash Wilson]

* Better wiring for the device autodetect feature. [Ash Wilson]

* Minor correction on how gps3 is called. [Ash Wilson]

* Changing over to gps3. [Ash Wilson]

* Wiring up GPS listener. [Ash Wilson]

* Fixing bad variable ref for GPS device. [Ash Wilson]

* Connecting the dots for gps global var. [Ash Wilson]

* Fixing try/except block. [Ash Wilson]

* Taking a stab at GPS devices. [Ash Wilson]

* Changing Logstash to use client authentication. [Ash Wilson]

* Breaking Kalibrate enricher to separate submodule. [Ash Wilson]

* No more auto DL of feed, static as fixtures.  Increasing travis testing routine coverage. [Ash Wilson]

* Fixes for unit tests. [Ash Wilson]

* Refactoring enricher component - WIP. [Ash Wilson]

* Adding GeoIp module. [Ash Wilson]

* Renaming sim808 and fona modules, adding Travis config. [Ash Wilson]

* Adding GPSD functionality. [Ash Wilson]

* Adding DeviceDetector class. [Ash Wilson]

* README corrections. [Ash Wilson]

* Correcting README. [Ash Wilson]

* Improving README. [Ash Wilson]

* Testing and contribution documentation. [Ash Wilson]

* README improvements. [Ash Wilson]

* Initial commit. [Ash Wilson]

* Kal enrich returns scan even if no towers found. [Ash Wilson]

* Corrected shite logic that didn't reset primary BTS. [Ash Wilson]

* Adding ARFCN to anomaly messaging. [Ash Wilson]

* Cleanup. [Ash Wilson]

* Fixed missing attribute in kal scan document. [Ash Wilson]

* Adding more meaningful errors to kal enricher. [Ash Wilson]

* Unfluning some bad queing logic. [Ash Wilson]

* Reduced verbosity of logger, fixed data structure for kal channels. [Ash Wilson]

* Fixed bad lat/lon formatting. [Ash Wilson]

* Cleaning up verbosity. [Ash Wilson]

* Cleaning up location acquisition. [Ash Wilson]

* Added log type for sitch_alert. [Ash Wilson]

* Better handling of device output in sim808, fix timedelta calc for enricher. [Ash Wilson]

* Cutting out unneeded feed manager thread. [Ash Wilson]

* Refactor for better imports. [Ash Wilson]

* Another forgotten import corrected. [Ash Wilson]

* Correcting missed import for FeedManager. [Ash Wilson]

* Dumb, dumb, dumb. [Ash Wilson]

* Debug messaging. [Ash Wilson]

* Testing messages for enricher. [Ash Wilson]

* Fixing syntax error in alert suppression logic. [Ash Wilson]

* Commit with waay more testing, alerts, geo, feed. [Ash Wilson]

* Testing feed... [Ash Wilson]

* Adding sensor public IP to scan output. [Ash Wilson]

* Getting the band back together. [Ash Wilson]

* More tweaks to channel field names. [Ash Wilson]

* Change output format for channel items. [Ash Wilson]

* Fixing output json formatting. [Ash Wilson]

* Rewiring scan_location to make room for GPS coords. [Ash Wilson]

* Changing to match indexes. [Ash Wilson]

* Adding some time for the FS to sync before kicking the daemons. [Ash Wilson]

* Fixing logstash forwarder startup routine. [Ash Wilson]

* Fixing cert formatting. [Ash Wilson]

* Cleanup, re-implement logstash daemon. [Ash Wilson]

* Troubleshooting log emission. [Ash Wilson]

* Fixing logstash emitter. [Ash Wilson]

* Cleaning up logger. [Ash Wilson]

* Getting to the logger now,  HOOOOAH. [Ash Wilson]

* Fixing kal enricher. [Ash Wilson]

* Fixing retval handling for enricher. [Ash Wilson]

* Fixing bad method calls. [Ash Wilson]

* Cleaning up enricher. [Ash Wilson]

* Stripping out the list. [Ash Wilson]

* Fixing bad type assignment. [Ash Wilson]

* More verbose logging. [Ash Wilson]

* Fixing syntax in SIM808 module. [Ash Wilson]

* Fixing references in logger. [Ash Wilson]

* Manual build of logstash handler. [Ash Wilson]

* Manual build of logstash handler. [Ash Wilson]

* Manual build of logstash handler. [Ash Wilson]

* Fix bad spelling. [Ash Wilson]

* Disable cron and logstash. [Ash Wilson]

* Fixing syntax. [Ash Wilson]

* Heartbeat logging. [Ash Wilson]

* Commenting out thread revival. [Ash Wilson]

* Attempting to isolate lockup. [Ash Wilson]

* Logger correction. [Ash Wilson]

* Logger correction. [Ash Wilson]

* Adding log streamer. [Ash Wilson]

* Adding log streamer. [Ash Wilson]

* Adding a clutch function. [Ash Wilson]

* Cleanup. [Ash Wilson]

* Cleanup, improve testing. [Ash Wilson]

* Changing logging. [Ash Wilson]

* Changing logging. [Ash Wilson]

* Refactor, tests. [Ash Wilson]

* Fix in init. [Ash Wilson]

* Restructure. [Ash Wilson]

* Simplify things. [Ash Wilson]

* Donwzo. [Ash Wilson]

* Whatevs. [Ash Wilson]

* Good night. [Ash Wilson]

* Whatevs. [Ash Wilson]

* Whatevs. [Ash Wilson]

* Getting tired.  bedtime. [Ash Wilson]

* Getting tired.  bedtime. [Ash Wilson]

* Dammmit. [Ash Wilson]

* Adding messaging. [Ash Wilson]

* Adding messaging. [Ash Wilson]

* Testing. [Ash Wilson]

* Cleanup. [Ash Wilson]

* Cleanup enricher. [Ash Wilson]

* Cleanup. [Ash Wilson]

* Testing. [Ash Wilson]

* Testing. [Ash Wilson]

* Cleanup. [Ash Wilson]

* Whatevs. [Ash Wilson]

* Fna. [Ash Wilson]

* Blah whatever. [Ash Wilson]

* Blah whatever. [Ash Wilson]

* Blah whatever. [Ash Wilson]

* More testing. [Ash Wilson]

* More output work. [Ash Wilson]

* Fix sim808 output format. [Ash Wilson]

* Bad syntax booooo. [Ash Wilson]

* Bad syntax booooo. [Ash Wilson]

* Bad syntax booooo. [Ash Wilson]

* Massaging GSM output. [Ash Wilson]

* Using GPS on board now. [Ash Wilson]

* Using GPS on board now. [Ash Wilson]

* Using GPS on board now. [Ash Wilson]

* Using GPS on board now. [Ash Wilson]

* Using GPS on board now. [Ash Wilson]

* GPS stuff. [Ash Wilson]

* Refining SIM808. [Ash Wilson]

* Refining SIM808. [Ash Wilson]

* Refining SIM808. [Ash Wilson]

* Better output formatting. [Ash Wilson]

* Better output formatting. [Ash Wilson]

* Sio crapp. [Ash Wilson]

* Sio crapp. [Ash Wilson]

* Sio crapp. [Ash Wilson]

* Sio crapp. [Ash Wilson]

* Sio crapp. [Ash Wilson]

* Sio crapp. [Ash Wilson]

* Fixong config helper. [Ash Wilson]

* Hacking on serial. [Ash Wilson]

* Hacking on serial. [Ash Wilson]

* Unicode to raw string. [Ash Wilson]

* Serial module work. [Ash Wilson]

* More output fixing. [Ash Wilson]

* No returns. [Ash Wilson]

* More massaging. [Ash Wilson]

* Tweaking output thread. [Ash Wilson]

* Blah blah output queue. [Ash Wilson]

* Blah blah output queue. [Ash Wilson]

* More messaging for logger. [Ash Wilson]

* Messaging in Runner. [Ash Wilson]

* Fising enricher. [Ash Wilson]

* Logging for sim808. [Ash Wilson]

* Fix kal perms. [Ash Wilson]

* Fixing ref to kal gain. [Ash Wilson]

* Fixing ref to utility obj. [Ash Wilson]

* Fixing platform info. [Ash Wilson]

* Fixing runner mishaps. [Ash Wilson]

* Fix ref to kal consumer. [Ash Wilson]

* Fix ref to crontab. [Ash Wilson]

* Adding kmod package. [Ash Wilson]

* Fixing mode for ls forwarder. [Ash Wilson]

* Figure out logstash no starty. [Ash Wilson]

* Fix reference to config file builders. [Ash Wilson]

* Fix reference to config file builders. [Ash Wilson]

* Fix reference to config file builders. [Ash Wilson]

* Fix reference to config file builders. [Ash Wilson]

* Fix reference to config file builders. [Ash Wilson]

* Fixing path mgmt. [Ash Wilson]

* Fixing dir creation. [Ash Wilson]

* Fixing dir creation. [Ash Wilson]

* Fixing dir creation. [Ash Wilson]

* Fix cert stuff. [Ash Wilson]

* Fix cert stuff. [Ash Wilson]

* Fix cert stuff. [Ash Wilson]

* Runner ref to config fix. [Ash Wilson]

* Runner ref to config fix. [Ash Wilson]

* Haggling with config helper. [Ash Wilson]

* Haggling with config helper. [Ash Wilson]

* Haggling with config helper. [Ash Wilson]

* Fising vault interaction. [Ash Wilson]

* Fising vault interaction. [Ash Wilson]

* Fising vault interaction. [Ash Wilson]

* Fix config helper. [Ash Wilson]

* Fix config helper. [Ash Wilson]

* Fixing config init. [Ash Wilson]

* Fixing ref to vault path. [Ash Wilson]

* Fis syntaxes. [Ash Wilson]

* Cleaning up CMD. [Ash Wilson]

* Fixing instantiation of config. [Ash Wilson]

* Fixing deque name. [Ash Wilson]

* Venv shit. [Ash Wilson]

* Venv shit. [Ash Wilson]

* Venv settings tweak. [Ash Wilson]

* Venv settings tweak. [Ash Wilson]

* Venv settings tweak. [Ash Wilson]

* Venv settings tweak. [Ash Wilson]

* Inching closer. [Ash Wilson]

* Rearranging. [Ash Wilson]

* More testing. [Ash Wilson]

* More testing. [Ash Wilson]

* More testing. [Ash Wilson]

* More testing. [Ash Wilson]

* Please just work. [Ash Wilson]

* Fixing Dockerfile venv config. [Ash Wilson]

* Fixing Dockerfile and missing imports. [Ash Wilson]

* Fixing Dockerfile and missing imports. [Ash Wilson]

* Fixing Dockerfile and missing imports. [Ash Wilson]

* Fixing Dockerfile and missing imports. [Ash Wilson]

* Fixing Dockerfile and missing imports. [Ash Wilson]

* Changing source image. [Ash Wilson]

* Changing source image. [Ash Wilson]

* Changing source image. [Ash Wilson]

* Dockerfile tweaks. [Ash Wilson]

* Dockerfile tweaks. [Ash Wilson]

* Fixing dockerfile again. [Ash Wilson]

* Fixed Dockerfile. [Ash Wilson]

* Squashing lots of things. [Ash Wilson]

* First release for DEF CON. [Ash Wilson]


## v2.0 (2016-07-25)

### Other

* Ready for Def Con. [Ash Wilson]

* First commit of all the things. [Ash Wilson]


