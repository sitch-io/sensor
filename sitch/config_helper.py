import hvac
import os
import sys


class ConfigHelper:
    def __init__(self):
        self.device_id = ConfigHelper.get_device_id()
        self.log_host = ConfigHelper.get_from_env("LOG_HOST")
        self.kal_band = ConfigHelper.get_from_env("KAL_BAND")
        self.kal_gain = ConfigHelper.get_from_env("KAL_GAIN")
        self.sim808_band = ConfigHelper.get_from_env("SIM808_BAND")
        self.sim808_port = ConfigHelper.get_from_env("SIM808_PORT")
        self.vault_ls_cert_path = ConfigHelper.get_from_env("VAULT_LS_CERT_PATH")
        self.vault_token = ConfigHelper.get_from_env("VAULT_TOKEN")
        self.vault_url = ConfigHelper.get_from_env("VAULT_URL")
        self.logstash_cert_path = "/run/dbus/crypto/logstash.crt"
        self.ls_cert = None
        ConfigHelper.set_secret_from_vault(self)
        return

    def build_logrotate_config(self):
        lr_options = "{\nrotate 14\ndaily\ncompress\ndelaycompress\nmissingok\nnotifempty\n}"
        lr_config = "%s/*.log %s" % (self.log_prefix, lr_options)
        return lr_config

    def build_logstash_config(self):
        ls_config = {"network": {"servers": ["servername:serverport"],
                                 "ssl ca": "/run/dbus/crypto/logstash.crt"},
                     "files": [{"paths": ["/var/log/cells.log"],
                                "fields": {"type": "syslog"}},
                               {"paths": ["/var/log/scanner.log"],
                                "fields": {"type": "scan"}},
                               {"paths": ["/var/log/kalibrate.log"],
                                "fields": {"type": "kalibrate"}},
                               {"paths": ["/var/log/channel.log"],
                                "fields": {"type": "channel"}},
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
                                "fields": {"type": "arfcn_rcv_level_access_minimum"}},
                               {"paths": ["/var/log/arfcn_txp.log"],
                                "fields": {"type": "arfcn_tx_power_maximum"}},
                               {"paths": ["/var/log/arfcn_lac.log"],
                                "fields": {"type": "arfcn_location_area_code"}},
                               {"paths": ["/var/log/arfcn_ta.log"],
                                "fields": {"type": "arfcn_timing_advance"}},
                               {"paths": ["/var/log/gps.log"],
                                "fields": {"type": "gpsd"}}]}
        log_host = self.log_host
        log_prefix = self.log_prefix
        cert_file_loc = self.logstash_cert_path
        ls_config["network"]["servers"][0] = log_host
        ls_config["network"]["ssl ca"][0] = cert_file_loc
        for f in ls_config["files"]:
            f["paths"][0] = f["paths"][0].replace('/var/log', log_prefix)
        return ls_config

    @classmethod
    def get_device_id(cls):
        device_id = "WHOKNOWS"
        resin = os.getenv('RESIN_DEVICE_UUID')
        override = os.getenv('LOCATION_NAME')
        for x in [resin, override]:
            if x is not None:
                device_id = x
        return device_id

    def set_secret_from_vault(self):
        client = hvac.Client(url=self.vault_url, token=self.vault_token)
        print "Get secrets from %s, with path %s" % (self.vault_url,
                                                     self.vault_ls_cert_path)
        self.ls_cert = client.read(self.vault_ls_cert_path)
        return

    @classmethod
    def get_from_env(cls, k):
        retval = os.getenv(k)
        if retval is None:
            print "Required config variable not set: %s" % k
            print "Unable to continue.  Exiting."
            sys.exit(2)
        return
