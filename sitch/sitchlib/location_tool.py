"""Location tools library."""

from geoip import geolite2
from haversine import haversine


class LocationTool(object):
    """Class with location-oriented functions."""

    @classmethod
    def get_geo_for_ip(cls, ip_address):
        """Get geo coordinates for IP address.

        Args:
            ip_address (str): IP address.

        """
        match = geolite2.lookup(ip_address)
        try:
            lat_lon = match.location
            coords = {"lat": lat_lon[0],
                      "lon": lat_lon[1]}
            return coords
        except:
            msg = "LocationTool: Can't get geo for %s" % ip_address
            print(msg)
            return None

    @classmethod
    def get_distance_between_points(cls, point_1, point_2):
        """Calculate distance between points.

        Args:
            point_1 (tuple): (lon, lat) for first point.
            point_2 (tuple): (lon, lat) for second point.

        Returns:
            int: Kilometers between `point_1` and `point_2`.
        """
        if None in [point_1, point_2]:
            print("LocationTool: Invalid geo value. Returning 0 for distance.")
            distance = 0
        else:
            point_1 = (float(point_1[0]), float(point_1[1]))
            point_2 = (float(point_2[0]), float(point_2[1]))
            distance = haversine(point_1, point_2)
        return distance
