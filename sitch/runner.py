"""This is the main process which runs all threads."""

import sitchlib
import kalibrate
import threading
import time
from collections import deque
from socket import error as SocketError


def main():
    """All magic happens under this fn."""
    global scan_results_queue
    global message_write_queue
    global arfcn_correlator_queue
    global cgi_correlator_queue
    global geo_correlator_queue
    global gps_location
    gps_location = {}
    scan_results_queue = deque([])
    message_write_queue = deque([])
    arfcn_correlator_queue = deque([])
    cgi_correlator_queue = deque([])
    geo_correlator_queue = deque([])
    sensor_version = sitchlib.__version__
    startup_string = "Starting SITCH Sensor v%s" % sensor_version
    print(startup_string)
    print("Runner: Setting config...")
    config = sitchlib.ConfigHelper()
    if config.mode == 'clutch':
        while True:
            time.sleep(30)
            print("Runner: Mode is clutch.  Wait cycle...")

    print("Runner: Verify paths for feed and logs...")
    sitchlib.Utility.create_path_if_nonexistent(config.feed_dir)
    sitchlib.Utility.create_path_if_nonexistent(config.log_prefix)

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

    print("Runner: Instantiating feed manager...")
    feed_mgr = sitchlib.FeedManager(config)
    feed_mgr.update_feed_files()
    print("Runner: Creating feed DB...")
    feed_mgr.update_feed_db()

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
    decomposer_thread = threading.Thread(target=decomposer,
                                         name="decomposer",
                                         args=[config])
    arfcn_correlator_thread = threading.Thread(target=arfcn_correlator,
                                               name="arfcn_correlator",
                                               args=[config])
    cgi_correlator_thread = threading.Thread(target=cgi_correlator,
                                             name="cgi_correlator",
                                             args=[config])
    geo_correlator_thread = threading.Thread(target=geo_correlator,
                                             name="geo_correlator",
                                             args=[config])
    writer_thread = threading.Thread(target=output,
                                     name="writer",
                                     args=[config])
    kalibrate_consumer_thread.daemon = True
    gsm_modem_consumer_thread.daemon = True
    geoip_consumer_thread.daemon = True
    gps_consumer_thread.daemon = True
    # enricher_thread.daemon = True
    decomposer_thread.daemon = True
    arfcn_correlator_thread.daemon = True
    cgi_correlator_thread.daemon = True
    geo_correlator_thread.daemon = True
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
    print("Runner: Starting decomposer thread...")
    decomposer_thread.start()
    print("Runner: Starting ARFCN correlator thread...")
    arfcn_correlator_thread.start()
    print("Runner: Starting CGI correlator thread...")
    cgi_correlator_thread.start()
    print("Runner: Starting geo correlator thread...")
    geo_correlator_thread.start()
    print("Runner: Starting writer thread...")
    writer_thread.start()
    while True:
        time.sleep(config.health_check_interval)
        active_threads = threading.enumerate()
        queue_sizes = {"scan_results": len(scan_results_queue),
                       "arfcn_correlator": len(cgi_correlator_queue),
                       "cgi_correlator": len(cgi_correlator_queue),
                       "geo_correlator": len(geo_correlator_queue)}
        #  Heartbeat messages
        for item in active_threads:
            message_write_queue.append(("heartbeat", sitchlib.Utility.heartbeat(item.name)))  # NOQA
        message_write_queue.append(("health_check", sitchlib.Utility.get_performance_metrics(queue_sizes)))  # NOQA

    return


def init_event_injector(init_event):
    """Pass the sitch init into this fn."""
    evt = [("sitch_init"), init_event]
    message_write_queue.append(evt)


def gsm_modem_circuit_breaker(band, tty_port):
    """Circuit breaker for GSM modem functionality."""
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
        print("Runner: Getting IMSI from SIM...")
        imsi = consumer.get_imsi()
        init_event_injector({"evt_cls": "gsm_consumer",
                             "evt_type": "sim_imsi",
                             "evt_data": str(imsi)})
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
                                 "scan_location": "",
                                 "scanner_public_ip": config.public_ip}
            retval = dict(scan_job_template)
            retval["scan_results"] = report
            retval["scan_finish"] = sitchlib.Utility.get_now_string()
            retval["scan_location"] = str(config.device_id)
            retval["scan_program"] = "GSM_MODEM"
            retval["band"] = config.gsm_modem_band
            retval["scanner_public_ip"] = config.public_ip
            retval["site_name"] = config.site_name
            processed = retval.copy()
            scan_results_queue.append(processed)


