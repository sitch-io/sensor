import copy
import time
from utility import Utility
from geoip import geolite2


class GeoIp(object):
    def __init__(self, delay=60):
        self.ip = ""
        self.geo = {}
        self.delay = delay
        self.set_ip()
        self.set_geo()
        return

    def __iter__(self):
        while True:
            self.set_ip
            self.set_geo
            yield copy.deepcopy(self.geo)
            time.sleep(self.delay)

    def set_ip(self):
        print("GeoIp: Setting public IP address")
        ip = Utility.get_public_ip()
        self.ip = ip
        return

    def set_geo(self):
        match = geolite2.lookup(self.ip)
        try:
            lat_lon = match.location
            self.geo = {"type": "Feature",
                        "geometry": {
                           "type": "Point",
                           "coordinates": [
                               lat_lon[1],
                               lat_lon[0]]}}
            return
        except:
            print("GeoIP: Unable to set geo by IP: %s" % self.ip)
            return None
