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
tempdir = tempfile.mkdtemp()
cgi_db = os.path.join(tempdir, "cgi.db")


class TestIntegrationFeedManager:
    def test_reconcile_cgi_db_create(self):
        expected = 279315
        actual = 0
        print("Using temp directory %s" % tempdir)
        sitchlib.FeedManager.reconcile_cgi_db(cgi_feed_files, cgi_db)
        conn = sqlite3.connect(cgi_db)
        c = conn.cursor()
        for row in c.execute('SELECT * FROM cgi'):
            actual += 1
        assert expected == actual
