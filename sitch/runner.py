""" Starts gpsd and logstash and runs a thread for collecting and enriching
SIM808 engineering mode data.
  One thread for serial interaction and collection
  One thread for enrichment and appending to logfile:
  If log message is GPS, we update the location var for the enrichment
  thread.
"""
import sitchlib
import datetime
import kalibrate
import threading
import time
from collections import deque


def main():
    global scan_results_queue
    global message_write_queue
    global gps_location
    gps_location = {}
    scan_results_queue = deque([])
    message_write_queue = deque([])
    config = sitchlib.ConfigHelper()
    if config.mode == 'clutch':
        while True:
            time.sleep(30)
            print "Mode is clutch.  Ain't doin' nothin'"

    # Write LS cert
    sitchlib.Utility.create_path_if_nonexistent(config.logstash_cert_path)
    sitchlib.Utility.write_file(config.logstash_cert_path,
                                config.ls_cert)

    # Write LS config
    sitchlib.Utility.write_file("/etc/logstash-forwarder",
                                config.build_logstash_config())

    # Write logrotate config
    sitchlib.Utility.write_file("/etc/logrotate.d/sitch",
                                config.build_logrotate_config())

    # Kill interfering driver
    try:
        sitchlib.Utility.start_component("modprobe -r dvb_usb_rtl28xxu")
    except:
        print "Error trying to unload stock driver"

    # Give everything a few seconds to catch up (writing files, etc...)
    time.sleep(5)
    # Start cron
    sitchlib.Utility.start_component("/etc/init.d/cron start")

    # Configure threads
    kalibrate_consumer_thread = threading.Thread(target=kalibrate_consumer,
                                                 args=[config])
    gsm_modem_consumer_thread = threading.Thread(target=gsm_modem_consumer,
                                                 args=[config])
    geoip_consumer_thread = threading.Thread(target=geoip_consumer,
                                             args=[config])
    gps_consumer_thread = threading.Thread(target=gps_consumer,
                                           args=[config])
    enricher_thread = threading.Thread(target=enricher,
                                       args=[config])
    writer_thread = threading.Thread(target=output,
                                     args=[config])
    kalibrate_consumer_thread.daemon = True
    gsm_modem_consumer_thread.daemon = True
    geoip_consumer_thread.daemon = True
    gps_consumer_thread.daemon = True
    enricher_thread.daemon = True
    writer_thread.daemon = True
    # Kick off threads
    print "Starting Kalibrate consumer thread..."
    kalibrate_consumer_thread.start()
    print "Starting GSM Modem consumer thread..."
    gsm_modem_consumer_thread.start()
    print "Starting GPS consumer thread..."
    gps_consumer_thread.start()
    print "Starting GeoIP consumer thread..."
    geoip_consumer_thread.start()
    print "Starting enricher thread..."
    enricher_thread.start()
    print "Starting writer thread..."
    writer_thread.start()
    while True:
        time.sleep(60)
        print "heartbeat..."
        if kalibrate_consumer_thread.is_alive is False:
            print "Kalibrate consumer is dead..."
        #    print "Kalibrate thread died... restarting!"
        #    kalibrate_consumer_thread.start()
        if gsm_modem_consumer_thread.is_alive is False:
            print "GSM Modem consumer is dead..."
        #    print "SIM808 consumer thread died... restarting!"
        #    sim808_consumer_thread.start()
        if gps_consumer_thread.is_alive is False:
            print "GPS consumer is dead..."
        if geoip_consumer_thread.is_alive is False:
            print "GPS consumer is dead..."
        if enricher_thread.is_alive is False:
            print "Enricher thread is dead..."
            # print "Enricher thread died... restarting!"
            # enricher_thread.start()
        if writer_thread.is_alive is False:
            print "Writer thread is dead..."
        #    print "Writer thread died... restarting!"
        #    writer_thread.start()
    return


def gsm_modem_consumer(config):
    scan_job_template = {"platform": config.platform_name,
                         "scan_results": [],
                         "scan_start": "",
                         "scan_finish": "",
                         "scan_program": "",
                         "scan_location": {},
                         "scanner_public_ip": config.public_ip}
    while True:
        print "GSM modem configured for %s" % config.gsm_modem_port
        tty_port = config.gsm_modem_port
        band = config.gsm_modem_band
        if band == "nope":
            print "Disabling GSM Modem scanning..."
            while True:
                time.sleep(120)
        # Sometimes the buffer is full and instantiation fails the first time
        try:
            consumer = sitchlib.GsmModem(tty_port)
        except:
            consumer = sitchlib.GsmModem(tty_port)
        consumer.set_band(band)
        time.sleep(2)
        # consumer.trigger_gps()
        time.sleep(2)
        consumer.set_eng_mode()
        time.sleep(2)
        for report in consumer:
            if report != {}:
                if "cell" in report[0]:
                    retval = dict(scan_job_template)
                    retval["scan_results"] = report
                    retval["scan_finish"] = sitchlib.Utility.get_now_string()
                    retval["scan_location"]["name"] = str(config.device_id)
                    retval["scan_program"] = "GSM_MODEM"
                    retval["band"] = config.gsm_modem_band
                    retval["scanner_public_ip"] = config.public_ip
                    scan_results_queue.append(retval.copy())
                    # print "SIM808 results sent for enrichment..."
                elif "lon" in report[0]:
                    retval = dict(scan_job_template)
                    retval["scan_results"] = report
                    retval["scan_finish"] = sitchlib.Utility.get_now_string()
                    retval["scan_location"]["name"] = str(config.device_id)
                    retval["scan_program"] = "GPS"
                    scan_results_queue.append(retval.copy())
                else:
                    print "No match!"
                    print report


