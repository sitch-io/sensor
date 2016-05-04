import datetime
import json
import subprocess


class Utility:
    def __init__():
        return

    @classmethod
    def get_now_string(cls):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return now

    @classmethod
    def get_platform_info(cls):
        lshw = "/usr/bin/lshw -json"
        try:
            raw_response = subprocess.check_output(lshw.split())
            platform_info = json.loads(raw_response.replace('\n', ''))
        except:
            platform_info = {}
        return platform_info

    @classmethod
    def start_component(cls, runcmd):
        try:
            subprocess.Popen(runcmd.split())
        except:
            return False
        return True

    @classmethod
    def write_file(cls, location, contents):
        with open(location, 'w') as fh:
            fh.write(contents)
