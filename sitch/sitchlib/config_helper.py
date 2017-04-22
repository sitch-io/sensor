"""Config Helper."""

import hvac
import json
import os
import pprint
import sys
import yaml
from device_detector import DeviceDetector as dd
from utility import Utility as utility


class ConfigHelper:
    """Manage configuration information for entire SITCH Sensor."""

    def __init__(self, sitch_var_base_dir="/data/sitch/"):
        """Initialize ConfigHelper.

        Args:
            sitch_var_base_dir (str): Base directory for feed and log data.
        """
        self.detector = dd()
        self.print_devices_as_detected()
        self.device_id = ConfigHelper.get_device_id()
        self.feed_radio_targets = self.get_list_from_env("FEED_RADIO_TARGETS")
        self.site_name = os.getenv('LOCATION_NAME', 'SITCH_SITE')
        self.platform_name = utility.get_platform_name()
        self.log_prefix = os.path.join(sitch_var_base_dir, "log/")
        self.log_host = ConfigHelper.get_from_env("LOG_HOST")
        self.log_method = "local_file"
        self.kal_band = ConfigHelper.get_from_env("KAL_BAND")
        self.kal_gain = ConfigHelper.get_from_env("KAL_GAIN")
        self.kal_threshold = ConfigHelper.get_from_env("KAL_THRESHOLD")
        self.gsm_modem_band = ConfigHelper.get_from_env("GSM_MODEM_BAND")
        self.health_check_interval = int(os.getenv("HEALTH_CHECK_INTERVAL",
                                                   3600))
        self.gsm_modem_port = self.get_gsm_modem_port()
        self.gps_device_port = self.get_gps_device_port()
        self.ls_ca_path = "/host/run/dbus/crypto/ca.crt"
        self.ls_cert_path = "/host/run/dbus/crypto/logstash.crt"
        self.ls_key_path = "/host/run/dbus/crypto/logstash.key"
        self.ls_crypto_base_path = "/host/run/dbus/crypto/"
        self.vault_token = ConfigHelper.get_from_env("VAULT_TOKEN")
        self.vault_url = ConfigHelper.get_from_env("VAULT_URL")
        self.vault_path = ConfigHelper.get_from_env("VAULT_PATH")
        self.mode = os.getenv("MODE", "GOGOGO")
        self.public_ip = str(utility.get_public_ip())
        self.feed_dir = os.path.join(sitch_var_base_dir, "feed/")
        self.feed_url_base = ConfigHelper.get_from_env("FEED_URL_BASE")
        self.mcc_list = ConfigHelper.get_list_from_env("MCC_LIST")
        self.state_list = ConfigHelper.get_list_from_env("STATE_LIST")
        self.vault_secrets = self.get_secret_from_vault()
        self.gps_drift_threshold = 1000
        self.filebeat_template = self.get_filebeat_template()
        self.filebeat_config_file_path = "/etc/filebeat.yml"
        self.arfcn_whitelist = ConfigHelper.get_list_from_env("ARFCN_WHITELIST",  # NOQA
                                                              optional=True)
        self.cgi_whitelist = ConfigHelper.get_list_from_env("CGI_WHITELIST",
                                                            optional=True)
        self.no_feed_update = os.getenv("NO_FEED_UPDATE")
        return

    def print_devices_as_detected(self):
        """Print detected GPS and GSM devices."""
        pp = pprint.PrettyPrinter()
        print("\nConfigurator: Detected GSM modems:")
        pp.pprint(self.detector.gsm_radios)
        print("Configurator: Detected GPS devices:")
        pp.pprint(self.detector.gps_devices)
        return

    def get_gsm_modem_port(self):
        """Get GSM modem port from detector, override with env var."""
        if os.getenv('GSM_MODEM_PORT') is None:
            if self.detector.gsm_radios != []:
                target_device = self.detector.gsm_radios[0]["device"]
                return target_device
        return os.getenv('GSM_MODEM_PORT')

    def get_gps_device_port(self):
        """Get GPS device from detector, override with env var."""
        if os.getenv('GPS_DEVICE_PORT') is None:
            if self.detector.gps_devices != []:
                target_device = self.detector.gps_devices[0]
                return target_device
        return os.getenv('GPS_DEVICE_PORT')

    def build_logrotate_config(self):
        """Generate logrotate config file contents."""
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
        """Get the filebeat config from template file."""
        with open(filename, 'r') as template_file:
            return json.load(template_file)

    def write_filebeat_config(self):
        """Write out filebeat config to file."""
        fb = self.filebeat_template
        fb["output.logstash"]["hosts"] = [self.log_host]
        fb["output.logstash"]["ssl.key"] = self.ls_key_path
        fb["output.logstash"]["ssl.certificate"] = self.ls_cert_path
        fb["output.logstash"]["ssl.certificate_authorities"] = [self.ls_ca_path]  # NOQA
        fb["filebeat.registry_file"] = os.path.join(self.log_prefix, "fb_registry")
        fb = self.set_filebeat_logfile_paths(self.log_prefix, fb)
        with open(self.filebeat_config_file_path, 'w') as out_file:
            yaml.safe_dump(fb, out_file)
        return

    @classmethod
    def set_filebeat_logfile_paths(cls, log_prefix, filebeat_config):
        """Sets all log file paths to align with configured log prefix."""
        placeholder = "/var/log/sitch/"
        for prospector in filebeat_config["filebeat.prospectors"]:
            working_paths = []
            for path in prospector["paths"]:
                w_path = path.replace(placeholder, "")
                working_paths.append(os.path.join(log_prefix, w_path))
            prospector["paths"] = working_paths
        return filebeat_config

    @classmethod
    def get_device_id(cls):
        """Get device ID from env var."""
        device_id = "WHOKNOWS"
        resin = os.getenv('RESIN_DEVICE_NAME_AT_INIT', '')
        override = os.getenv('LOCATION_NAME', '')
        for x in [resin, override]:
            if x != '':
                device_id = x
                print("Configurator: Detected device_id: %s" % x)
        return device_id

    def get_secret_from_vault(self):
        """Retrieve secrets from Vault."""
        client = hvac.Client(url=self.vault_url, token=self.vault_token)
        print("Configurator: Get secrets from %s, with path %s" % (self.vault_url,  # NOQA
                                                                   self.vault_path))  # NOQA
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
        """Get configuration items from env vars.  Hard exit if not set."""
        retval = os.getenv(k)
        if retval is None:
            print("Configurator: Required config variable not set: %s" % k)
            print("Configurator: Unable to continue.  Exiting.")
            sys.exit(2)
        return retval

    @classmethod
    def get_list_from_env(cls, k, optional=False):
        """Get a list from environment variables.

        If optional=True, the absence of this var will cause a hard exit.
        """
        try:
            retval = os.getenv(k).split(',')
        except AttributeError:
            retval = None
        if retval is None and optional is False:
            print("Configurator: Required config variable not set: %s" % k)
            print("Configurator: Unable to continue.  Exiting.")
            sys.exit(2)
        elif retval is None and optional is True:
            retval = []
        return retval
