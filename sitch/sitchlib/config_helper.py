import hvac
import json
import os
import pprint
import sys
import yaml
from device_detector import DeviceDetector as dd
from utility import Utility as utility


class ConfigHelper:
    def __init__(self, feed_dir="/data/"):
        self.detector = dd()
        self.print_devices_as_detected()
        self.device_id = ConfigHelper.get_device_id()
        self.platform_name = utility.get_platform_name()
        self.log_prefix = "/var/log/sitch/"
        self.log_host = ConfigHelper.get_from_env("LOG_HOST")
        self.log_method = "local_file"
        self.kal_band = ConfigHelper.get_from_env("KAL_BAND")
        self.kal_gain = ConfigHelper.get_from_env("KAL_GAIN")
        self.kal_threshold = ConfigHelper.get_from_env("KAL_THRESHOLD")
        self.gsm_modem_band = ConfigHelper.get_from_env("GSM_MODEM_BAND")
        self.gsm_modem_port = self.get_gsm_modem_port()
        self.gps_device_port = self.get_gps_device_port()
        self.ls_ca_path = "/run/dbus/crypto/ca.crt"
        self.ls_cert_path = "/run/dbus/crypto/logstash.crt"
        self.ls_key_path = "/run/dbus/crypto/logstash.key"
        self.ls_crypto_base_path = "/run/dbus/crypto/"
        self.vault_token = ConfigHelper.get_from_env("VAULT_TOKEN")
        self.vault_url = ConfigHelper.get_from_env("VAULT_URL")
        self.vault_path = ConfigHelper.get_from_env("VAULT_PATH")
        self.mode = os.getenv("MODE", "GOGOGO")
        self.public_ip = str(utility.get_public_ip())
        self.feed_dir = feed_dir
        self.feed_url_base = ConfigHelper.get_from_env("FEED_URL_BASE")
        self.mcc_list = ConfigHelper.get_list_from_env("MCC_LIST")
        self.state_list = ConfigHelper.get_list_from_env("STATE_LIST")
        self.vault_secrets = self.get_secret_from_vault()
        self.gps_drift_threshold = 1000
        self.filebeat_template = self.get_filebeat_template()
        self.filebeat_config_file_path = "/etc/filebeat.yml"
        self.cgi_whitelist = ConfigHelper.get_list_from_env("CGI_WHITELIST",
                                                            optional=True)
        return

    def print_devices_as_detected(self):
        pp = pprint.PrettyPrinter()
        print("\nConfigurator: Detected GSM modems:")
        pp.pprint(self.detector.gsm_radios)
        print("Configurator: Detected GPS devices:")
        pp.pprint(self.detector.gps_devices)
        return

    def get_gsm_modem_port(self):
        if os.getenv('GSM_MODEM_PORT') is None:
            if self.detector.gsm_radios != []:
                target_device = self.detector.gsm_radios[0]["device"]
                return target_device
        return os.getenv('GSM_MODEM_PORT')

    def get_gps_device_port(self):
        if os.getenv('GPS_DEVICE_PORT') is None:
            if self.detector.gps_devices != []:
                target_device = self.detector.gps_devices[0]
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

    @classmethod
    def get_filebeat_template(cls, filename="/etc/templates/filebeat.json"):
        with open(filename, 'r') as template_file:
            return json.load(template_file)

    def write_filebeat_config(self):
        fb = self.filebeat_template
        fb["output.logstash"]["hosts"] = [self.log_host]
        fb["output.logstash"]["ssl.key"] = self.ls_key_path
        fb["output.logstash"]["ssl.certificate"] = self.ls_cert_path
        fb["output.logstash"]["ssl.certificate_authorities"] = [self.ls_ca_path]
        with open(self.filebeat_config_file_path, 'w') as out_file:
            yaml.safe_dump(fb, out_file)
        return


    @classmethod
    def get_device_id(cls):
        device_id = "WHOKNOWS"
        resin = os.getenv('RESIN_DEVICE_UUID', '')
        override = os.getenv('LOCATION_NAME', '')
        for x in [resin, override]:
            if x != '':
                device_id = x
                print("Configurator: Detected device_id: %s" % x)
        return device_id

    def get_secret_from_vault(self):
        client = hvac.Client(url=self.vault_url, token=self.vault_token)
        print("Configurator: Get secrets from %s, with path %s" % (self.vault_url,
                                                                   self.vault_path))
        try:
            response = client.read(self.vault_path)
            secrets = response["data"]
        except Exception as e:
            print("Configurator: Error in getting secret from vault!")
            print(e)
            secrets = "NONE"
        return secrets

    @classmethod
    def get_from_env(cls, k):
        retval = os.getenv(k)
        if retval is None:
            print("Configurator: Required config variable not set: %s" % k)
            print("Configurator: Unable to continue.  Exiting.")
            sys.exit(2)
        return retval

    @classmethod
    def get_list_from_env(cls, k, optional=False):
        """Gets a list from environment variables.

        If optional=True, the absence of this var will cause a hard exit.
        """
        retval = os.getenv(k).split(',')
        if retval is None and optional is False:
            print("Configurator: Required config variable not set: %s" % k)
            print("Configurator: Unable to continue.  Exiting.")
            sys.exit(2)
        else: retval = []
        return retval
