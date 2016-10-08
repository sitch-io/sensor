import hvac
import json
import os
import sys
from device_detector import DeviceDetector as dd
from utility import Utility as utility


class ConfigHelper:
    def __init__(self, feed_dir="/data/"):
        self.device_id = ConfigHelper.get_device_id()
        self.platform_name = utility.get_platform_name()
        self.log_prefix = "/var/log/sitch/"
        self.log_host = ConfigHelper.get_from_env("LOG_HOST")
        self.log_method = ConfigHelper.get_from_env("LOG_METHOD")
        self.kal_band = ConfigHelper.get_from_env("KAL_BAND")
        self.kal_gain = ConfigHelper.get_from_env("KAL_GAIN")
        self.kal_threshold = ConfigHelper.get_from_env("KAL_THRESHOLD")
        self.gsm_modem_band = ConfigHelper.get_from_env("GSM_MODEM_BAND")
        self.gsm_modem_port = ConfigHelper.get_gsm_modem_port()
        self.gps_device_port = ConfigHelper.get_gps_device_port()
        self.ls_ca_path = "/run/dbus/crypto/ca.crt"
        self.ls_cert_path = "/run/dbus/crypto/logstash.crt"
        self.ls_key_path = "/run/dbus/crypto/logstash.key"
        self.ls_crypto_base_path = "/run/dbus/crypto/"
        self.vault_token = ConfigHelper.get_from_env("VAULT_TOKEN")
        self.vault_url = ConfigHelper.get_from_env("VAULT_URL")
        self.vault_path = ConfigHelper.get_from_env("VAULT_PATH")
        self.mode = ConfigHelper.get_from_env("MODE")
        self.public_ip = str(utility.get_public_ip())
        self.feed_dir = feed_dir
        self.feed_url_base = ConfigHelper.get_from_env("FEED_URL_BASE")
        self.mcc_list = ConfigHelper.get_list_from_env("MCC_LIST")
        self.vault_secrets = self.get_secret_from_vault()
        self.gps_drift_threshold = 1000
        return

    @classmethod
    def get_gsm_modem_port(cls):
        if os.getenv('GSM_MODEM_PORT') is None:
            detector = dd()
            if detector.gsm_radios != []:
                target_device = dd().gsm_radios[0]["device"]
                print "Detected GSM modem at %s" % target_device
                return target_device
        return os.getenv('GSM_MODEM_PORT')

    @classmethod
    def get_gps_device_port(cls):
        if os.getenv('GPS_DEVICE_PORT') is None:
            detector = dd()
            if detector.gps_devices != []:
                target_device = dd().gps_devices[0]
                print "Detected GPS device at %s" % target_device
                return target_device
        return os.getenv('GPS_DEVICE_PORT')

    def build_logrotate_config(self):
        lr_options = str("{\nrotate 14" +
                         "\ndaily" +
                         "\ncompress" +
                         "\ndelaycompress" +
                         "\nmissingok" +
                         "\nnotifempty\n}")
        lr_config = "%s/*.log %s" % (self.log_prefix, lr_options)
        return lr_config

    def build_logstash_config(self):
        ls_config = {"network": {"servers": ["servername:serverport"],
                                 "ssl ca": self.ls_ca_path,
                                 "ssl certificate": self.ls_cert_path,
                                 "ssl key": self.ls_key_path},
                     "files": [{"paths": ["/var/log/cells.log"],
                                "fields": {"type": "syslog"}},
                               {"paths": ["/var/log/scanner.log"],
                                "fields": {"type": "scan"}},
                               {"paths": ["/var/log/kalibrate.log"],
                                "fields": {"type": "kalibrate"}},
                               {"paths": ["/var/log/channel.log"],
                                "fields": {"type": "channel"}},
                               {"paths": ["/var/log/gsm_modem_channel.log"],
                                "fields": {"type": "gsm_modem_channel"}},
                               {"paths": ["/var/log/kal_channel.log"],
                                "fields": {"type": "kal_channel"}},
                               {"paths": ["/var/log/arfcn_power.log"],
                                "fields": {"type": "arfcn_power"}},
                               {"paths": ["/var/log/radio_prio_arfcn.log"],
                                "fields": {"type": "radio_prio_arfcn"}},
                               {"paths": ["/var/log/arfcn_rxl.log"],
                                "fields": {"type": "arfcn_signal_strength"}},
                               {"paths": ["/var/log/arfcn_rxq.log"],
                                "fields": {"type": "arfcn_signal_quality"}},
                               {"paths": ["/var/log/arfcn_mcc.log"],
                                "fields": {"type": "arfcn_mcc"}},
                               {"paths": ["/var/log/arfcn_mnc.log"],
                                "fields": {"type": "arfcn_mnc"}},
                               {"paths": ["/var/log/arfcn_bsic.log"],
                                "fields": {"type": "arfcn_bsic"}},
                               {"paths": ["/var/log/arfcn_cellid.log"],
                                "fields": {"type": "arfcn_cellid"}},
                               {"paths": ["/var/log/arfcn_rla.log"],
                                "fields": {"type":
                                           "arfcn_rcv_level_access_minimum"}},
                               {"paths": ["/var/log/arfcn_txp.log"],
                                "fields": {"type": "arfcn_tx_power_maximum"}},
                               {"paths": ["/var/log/arfcn_lac.log"],
                                "fields": {"type":
                                           "arfcn_location_area_code"}},
                               {"paths": ["/var/log/arfcn_ta.log"],
                                "fields": {"type": "arfcn_timing_advance"}},
                               {"paths": ["/var/log/geoip.log"],
                                "fields": {"type": "geoip"}},
                               {"paths": ["/var/log/gps.log"],
                                "fields": {"type": "gpsd"}},
                               {"paths": ["/var/log/sitch_alert.log"],
                                "fields": {"type": "sitch_alert"}}]}
        log_host = self.log_host
        log_prefix = self.log_prefix
        ls_config["network"]["servers"][0] = log_host
        # ls_config["network"]["ssl ca"] = cert_file_loc
        for f in ls_config["files"]:
            f["paths"][0] = f["paths"][0].replace('/var/log', log_prefix)
        return json.dumps(ls_config)

    @classmethod
    def get_device_id(cls):
        device_id = "WHOKNOWS"
        resin = os.getenv('RESIN_DEVICE_UUID', '')
        override = os.getenv('LOCATION_NAME', '')
        for x in [resin, override]:
            if x != '':
                device_id = x
                print "Detected device_id: %s" % x
        return device_id

    def get_secret_from_vault(self):
        client = hvac.Client(url=self.vault_url, token=self.vault_token)
        print "Get secrets from %s, with path %s" % (self.vault_url,
                                                     self.vault_path)
        try:
            response = client.read(self.vault_path)
            secrets = response["data"]
        except Exception as e:
            print "Error in getting secret from vault!"
            print e
            secrets = "NONE"
        return secrets

    @classmethod
    def get_from_env(cls, k):
        retval = os.getenv(k)
        if retval is None:
            print "Required config variable not set: %s" % k
            print "Unable to continue.  Exiting."
            sys.exit(2)
        return retval

    @classmethod
    def get_list_from_env(cls, k):
        retval = os.getenv(k).split(',')
        if retval is None:
            print "Required config variable not set: %s" % k
            print "Unable to continue.  Exiting."
            sys.exit(2)
        return retval
