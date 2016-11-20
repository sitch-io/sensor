import imp
import os
modulename = 'sitchlib'
modulepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")
file, pathname, description = imp.find_module(modulename, [modulepath])
sitchlib = imp.load_module(modulename, file, pathname, description)


class TestDeviceDetector:
    def test_interrogator_matcher(self):
        matchers = ["foo", "bar", "hillbilly"]
        test_line = "I hear a hillbilly"
        assert sitchlib.DeviceDetector.interrogator_matcher(matchers, test_line)
