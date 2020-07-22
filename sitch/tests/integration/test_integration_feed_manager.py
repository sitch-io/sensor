import imp
import os
import mock
import sqlite3
import sys
import tempfile

sys.modules['pyudev'] = mock.Mock()
modulename = 'sitchlib'
modulepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "../../")
file, pathname, description = imp.find_module(modulename, [modulepath])
sitchlib = imp.load_module(modulename, file, pathname, description)

cgi_feed_files = [os.path.join(modulepath, "tests/fixture/feed/310.csv.gz")]
fcc_feed_files = [os.path.join(modulepath, "tests/fixture/feed/CA.csv.gz")]
tempdir = tempfile.mkdtemp()
cgi_db = os.path.join(tempdir, "cgi.db")
arfcn_db = os.path.join(tempdir, "arfcn.db")
schemas = sitchlib.ConfigHelper.get_db_schemas("/etc/schemas/feed_db_schema.yaml")  # NOQA
translates = sitchlib.ConfigHelper.get_db_schema_translations("/etc/schemas/feed_db_translation.yaml")  # NOQA


class TestIntegrationFeedManager:
    def test_reconcile_cgi_db_create(self):
        expected = 279315
        actual = 0
        print("Using temp directory %s" % tempdir)
        db_schema = {"cgi": schemas["cgi"]}
        db_translate_schema = translates["ocid"]
        sitchlib.FeedManager.reconcile_db(db_schema, db_translate_schema,
                                          cgi_feed_files, cgi_db, "GSM", 0)
        conn = sqlite3.connect(cgi_db)
        c = conn.cursor()
        for row in c.execute('SELECT * FROM cgi'):
            actual += 1
        assert expected == actual

    def test_reconcile_arfcn_db_create(self):
        expected = 61488
        actual = 0
        print("Using temp directory %s" % tempdir)
        db_schema = {"arfcn": schemas["arfcn"]}
        db_translate_schema = translates["fcc"]
        sitchlib.FeedManager.reconcile_db(db_schema, db_translate_schema,
                                          fcc_feed_files, arfcn_db, "GSM", 0)
        conn = sqlite3.connect(arfcn_db)
        c = conn.cursor()
        for row in c.execute('SELECT * FROM arfcn'):
            actual += 1
        assert expected == actual
