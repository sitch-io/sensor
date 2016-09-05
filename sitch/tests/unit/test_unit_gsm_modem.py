import imp
import os
modulename = 'sitchlib'
modulepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")
file, pathname, description = imp.find_module(modulename, [modulepath])
fixturepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "../fixture/ceng.txt")
sitchlib = imp.load_module(modulename, file, pathname, description)
sample_12 = '+CENG: 0,"0154,28,00,310,411,12,000f,00,05,178d,255"'
sample_7 = '+CENG: 1,"0128,15,30,310,411,178d"'


class TestGsmModem:
    def get_sample_lines(self):
        with open(fixturepath, 'r') as fixtures:
            retval = fixtures.read()
        return retval

    def test_process_line_12(self):
        result = sitchlib.GsmModem.process_line(sample_12)
        for k, v in result.items():
            assert v is not None

    def test_process_line_7(self):
        result = sitchlib.GsmModem.process_line(sample_7)
        for k, v in result.items():
            assert v is not None

    def test_process_fixturelines(self):
        fixture = self.get_sample_lines()
        for line in fixture.splitlines():
            parsed_result = sitchlib.GsmModem.process_line(line)
            assert type(parsed_result) is dict
