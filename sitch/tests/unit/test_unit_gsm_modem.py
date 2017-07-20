import imp
import os
modulename = 'sitchlib'
modulepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")
file, pathname, description = imp.find_module(modulename, [modulepath])
fixturepath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "../fixture/ceng-SIM900.txt")
sitchlib = imp.load_module(modulename, file, pathname, description)
sample_12 = '+CENG: 0,"0154,28,00,310,411,12,000f,00,05,178d,255"'
sample_7 = '+CENG: 1,"0128,15,30,310,411,178d"'
sample_sim900 = '+CENG:0,"0672,12,99,310,260,80,0007,06,242,113,2"'


class TestGsmModem:
    def get_sample_lines(self):
        with open(fixturepath, 'r') as fixtures:
            retval = fixtures.read()
        return retval

    def test_process_line_12(self):
        result = sitchlib.GsmModem.process_line(sample_12)
        assert result["arfcn"] == 154
        assert result["ta"] == 255

    def test_process_sim900(self):
        result = sitchlib.GsmModem.process_line(sample_sim900)
        assert result["arfcn"] == 672
        assert result["ta"] == 2

    def test_process_line_7(self):
        result = sitchlib.GsmModem.process_line(sample_7)
        assert result["arfcn"] == 128

    def test_process_fixturelines(self):
        fixture = self.get_sample_lines()
        for line in fixture.splitlines():
            parsed_result = sitchlib.GsmModem.process_line(line)
            assert type(parsed_result) is dict

    def test_clean_operator_string(self):
        example = '+COPS: 0,0,"T-Mobile USA"'
        desired = "T-Mobile USA"
        cleaned = sitchlib.GsmModem.clean_operator_string(example)
        assert cleaned == desired
