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
    scan_results_queue = deque([])
    message_write_queue = deque([])
    gps_location = {}
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
    gps_consumer_thread = threading.Thread(target=gps_consumer,
                                           args=[config])
    enricher_thread = threading.Thread(target=enricher,
                                       args=[config])
    writer_thread = threading.Thread(target=output,
                                     args=[config])
    kalibrate_consumer_thread.daemon = True
    gsm_modem_consumer_thread.daemon = True
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
    time.sleep(5)
    print "Starting GPS Consumer"
    gpsd_command = "gpsd %s" % config.gps_device
    sitchlib.Utility.start_component(gpsd_command)
    while True:
        gps_listener = sitchlib.GpsListener()
        for fix in gps_listener:
            gps_location = fix
            print "GPS location:"
            print gps_location
    except IndexError:
            # print "Output queue empty"
            time.sleep(3)


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
    override_suppression = [110]
    print "Now starting enricher"
    enr = sitchlib.Enricher(config, gps_location)
    while True:
        if abs((datetime.datetime.now() - enr.born_on_date).total_seconds()) > 86400:
            print "Recycling enricher..."
            print "Cycling enricher module for feed update"
            enr = sitchlib.Enricher(config, gps_location)
        try:
            scandoc = scan_results_queue.popleft()
            doctype = enr.determine_scan_type(scandoc)
            outlist = []
            if doctype == 'Kalibrate':
                # print "Enriching Kalibrate scan"
                outlist = enr.enrich_kal_scan(scandoc)
            elif doctype == 'GSM_MODEM':
                # print "Enriching SIM808 scan"
                outlist = enr.enrich_gsm_modem_scan(scandoc)
            elif doctype == 'GPS':
                # print "Updating GPS coordinates"
                outlist = enr.enrich_gps_scan(scandoc.copy())
                gps_location = scandoc
            else:
                print "Can't determine scan type for: "
                print scandoc
            # Clean the suppression list, everything over 12 hours
            for suppressed, tstamp in enr.suppressed_alerts.items():
                if abs((datetime.datetime.now() - tstamp).total_seconds()) > 43200:
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
                            enr.suppressed_alerts[log_bolus[1]["details"]] = datetime.datetime.now()
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
