"""GeoIP Device, so to speak."""

import copy
import time
from utility import Utility
from geoip import geolite2


class GeoIp(object):
    """Generate GeoIP events."""

    def __init__(self, delay=60):
        """Initialize the GeoIP object.

        Args:
            delay (int, optional): The number of seconds to delay between
                yielded queries for GeoIP.  Defaults to 60.
        """
        self.ip = ""
        self.geo = {}
        self.delay = delay
        self.set_ip()
        self.set_geo()
        return

    def __iter__(self):
        """Periodically yield GeoIP results.

        Yields:
            dict: GeoJSON representing GeoIP of sensor.
        """
        while True:
            self.set_ip
            self.set_geo
            result = copy.deepcopy(self.geo)
            result["event_timestamp"] = Utility.get_now_string()
            yield result
            time.sleep(self.delay)

    def set_ip(self):
        """Set public IP address."""
        print("GeoIp: Setting public IP address")
        ip = Utility.get_public_ip()
        self.ip = ip
        return

    def set_geo(self):
        """Use public IP to determine GeoIP."""
        match = geolite2.lookup(self.ip)
        try:
            lat_lon = match.location
            self.geo = {"scan_program": "geo_ip",
                        "type": "Feature",
                        "location": {
                           "type": "Point",
                           "coordinates": [
                               lat_lon[1],
                               lat_lon[0]]}}
            return
        except:
            print("GeoIP: Unable to set geo by IP: %s" % self.ip)
            return None
