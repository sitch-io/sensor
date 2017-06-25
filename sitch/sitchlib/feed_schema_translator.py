"""This is the object that translates from source feed to sensor schema."""
from string import Template
import LatLon


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
            sensor_field, feed_field = field.items()[0]
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
            sensor_field, feed_field = field.items()[0]
            if feed_field == "latlon_fcc":
                translators[sensor_field] = cls.latlon_trans_fcc
        return translators

    @classmethod
    def latlon_trans_fcc(cls, row):
        """returns dict with lat, lon"""
        latlon = {}
        lat_pre = Template('$LOC_LAT_DEG $LOC_LAT_MIN $LOC_LAT_SEC $LOC_LAT_DIR').substitute(row)  # NOQA
        lon_pre = Template('$LOC_LONG_DEG $LOC_LONG_MIN $LOC_LONG_SEC $LOC_LONG_DIR').substitute(row)  # NOQA
        ll = LatLon.string2latlon(lat_pre, lon_pre, "d% %m% %S% %H")
        latlon["lat"] = ll.to_string('D%')[0]
        latlon["lon"] = ll.to_string('D%')[1]
        return latlon
