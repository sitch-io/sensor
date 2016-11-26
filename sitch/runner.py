""" This is the main process which runs collector, enricher, and output
threads.
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
    sensor_version = sitchlib.__version__
    startup_string = "Starting SITCH Sensor v%s" % sensor_version
    print(startup_string)
    print("Runner: Setting config...")
    config = sitchlib.ConfigHelper()
    if config.mode == 'clutch':
        while True:
            time.sleep(30)
            print("Runner: Mode is clutch.  Wait cycle...")

    print("Runner: Writing Filebeat key material...")
    sitchlib.Utility.create_path_if_nonexistent(config.ls_crypto_base_path)
    sitchlib.Utility.write_file(config.ls_ca_path,
                                config.vault_secrets["ca"])
    sitchlib.Utility.write_file(config.ls_cert_path,
                                config.vault_secrets["crt"])
    sitchlib.Utility.write_file(config.ls_key_path,
                                config.vault_secrets["key"])
    sitchlib.Utility.write_file("/etc/ssl/certs/logstash-ca.pem",
                                config.vault_secrets["ca"])

    # Write FB config
    config.write_filebeat_config()

    # Write logrotate config
    sitchlib.Utility.write_file("/etc/logrotate.d/sitch",
                                config.build_logrotate_config())

    # Kill interfering driver
    try:
        sitchlib.Utility.start_component("modprobe -r dvb_usb_rtl28xxu")
    except:
        print("Runner: Error trying to unload stock driver")

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
    print("Runner: Starting Kalibrate consumer thread...")
    kalibrate_consumer_thread.start()
    print("Runner: Starting GSM Modem consumer thread...")
    gsm_modem_consumer_thread.start()
    print("Runner: Starting GPS consumer thread...")
    gps_consumer_thread.start()
    print("Runner: Starting GeoIP consumer thread...")
    geoip_consumer_thread.start()
    print("Runner: Starting enricher thread...")
    enricher_thread.start()
    print("Runner: Starting writer thread...")
    writer_thread.start()
    while True:
        time.sleep(60)
        active_threads = threading.enumerate()
        #  Heartbeat messages
        for item in active_threads:
            scan_results_queue.append(sitchlib.Utility.heartbeat(item.name))
    return

def init_event_injector(init_event):
    "Pass a dict into this fn."
    evt = [("sitch_init"), init_event]
    message_write_queue.append(evt)

def gsm_modem_circuit_breaker(band, tty_port):
    if band == "nope":
        disable_scanner({"evt_cls": "gsm_consumer",
                         "evt_type": "config_state",
                         "evt_data": "GSM scanning disabled"})
    if tty_port is None:
        print("Runner: No GSM modem auto-detected or otherwise configured!")
        disable_scanner({"evt_cls": "gsm_consumer",
                         "evt_type": "config_state",
                         "evt_data": "GSM scanning not configured"})

def gsm_modem_consumer(config):
    while True:
        print("Runner: GSM modem configured for %s" % config.gsm_modem_port)
        tty_port = config.gsm_modem_port
        band = config.gsm_modem_band
        # Catch this thread before initialization if configis insufficient
        gsm_modem_circuit_breaker(band, tty_port)
        # Sometimes the buffer is full and instantiation fails the first time
        try:
            consumer = sitchlib.GsmModem(tty_port)
        except:
            consumer = sitchlib.GsmModem(tty_port)
        time.sleep(2)
        consumer.eng_mode(False)
        print("Runner: Getting registration info...")
        reg_info = consumer.get_reg_info()
        init_event_injector({"evt_cls": "gsm_consumer",
                             "evt_type": "registration",
                             "evt_data": str(reg_info)})
        print("Runner: Dumping current GSM modem config...")
        dev_config = consumer.dump_config()
        init_event_injector({"evt_cls": "gsm_consumer",
                             "evt_type": "device_config",
                             "evt_data": " | ".join(dev_config)})
        time.sleep(2)
        consumer.set_band(band)
        time.sleep(2)
        consumer.eng_mode(True)
        time.sleep(2)
        for report in consumer:
            scan_job_template = {"platform": config.platform_name,
                                 "scan_results": [],
                                 "scan_start": "",
                                 "scan_finish": "",
                                 "scan_program": "",
                                 "scan_location": {},
                                 "scanner_public_ip": config.public_ip}
            retval = dict(scan_job_template)
            retval["scan_results"] = report
            retval["scan_finish"] = sitchlib.Utility.get_now_string()
            retval["scan_location"]["name"] = str(config.device_id)
            retval["scan_program"] = "GSM_MODEM"
            retval["band"] = config.gsm_modem_band
            retval["scanner_public_ip"] = config.public_ip
            processed = retval.copy()
            scan_results_queue.append(processed)


def gps_consumer(config):
    global gps_location
    print("Runner: Starting GPS Consumer")
    print("Runner: gpsd configured for %s" % config.gps_device_port)
    gpsd_command = "gpsd -n %s" % config.gps_device_port
    sitchlib.Utility.start_component(gpsd_command)
    print("Runner: Starting gpsd with:")
    print(gpsd_command)
    time.sleep(10)
    gps_event = {"scan_program": "gps",
                 "scan_results": {}}
    while True:
        try:
            gps_listener = sitchlib.GpsListener(delay=120)
            for fix in gps_listener:
                scan_compile_and_queue(gps_event, fix)
        except IndexError:
            time.sleep(3)
        except SocketError as e:
            print(e)


def geoip_consumer(config):
    print("Runner: Starting GeoIP Consumer")
    geoip_event = {"scan_program": "geo_ip",
                   "scan_results": {}}
    while True:
        geoip_listener = sitchlib.GeoIp(delay=600)
        for result in geoip_listener:
            scan_compile_and_queue(geoip_event, result)

def scan_compile_and_queue(scan_template, result):
    scan_template["scan_results"] = result
    scan_results_queue.append(scan_template.copy())

def disable_scanner(event_struct):
    stdout_msg = "Runner: %s" % event_struct["evt_data"]
    print(stdout_msg)
    init_event_injector(event_struct)
    while True:
        time.sleep(120)
    return

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
            disable_scanner({"evt_cls": "kalibrate_consumer",
                             "evt_type": "config_state",
                             "evt_data": "Kalibrate scanning disabled"})
        gain = config.kal_gain
        kal_scanner = kalibrate.Kal("/usr/local/bin/kal-linux-arm")
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
    return


def enricher(config):
    """ Enricher breaks apart kalibrate doc into multiple log entries, and
    assembles lines from gsm_modem into a main doc as well as writing multiple
    lines to the output queue for metadata """
    state = {"gps": {},
             "geoip": {},
             "geo_anchor": {},
             "geo_distance_meters": 0}
    override_suppression = [110]
    print("Runner: Now starting enricher")
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
                if state["geo_anchor"] == {}:
                    state["geo_anchor"] = scandoc["scan_results"].copy()
                    msg = "Runner: Geo anchor: %s" % sitchlib.Utility.pretty_string(state["geo_anchor"])
                    print(msg)
                outlist = enr.enrich_gps_scan(scandoc.copy())
                geo_problem = enr.geo_drift_check(state["geo_distance_meters"],
                                                  state["geo_anchor"],
                                                  scandoc["scan_results"],
                                                  config.gps_drift_threshold)
                if geo_problem:
                    outlist.append(geo_problem)
                state["gps"] = scandoc["scan_results"]
                lat_1 = state["geo_anchor"]["geometry"]["coordinates"][0]
                lon_1 = state["geo_anchor"]["geometry"]["coordinates"][1]
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
                print("Runner: Can't determine scan type for: ")
                print(scandoc)
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
                        continue
                    else:
                        if log_bolus[1]["details"] in enr.suppressed_alerts:
                            continue
                        else:
                            enr.suppressed_alerts[log_bolus[1]["details"]] = datetime.datetime.now()  # NOQA
                message_write_queue.append(log_bolus)
            for log_bolus in outlist:
                channel_events = ["gsm_modem_channel", "kal_channel"]
                if log_bolus[0] in channel_events:
                    target_arfcn = log_bolus[1]["arfcn_int"]
                    enriched_arfcn = enr.check_arfcn_in_range(target_arfcn)
                    for item in enriched_arfcn:
                        message_write_queue.append(item)
        except IndexError:
            time.sleep(1)

def output(config):
    time.sleep(5)
    l = sitchlib.LogHandler(config)
    print("Runner: Output module instantiated.")
    print("Runner: Starting Filebeat...")
    time.sleep(5)
    sitchlib.Utility.start_component("/usr/local/bin/filebeat-linux-arm -c /etc/filebeat.yml")
    while True:
        try:
            msg_bolus = message_write_queue.popleft()
            l.record_log_message(msg_bolus)
            del msg_bolus
        except IndexError:
            time.sleep(3)
        except Exception as e:
            print("Runner: Exception caught while processing message for output:")
            print(e)
            print(msg_bolus)

if __name__ == "__main__":
    main()
