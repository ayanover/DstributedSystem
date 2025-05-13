import os
import json
import logging

logger = logging.getLogger('device.persistence')


class DevicePersistence:
    """Handles persistence of device identity and credentials"""

    def __init__(self, device_type, base_dir=None):
        """
        Initialize the persistence module

        Args:
            device_type (str): Type of the device (used in filename)
            base_dir (str, optional): Directory to store config files. Defaults to ~/.math_devices/
        """
        if base_dir is None:
            base_dir = os.path.join(os.path.expanduser("~"), ".math_devices")

        # Ensure directory exists
        os.makedirs(base_dir, exist_ok=True)

        self.config_file = os.path.join(base_dir, f"{device_type}.json")
        logger.info(f"Using config file: {self.config_file}")

    def save_device_info(self, device_info):
        """
        Save device information to the config file

        Args:
            device_info (dict): Device information to save
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(device_info, f, indent=2)
            logger.info(f"Saved device information to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save device information: {str(e)}")
            return False

    def load_device_info(self):
        """
        Load device information from the config file

        Returns:
            dict: Device information or None if not found
        """
        if not os.path.exists(self.config_file):
            logger.info(f"No existing configuration found at {self.config_file}")
            return None

        try:
            with open(self.config_file, 'r') as f:
                device_info = json.load(f)
            logger.info(f"Loaded device information from {self.config_file}")
            return device_info
        except Exception as e:
            logger.error(f"Failed to load device information: {str(e)}")
            return None