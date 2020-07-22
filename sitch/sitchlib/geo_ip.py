"""GeoIP Device, so to speak."""

import copy
import time

import geoip2.database

from .utility import Utility


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
        try:
            self.reader = geoip2.database.Reader(GEO_DB_LOCATION)
            self.set_ip()
            self.set_geo()
        except FileNotFoundError:
            print("Missing MaxMind DB! No GeoIP correlation...")
            self.reader = None
            self.set_ip()
            # Welcome to Null Island...
            self.geo = {"scan_program": "geo_ip",
                        "type": "Feature",
                        "location": {
                            "type": "Point",
                            "coordinates": [
                                float(0),
                                float(0)]}}

    def __iter__(self):
        """Periodically yield GeoIP results.

        Yields:
            dict: GeoJSON representing GeoIP of sensor.
        """
        while not self.reader:
            print("No GeoIP DB.\nRebuild with MaxMind creds to enable GeoIP")
            result = copy.deepcopy(self.geo)
            yield result
            time.sleep(self.delay)
        while True:
            self.set_ip()
            self.set_geo()
            result = copy.deepcopy(self.geo)
            result["event_timestamp"] = Utility.get_now_string()
            yield result
            time.sleep(self.delay)

    def set_ip(self):
        """Set public IP address."""
        print("GeoIp: Setting public IP address")
        ip = Utility.get_public_ip()
        self.ip = ip

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
        except TypeError as err:
            print(err)
            print(dir(lat_lon))
            print("GeoIP: Unable to set geo by IP: %s" % self.ip)
            return None
