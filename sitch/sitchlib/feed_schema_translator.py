"""This is the object that translates from source feed to sensor schema."""
from string import Template
import geopy


class FeedSchemaTranslator(object):
    def __init__(self, schema):
        self.field_maps = schema
        self.translators = self.translators_from_schema(schema)

    def translate_row(self, row):
        """Translate source DB row to sensor DB schema.

        Args:
            row (dict): Row from source database.

        Returns:
            dict: Source row translated into sensor DB format.
        """
        result = {}
        for field in self.field_maps:
            sensor_field, feed_field = list(field.items())[0]
            if sensor_field in self.translators:
                result[sensor_field] = self.translators[sensor_field](row)[sensor_field]  # NOQA
            else:
                result[sensor_field] = row[feed_field]
        return result

    @classmethod
    def translators_from_schema(cls, fields):
        """Return dict of translators."""
        translators = {}
        for field in fields:
            sensor_field, feed_field = list(field.items())[0]
            if feed_field == "latlon_fcc":
                translators[sensor_field] = cls.latlon_trans_fcc
        return translators

    @classmethod
    def latlon_trans_fcc(cls, row):
        """returns dict with lat, lon"""
        lat_t = '$LOC_LAT_DEG ${LOC_LAT_MIN}m ${LOC_LAT_SEC}s $LOC_LAT_DIR'
        lon_t = '$LOC_LONG_DEG ${LOC_LONG_MIN}m ${LOC_LONG_SEC}s $LOC_LONG_DIR'
        lat = Template(lat_t).substitute(row)
        lon = Template(lon_t).substitute(row)
        point = geopy.point.Point(" ".join([lat, lon]))
        latlon = {"lat": str(point.latitude), "lon": str(point.longitude)}
        return latlon
