"""Device Detector interrogates USB TTY devices."""

import pyudev
import serial
import time
from utility import Utility


class DeviceDetector(object):
    """Interrogate all USB TTY ports.

    Attributes:
        gsm_radios (list): This is a list of GSM radios, represented in dict
            type objects.

        gps_devices (list): This is a list of GPS devices.  Just strings like
            '/dev/ttyUSB0'.

    """

    def __init__(self):
        """Initialization triggers interrogation of USB TTY devices."""
        print("DeviceDetector: Initializing Device Detector...")
        self.usbtty_ports = DeviceDetector.get_devices_by_subsys('usb-serial')
        usbtty_message = "DeviceDetector: Detected USB devices: \n"
        print(usbtty_message + Utility.pretty_string(self.usbtty_ports))
        time.sleep(1)
        print("DeviceDetector: Searching for GSM modem...")
        self.gsm_radios = DeviceDetector.find_gsm_radios(self.usbtty_ports)
        time.sleep(1)
        print("DeviceDetector: Searching for GPS device...")
        self.gps_devices = DeviceDetector.find_gps_radios(self.usbtty_ports)
        time.sleep(1)
        return

    @classmethod
    def find_gsm_radios(cls, usbtty_ports):
        """Interrogate USB TTY ports, return GSM radios."""
        retval = []
        for port in usbtty_ports:
            devpath = "/dev/%s" % port["sys_name"]
            print("DeviceDetector:  Checking %s" % port["sys_name"])
            if DeviceDetector.is_a_gsm_modem(devpath):
                gsm_modem_info = DeviceDetector.get_gsm_modem_info(devpath)
                retval.append(gsm_modem_info)
        return retval

    @classmethod
    def find_gps_radios(cls, usbtty_ports):
        """Interrogate USB TTY ports, return a list of GPS devices."""
        retval = []
        for port in usbtty_ports:
            devpath = "/dev/%s" % port["sys_name"]
            print("DeviceDetector:  Checking %s" % port["sys_name"])
            if DeviceDetector.is_a_gps(devpath):
                retval.append(devpath)
        return retval

    @classmethod
    def get_devices_by_subsys(cls, subsys_type):
        """Get devices from udev, by type."""
        results = []
        ctx = pyudev.Context()
        for device in ctx.list_devices(subsystem=subsys_type):
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
        """Wrap interrogator for determining when a GPS is discovered."""
        time.sleep(2)
        positive_match = ["$GPGGA", "$GPGLL", "$GPGSA", "$GPGSV", "$GPRMC"]
        result = DeviceDetector.interrogator(positive_match, port)
        return result

    @classmethod
    def is_a_gsm_modem(cls, port):
        """Wrap interrogator for determining when a GSM modem is discovered."""
        time.sleep(2)
        test_command = "ATI \r\n"
        positive_match = ["SIM808", "SIM900", "SIM800"]
        result = DeviceDetector.interrogator(positive_match, port,
                                             test_command)
        return result

    @classmethod
    def interrogator(cls, match_list, port, test_command=None):
        """Interrogate serial port, and attempt to match output.

        Args:
            match_list (list): List of strings that positively identify a
                device of a specific type.
            port (str): Port to be interrogated.
            test_command (str): Command to trigger output to match against
                match_list.
        Return:
            bool: True if the device is a positive match, False if not.
        """
        detected = False
        time.sleep(2)
        serconn = serial.Serial(port, 4800, timeout=1)
        if test_command:
            serconn.write(test_command)
        serconn.flush()
        for i in xrange(10):
            line = None
            line = serconn.readline()
            if line is None:
                time.sleep(1)
                pass
            elif DeviceDetector.interrogator_matcher(match_list, line):
                detected = True
                break
            else:
                pass
        serconn.flush()
        serconn.close()
        serconn = None
        return detected

    @classmethod
    def interrogator_matcher(cls, matchers, line):
        """Attempt to match output against known identifing strings.

        Args:
            matchers (list): List of strings which represent positive matches.
            line (str): Output from USB TTY device.

        Returns:
            bool: True if it's a match, False if not.
        """
        match = False
        for m in matchers:
            if m in line:
                match = True
        return match

    @classmethod
    def get_gsm_modem_info(cls, port):
        """Get modem information.

        Args:
            port (str): Device/port to interrogate.

        Returns:
            dict: metadata describing modem manufacturer, model, revision,
                and serial.
        """
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
        """Issue command on port, return output.

        Args:
            port (str): Port/device to interrogate.
            commmand (str): Command to be issued.

        Returns:
            str: Response from device, if any.  If none, returns an empty
                string.
        """
        time.sleep(2)
        serconn = serial.Serial(port, 4800, timeout=1)
        cmd = "%s\r\n" % command
        serconn.write(cmd)
        serconn.flush()
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
                serconn.flush()
                serconn.close()
                serconn = None
                return line
        serconn.flush()
        serconn.close()
        serconn = None
        return ""  # Returning an empty string for return type consistency
