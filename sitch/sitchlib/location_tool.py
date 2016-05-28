from geoip import geolite2
import haversine


class LocationTool(object):
    def __init__(self):
        return None

    @classmethod
    def get_geo_for_ip(cls, ip_address):
        match = geolite2.lookup(ip_address)
        try:
            lat_lon = match.location
            return lat_lon
        except:
            return None

    @classmethod
    def get_distance_between_points(cls, point_1, point_2):
        if None in [point_1, point_2]:
            print "Invalid geo value... returning 0 for distance."
            distance = 0
        else:
            distance = haversine(point_1, point_2)
        return distance
