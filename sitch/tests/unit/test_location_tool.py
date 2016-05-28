import imp
import os
modulename = 'sitchlib'
modulepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")
file, pathname, description = imp.find_module(modulename, [modulepath])
sitchlib = imp.load_module(modulename, file, pathname, description)


class TestLocationTool:
    def test_get_geo_for_ip(self):
        loc_tool = sitchlib.LocationTool
        test_ip = '66.18.61.90'
        location = loc_tool.get_geo_for_ip(test_ip)
        assert location is not None

    def test_fail_geo_for_ip(self):
        loc_tool = sitchlib.LocationTool
        test_ip = '127.0.0.1'
        location = loc_tool.get_geo_for_ip(test_ip)
        assert location is None

    def test_get_distance_between_points(self):
        loc_tool = sitchlib.LocationTool
        madrid = (40.24, 3.41)
        chattanooga = (35.244, 85.1835)
        distance = loc_tool.get_distance_between_points(madrid, chattanooga)
        assert distance > 1000

    def test_get_distance_between_points(self):
        loc_tool = sitchlib.LocationTool
        elseweyr = None
        chattanooga = (35.244, 85.1835)
        distance = loc_tool.get_distance_between_points(elseweyr, chattanooga)
        assert distance == 0
