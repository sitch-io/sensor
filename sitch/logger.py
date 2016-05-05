import json
import os
import utility.Utility as utility


class LogHandler:
    """ Instantiate this class with the log file prefix"""
    def __init__(self, log_prefix):
        self.log_prefix = log_prefix

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
                        "gps": "gps.log"}
        if ltype in type_to_file:
            log_file = type_to_file[ltype]
        else:
            print "Unable to determine log file for type %s" % ltype
            log_file = None
        return log_file

    def write_log_message(self, log_file_type, message):
        """You should only ever send a string to this method"""
        log_file = self.get_log_file_name(log_file_type)
        utility.create_path_if_nonexistent(self.log_prefix)
        utility.create_file_if_nonexistent(log_file)
        with open(log_file, 'a') as lf:
            lf.write(str(message))
        return
