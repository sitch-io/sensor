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
from socket import error as SocketError


def main():
    global scan_results_queue
    global message_write_queue
    global gps_location
    gps_location = {}
    scan_results_queue = deque([])
    message_write_queue = deque([])
    print "Setting config..."
    config = sitchlib.ConfigHelper()
    if config.mode == 'clutch':
        while True:
            time.sleep(30)
            print "Mode is clutch.  Ain't doin' nothin'"

    print "Writing Logstash key material..."
    sitchlib.Utility.create_path_if_nonexistent(config.ls_crypto_base_path)
    sitchlib.Utility.write_file(config.ls_ca_path,
                                config.vault_secrets["ca"])
    sitchlib.Utility.write_file(config.ls_cert_path,
                                config.vault_secrets["crt"])
    sitchlib.Utility.write_file(config.ls_key_path,
                                config.vault_secrets["key"])
    sitchlib.Utility.write_file("/etc/ssl/certs/logstash-ca.pem",
                                config.vault_secrets["ca"])

    # Write LS config
    sitchlib.Utility.write_file("/etc/logstash-forwarder",
                                config.build_logstash_config())

    # Write FB config
    config.write_filebeat_config()

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
                                                 name="kalibrate_consumer",
                                                 args=[config])
    gsm_modem_consumer_thread = threading.Thread(target=gsm_modem_consumer,
                                                 name="gsm_modem_consumer",
                                                 args=[config])
    geoip_consumer_thread = threading.Thread(target=geoip_consumer,
                                             name="geoip_consumer",
                                             args=[config])
    gps_consumer_thread = threading.Thread(target=gps_consumer,
                                           name="gps_consumer",
                                           args=[config])
    enricher_thread = threading.Thread(target=enricher,
                                       name="enricher",
                                       args=[config])
    writer_thread = threading.Thread(target=output,
                                     name="writer",
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
        active_threads = threading.enumerate()
        #  Heartbeat messages
        for item in active_threads:
            scan_results_queue.append(sitchlib.Utility.heartbeat(item.name))
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
        if tty_port is None:
            print "No GSM modem auto-detected or otherwise configured!"
            while True:
                time.sleep(120)
        # Sometimes the buffer is full and instantiation fails the first time
        try:
            consumer = sitchlib.GsmModem(tty_port)
        except:
            consumer = sitchlib.GsmModem(tty_port)
        time.sleep(2)
        print "Getting registration info..."
        consumer.get_reg_info()
        print "Dumping current GSM modem config..."
        consumer.dump_config()
        time.sleep(2)
        consumer.set_band(band)
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
    global gps_location
    print "Starting GPS Consumer"
    print "  gpsd configured for %s" % config.gps_device_port
    gpsd_command = "gpsd -n %s" % config.gps_device_port
    sitchlib.Utility.start_component(gpsd_command)
    print "Starting gpsd with:"
    print gpsd_command
    time.sleep(10)
    gps_event = {"scan_program": "gps",
                 "scan_results": {}}
    while True:
        try:
            gps_listener = sitchlib.GpsListener(delay=120)
            for fix in gps_listener:
                gps_event["scan_results"] = fix
                scan_results_queue.append(gps_event.copy())
        except IndexError:
            time.sleep(3)
        except SocketError as e:
            print e


def geoip_consumer(config):
    print "Starting GeoIP Consumer"
    geoip_event = {"scan_program": "geo_ip",
                   "scan_results": {}}
    while True:
        geoip_listener = sitchlib.GeoIp(delay=600)
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
    enr.update_feeds()
    while True:
        try:
            scandoc = scan_results_queue.popleft()
            doctype = enr.determine_scan_type(scandoc)
            outlist = []
            if doctype == 'Kalibrate':
                outlist = enr.enrich_kal_scan(scandoc)
            elif doctype == 'HEARTBEAT':
                outlist.append(("heartbeat", scandoc))
            elif doctype == 'GSM_MODEM':
                outlist = enr.enrich_gsm_modem_scan(scandoc, state)
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
                new_distance = (sitchlib.Utility.calculate_distance(lon_1,
                                                                    lat_1,
                                                                    lon_2,
                                                                    lat_2))
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
        # except KeyError as e:
        #    print "Getting a key error!  Taking a dump!"
        #    print e
        #    print "outlist:"
        #    print outlist


def output(config):
    time.sleep(5)
    l = sitchlib.LogHandler(config)
    print "Output module instantiated."
    print "Starting Logstash forwarder..."
    time.sleep(5)
    # sitchlib.Utility.start_component("/etc/init.d/logstash-forwarder start")
    sitchlib.Utility.start_component("/usr/local/bin/filebeat-linux-arm -c /etc/filebeat.yml")
    while True:
        try:
            msg_bolus = message_write_queue.popleft()
            l.record_log_message(msg_bolus)
            del msg_bolus
        except IndexError:
            # print "Output queue empty"
            time.sleep(3)
        except Exception as e:
            print "Exception caught while processing message for output:"
            print e
            print msg_bolus

if __name__ == "__main__":
    main()
