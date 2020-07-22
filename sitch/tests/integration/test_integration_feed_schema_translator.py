import imp
import os
import mock
import sys
import yaml


sys.modules['pyudev'] = mock.Mock()
modulename = 'sitchlib'
modulepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "../../")
file, pathname, description = imp.find_module(modulename, [modulepath])
sitchlib = imp.load_module(modulename, file, pathname, description)

schemas = "/etc/schemas/feed_db_translation.yaml"


class TestIntegrationFeedSchemaTranslator:
    def get_schemas_from_file(self):
        with open(schemas, 'r') as schemas_file:
            result = yaml.load(schemas_file)
        return result

    def test_feed_schema_translate_ocid(self):
        row = {"radio": "Ray-Dee-Oh",
               "mcc": "EmmCeeCee",
               "net": "Nayut",
               "area": "AirEUh",
               "cell": "SayOll",
               "unit": "YouNitt",
               "lon": "Lawn",
               "lat": "Layut",
               "range": "Rhaynge",
               "samples": "Sayumpulls",
               "changeable": "maybemaybenot",
               "created": "inhebeginning",
               "updated": "sometimelater",
               "averageSignal": "middle",
               "carrier": "pigeon"}
        schema = self.get_schemas_from_file()["ocid"]
        translator = sitchlib.FeedSchemaTranslator(schema)
        result = translator.translate_row(row)
        assert result["radio"] == "Ray-Dee-Oh"
        assert len(result) == 10
        assert "averageSignal" not in result

    def test_feed_schema_translate_fcc(self):
        row = {"ARFCN": "12345",
               "COMMON_NAME": "Elseweyr Communications",
               "LOC_LAT_DEG": "35",
               "LOC_LAT_MIN": "1",
               "LOC_LAT_SEC": "6.2796",
               "LOC_LAT_DIR": "N",
               "LOC_LONG_DEG": "85",
               "LOC_LONG_MIN": "1",
               "LOC_LONG_SEC": "34.0032",
               "LOC_LONG_DIR": "W",
               "LEAVE_ME": "BEHIND"}
        schema = self.get_schemas_from_file()["fcc"]
        translator = sitchlib.FeedSchemaTranslator(schema)
        result = translator.translate_row(row)
        assert "LEAVE_ME" not in result
        assert len(result) == 4
        assert result["lat"] == "35.018411"
