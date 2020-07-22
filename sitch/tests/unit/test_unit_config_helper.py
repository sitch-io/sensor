from mock import MagicMock
import imp
import os
modulename = 'sitchlib'
modulepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")
file, pathname, description = imp.find_module(modulename, [modulepath])
fixturepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "../fixture/ceng.txt")
sitchlib = imp.load_module(modulename, file, pathname, description)

test_conf = {"filebeat.prospectors": [
              {"input_type": "log",
               "document_type": "cells",
               "keys_under_root": True,
               "paths": [
                 "/var/log/sitch/cells.log"
                ]},
              {"input_type": "log",
               "document_type": "scan",
               "keys_under_root": True,
               "paths": [
                 "/var/log/sitch/scanner.log"
                ]}]}


class TestConfigHelper:
    def create_config(self):
        config = sitchlib.ConfigHelper
        config.__init__ = (MagicMock(return_value=None))
        config.device_id = "12345"
        config.feed_dir = "/tmp/"
        config.mcc_list = []
        config.feed_url_base = "https://s3.amazonaws.com/Sitchey//GSM"
        return config

    def test_unit_set_filebeat_file_paths(self):
        print(test_conf)
        res = sitchlib.ConfigHelper.set_filebeat_logfile_paths("/pre/fix/",
                                                               test_conf)
        print(res)
        assert len(res["filebeat.prospectors"][0]["paths"]) == 1
        assert res["filebeat.prospectors"][0]["paths"][0] == "/pre/fix/cells.log"
        assert len(res["filebeat.prospectors"][1]["paths"]) == 1
        assert res["filebeat.prospectors"][1]["paths"][0] == "/pre/fix/scanner.log"

    def test_unit_create_config_object(self):
        assert self.create_config()

    def test_unit_config_helper_get_from_env(self):
        assert sitchlib.ConfigHelper.get_from_env("PATH")

    def test_unit_config_helper_get_list_from_env(self):
        assert sitchlib.ConfigHelper.get_list_from_env("PATH")

    def test_unit_config_helper_get_list_from_env_2(self):
        result = sitchlib.ConfigHelper.get_list_from_env("NONEXIST",
                                                         optional=True)
        assert result == []
