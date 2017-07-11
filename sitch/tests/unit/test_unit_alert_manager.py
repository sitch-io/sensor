import imp
import os
modulename = 'sitchlib'
modulepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")
file, pathname, description = imp.find_module(modulename, [modulepath])
sitchlib = imp.load_module(modulename, file, pathname, description)


class TestAlertManager:
    def test_alert_manager_init(self):
        alert_manager = sitchlib.AlertManager("DEVICE_ID")
        assert alert_manager

    def test_get_alert_type(self):
        types = [100, 110, 200]
        alert_manager = sitchlib.AlertManager("DEVICE_ID")
        for t in types:
            assert alert_manager.get_alert_type(t)

    def test_build_alert(self):
        alert_type = 100
        alert_body = "Hello World"
        alert_manager = sitchlib.AlertManager("DEVICE_ID")
        result = alert_manager.build_alert(alert_type, alert_body)
        assert result[1]["alert_id"] == alert_type
        assert result[1]["alert_type"] is not None
        assert alert_body in result[1]["details"]
