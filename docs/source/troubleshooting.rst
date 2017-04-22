----------------------
Sensor Troubleshooting
----------------------


GSM modem device detection
--------------------------

If you're using a GSM modem that's not recognized by the device detector,
please add the output from running the `ATI` command against your GSM modem in
the variable named `positive_match` in the `is_a_gsm_modem()` method, in the
`sensor/sitch/sitchlib/device_detector.py` file.  Then send a pull request so
that everyone can get the benefit of your discovery.

You can do this using the resin.io terminal on the device by doing the following steps.

1. Set the environment variable 'GSM_MODEM_BAND' to 'nope' to disable the scanner.

2. Identify which TTY port your device is running on. You can find this in the startup logs under the string 'DeviceDetector: Detected USB devices'.

3. Run python from the sensors virtual environment

.. code-block:: bash

  /app/sitch/venv/bin/python

4. Create a serial connection to the GSM modem.

.. code-block:: python

  > import serial
  > port = '/dev/[THE_MODEMS_TTY_SYS_NAME]'
  > serconn = serial.Serial(port, 4800, timeout=1)

5. Run the following snippet to get the string you need.

.. code-block:: python

  > test_command = "ATI \r\n"
  > serconn.flush()
  > for i in xrange(10):
  > line = None
  > line = serconn.readline()
  > if line is None:
  >     time.sleep(1)
  >     pass
  > else:
  >     print("Use this GSM Modem String in your pull request: {0}".format(line))
  > serconn.flush()
  > serconn.close()

Found but undetected TTY
------------------------

"The DeviceDetector shows it found my GSM Modem or GPS Device by the Configurator does not detect it"

How to identify if this is your issue
*************************************

You will be able to recognize this issue if three conditions are met.

1. You are receiving an error that the device is not configured or cannot bind to its socket.

.. code-block:: guess
    :name: GSM Modem configuration error

  > 22.04.17 08:41:58 (-0400) Runner: Starting GSM Modem consumer thread...
  > 22.04.17 08:41:58 (-0400) Runner: GSM modem configured for None
  > 22.04.17 08:41:58 (-0400) Runner: No GSM modem auto-detected or otherwise configured!
  > 22.04.17 08:41:58 (-0400) Runner: GSM scanning not configured

.. code-block:: guess
    :name: One example of GPS device errors

  > 22.04.17 08:41:58 (-0400) gpsd:ERROR: can't bind to local socket /dev/ttyUSB0


2. Your Configurator returns an empty array instead of a USB-TTY device name when it attempts to detect a device.

.. code-block:: guess
    :name: USB-TTY not found

  > 22.04.17 08:53:27 (-0400) Configurator: Detected GSM modems:
  > 22.04.17 08:53:27 (-0400) []
  > 22.04.17 08:53:27 (-0400) Configurator: Detected GPS devices:
  > 22.04.17 08:53:27 (-0400) []


.. code-block:: guess
    :name: USB-TTY correctly found

  > 22.04.17 08:53:27 (-0400) Configurator: Detected GSM modems:
  > 22.04.17 08:53:27 (-0400) [u'/dev/ttyUSB1']
  > 22.04.17 08:53:27 (-0400) Configurator: Detected GPS devices:
  > 22.04.17 08:53:27 (-0400) [u'/dev/ttyUSB0']

3. Your device detector is detecting these devices

.. code-block:: guess
    :name: Correctly detected devices

  > 22.04.17 08:52:42 (-0400) DeviceDetector: Initializing Device Detector...
  > 22.04.17 08:52:42 (-0400) DeviceDetector: Detected USB devices:
  > 22.04.17 08:52:42 (-0400)     [{'dev_path': u'/devices/platform/soc/3f980000.usb/usb1/1-1/1-1.2/1-1.2:1.0/ttyUSB0',
  > 22.04.17 08:52:42 (-0400)       'device_type': None,
  > 22.04.17 08:52:42 (-0400)       'driver': u'pl2303',
  > 22.04.17 08:52:42 (-0400)       'subsystem': u'usb-serial',
  > 22.04.17 08:52:42 (-0400)       'sys_name': u'ttyUSB0',
  > 22.04.17 08:52:42 (-0400)       'sys_path': u'/sys/devices/platform/soc/3f980000.usb/usb1/1-1/1-1.2/1-1.2:1.0/ttyUSB0'},
  > 22.04.17 08:52:42 (-0400)      {'dev_path': u'/devices/platform/soc/3f980000.usb/usb1/1-1/1-1.4/1-1.4:1.0/ttyUSB1',
  > 22.04.17 08:52:42 (-0400)       'device_type': None,
  > 22.04.17 08:52:42 (-0400)       'driver': u'pl2303',
  > 22.04.17 08:52:42 (-0400)       'subsystem': u'usb-serial',
  > 22.04.17 08:52:42 (-0400)       'sys_name': u'ttyUSB1',
  > 22.04.17 08:52:42 (-0400)       'sys_path': u'/sys/devices/platform/soc/3f980000.usb/usb1/1-1/1-1.4/1-1.4:1.0/ttyUSB1'}]

