"""eWeLink API client for Home Assistant integration."""
import logging
import requests
import hashlib
import base64
import time
from datetime import datetime

from .const import API_URLS, APP_ID, APP_SECRET, POWER_METER_UIDS

_LOGGER = logging.getLogger(__name__)


class EWeLinkRefreshAPI:
    """eWeLink API client."""

    def __init__(self, email, password, region="eu", hass=None):
        """Initialize the API client."""
        self.email = email
        self.password_hash = self._hash_password(password)
        self.region = region
        self.base_url = API_URLS.get(region, API_URLS["eu"])
        self.token = None
        self.api_key = None
        self.token_expiry = None
        self.devices = []
        self.hass = hass

    def _hash_password(self, password):
        """Hash password for authentication."""
        if not password:
            return None
        return base64.b64encode(hashlib.md5(password.encode()).digest()).decode()

    def _is_token_valid(self):
        """Check if token is still valid."""
        if not self.token:
            return False
        if self.token_expiry and time.time() > self.token_expiry:
            return False
        return True

    def login(self):
        """Authenticate with eWeLink."""
        url = f"{self.base_url}/api/user/login"

        headers = {
            "Content-Type": "application/json",
            "X-CK-Appid": APP_ID,
        }

        payload = {
            "email": self.email,
            "password": self.password_hash,
            "countryCode": "+34",
        }

        try:
            response = requests.post(
                url, json=payload, headers=headers, timeout=10, verify=True
            )

            if response.status_code != 200:
                _LOGGER.error(f"HTTP error: {response.status_code}")
                return False

            data = response.json()

            if data.get("error") == 0:
                self.token = data["at"]
                self.api_key = data["user"]["apikey"]
                self.token_expiry = time.time() + (30 * 24 * 60 * 60)
                _LOGGER.info("eWeLink authentication successful")
                return True
            else:
                _LOGGER.error(f"Login error: {data.get('msg', 'Unknown error')}")
                return False

        except requests.exceptions.SSLError:
            _LOGGER.error("SSL certificate error")
            return False
        except requests.exceptions.Timeout:
            _LOGGER.error("Connection timeout")
            return False
        except requests.exceptions.ConnectionError:
            _LOGGER.error("Connection error")
            return False
        except Exception as e:
            _LOGGER.error(f"Unexpected error during login: {e}")
            return False

    def _ensure_authenticated(self):
        """Ensure valid authentication."""
        if not self._is_token_valid():
            _LOGGER.info("Token expired, re-authenticating...")
            return self.login()
        return True

    def get_all_devices_from_api(self):
        """Get all devices from eWeLink account."""
        if not self._ensure_authenticated():
            return None

        url = f"{self.base_url}/api/user/device"

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "X-CK-Appid": APP_ID,
        }

        try:
            response = requests.get(url, headers=headers, timeout=10, verify=True)

            if response.status_code == 401:
                _LOGGER.warning("Token invalid, re-authenticating...")
                if self.login():
                    return self.get_all_devices_from_api()
                return None

            data = response.json()

            if data.get("error") == 0:
                return data.get("devicelist", [])
            else:
                _LOGGER.error(f"Error getting devices: {data.get('msg', 'Error')}")
                return None

        except Exception as e:
            _LOGGER.error(f"Error getting device list: {e}")
            return None

    def detect_power_meters(self):
        """Detect devices with power measurement capability."""
        _LOGGER.info("Detecting power meter devices...")

        all_devices = self.get_all_devices_from_api()

        if not all_devices:
            _LOGGER.warning("Could not retrieve devices")
            return []

        power_meters = []

        for device in all_devices:
            device_id = device.get("deviceid")
            device_name = device.get("name", "Unknown")
            brand_name = device.get("brandName", "")
            product_model = device.get("productModel", "")
            ui_id = str(device.get("uiid", ""))
            extra = device.get("extra", {})

            has_power_measurement = False

            # Check by UIID
            if ui_id in POWER_METER_UIDS:
                has_power_measurement = True

            # Check extra parameters
            if isinstance(extra, dict):
                extra_data = extra.get("extra", {})
                if isinstance(extra_data, dict):
                    if any(key in extra_data for key in ["power", "voltage", "current"]):
                        has_power_measurement = True

            # Check params
            params = device.get("params", {})
            if isinstance(params, dict):
                if any(key in params for key in ["power", "voltage", "current"]):
                    has_power_measurement = True

            # Check model name
            power_keywords = ["POW", "POWER", "METER", "MEDIDOR", "ENERGIA"]
            if any(keyword in product_model.upper() for keyword in power_keywords):
                has_power_measurement = True

            if has_power_measurement:
                power_meters.append(
                    {
                        "id": device_id,
                        "name": device_name,
                        "model": product_model or brand_name or "Unknown",
                        "uiid": ui_id,
                        "enabled": True,
                        "online": device.get("online", False),
                    }
                )

        _LOGGER.info(f"Found {len(power_meters)} power meter device(s)")
        return power_meters

    def refresh_device(self, device_id):
        """Force device refresh."""
        if not self._ensure_authenticated():
            return False

        url = f"{self.base_url}/api/user/device/status"

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "X-CK-Appid": APP_ID,
        }

        params = {
            "deviceid": device_id,
            "params": "switch|power|voltage|current|uiActive",
        }

        try:
            response = requests.get(
                url, params=params, headers=headers, timeout=10, verify=True
            )

            if response.status_code == 401:
                _LOGGER.warning("Token invalid, re-authenticating...")
                if self.login():
                    return self.refresh_device(device_id)
                return False

            data = response.json()

            if data.get("error") == 0:
                _LOGGER.debug(f"Device {device_id} refreshed successfully")
                return True
            else:
                _LOGGER.warning(
                    f"Error refreshing device {device_id}: {data.get('msg', 'Error')}"
                )
                return False

        except Exception as e:
            _LOGGER.error(f"Error refreshing device {device_id}: {e}")
            return False

    def get_device_status(self, device_id):
        """Get device status."""
        if not self._ensure_authenticated():
            return None

        url = f"{self.base_url}/api/user/device/status"

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "X-CK-Appid": APP_ID,
        }

        params = {"deviceid": device_id, "params": "switch|power|voltage|current"}

        try:
            response = requests.get(
                url, params=params, headers=headers, timeout=10, verify=True
            )

            if response.status_code == 401:
                if self.login():
                    return self.get_device_status(device_id)
                return None

            data = response.json()

            if data.get("error") == 0:
                return data.get("params", {})
            else:
                _LOGGER.warning(
                    f"Error getting status for {device_id}: {data.get('msg', 'Error')}"
                )
                return None

        except Exception as e:
            _LOGGER.error(f"Error getting device status: {e}")
            return None
