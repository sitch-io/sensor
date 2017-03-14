"""GPS device wrapper."""

from gps3 import gps3
from utility import Utility
import copy
import time


class GpsListener(object):
    """Wrap the GPS device with an iterator."""

    def __init__(self, delay=60):
        """Initialize the GPS listener.

        Args:
            delay (int, optional): Delay between polls of gpsd.
        """
        self.delay = delay
        self.gps_socket = gps3.GPSDSocket()
        self.data_stream = gps3.DataStream()
        self.gps_socket.connect()
        self.gps_socket.watch()

    def __iter__(self):
        """Periodically yield GPS coordinates of sensor.

        Yields:
            dict: GeoJSON representing GPS coordinates of sensor.
        """
        for new_data in self.gps_socket:
            if Utility.is_valid_json(new_data):
                self.data_stream.unpack(new_data)
                if "lon" in self.data_stream.TPV:
                    if self.data_stream.TPV['lon'] != 'n/a':
                        geojson = {"scan_program": "gpsd",
                                   "type": "Feature",
                                   "geometry": {
                                       "type": "Point",
                                       "coordinates": [
                                           self.data_stream.TPV["lon"],
                                           self.data_stream.TPV["lat"]]}}
                        yield copy.deepcopy(geojson)
                        time.sleep(self.delay)
