from geoip import geolite2
from haversine import haversine


class LocationTool(object):
    def __init__(self):
        return None

    @classmethod
    def get_geo_for_ip(cls, ip_address):
        match = geolite2.lookup(ip_address)
        try:
            lat_lon = match.location
            coords = {"lat": lat_lon[0],
                      "lon": lat_lon[1]}
            return coords
        except:
            print "LocationTool: LocationTool cannot get geo for IP: %s" % ip_address
            return None

    @classmethod
    def get_distance_between_points(cls, point_1, point_2):
        """ Forces type to float if it isn't already """
        if None in [point_1, point_2]:
            print "LocationTool: Invalid geo value... returning 0 for distance."
            distance = 0
        else:
            point_1 = (float(point_1[0]), float(point_1[1]))
            point_2 = (float(point_2[0]), float(point_2[1]))
            distance = haversine(point_1, point_2)
        return distance
