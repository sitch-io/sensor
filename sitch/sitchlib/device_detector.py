import pyudev
import serial
import time


class DeviceDetector(object):
    """ This class interrogates all detected serial ports and attempts to
    identify the devices attached.

    Attributes:
    gsm_radios (list): This is a list of GSM radios, represented in dict \
    type objects.

    gps_devices (list): This is a list of GPS devices.  Just strings like \
    '/dev/ttyUSB0'.

    """

    def __init__(self):
        print "Initializing Device Detector..."
        self.usbtty_ports = DeviceDetector.get_devices_by_subsys('usb-serial')
        self.gsm_radios = DeviceDetector.find_gsm_radios(self.usbtty_ports)
        self.gps_devices = DeviceDetector.find_gps_radios(self.usbtty_ports)
        return

    @classmethod
    def find_gsm_radios(cls, usbtty_ports):
        retval = []
        for port in usbtty_ports:
            devpath = "/dev/%s" % port["sys_name"]
            if DeviceDetector.is_a_gsm_modem(devpath):
                gsm_modem_info = DeviceDetector.get_gsm_modem_info(devpath)
                retval.append(gsm_modem_info)
        return retval

    @classmethod
    def find_gps_radios(cls, usbtty_ports):
        retval = []
        for port in usbtty_ports:
            devpath = "/dev/%s" % port["sys_name"]
            if DeviceDetector.is_a_gps(devpath):
                retval.append(devpath)
        return retval

    @classmethod
    def get_devices_by_subsys(cls, type):
        results = []
        ctx = pyudev.Context()
        for device in ctx.list_devices(subsystem=type):
            dev_struct = {"sys_path": device.sys_path,
                          "sys_name": device.sys_name,
                          "dev_path": device.device_path,
                          "subsystem": device.subsystem,
                          "driver": device.driver,
                          "device_type": device.device_type
                          }
            results.append(dev_struct)
        return results

    @classmethod
    def is_a_gps(cls, port):
        positive_match = ["$GPGGA", "$GPGLL", "$GPGSA", "$GPGSV", "$GPRMC"]
        serconn = serial.Serial(port, 4800, timeout=1)
        serconn.flushInput()
        serconn.flushOutput()
        for i in xrange(10):
            line = None
            line = serconn.readline()
            if line is None:
                time.sleep(1)
                pass
            else:
                for pm in positive_match:
                    if pm in line:
                        serconn = None
                        return True
        serconn = None
        time.sleep(3)
        return False

    @classmethod
    def is_a_gsm_modem(cls, port):
        test_command = "ATI \r\n"
        positive_match = ["SIM808"]
        serconn = serial.Serial(port, 9600, timeout=1)
        serconn.write(test_command)
        serconn.flushInput()
        serconn.flushOutput()
        for i in xrange(10):
            line = None
            line = serconn.readline()
            if line is None:
                time.sleep(1)
                pass
            else:
                for pm in positive_match:
                    if pm in line:
                        serconn = None
                        return True
        serconn = None
        time.sleep(3)
        return False

    @classmethod
    def get_gsm_modem_info(cls, port):
        retval = {"device": port}
        queries = {"manufacturer": "AT+GMI",
                   "model": "AT+GMM",
                   "revision": "AT+GMR",
                   "serial": "AT+GSN"}
        for query in queries.items():
            retval[query[0]] = DeviceDetector.interrogate_gsm_modem(port,
                                                                    query[1])
        return retval

    @classmethod
    def interrogate_gsm_modem(cls, port, command):
        serconn = serial.Serial(port, 4800, timeout=1)
        cmd = "%s\r\n" % command
        serconn.write(cmd)
        serconn.flushInput()
        serconn.flushOutput()
        for i in xrange(10):
            line = None
            line = serconn.readline()
            if line is None:
                time.sleep(1)
                pass
            elif command in line:
                time.sleep(1)
                pass
            else:
                serconn = None
                return line
        serconn = None
        return ""
