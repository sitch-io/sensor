import gps
import time


class GpsListener(object):
    def __init__(self):
        self.session = gps.gps("localhost", "2947")
        self.session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

    def __iter__(self):
        while True:
            try:
                report = self.session.next()
                if report["class"] == 'TPV':
                    if hasattr(report, 'time'):
                        geojson = {"type": "Feature",
                                   "geometry": {
                                       "type": "Point",
                                       "coordinates": [
                                           report["lon"],
                                           report["lat"]]}}
                        yield geojson
                        time.sleep(30)
            except KeyError:
                pass
