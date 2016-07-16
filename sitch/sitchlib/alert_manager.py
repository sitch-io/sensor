class AlertManager(object):
    def __init__(self):
        self.alert_map = {
            100: "Tower out of range.",
            110: "Primary BTS metadata change.",
            120: "Tower not in feed DB.",
            200: "ARFCN FCCH detected above power threshold."
        }
        return

    def get_alert_type(self, alert_id):
        fixed_id = int(alert_id)
        alert_text = self.alert_map[fixed_id]
        return alert_text

    def build_alert(self, alert_id, alert_message):
        message = {}
        message["id"] = alert_id
        message["type"] = self.get_alert_type(alert_id)
        message["details"] = alert_message
        retval = ("sitch_alert", message)
        return retval
