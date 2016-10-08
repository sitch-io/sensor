import json
import logging
from logstash_formatter import LogstashFormatter
from logstash_handler import LogstashHandler
import os
from utility import Utility as utility


class LogHandler:
    """ Instantiate this class with the log file prefix"""
    def __init__(self, config):
        self.log_prefix = config.log_prefix
        self.log_method = config.log_method
        self.logstash_host = config.log_host.split(':')[0]
        self.logstash_port = config.log_host.split(':')[1]
        self.logstash_ca_path = config.ls_ca_path
        self.logstash_cert_path = config.ls_cert_path
        self.logstash_key_path = config.ls_key_path
        self.ls_logger = logging.getLogger()
        self.ls_handler = LogstashHandler(self.logstash_host,
                                          self.logstash_port,
                                          ssl=True,
                                          ca_certs=self.logstash_ca_path,
                                          keyfile=self.logstash_key_path,
                                          certfile=self.logstash_cert_path)
        self.ls_formatter = LogstashFormatter()
        self.ls_handler.setFormatter(self.ls_formatter)
        self.ls_logger.addHandler(self.ls_handler)
        utility.create_path_if_nonexistent(self.log_prefix)

    @classmethod
    def get_log_file_name(cls, ltype):
        type_to_file = {"cell": "cells.log",  # sim808 scan doc
                        "scan": "scanner.log",  # kal scan doc
                        "arfcn_power": "arfcn_power.log",  # kal
                        "arfcn_prio": "radio_prio_arfcn.log",  # sim808
                        "arfcn_rxl": "arfcn_rxl.log",  # sim808
                        "arfcn_rxq": "arfcn_rxq.log",  # sim808
                        "arfcn_mcc": "arfcn_mcc.log",  # sim808
                        "arfcn_mnc": "arfcn_mnc.log",  # sim808
                        "arfcn_bsic": "arfcn_bsic.log",  # sim808
                        "arfcn_cellid": "arfcn_cellid.log",  # sim808
                        "arfcn_rla": "arfcn_rla.log",  # sim808
                        "arfcn_txp": "arfcn_txp.log",  # sim808
                        "arfcn_lac": "arfcn_lac.log",  # sim808
                        "arfcn_ta": "arfcn_ta.log",  # sim808
                        "kal_channel": "kal_channel.log",  # cells from Kal
                        "sim808_channel": "sim808_channel.log",  # sim808 cells
                        "gps": "gps.log",
                        "sitch_alert": "sitch_alert.log"}
        if ltype in type_to_file:
            log_file = type_to_file[ltype]
        else:
            print "Unable to determine log file for type %s" % ltype
            log_file = None
        return log_file

    def record_log_message(self, bolus):
        msg_type = bolus[0]
        msg_body = bolus[1]
        if type(msg_body) == dict:
            msg_string = json.dumps(msg_body)
            msg_json = msg_body
        elif type(msg_body) is str:
            msg_string = msg_body
            msg_json = json.loads(msg_body)
        if self.log_method == 'local_file':
            self.write_log_message(bolus[0], msg_string)
        elif self.log_method == 'direct':
            self.transmit_log_message(msg_json)

    def write_log_message(self, log_file_type, message):
        """You should only ever send a string to this method"""
        log_file = os.path.join(self.log_prefix,
                                self.get_log_file_name(log_file_type))
        with open(log_file, 'a') as lf:
            lf.write(str(str(message) + '\n'))
        return

    def transmit_log_message(self, message):
        """You should only ever send a dict to this method"""
        self.ls_logger.info(message)
        return