If the device detector cannot find the devices, as the following log message shows, then *this is not your issue.*

.. code-block:: guess
    :name: Detector cannot find devices

  > 22.04.17 08:52:42 (-0400) DeviceDetector: Initializing Device Detector...
  > 22.04.17 08:52:42 (-0400) DeviceDetector: Detected USB devices:
  > 22.04.17 08:52:42 (-0400) []



How to fix this issue
*********************

To fix this issue you can set the hard-coded environment variable for the device that is not detected.

In the following example the GSM modem is not detected.

.. code-block:: guess

  > 22.04.17 08:53:27 (-0400) Configurator: Detected GSM modems:
  > 22.04.17 08:53:27 (-0400) []
  > 22.04.17 08:53:27 (-0400) Configurator: Detected GPS devices:
  > 22.04.17 08:53:27 (-0400) [u'/dev/ttyUSB0']

This shows me that the GSM modem was not detected and that my GPS device can be found at '/dev/ttyUSB0'.

By looking at my DeviceDetector I can see that I have two USB devices connected. It also gives me the 'sys_name' of each device.

.. code-block:: guess
    :name: Device Detector USB device information

  > 22.04.17 08:52:42 (-0400) DeviceDetector: Detected USB devices:
  > 22.04.17 08:52:42 (-0400)     [{'dev_path': u'/devices/platform/soc/3f980000.usb/usb1/1-1/1-1.2/1-1.2:1.0/ttyUSB0',
  > 22.04.17 08:52:42 (-0400)       'device_type': None,
  > 22.04.17 08:52:42 (-0400)       'driver': u'pl2303',
  > 22.04.17 08:52:42 (-0400)       'subsystem': u'usb-serial',
  > 22.04.17 08:52:42 (-0400)       'sys_name': u'ttyUSB0',
  > 22.04.17 08:52:42 (-0400)       'sys_path': u'/sys/devices/platform/soc/3f980000.usb/usb1/1-1/1-1.2/1-1.2:1.0/ttyUSB0'},
  > 22.04.17 08:52:42 (-0400)      {'dev_path': u'/devices/platform/soc/3f980000.usb/usb1/1-1/1-1.4/1-1.4:1.0/ttyUSB1',
  > 22.04.17 08:52:42 (-0400)       'device_type': None,
  > 22.04.17 08:52:42 (-0400)       'driver': u'pl2303',
  > 22.04.17 08:52:42 (-0400)       'subsystem': u'usb-serial',
  > 22.04.17 08:52:42 (-0400)       'sys_name': u'ttyUSB1',
  > 22.04.17 08:52:42 (-0400)       'sys_path': u'/sys/devices/platform/soc/3f980000.usb/usb1/1-1/1-1.4/1-1.4:1.0/ttyUSB1'}]

Since I know that my GPS device has a sys_name of 'ttyUSB0' I know that the sys_name GSM device is 'ttyUSB1'.

I can now set the 'GSM_MODEM_PORT' environment variable to point to /dev/ttyUSB1 in the resin.io "Environment Variables' interface.

(NOTE: for those unfamiliar with python strings it should be noted that the 'u' in front of each quoted value in these example logs is specifying that the string is a Unicode string. You do not want to enter the 'u' in front of /dev/ttyUSB1  when setting your environment variables.)


If you have successfully set the environment variable you will no longer receive an error message.

In the case of the GSM modem you will also see that the following message has replaced the original error.

.. code-block:: guess
    :name: GSM modem error replacement

  > 22.04.17 08:53:33 (-0400) Runner: Starting GSM Modem consumer thread...
  > 22.04.17 08:53:33 (-0400) Runner: GSM modem configured for /dev/ttyUSB1
  > 22.04.17 08:53:33 (-0400) GSM: opening serial port: /dev/ttyUSB1