def gps_consumer(config):
    """Take events from gpsd, put them in queue."""
    global gps_location
    print("Runner: Starting GPS Consumer")
    print("Runner: gpsd configured for %s" % config.gps_device_port)
    gpsd_command = "gpsd -n %s" % config.gps_device_port
    sitchlib.Utility.start_component(gpsd_command)
    print("Runner: Starting gpsd with:")
    print(gpsd_command)
    time.sleep(10)
    while True:
        try:
            gps_listener = sitchlib.GpsListener(delay=120)
            for fix in gps_listener:
                scan_results_queue.append(fix)
        except IndexError:
            time.sleep(3)
        except SocketError as e:
            print(e)


def geoip_consumer(config):
    """Take events from GeoIP and put them in queue."""
    print("Runner: Starting GeoIP Consumer")
    while True:
        geoip_listener = sitchlib.GeoIp(delay=600)
        for result in geoip_listener:
            scan_results_queue.append(result)


def disable_scanner(event_struct):
    """Scanner circuit breaker."""
    stdout_msg = "Runner: %s" % event_struct["evt_data"]
    print(stdout_msg)
    init_event_injector(event_struct)
    while True:
        time.sleep(120)
    return


def kalibrate_consumer(config):
    """Take calibrate scans, and put them in queue."""
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
        scan_document["scan_location"] = str(config.device_id)
        scan_document["site_name"] = config.site_name,
        scan_document["scanner_public_ip"] = config.public_ip
        scan_results_queue.append(scan_document.copy())
    return


def arfcn_correlator(config):
    """ARFCN correlator thread."""
    correlator = sitchlib.ArfcnCorrelator(config.state_list,
                                          config.feed_dir,
                                          config.arfcn_whitelist,
                                          config.kal_threshold,
                                          config.device_id)
    while True:
        try:
            item = arfcn_correlator_queue.popleft()
            alarms = correlator.correlate(item)
            if len(alarms) > 0:
                message_write_queue.extend(alarms)
        except IndexError:
            # Queue must be empty...
            time.sleep(1)


def cgi_correlator(config):
    """CGI correlator thread."""
    correlator = sitchlib.CgiCorrelator(config.feed_dir,
                                        config.cgi_whitelist,
                                        config.mcc_list,
                                        config.device_id)
    while True:
        try:
            item = cgi_correlator_queue.popleft()
            alarms = correlator.correlate(item)
            if len(alarms) > 0:
                message_write_queue.extend(alarms)
        except IndexError:
            # Queue must be empty...
            time.sleep(1)


def geo_correlator(config):
    """Correlate GPS events, look for drift."""
    correlator = sitchlib.GeoCorrelator(config.device_id)
    while True:
        try:
            item = geo_correlator_queue.popleft()
            alarms = correlator.correlate(item)
            if len(alarms) > 0:
                message_write_queue.extend(alarms.copy())
        except IndexError:
            # Queue must be empty...
            time.sleep(1)


def decomposer(config):
    """Decompose all scans we get from devices.

    Expected types:
        * `scan` (Kalibrate)
        * `kal_channel` (channel extracted from Kalibrate scan)
        * `cell` (full scan from cellular radio)
        * `gsm_modem_channel` (channel extracted from GSM modem output)
        * `gps` (output from gpsd)
    """
    d_composer = sitchlib.Decomposer
    while True:
        try:
            scandoc = scan_results_queue.popleft()
            decomposed = d_composer.decompose(scandoc)
            if decomposed == []:
                continue
            else:
                for result in decomposed:
                    s_type = result[0]
                    if s_type == "scan":
                        message_write_queue.append(result)
                    elif s_type == "kal_channel":
                        arfcn_correlator_queue.append(result)
                        message_write_queue.append(result)
                    elif s_type == "cell":
                        message_write_queue.append(result)
                    elif s_type == "gsm_modem_channel":
                        cgi_correlator_queue.append(result)
                        arfcn_correlator_queue.append(result)
                        message_write_queue.append(result)
                    elif s_type == "gps":
                        arfcn_correlator_queue.append(result)
                        cgi_correlator_queue.append(result)
                        message_write_queue.append(result)
                    elif s_type == "geo_ip":
                        message_write_queue.append(result)
                    else:
                        print("Decomposer: Unrecognized scan type %s" % s_type)
        except IndexError:
            # Queue is empty...
            time.sleep(1)


def output(config):
    """Retrieve messages from queue and write to disk."""
    time.sleep(5)
    logger = sitchlib.LogHandler(config)
    print("Runner: Output module instantiated.")
    print("Runner: Starting Filebeat...")
    time.sleep(5)
    sitchlib.Utility.start_component("/usr/local/bin/filebeat-linux-arm -c /etc/filebeat.yml")  # NOQA
    while True:
        try:
            msg_bolus = message_write_queue.popleft()
            logger.record_log_message(msg_bolus)
            del msg_bolus
        except IndexError:
            time.sleep(3)
        except Exception as e:
            print("Runner: Exception caught while processing message for output:")  # NOQA
            print(e)
            print(msg_bolus)


if __name__ == "__main__":
    main()
