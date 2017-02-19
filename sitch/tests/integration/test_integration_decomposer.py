import imp
import os
import mock
import sys

sys.modules['pyudev'] = mock.Mock()
modulename = 'sitchlib'
modulepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "../../")
feedpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "../fixture/feed/")
file, pathname, description = imp.find_module(modulename, [modulepath])
sitchlib = imp.load_module(modulename, file, pathname, description)


class TestIntegrationDecomposeGps:
    def test_decomposer_unrecognized_scan(self):
        decomposer = sitchlib.Decomposer
        scan = {"scan_program": "Something you'll never see"}
        result = decomposer.decompose(scan)
        assert len(result) == 0
