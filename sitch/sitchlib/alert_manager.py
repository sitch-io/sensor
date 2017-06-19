"""Alert Manager."""
from utility import Utility


class AlertManager(object):
    """AlertManager is used to ensure alerts are consistently formatted."""

    def __init__(self, device_id):
        """The device_id arg gets embedded into the alert."""
        self.device_id = device_id
        self.alert_map = {
            100: "Tower out of range.",
            110: "Primary BTS metadata change.",
            120: "Tower not in feed DB.",
            130: "Bad MCC (Mobile Country Code) detected.",
            140: "No neighbor for serving cell.",
            200: "ARFCN FCCH detected above power threshold.",
            300: "GPS geo drift over threshold.",
            310: "GPS time delta over threshold.",
            400: "Failed to locate a valid license for ARFCN in this area."
        }
        return

    def get_alert_type(self, alert_id):
        """Return the alert description for alert_id."""
        fixed_id = int(alert_id)
        alert_text = self.alert_map[fixed_id]
        return alert_text

    def build_alert(self, alert_id, alert_message):
        """Build the actual alert and returns it, formatted.

        DEPRECATION NOTICE:  The 'alert_id' field has been introduced for
        better readability.  It's currently set to be the same as 'id'.
        At some point in the future, the 'id' field will be removed.

        Args:
            alert_id (int): The ID of the alert you want to build
            alert_message (str): The message to be embedded in the alert.

        Returns:
            tuple: Position 0 contains the string 'sitch_alert'.  Position 1
                contains the alert and metadata.
        """
        message = Utility.generate_base_event()
        message["alert_id"] = alert_id
        message["id"] = alert_id
        message["type"] = self.get_alert_type(alert_id)
        message["event_type"] = "sitch_alert"
        message["details"] = alert_message
        retval = ("sitch_alert", message)
        return retval
