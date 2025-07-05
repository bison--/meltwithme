import os
import subprocess
import config_loader as config

class DetectPath:
    def __init__(self):
        # ID_MODEL_FROM_DATABASE=USB-zyTemp
        self.device_name = "USB-zyTemp"
        self.device_prefix = "hidraw"
        self.detected_path = ""

    def need_detection(self):
        if config.DEVICE_PATH:
            return False

        if self.detected_path:
            return False

        return True


    def detect_path(self):
        """
        Scans /dev for hidraw devices, queries udevadm for each one, and
        returns the first path whose ID_MODEL_FROM_DATABASE matches.
        """

        # reset path
        self.detected_path = ""

        for entry in os.listdir('/dev'):
            if not entry.startswith(self.device_prefix):
                continue

            device_node = os.path.join('/dev', entry)
            try:
                # call udevadm to dump properties for this device node
                output = subprocess.check_output(
                    ['udevadm', 'info', '--query=property', '--name', device_node],
                    text=True,  # returns a str instead of bytes
                    stderr=subprocess.DEVNULL
                )
            except (subprocess.CalledProcessError, FileNotFoundError):
                # skip nodes we can’t query (or if udevadm isn’t present)
                continue

            for line in output.splitlines():
                # look for the model field
                if line.startswith('ID_MODEL_FROM_DATABASE='):
                    model = line.partition('=')[2]
                    if model == self.device_name:
                        self.detected_path = device_node
                        return device_node

        # if we get here, nothing matched
        return ""
