import imp
import os
import re
modulename = 'sitchlib'
modulepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")
file, pathname, description = imp.find_module(modulename, [modulepath])
sitchlib = imp.load_module(modulename, file, pathname, description)


class TestUtility:
    def test_get_now_string(self):
        util = sitchlib.Utility
        dtstring = util.get_now_string()
        assert type(dtstring) is str

    def test_strip_list(self):
        util = sitchlib.Utility
        starting_var = [('one', 'two')]
        result = util.strip_list(starting_var)
        assert type(result) is tuple

    def test_get_public_ip(self):
        util = sitchlib.Utility
        result = util.get_public_ip()
        ip_match = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        ip_matcher = re.compile(ip_match)
        assert ip_matcher.match(result)

    def test_calculate_distance(self):
        madrid = (40.24, 3.41)
        chattanooga = (35.244, 85.1835)
        result = sitchlib.Utility.calculate_distance(madrid[0], madrid[1],
                                                     chattanooga[0],
                                                     chattanooga[1])
        assert result != 0
