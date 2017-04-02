"""General utilities."""

import datetime
import dateutil.parser as du_parser
import json
import os
import pprint
import psutil
import subprocess
import requests
from location_tool import LocationTool


class Utility:
    """General utility class."""

    @classmethod
    def dt_delta_in_minutes(cls, dt_1, dt_2):
        """Calculate the delta between two datetime objects, in minutes."""
        delta_seconds = abs((dt_1.replace(tzinfo=None) -
                             dt_2.replace(tzinfo=None)).total_seconds())
        retval = delta_seconds / 60
        return retval

    @classmethod
    def dt_from_iso(cls, iso_time):
        """Exchange an ISO8601-formatted string for a datetime object."""
        return du_parser.parse(iso_time)

    @classmethod
    def epoch_to_iso8601(cls, unix_time):
        """Transform epoch time to ISO8601 format."""
        cleaned = float(unix_time)
        return datetime.datetime.utcfromtimestamp(cleaned).isoformat()

    @classmethod
    def get_now_string(cls):
        """Get ISO8601 timestamp for now."""
        now = datetime.datetime.now().isoformat()
        return now

    @classmethod
    def get_platform_info(cls):
        """Get information on platform and hardware."""
        lshw = "/usr/bin/lshw -json"
        try:
            raw_response = subprocess.check_output(lshw.split())
            platform_info = json.loads(raw_response.replace('\n', ''))
        except:
            print("Utility: Unable to get platform info from lshw!")
            platform_info = {}
        return platform_info

    @classmethod
    def start_component(cls, runcmd):
        """Start a thing."""
        try:
            subprocess.Popen(runcmd.split())
        except KeyError as e:
            print(e)
            return False
        return True

    @classmethod
    def create_path_if_nonexistent(cls, path):
        """Create filesystem directory path."""
        if os.path.exists(path) and os.path.isdir(path):
            return
        elif os.path.exists(os.path.dirname(path)):
            return
        os.makedirs(os.path.dirname(path))
        print(("Utility: Creating directory: %s") % path)
        return

    @classmethod
    def create_file_if_nonexistent(cls, path, lfile):
        """Create file and path, if it doesn't already exist."""
        fullpath = os.path.join(path, lfile)
        if os.path.isfile(fullpath):
            return
        else:
            logmsg = "Utility: Creating log file: %s" % fullpath
            print(logmsg)
            open(fullpath, 'a').close()
        return

    @classmethod
    def write_file(cls, location, contents):
        """Write string to file."""
        with open(location, 'w') as fh:
            fh.write(contents)

    @classmethod
    def get_platform_name(cls):
        """Get platform name from lshw output."""
        platform_info = Utility.get_platform_info
        try:
            platform_name = platform_info["product"]
        except:
            print("Utility: Failed to obtain platform name!")
            platform_name = "Unspecified"
        return platform_name

    @classmethod
    def strip_list(cls, raw_struct):
        """Strip contents from single-item list."""
        if (type(raw_struct) is list and len(raw_struct)) == 1:
            return raw_struct[0]
        else:
            return raw_struct

    @classmethod
    def get_public_ip(cls):
        """Get public IP."""
        url = 'https://api.ipify.org/?format=json'
        result = (requests.get(url).json())['ip']
        return result

    @classmethod
    def calculate_distance(cls, lon_1, lat_1, lon_2, lat_2):
        """Wrap the LocationTool.get_distance_between_points() fn."""
        if None in [lon_1, lat_1, lon_2, lat_2]:
            print("Utility: Geo coordinate is zero, not resolving distance.")
            return 0
        pos_1 = (lat_1, lon_1)
        pos_2 = (lat_2, lon_2)
        dist_in_km = LocationTool.get_distance_between_points(pos_1, pos_2)
        dist_in_m = dist_in_km * 1000
        return dist_in_m

    @classmethod
    def str_to_float(cls, s):
        """Change string to float."""
        retval = None
        try:
            retval = float(s)
        except:
            errmsg = "Utility: Unable to convert %s to float" % str(s)
            print(errmsg)
        return retval

    @classmethod
    def heartbeat(cls, service_name):
        """Generate heartbeat message."""
        scan = {"scan_program": "heartbeat",
                "heartbeat_service_name": service_name,
                "timestamp": Utility.get_now_string()}
        return scan

    @classmethod
    def is_valid_json(cls, in_str):
        """Test string for json validity."""
        try:
            json.loads(in_str)
            return True
        except:
            return False

    @classmethod
    def pretty_string(cls, structure):
        """Pretty-print lines."""
        result = ""
        pp = pprint.PrettyPrinter()
        formatted = pp.pformat(structure)
        for line in formatted.splitlines():
            nextline = "    %s\n" % line
            result = result + nextline
        return result

    @classmethod
    def hex_to_dec(cls, hx):
        """Change hex to decimal."""
        integer = int(hx, 16)
        return str(integer)

    @classmethod
    def construct_feed_file_name(cls, feed_dir, prefix):
        """Construct full path for feed file."""
        file_name = "%s.csv.gz" % prefix
        dest_file_name = os.path.join(feed_dir, file_name)
        return dest_file_name

    @classmethod
    def get_performance_metrics(cls, queue_sizes={}):
        """Get sensor hardware and os performance statistics."""
        retval = {}
        retval["queue_sizes"] = queue_sizes
        cpu_times = psutil.cpu_times()
        retval["scan_program"] = "health_check"
        retval["timestamp"] = Utility.get_now_string()
        retval["cpu_percent"] = psutil.cpu_percent(percpu=True)
        retval["cpu_times"] = {"user": cpu_times.user,
                               "system": cpu_times.system,
                               "idle": cpu_times.idle,
                               "iowait": cpu_times.iowait}
        retval["mem"] = {"free": psutil.virtual_memory().free,
                         "swap_percent_used": psutil.swap_memory().percent}
        retval["root_vol"] = psutil.disk_usage('/').percent
        retval["data_vol"] = psutil.disk_usage('/data/').percent
        return retval
