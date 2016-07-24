from mock import MagicMock
import imp
import os
modulename = 'sitchlib'
modulepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")
file, pathname, description = imp.find_module(modulename, [modulepath])
fixturepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "../fixture/ceng.txt")
sitchlib = imp.load_module(modulename, file, pathname, description)


class TestConfigHelper:
    def create_config(self):
        config = sitchlib.ConfigHelper
        config.__init__ = (MagicMock(return_value=None))
        config.device_id = "12345"
        config.feed_dir = "/tmp/"
        config.mcc_list = []
        config.feed_url_base = "https://s3.amazonaws.com/Sitchey//GSM"
        return config
