import imp
import os
import re
modulename = 'sitchlib'
modulepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")
file, pathname, description = imp.find_module(modulename, [modulepath])
sitchlib = imp.load_module(modulename, file, pathname, description)


class TestUtility:
    def test_epoch_to_iso8601(self):
        epoch = 1488857883
        desired = "2017-03-07T03:38:03"
        result = sitchlib.Utility.epoch_to_iso8601(epoch)
        assert desired == result

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

    def test_hex_to_dec(self):
        testval = 'ffff'
        desired_result = '65535'
        result = sitchlib.Utility.hex_to_dec(testval)
        assert result == desired_result

    def test_unit_utility_get_platform_info(self):
        result = sitchlib.Utility.get_platform_info()
        assert result

    def test_unit_utility_start_component(self):
        result = sitchlib.Utility.start_component("/bin/true")
        assert result

    def test_unit_utility_get_performance_metrics(self):
        assert sitchlib.Utility.get_performance_metrics()

    def test_unit_utility_8601_to_dt(self):
        test_start = "2017-03-24T04:44:58.000Z"
        dt = sitchlib.Utility.dt_from_iso(test_start)
        assert dt.isoformat() == test_start
