import imp
import os
import mock
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


class TestIntegrationFeedManager:
    def test_reconcile_cgi_db_create(self):
        print("Using temp directory %s" % tempdir)
        assert sitchlib.FeedManager.reconcile_cgi_db(cgi_feed_files,
                                                     os.path.join(tempdir,
                                                                  "cgi.db"))