def gps_consumer(config):
    print "Starting GPS Consumer"
    print "  gpsd configured for %s" % config.gps_device_port
    gpsd_command = "gpsd -n %s" % config.gps_device_port
    sitchlib.Utility.start_component(gpsd_command)
    time.sleep(10)
    gps_event = {"scan_program": "gps",
                 "scan_results": {}}
    while True:
        try:
            gps_listener = sitchlib.GpsListener(delay=60)
            for fix in gps_listener:
                gps_event["scan_results"] = fix
                scan_results_queue.append(gps_event.copy())
        except IndexError:
            time.sleep(3)


def geoip_consumer(config):
    print "Starting GeoIP Consumer"
    geoip_event = {"scan_program": "geo_ip",
                   "scan_results": {}}
    while True:
        geoip_listener = sitchlib.GeoIP(delay=60)
        for result in geoip_listener:
            geoip_event["scan_results"] = result
            scan_results_queue.append(geoip_event.copy())


def kalibrate_consumer(config):
    while True:
        scan_job_template = {"platform": config.platform_name,
                             "scan_results": [],
                             "scan_start": "",
                             "scan_finish": "",
                             "scan_program": "",
                             "scan_location": {}}
        band = config.kal_band
        if band == "nope":
            print "Disabling Kalibrate scanning..."
            while True:
                time.sleep(120)
        gain = config.kal_gain
        kal_scanner = kalibrate.Kal("/usr/local/bin/kal")
        start_time = sitchlib.Utility.get_now_string()
        kal_results = kal_scanner.scan_band(band, gain=gain)
        end_time = sitchlib.Utility.get_now_string()
        scan_document = scan_job_template.copy()
        scan_document["scan_start"] = start_time
        scan_document["scan_finish"] = end_time
        scan_document["scan_results"] = kal_results
        scan_document["scan_program"] = "Kalibrate"
        scan_document["scanner_name"] = config.device_id
        scan_document["scan_location"]["name"] = str(config.device_id)
        scan_document["scanner_public_ip"] = config.public_ip
        scan_results_queue.append(scan_document.copy())
        # print "Kalibrate results sent for enrichment..."
    return


def enricher(config):
    """ Enricher breaks apart kalibrate doc into multiple log entries, and
    assembles lines from gsm_modem into a main doc as well as writing multiple
    lines to the output queue for metadata """
    state = {"gps": {},
             "geoip": {},
             "geo_distance_meters": 0}
    override_suppression = [110]
    print "Now starting enricher"
    enr = sitchlib.Enricher(config, state)
    while True:
        try:
            scandoc = scan_results_queue.popleft()
            doctype = enr.determine_scan_type(scandoc)
            outlist = []
            if doctype == 'Kalibrate':
                outlist = enr.enrich_kal_scan(scandoc)
            elif doctype == 'GSM_MODEM':
                outlist = enr.enrich_gsm_modem_scan(state, scandoc)
            elif doctype == 'GPS':
                """ Every time we get a GPS reading, we check to make sure
                that it is close to the same distance from GeoIP as it was
                when it was last measured.  Alerts are generated if the drift
                is beyond threshold."""
                outlist = enr.enrich_gps_scan(scandoc.copy())
                geo_problem = enr.geo_drift_check(state["geo_distance_meters"],
                                                  state["geoip"],
                                                  scandoc["scan_results"],
                                                  config.gps_drift_threshold)
                if geo_problem:
                    outlist.append(geo_problem.copy())
                state["gps"] = scandoc["scan_results"]
                lat_1 = state["geoip"]["geometry"]["coordinates"][0]
                lon_1 = state["geoip"]["geometry"]["coordinates"][1]
                lat_2 = state["gps"]["geometry"]["coordinates"][0]
                lon_2 = state["gps"]["geometry"]["coordinates"][1]
                new_distance = (enr.calculate_distance(lon_1, lat_1,
                                                       lon_2, lat_2))
                state["geo_distance_meters"] = int(new_distance)
            elif doctype == 'GEOIP':
                outlist = enr.enrich_geoip_scan(scandoc.copy())
                state["geoip"] = scandoc["scan_results"]
            else:
                print "Can't determine scan type for: "
                print scandoc
            # Clean the suppression list, everything over 12 hours
            for suppressed, tstamp in enr.suppressed_alerts.items():
                if abs((datetime.datetime.now() -
                        tstamp).total_seconds()) > 43200:
                    del enr.suppressed_alerts[suppressed]
            # Send all the things to the outbound queue
            for log_bolus in outlist:
                if log_bolus[0] == 'sitch_alert':
                    if log_bolus[1]["id"] in override_suppression:
                        message_write_queue.append(log_bolus)
                        print log_bolus
                        continue
                    else:
                        if log_bolus[1]["details"] in enr.suppressed_alerts:
                            continue
                        else:
                            enr.suppressed_alerts[log_bolus[1]["details"]] = datetime.datetime.now()  # NOQA
                            print log_bolus
                message_write_queue.append(log_bolus)
        except IndexError:
            # print "Enricher queue empty"
            time.sleep(1)


def output(config):
    time.sleep(5)
    l = sitchlib.LogHandler(config)
    print "Output module instantiated."
    print "Starting Logstash forwarder..."
    time.sleep(5)
    sitchlib.Utility.start_component("/etc/init.d/logstash-forwarder start")
    while True:
        try:
            msg_bolus = message_write_queue.popleft()
            l.record_log_message(msg_bolus)
            del msg_bolus
        except IndexError:
            # print "Output queue empty"
            time.sleep(3)

if __name__ == "__main__":
    main()
