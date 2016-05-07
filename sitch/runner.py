""" Starts gpsd and logstash and runs a thread for collecting and enriching
SIM808 engineering mode data.
  One thread for serial interaction and collection
  One thread for enrichment and appending to logfile:
  If log message is GPS, we update the location var for the enrichment
  thread.
"""
from sitchlib import ConfigHelper as config_helper
from sitchlib import Enricher as enricher_module
from sitchlib import Utility as utility
from sitchlib import LogHandler as logger
from sitchlib import FonaReader as sim808
import json
import kalibrate
import sys
import threading
import time
from collections import deque
from multiprocessing import Pool


def main():
    global scan_results_queue
    global message_write_queue
    global gps_location
    scan_results_queue = deque([])
    message_write_queue = deque([])
    gps_location = {}
    config = config_helper()
    if config.mode == 'clutch':
        while True:
            time.sleep(30)
            print "Mode is clutch.  Ain't doin' nothin'"
    # Write LS cert
    utility.create_path_if_nonexistent(config.logstash_cert_path)
    utility.write_file(config.logstash_cert_path,
                       config.ls_cert)
    # Write LS config
    utility.write_file("/etc/logstash-forwarder",
                       config.build_logstash_config())
    # Write logrotate config
    utility.write_file("/etc/logrotate.d/sitch",
                       config.build_logrotate_config())
    # Start logstash service
    ls_success = utility.start_component("/etc/init.d/logstash-forwarder start")
    if ls_success is False:
        print "Failed to start logstash-forwarder!!!\nExiting!"
        sys.exit(2)
    # Kill interfering driver
    utility.start_component("modprobe -r dvb_usb_rtl28xxu")
    # Start cron
    cron_success = utility.start_component("/etc/init.d/cron start")
    if cron_success is False:
        print "Failed to start cron, so no logrotate... keep an eye on your disk!"
    # Configure threads
    kalibrate_consumer_thread = threading.Thread(target=kalibrate_consumer,
                                                 args=[config])
    sim808_consumer_thread = threading.Thread(target=sim808_consumer,
                                              args=[config])
    enricher_thread = threading.Thread(target=enricher,
                                       args=[config])
    writer_thread = threading.Thread(target=output,
                                     args=[config])
    kalibrate_consumer_thread.daemon = True
    sim808_consumer_thread.daemon = True
    enricher_thread.daemon = True
    writer_thread.daemon = True
    # Kick off threads
    print "Starting Kalibrate consumer thread..."
    kalibrate_consumer_thread.start()
    print "Starting SIM808 consumer thread..."
    sim808_consumer_thread.start()
    print "Starting enricher thread..."
    enricher_thread.start()
    print "Starting writer thread..."
    writer_thread.start()
    # Periodically check to see if threads are still alive
    while True:
        time.sleep(60)
        print "heartbeat..."
        # if kalibrate_consumer_thread.is_alive is False:
        #    print "Kalibrate thread died... restarting!"
        #    kalibrate_consumer_thread.start()
        # if sim808_consumer_thread.is_alive is False:
        #    print "SIM808 consumer thread died... restarting!"
        #    sim808_consumer_thread.start()
        # if enricher_thread.is_alive is False:
        #    print "Enricher thread died... restarting!"
        #    enricher_thread.start()
        # if writer_thread.is_alive is False:
        #    print "Writer thread died... restarting!"
        #    writer_thread.start()
    return


def sim808_consumer(config):
    scan_job_template = {"platform": config.platform_name,
                         "scan_results": [],
                         "scan_start": "",
                         "scan_finish": "",
                         "scan_program": "",
                         "scan_location": {}}
    while True:
        tty_port = config.sim808_port
        band = config.sim808_band
        # Sometimes the buffer is full and causes a failed instantiation the first time
        try:
            consumer = sim808(tty_port)
        except:
            consumer = sim808(tty_port)
        consumer.set_band(band)
        for report in consumer:
            if report != {}:
                if "cell" in report[0]:
                    retval = dict(scan_job_template)
                    retval["scan_results"] = report
                    retval["scan_finish"] = utility.get_now_string()
                    retval["scan_location"] = str(config.device_id)
                    retval["scan_program"] = "SIM808"
                    scan_results_queue.append(retval.copy())
                    print "SIM808 results sent for enrichment..."
                elif "lon" in report[0]:
                    retval = dict(scan_job_template)
                    retval["scan_results"] = report
                    retval["scan_finish"] = utility.get_now_string()
                    retval["scan_location"] = str(config.device_id)
                    retval["scan_program"] = "GPS"
                    scan_results_queue.append(retval.copy())
                else:
                    print "No match!"
                    print report


def kalibrate_consumer(config):
    while True:
        scan_job_template = {"platform": config.platform_name,
                             "scan_results": [],
                             "scan_start": "",
                             "scan_finish": "",
                             "scan_program": "",
                             "scan_location": str(config.device_id)}
        band = config.kal_band
        gain = config.kal_gain
        kal_scanner = kalibrate.Kal("/usr/local/bin/kal")
        start_time = utility.get_now_string()
        kal_results = kal_scanner.scan_band(band, gain=gain)
        end_time = utility.get_now_string()
        scan_document = scan_job_template.copy()
        scan_document["scan_start"] = start_time
        scan_document["scan_finish"] = end_time
        scan_document["scan_results"] = kal_results
        scan_document["scan_program"] = "Kalibrate"
        scan_document["scanner_name"] = config.device_id
        scan_document["scan_location"] = gps_location
        scan_results_queue.append(scan_document.copy())
        print "Kalibrate results sent for enrichment..."
    return


def enricher(config):
    """ Enricher breaks apart kalibrate doc into multiple log entries, and
    assembles lines from sim808 into a main doc as well as writing multiple
    lines to the output queue for metadata """
    while True:
        enr = enricher_module(config)
        try:
            scandoc = scan_results_queue.popleft()
            doctype = enr.determine_scan_type(scandoc)
            results = []
            if doctype == 'Kalibrate':
                print "Processing Kalibrate scan"
                results = enr.enrich_kal_scan(scandoc)
                message_write_queue.append(results.copy())
            elif doctype == 'SIM808':
                print "Processing SIM808 scan"
                results = enr.enrich_sim808_scan(scandoc)
                message_write_queue.append(results.copy())
            elif doctype == 'GPS':
                print "Updating GPS coordinates"
                print results
                results = enr.enrich_gps_scan(scandoc.copy())
                gps_location = scandoc
            else:
                print "Can't determine scan type for: "
                print scandoc
        except IndexError:
            print "Enricher queue empty"
            time.sleep(1)


def output(config):
    l = logger(config)
    print "Output module instantiated."
    while True:
        try:
            msg_bolus = message_write_queue.popleft()
            print msg_bolus
            l.record_log_message(msg_type, writemsg)
            print writemsg
            del msg_bolus
        except IndexError:
            print "Output queue empty"
            time.sleep(3)

if __name__ == "__main__":
    main()
