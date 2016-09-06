from gps3 import gps3
import time


class GpsListener(object):
    def __init__(self):
        self.gps_socket = gps3.GPSDSocket()
        self.data_stream = gps3.DataStream()
        self.gps_socket.connect()
        self.gps_socket.watch()

    def __iter__(self):
        for new_data in self.gps_socket:
            if new_data:
                self.data_stream.unpack(new_data)
                if "lon" in self.data_stream.TPV:
                    if self.data_stream.TPV['lon'] != 'n/a':
                        geojson = {"type": "Feature",
                                   "geometry": {
                                       "type": "Point",
                                       "coordinates": [
                                           self.data_stream.TPV['lon'],
                                           self.data_stream.TPV['lat']]}}
                        yield geojson
                        time.sleep(30)
