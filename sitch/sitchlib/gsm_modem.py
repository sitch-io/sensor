"""GSM Modem device ...driver?..."""

import re
import serial
import sys
import time


class GsmModem(object):
    """GSM Modem handler class.  Interfaces with device over serial.

    Calling GsmModem.set_eng_mode() causes the module to go into
        engineering mode, which will cause it to return cell network
        information. It has an iterator (generator) built in that cranks
        out dicts.
    """

    def __init__(self, ser_port):
        """Initialization opens the port.

        Args:
            ser_port (str): Device to open and interact with.
        """
        self.eng_init = 'AT+CENG=2,1 \r\n'
        self.unset_eng = 'AT+CENG=0 \r\n'
        self.gps_init = 'AT+CGPSINF=0 \r\n'
        self.echo_off = 'ATE0 \r\n'
        self.reg_info = 'AT+COPS? \r\n'
        self.imsi_info = 'AT+CIMI \r\n'
        self.config_dump = 'ATV1Q0&V \r\n'
        print("GSM: opening serial port: %s" % ser_port)
        time.sleep(10)
        self.serconn = serial.Serial(ser_port, 4800, timeout=1)
        ser_open_iter = 0
        while not self.serconn.is_open:
            print("GSM: Attempting to open %s again..." % ser_port)
            time.sleep(1)
            ser_open_iter = ser_open_iter + 1
            self.serconn.open()
            if ser_open_iter > 5:
                print("GSM: Failed to open serial port %s!" % ser_port)
                sys.exit(2)
        return

    def __iter__(self):
        """Yield scans from GSM modem."""
        page = []
        while True:
            line = None
            line = self.serconn.readline()
            processed_line = self.process_line(line)
            if line is None:
                pass
            elif processed_line is None:
                pass
            elif processed_line == {}:
                pass
            elif "cell" in processed_line:
                if (str(processed_line["cell"]) == str(0) and page != []):
                    yield page
                    page = []
                    page.append(processed_line)
                else:
                    page.append(processed_line)

    def eng_mode(self, status):
        """Set or unset engineering mode on the modem.

        Args:
            status (bool): True to enable engineering mode, False to disable.
        """
        self.serconn.flush()
        if status is False:
            print("GsmModem: Unsetting engineering mode, flushing")
            self.serconn.write(self.unset_eng)
            while True:
                output = self.serconn.readline()
                if output == '':
                    break
                else:
                    print(output)
        else:
            print("GsmModem: Setting engineering mode")
            self.serconn.write(self.eng_init)
        self.serconn.flush()
        time.sleep(2)
        output = self.serconn.readline()
        print(output)
        self.serconn.flush()
        return

    def get_reg_info(self):
        """Get registration information from the modem."""
        self.serconn.write(self.reg_info)
        self.serconn.flush()
        time.sleep(2)
        output = self.serconn.readline()
        if "AT+" in output:
            output = GsmModem.clean_operator_string(self.serconn.readline())
        print(output)
        self.serconn.flush()
        return output

    def dump_config(self):
        """Dump modem's configuration."""
        self.serconn.write(self.config_dump)
        self.serconn.flush()
        time.sleep(2)
        retval = []
        while True:
            output = self.serconn.readline()
            if output == '':
                break
            retval.append(str(output))
        self.serconn.flush()
        return retval

    def get_imsi(self):
        """Get the IMSI of the SIM installed in the modem."""
        rx = r'(?P<imsi>\S+)'
        self.serconn.write(self.imsi_info)
        self.serconn.flush()
        time.sleep(2)
        retval = []
        while True:
            output = self.serconn.readline()
            if output == '':
                break
            if "AT+CIMI" in output:
                continue
            if output == "\r\n":
                continue
            if "OK\r\n" in output:
                continue
            retval.append(str(output))
        self.serconn.flush()
        try:
            test_string = "".join(retval).replace('\r\n', '')
            retval = re.match(rx, test_string).group("imsi")
        except AttributeError as e:
            print("GSM: Unable to clean up IMSI")
            print(e)
        return retval

    def set_band(self, band):
        """Set the band the GSM modem should communicate on.

        If the band does not set correctly, an error will print to stdout and
        the original setting will persist.

        Args:
            band (str): Pick one: `EGSM_MODE`, `PGSM_MODE`, `DCS_MODE`,
                `GSM850_MODE`, `PCS_MODE`, `EGSM_DCS_MODE`, `GSM850_PCS_MODE`,
                `EGSM_PCS_MODE`, or `ALL_BAND`.
        """
        if band in ["EGSM_MODE", "PGSM_MODE", "DCS_MODE", "GSM850_MODE",
                    "PCS_MODE", "EGSM_DCS_MODE", "GSM850_PCS_MODE",
                    "EGSM_PCS_MODE", "ALL_BAND"]:
            term_command = "AT+CBAND=\"%s\" \r\n" % band
            print("GSM: Setting GSM band with: %s" % term_command)
            self.serconn.write(term_command)
            self.serconn.flush()
            time.sleep(2)
            output = self.serconn.readline()
            print(output)
            self.serconn.flush()
        else:
            print("GSM: Not setting band, unrecognized value: %s" % band)

    @classmethod
    def clean_operator_string(cls, operator_string):
        """Clean up the operator string."""
        rx = r'^[^\"]+\"(?P<operator_name>[^\"]+)\"'
        try:
            cleaned = re.match(rx, operator_string).group("operator_name")
        except AttributeError as e:
            print("GSM: Unable to clean up operator string")
            print(e)
            cleaned = operator_string
        return cleaned

    @classmethod
    def process_line(cls, line):
        """Process line output from GSM modem.

        We expect to see only lines starting with `+CENG:`.  Otherwise, it's
            an empty dictionary getting returned.

        Args:
            line (str): Raw line output from GSM modem.

        Returns:
            dict: Structured data parsed from `line`.
        """
        processed = None
        if line.startswith('+CENG:'):
            dataz = line.split(':')[1].lstrip().replace('"', '').replace('\r\n', '')  # NOQA
            line_parts = dataz.split(',')
            if len(line_parts) == 12:
                processed = GsmModem.process_12(line_parts)
            elif len(line_parts) == 7:
                processed = GsmModem.process_7(line_parts)
            elif len(line_parts) == 8:
                processed = GsmModem.process_8(line_parts)
            else:
                print("GSM: Unrecognized GSM message format:")
                print(line)
        elif line.startswith('AT+'):
            processed = {}
        elif re.match('^\s*$', line):
            processed = {}
        elif re.match('^OK\s*$', line):
            processed = {}
        else:
            print("GSM: Unprocessable line from modem!")
            print(line)
            processed = {}
        return processed

    @classmethod
    def process_12(cls, parts):
        """Process a 12-part CENG message.

        Args:
            parts (list): Parts parsed from original CENG message.

        Returns:
            dict: Structured cell channel metadata.

        """
        retval = {"cell": int(parts[0]),
                  "arfcn": int(parts[1]),
                  "rxl": int(parts[2]),
                  "rxq": int(parts[3]),
                  "mcc": parts[4],
                  "mnc": parts[5],
                  "bsic": parts[6],
                  "cellid": parts[7],
                  "rla": int(parts[8]),
                  "txp": int(parts[9]),
                  "lac": parts[10],
                  "ta": int(parts[11])
                  }
        return retval

    @classmethod
    def process_8(cls, parts):
        """Process an 8-part CENG message.

        Args:
            parts (list): Parts parsed from original CENG message.

        Returns:
            dict: Structured cell channel metadata.
        """
        retval = {"cell": int(parts[0]),
                  "arfcn": int(parts[1]),
                  "rxl": int(parts[2]),
                  "bsic": parts[3],
                  "cellid": parts[4],
                  "mcc": parts[5],
                  "mnc": parts[6],
                  "lac": parts[7]
                  }
        return retval

    @classmethod
    def process_7(cls, parts):
        """Process a 7-part CENG message.

        In a 7-item line, cellid is not provided.  We set
            it to 0 to prevent barfing elsewhere.

        Args:
            parts (list): Parts parsed from original CENG message.

        Returns:
            dict: Structured cell channel metadata.
        """
        retval = {"cell": int(parts[0]),
                  "arfcn": int(parts[1]),
                  "rxl": int(parts[2]),
                  "bsic": parts[3],
                  "mcc": parts[4],
                  "mnc": parts[5],
                  "lac": parts[6],
                  "cellid": 0
                  }
        return retval
