import imp
import os
import random
import pytest
from contextlib import contextmanager
from tests.utils.udev import DeviceDatabase
from pyudev import Monitor, Devices

modulename = 'sitchlib'
modulepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")
file, pathname, description = imp.find_module(modulename, [modulepath])
sitchlib = imp.load_module(modulename, file, pathname, description)




class TestDeviceDetector:
    @pytest.fixture
    def monitor(request):
        return Monitor.from_netlink(request.getfuncargvalue('context'))

    @pytest.fixture
    def fake_monitor_device(request):
        context = request.getfuncargvalue('context')
        device = random.choice(list(DeviceDatabase.db()))
        return Devices.from_path(context, device.device_path)

    @contextmanager
    def patch_filter_by(type):
        add_match = 'udev_monitor_filter_add_match_{0}'.format(type)
        filter_update = 'udev_monitor_filter_update'
        with pytest.patch_libudev(add_match) as add_match:
            add_match.return_value = 0
            with pytest.patch_libudev(filter_update) as filter_update:
                filter_update.return_value = 0
                yield add_match, filter_update

    @pytest.mark.privileged
    @pytest.mark.not_on_travis
    def test_interrogator_instantiation(self):
        assert sitchlib.DeviceDetector()
