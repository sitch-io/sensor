"""GeoIP Device, so to speak."""

import copy
import time
from .utility import Utility
import geoip2.database

GEO_DB_LOCATION = "/var/mmdb//GeoLite2-City.mmdb"  # NOQA

class GeoIp:
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
        self.reader = geoip2.database.Reader(GEO_DB_LOCATION)
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
        match = self.reader.city(self.ip)
        try:
            lat_lon = match.location
            self.geo = {"scan_program": "geo_ip",
                        "type": "Feature",
                        "location": {
                           "type": "Point",
                           "coordinates": [
                               float(lat_lon.longitude),
                               float(lat_lon.latitude)]}}
            return
        except TypeError as e:
            print(e)
            print(dir(lat_lon))
            print("GeoIP: Unable to set geo by IP: %s" % self.ip)
            return None
