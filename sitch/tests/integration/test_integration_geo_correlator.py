import imp
import os


modulename = 'sitchlib'
modulepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "../../")
feedpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "../fixture/feed/")
file, pathname, description = imp.find_module(modulename, [modulepath])
sitchlib = imp.load_module(modulename, file, pathname, description)


geo_state = {"scan_program": "gpsd",
             "type": "Feature",
             "sat_time": "2017-03-25T00:30:48.000Z",
             "time_drift": 2,
             "sys_time": "2017-03-25T00:32:48.416592",
             "site_name": "SITE_NAME",
             "sensor_name": "SENSOR_NAME",
             "sensor_id": "SENSOR_ID",
             "geometry": {
                 "type": "Point",
                 "coordinates": [-122.431297, 37.773972]}}
geo_other_state = {"scan_program": "gpsd",
                   "type": "Feature",
                   "sat_time": "2017-03-25T00:30:48.000Z",
                   "time_drift": 2,
                   "sys_time": "2017-03-25T00:32:48.416592",
                   "site_name": "SITE_NAME",
                   "sensor_name": "SENSOR_NAME",
                   "sensor_id": "SENSOR_ID",
                   "geometry": {
                       "type": "Point",
                       "coordinates": [-100.431297, 32.773972]}}
geo_time_alarm = {"scan_program": "gpsd",
                  "type": "Feature",
                  "sat_time": "2017-03-25T00:30:48.000Z",
                  "time_drift": 20,
                  "sys_time": "2017-03-25T00:50:48.416592",
                  "site_name": "SITE_NAME",
                  "sensor_name": "SENSOR_NAME",
                  "sensor_id": "SENSOR_ID",
                  "geometry": {
                      "type": "Point",
                      "coordinates": [-100.431297, 32.773972]}}


class TestIntegrationCorrelateGeo:
    def instantiate_geo(self):
        geo_correlator = sitchlib.GeoCorrelator("SENSOR_ID")
        return geo_correlator

    def test_instantiate_measure_drift(self):
        correlator = self.instantiate_geo()
        result_1 = correlator.correlate(("gps", geo_state))
        result_2 = correlator.correlate(("gps", geo_other_state))
        assert len(result_1) == 0
        assert len(result_2) == 1

    def test_measure_time_drift_alarm(self):
        correlator = self.instantiate_geo()
        correlator.correlate(("gps", geo_other_state))
        result = correlator.correlate(("gps", geo_time_alarm))
        assert len(result) == 1
        assert result[0][1]["id"] == 310
