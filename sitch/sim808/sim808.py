import serial


class FonaReader(object):
    """ Initialization causes the module to go into engineering mode, which will
    cause it to return cell network information.
    It has an iterator (generator) built in that cranks out dicts.

    """
    def __init__(self, ser_port):
        self.initstring = u'AT+CENG=2,1\r\n'
        self.serconn = serial.Serial(port=ser_port,
                                     baudrate=115200)
        self.sio = io.TextIOWrapper(io.BufferedRWPair(self.serconn,
                                                      self.serconn))
        self.sio.write(self.initstring)
        self.sio.flush()

    def __iter__(self):
        while True:
            line = None
            line = self.sio.readline()
            if line is not None:
                processed_line = self.process_line(line)
                yield processed_line

    def trigger_gps(self):
        self.sio.write(u'AT+CIPGSMLOC=1,1\r\n')
        self.sio.flush()
        return None

    def set_band(self, band):
        if band in ["EGSM_MODE", "PGSM_MODE", "DCS_MODE", "GSM850_MODE",
                    "PCS_MODE", "EGSM_DCS_MODE", "GSM850_PCS_MODE",
                    "EGSM_PCS_MODE", "ALL_BAND"]:
            term_command = "AT+CBAND=\"%s\"" % band
            self.sio.write(term_command)

    @classmethod
    def process_line(cls, line):
        processed = None
        if line.startswith('+CENG: '):
            dataz = line.split(' ')[1].replace('"', '')
            line_parts = dataz.split(',')
            if len(line_parts) == 12:
                processed = FonaReader.process_12(line_parts)
            if len(line_parts) == 7:
                processed = FonaReader.process_7(line_parts)
            if len(line_parts) == 8:
                processed = FonaReader.process_8(line_parts)
        elif line.startswith('+CIPGSMLOC:'):
            dataz = line.split(' ')[1]
            line_parts = dataz_split(',')
            if line_parts[0] == 0:
                processed = FonaReader.process_gps(line_parts)
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
        retval = {"cell": parts[0],
                  "arfcn": parts[1],
                  "rxl": parts[2],
                  "bsic": parts[3],
                  "mcc": parts[4],
                  "mnc": parts[5],
                  "lac": parts[6]
                  }
        return retval

    @classmethod
    def process_gps(cls, parts):
        retval = {"status": parts[0],
                  "lon": parts[1],
                  "lat": parts[2],
                  "date": parts[3],
                  "time": parts[4]
                  }
        return retval
