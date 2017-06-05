----------------------
Sensor Troubleshooting
----------------------


GSM modem device detection
--------------------------

If you're using a GSM modem that's not recognized by the device detector,
please add the output from running the ``ATI`` command against your GSM modem in
the variable named ``positive_match`` in the ``is_a_gsm_modem()``` method, in the
``sensor/sitch/sitchlib/device_detector.py`` file.  Then send a pull request so
that everyone can get the benefit of your discovery.

You can do this using the resin.io terminal on the device by doing the following steps.

1. Set the environment variable ``GSM_MODEM_BAND`` to ``nope`` to disable the scanner.

2. Identify which TTY port your device is running on. You can find this in the startup logs under the string ``DeviceDetector: Detected USB devices``.

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

The DeviceDetector shows it found my GSM Modem or GPS Device by the Configurator does not detect it

How to identify if this is your issue
*************************************

You will be able to recognize this issue if three conditions are met.

1. You are receiving an error that the device is not configured or cannot bind to its socket.

.. code-block:: guess
    :name: GSM_Modem_configuration_error

  > 22.04.17 08:41:58 (-0400) Runner: Starting GSM Modem consumer thread...
  > 22.04.17 08:41:58 (-0400) Runner: GSM modem configured for None
  > 22.04.17 08:41:58 (-0400) Runner: No GSM modem auto-detected or otherwise configured!
  > 22.04.17 08:41:58 (-0400) Runner: GSM scanning not configured

.. code-block:: guess
    :name: One_example_of_GPS_device_errors

  > 22.04.17 08:41:58 (-0400) gpsd:ERROR: can't bind to local socket /dev/ttyUSB0


2. Your Configurator returns an empty array instead of a USB-TTY device name when it attempts to detect a device.

.. code-block:: guess
    :name: USB-TTY_not_found

  > 22.04.17 08:53:27 (-0400) Configurator: Detected GSM modems:
  > 22.04.17 08:53:27 (-0400) []
  > 22.04.17 08:53:27 (-0400) Configurator: Detected GPS devices:
  > 22.04.17 08:53:27 (-0400) []


.. code-block:: guess
    :name: USB-TTY_correctly_found

  > 22.04.17 08:53:27 (-0400) Configurator: Detected GSM modems:
  > 22.04.17 08:53:27 (-0400) [u'/dev/ttyUSB1']
  > 22.04.17 08:53:27 (-0400) Configurator: Detected GPS devices:
  > 22.04.17 08:53:27 (-0400) [u'/dev/ttyUSB0']

3. Your device detector is detecting these devices

.. code-block:: guess
    :name: Correctly_detected_devices

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
    :name: Detector_cannot_find_devices

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
    :name: Device_Detector_USB_device_information

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


Since I know that my GPS device has a sys_name of ``ttyUSB0`` I know that the sys_name GSM device is ``ttyUSB1``.

I can now set the ``GSM_MODEM_PORT`` environment variable to point to /dev/ttyUSB1 in the resin.io ``Environment Variables`` interface.

(NOTE: for those unfamiliar with python strings it should be noted that the ``u`` in front of each quoted value in these example logs is specifying that the string is a Unicode string. You do not want to enter the ``u`` in front of /dev/ttyUSB1  when setting your environment variables.)


If you have successfully set the environment variable you will no longer receive an error message.

In the case of the GSM modem you will also see that the following message has replaced the original error.

.. code-block:: guess
    :name: GSM_modem_error_replacement

  > 22.04.17 08:53:33 (-0400) Runner: Starting GSM Modem consumer thread...
  > 22.04.17 08:53:33 (-0400) Runner: GSM modem configured for /dev/ttyUSB1
  > 22.04.17 08:53:33 (-0400) GSM: opening serial port: /dev/ttyUSB1


No events in Kibana
===================

The SITCH sensor relies on Filebeat to read events from log files and transmit
them to the Logstash instance running in the SITCH service.  There are a few
indicators when the transmission process is broken:

1. No log files being written:
  Confirm that log files are being written at ``/data/sitch/log/``.  If your
  sensor isn't populating log files, the most likely reason is that the
  sensor is in a reboot loop due to mis-configuration.  Check the
  Device Summary page in Resin, for the affected sensor.  If the reason that
  the sensor isn't coming online cleanly isn't celarly explained in the log
  messages, please reach out in the gitter channel
  (https://gitter.im/sitch-io/sensor) or open an issue in the sensor project
  on Github: https://github.com/sitch-io/sensor/issues

1. Make sure that the filebeat process is running on the sensor:
  Check using ``ps ef`` from the terminal: you should see a line containing:
  ``/usr/local/bin/filebeat-linux-arm -c /etc/filebeat.yml``.  If you don't,
  you can try to start the process manually and look for errors printed to
  stdout.  Your crypto certs and keys are retieved in the sensor initialization
  process and dropped at ``/host/run/dbus/crypto/``.  You should see three files
  there: ``ca.crt``, ``logstash.crt``, and ``logstash.key``.  If you don't have
  those files on your system, there's a really good chance that your sensor
  environment variables aren't set correctly.  You should confirm that the
  ``VAULT_PATH``, ``VAULT_TOKEN``, and ``VAULT_URL`` environment variables
  are correct, and that the network path is open between your sensor and Vault.
  You can confirm the network path is open by running this command:
  ``openssl s_client -connect VAULT_HOSTNAME:8200``.  Replace
  ``VAULT_HOSTNAME`` with the DNS name from the output of ``echo $VAULT_URL``,
  when run in the terminal on the sensor.  So if your $VAULT_URL is
  ``https://myvault.mydomain.com:8200``, the command you should run in the
  terminal on the sensor is:
  ``openssl s_client -connect myvault.mydomain.com:8200``.  An error message
  containing ``gethostbyname failure`` indicates a failure in DNS resolution.
  A message containing ``connect: Connection refused`` indicates that the
  OpenSSL client is unable to connect to the port that Vault is running on,
  and you need to check your iptables and security groups settings, and confirm
  that Vault is actually listening on that port.  You should also confirm that
  Vault is actually running.  If the Vault container is stopped and restarted,
  you will need to unseal the Vault again.  See the docs for the demo
  environment (https://github.com/sitch-io/demo) for details on how to unseal
  the vault.

1. Confirm that Filebeat is processing the log files:
  There's a registry file managed by Filebeat, located at
  ``/data/sitch/log/fb_registry``.  This file is what Filebeat uses to maintain
  its place in your log files, in the event it gets restarted.

1. If Filebeat appears to be transmitting events to Logstash and you still
  don't see events in Kibana, you can run the logstash container in debug
  mode by changing the docker-compose.yml file's setting for
  ``services.logstash.image`` from ``docker.io/sitch/logstash`` to
  ``docker.io/sitch/logstash:debug``.  This will be very verbose, and can
  cause a substantial amount of disk space consumption.  Don't leave it like
  that forever.

1. If there is no indication that Logstash is having trouble getting events
  into Elasticsearch, check that you have an index for logstash
  built in Kibana by navigating to this URL:
  https://MY_SITCH_SERVICE_HOSTNAME:8443/app/kibana#/management/kibana/indices ,
  replacing MY_SITCH_SERVICE_HOSTNAME with the hostname of your SITCH
  service-side environment.  If you have an index, you should have events.
  Try adjusting your time window, and confirm that the system clocks in your
  SITCH service side components are correct.  Time drift can not only cause the
  query in Kibana to look weird, but it can cause a connection negotiation
  failure between the sensor and service.

If none of the above lead you to success, please don't hesitate to file an
issue in the sensor's Github repository:
https://github.com/sitch-io/sensor/issues and/or reach out in the Gitter
channel: https://gitter.im/sitch-io/sensor.
