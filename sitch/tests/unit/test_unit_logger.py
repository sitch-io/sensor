from mock import MagicMock
import imp
import os
modulename = 'sitchlib'
modulepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")
file, pathname, description = imp.find_module(modulename, [modulepath])
fixturepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "../fixture/ceng.txt")
sitchlib = imp.load_module(modulename, file, pathname, description)


class TestUnitLogHandler:
    def create_config(self):
        config = sitchlib.ConfigHelper
        config.__init__ = (MagicMock(return_value=None))
        config.log_prefix = "/tmp/"
        config.log_method = "local_file"
        config.log_host = "host-here:3345"
        config.ls_ca_path = "/etc/1"
        config.ls_cert_path = "/etc/2"
        config.ls_key_path = "/etc/3"
        return config

    def create_log_handler_object(self):
        return sitchlib.LogHandler(self.create_config())

    def test_unit_create_log_handler(self):
        assert self.create_log_handler_object()

    def test_unit_log_handler_get_log_file_name_success(self):
        assert sitchlib.LogHandler.get_log_file_name("sitch_init")

    def test_unit_log_handler_get_log_file_name_fail(self):
        assert sitchlib.LogHandler.get_log_file_name("sitch_nonexist") is None

    def test_unit_log_handler_record_log_message(self):
        bolus = ('sitch_init', "init your mom")
        lh = self.create_log_handler_object()
        assert lh.record_log_message(bolus) is None
