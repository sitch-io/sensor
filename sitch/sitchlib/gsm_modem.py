import re
import serial
import sys
import time


class GsmModem(object):
    """ Initialization opens the port.  Calling GsmModem.set_eng_mode() causes
    the module to go into engineering mode, which will
    cause it to return cell network information.
    It has an iterator (generator) built in that cranks out dicts.

    """
    def __init__(self, ser_port):
        self.eng_init = 'AT+CENG=2,1 \r\n'
        self.unset_eng = 'AT+CENG=0 \r\n'
        self.gps_init = 'AT+CGPSINF=0 \r\n'
        self.echo_off = 'ATE0 \r\n'
        self.reg_info = 'AT+COPS? \r\n'
        self.config_dump = 'ATV1Q0&V \r\n'
        print "GSM: opening serial port: %s" % ser_port
        time.sleep(10)
        self.serconn = serial.Serial(ser_port, 4800, timeout=1)
        ser_open_iter = 0
        while not self.serconn.is_open:
            print "GSM: Attempting to open %s again..." % ser_port
            time.sleep(1)
            ser_open_iter = ser_open_iter + 1
            self.serconn.open()
            if ser_open_iter > 5:
                print "GSM: Failed to init and open serial port %s!" % ser_port
                sys.exit(2)
        return

    def __iter__(self):
        page = []
        while True:
            line = None
            line = self.serconn.readline()
            processed_line = self.process_line(line)
            if line is None:
                pass
            elif processed_line == {}:
                pass
            elif "lon" in processed_line:
                yield [processed_line]
            elif "cell" in processed_line:
                if (str(processed_line["cell"]) == str(0) and page != []):
                    yield page
                    page = []
                    page.append(processed_line)
                else:
                    page.append(processed_line)

    def trigger_gps(self):
        self.serconn.write(self.gps_init)
        self.serconn.flush()
        return

    def eng_mode(self, status):
        """ Status is bool. """
        if status is False:
            mode_string = self.unset_eng
        else:
            mode_string = self.eng_init
        self.serconn.write(mode_string)
        self.serconn.flush()
        time.sleep(2)
        output = self.serconn.readline()
        print output
        self.serconn.flush()
        return

    def get_reg_info(self):
        self.serconn.write(self.reg_info)
        self.serconn.flush()
        time.sleep(2)
        output = self.serconn.readline()
        print output
        self.serconn.flush()
        return output

    def dump_config(self):
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

    def set_band(self, band):
        if band in ["EGSM_MODE", "PGSM_MODE", "DCS_MODE", "GSM850_MODE",
                    "PCS_MODE", "EGSM_DCS_MODE", "GSM850_PCS_MODE",
                    "EGSM_PCS_MODE", "ALL_BAND"]:
            term_command = "AT+CBAND=\"%s\" \r\n" % band
            print "GSM: Setting GSM band with: %s" % term_command
            self.serconn.write(term_command)
            self.serconn.flush()
            time.sleep(2)
            output = self.serconn.readline()
            print output
            self.serconn.flush()
        else:
            print "GSM: Not setting band, unrecognized value: %s" % band

    @classmethod
    def process_line(cls, line):
        processed = None
        if line.startswith('+CENG: '):
            dataz = line.split(' ')[1].replace('"', '').replace('\r\n', '')
            line_parts = dataz.split(',')
            if len(line_parts) == 12:
                processed = GsmModem.process_12(line_parts)
            elif len(line_parts) == 7:
                processed = GsmModem.process_7(line_parts)
            elif len(line_parts) == 8:
                processed = GsmModem.process_8(line_parts)
            else:
                print "GSM: Unrecognized GSM message format:"
                print line_parts
        elif line.startswith('AT+'):
            processed = {}
        elif re.match('^\s*$', line):
            processed = {}
        elif re.match('^OK\s*$', line):
            processed = {}
        else:
            print "GSM: Unprocessable line from SIM808!"
            print line
            processed = {}
        return processed

    @classmethod
    def process_12(cls, parts):
        retval = {"cell": parts[0],
                  "arfcn": parts[1],
                  "rxl": parts[2],
                  "rxq": parts[3],
                  "mcc": parts[4],
                  "mnc": parts[5],
                  "bsic": parts[6],
                  "cellid": parts[7],
                  "rla": parts[8],
                  "txp": parts[9],
                  "lac": parts[10],
                  "ta": parts[11]
                  }
        return retval

    @classmethod
    def process_8(cls, parts):
        retval = {"cell": parts[0],
                  "arfcn": parts[1],
                  "rxl": parts[2],
                  "bsic": parts[3],
                  "cellid": parts[4],
                  "mcc": parts[5],
                  "mnc": parts[6],
                  "lac": parts[7]
                  }
        return retval

    @classmethod
    def process_7(cls, parts):
        # In a 7-item line, cellid is not provided.  We set
        # it to 0 to prevent barfing elsewhere.
        retval = {"cell": parts[0],
                  "arfcn": parts[1],
                  "rxl": parts[2],
                  "bsic": parts[3],
                  "mcc": parts[4],
                  "mnc": parts[5],
                  "lac": parts[6],
                  "cellid": 0
                  }
        return retval
