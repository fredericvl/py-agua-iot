"""py_agua_iot provides controlling heating devices connected via
the IOT Agua platform of Micronova
"""
import jwt
import json
import logging
import re
import requests
import time

try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client

name = "py_agua_iot"

logging.basicConfig()
_LOGGER = logging.getLogger(__name__)

API_PATH_APP_SIGNUP = "/appSignup"
API_PATH_LOGIN = "/userLogin"
API_PATH_REFRESH_TOKEN = "/refreshToken"
API_PATH_DEVICE_LIST = "/deviceList"
API_PATH_DEVICE_INFO = "/deviceGetInfo"
API_PATH_DEVICE_REGISTERS_MAP = "/deviceGetRegistersMap"
API_PATH_DEVICE_BUFFER_READING = "/deviceGetBufferReading"
API_PATH_DEVICE_JOB_STATUS = "/deviceJobStatus/"
API_PATH_DEVICE_WRITING = "/deviceRequestWriting"
API_LOGIN_APPLICATION_VERSION = "1.6.0"
DEFAULT_TIMEOUT_VALUE = 5

HEADER_ACCEPT = (
    "application/json, text/javascript, */*; q=0.01"
)
HEADER_CONTENT_TYPE = (
    "application/json"
)
HEADER = {
    'Accept': HEADER_ACCEPT,
    'Content-Type': HEADER_CONTENT_TYPE
}


class agua_iot(object):
    """Provides access to Micronova's IOT Agua platform."""

    statusTranslated = {
        0: "OFF", 1: "START", 2: "LOAD PELLETS", 3: "FLAME LIGHT", 4: "ON",
        5: "CLEANING FIRE-POT", 6: "CLEANING FINAL", 7: "ECO-STOP", 8: "?",
        9: "NO PELLETS", 10: "?", 11: "?", 12: "?", 13: "?", 14: "?", 15: "?",
        16: "?", 17: "?", 18: "?", 19: "?"
    }

    def __init__(self, api_url, customer_code, email, password, unique_id, login_api_url=None, brand_id=1, debug=False):
        """agua_iot object constructor"""
        if debug is True:
            _LOGGER.setLevel(logging.DEBUG)
            _LOGGER.debug("Debug mode is explicitly enabled.")

            requests_logger = logging.getLogger("requests.packages.urllib3")
            requests_logger.setLevel(logging.DEBUG)
            requests_logger.propagate = True

            http_client.HTTPConnection.debuglevel = 1
        else:
            _LOGGER.debug(
                "Debug mode is not explicitly enabled "
                "(but may be enabled elsewhere)."
            )

        if len(api_url) > 0:
            self.api_url = api_url.rstrip("/")
        else:
            # Default to Micronova URL if empty API URL string is given
            self.api_url = "https://micronova.agua-iot.com"

        self.customer_code = str(customer_code)
        self.email = email
        self.password = password
        self.unique_id = unique_id
        self.brand_id = str(brand_id)
        self.login_api_url = login_api_url

        self.token = None
        self.token_expires = None
        self.refresh_token = None

        self.devices = list()

        self._login()

    def _login(self):
        self.register_app_id()
        self.login()
        self.fetch_devices()
        self.fetch_device_information()

    def _headers(self):
        """Correctly set headers for requests to Agua IOT."""

        return {'Accept': HEADER_ACCEPT,
                'Content-Type': HEADER_CONTENT_TYPE,
                'Origin': 'file://',
                'id_brand': self.brand_id,
                'customer_code': self.customer_code}

    def register_app_id(self):
        """Register app id with Agua IOT"""

        url = self.api_url + API_PATH_APP_SIGNUP

        payload = {
            "phone_type": "Android",
            "phone_id": self.unique_id,
            "phone_version": "1.0",
            "language": "en",
            "id_app": self.unique_id,
            "push_notification_token": self.unique_id,
            "push_notification_active": False
        }
        payload = json.dumps(payload)

        try:
            response = requests.post(url,
                                     data=payload,
                                     headers=self._headers(),
                                     allow_redirects=False,
                                     timeout=DEFAULT_TIMEOUT_VALUE)
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout):
            raise ConnectionError(str.format(
                "Connection to {0} not possible", url))

        if response.status_code != 201:
            raise UnauthorizedError('Failed to register app id')

        return True

    def login(self):
        """Authenticate with email and password to Agua IOT"""

        url = self.api_url + API_PATH_LOGIN

        payload = {
            'email': self.email,
            'password': self.password
        }
        payload = json.dumps(payload)

        extra_headers = {
            'local': 'true',
            'Authorization': self.unique_id
        }

        headers = self._headers()
        headers.update(extra_headers)

        if self.login_api_url is not None:
            extra_login_headers = {
                'applicationversion': API_LOGIN_APPLICATION_VERSION,
                'url': API_PATH_LOGIN.lstrip("/")
            }
            headers.update(extra_login_headers)
            url = self.login_api_url

        try:
            response = requests.post(url,
                                     data=payload,
                                     headers=headers,
                                     allow_redirects=False,
                                     timeout=DEFAULT_TIMEOUT_VALUE)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            raise ConnectionError(str.format(
                "Connection to {0} not possible", url))

        if response.status_code != 200:
            raise UnauthorizedError(
                'Failed to login, please check credentials')

        res = response.json()
        self.token = res['token']
        self.refresh_token = res['refresh_token']

        claimset = jwt.decode(res['token'], verify=False)
        self.token_expires = claimset.get('exp')

        return True

    def do_refresh_token(self):
        """Refresh auth token for Agua IOT"""

        url = self.api_url + API_PATH_REFRESH_TOKEN

        payload = {
            'refresh_token': self.refresh_token
        }
        payload = json.dumps(payload)

        try:
            response = requests.post(url,
                                     data=payload,
                                     headers=self._headers(),
                                     allow_redirects=False,
                                     timeout=DEFAULT_TIMEOUT_VALUE)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            raise ConnectionError(str.format(
                "Connection to {0} not possible", url))

        if response.status_code != 201:
            _LOGGER.warning("Refresh auth token failed, forcing new login...")
            self.login()
            return

        res = response.json()
        self.token = res['token']

        claimset = jwt.decode(res['token'], verify=False)
        self.token_expires = claimset.get('exp')

        return True

    def fetch_devices(self):
        """Fetch heating devices"""
        url = (self.api_url + API_PATH_DEVICE_LIST)

        payload = {}
        payload = json.dumps(payload)

        res = self.handle_webcall("POST", url, payload)
        if res is False:
            raise Error("Error while fetching devices")

        for dev in res['device']:
            url = (self.api_url + API_PATH_DEVICE_INFO)

            payload = {
                'id_device': dev['id_device'],
                'id_product': dev['id_product']
            }
            payload = json.dumps(payload)

            res2 = self.handle_webcall("POST", url, payload)
            if res2 is False:
                raise Error("Error while fetching device info")

            self.devices.append(
                Device(
                    dev['id'],
                    dev['id_device'],
                    dev['id_product'],
                    dev['product_serial'],
                    dev['name'],
                    dev['is_online'],
                    dev['name_product'],
                    res2['device_info'][0]['id_registers_map'],
                    self
                )
            )

    def fetch_device_information(self):
        """Fetch device information of heating devices """
        for dev in self.devices:
            dev.update()

    def handle_webcall(self, method, url, payload):
        if time.time() > self.token_expires:
            self.do_refresh_token()

        extra_headers = {
            'local': 'false',
            'Authorization': self.token
        }

        headers = self._headers()
        headers.update(extra_headers)

        try:
            if method == "POST":
                response = requests.post(url,
                                         data=payload,
                                         headers=headers,
                                         allow_redirects=False,
                                         timeout=DEFAULT_TIMEOUT_VALUE)
            else:
                response = requests.get(url,
                                        data=payload,
                                        headers=headers,
                                        allow_redirects=False,
                                        timeout=DEFAULT_TIMEOUT_VALUE)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            raise ConnectionError(str.format(
                "Connection to {0} not possible", url))

        if response.status_code == 401:
            self.do_refresh_token()
            return self.handle_webcall(method, url, payload)
        elif response.status_code != 200:
            return False

        return response.json()


class Device(object):
    """Agua IOT heating device representation"""

    def __init__(self, id, id_device, id_product, product_serial, name,
                 is_online, name_product, id_registers_map, agua_iot):
        self.__id = id
        self.__id_device = id_device
        self.__id_product = id_product
        self.__product_serial = product_serial
        self.__name = name
        self.__is_online = is_online
        self.__name_product = name_product
        self.__id_registers_map = id_registers_map
        self.__agua_iot = agua_iot
        self.__register_map_dict = dict()
        self.__information_dict = dict()

    def update(self):
        """Update device information"""
        self.__update_device_registers_mapping()
        self.__update_device_information()

    def __update_device_registers_mapping(self):
        url = (self.__agua_iot.api_url + API_PATH_DEVICE_REGISTERS_MAP)

        payload = {
            'id_device': self.__id_device,
            'id_product': self.__id_product,
            'last_update': '2018-06-03T08:59:54.043'
        }
        payload = json.dumps(payload)

        res = self.__agua_iot.handle_webcall("POST", url, payload)
        if res is False:
            _LOGGER.debug("GETREGISTERSMAP CALL FAILED!")
            raise Error("Error while fetching registers map")

        for registers_map in res['device_registers_map']['registers_map']:
            if registers_map['id'] == self.__id_registers_map:
                register_map_dict = dict()
                for register in registers_map['registers']:
                    register_dict = dict()
                    register_dict.update({
                        'reg_type': register['reg_type'],
                        'offset': register['offset'],
                        'formula': register['formula'],
                        'formula_inverse': register['formula_inverse'],
                        'format_string': register['format_string'],
                        'set_min': register['set_min'],
                        'set_max': register['set_max'],
                        'mask': register['mask']
                    })
                    if 'enc_val' in register:
                        for v in register['enc_val']:
                            if v['lang'] == "ENG" and v['description'] == 'ON':
                                register_dict.update({
                                    'value_on': v['value']
                                })
                            elif v['lang'] == "ENG" and v['description'] == 'OFF':
                                register_dict.update({
                                    'value_off': v['value']
                                })
                    register_map_dict.update({
                        register['reg_key']: register_dict
                    })
                _LOGGER.debug("SUCCESSFULLY UPDATED REGISTERS MAP!")
                _LOGGER.debug("REGISTERS MAP: %s", str(register_map_dict))
                self.__register_map_dict = register_map_dict

    def __update_device_information(self):
        url = (self.__agua_iot.api_url + API_PATH_DEVICE_BUFFER_READING)

        payload = {
            'id_device': self.__id_device,
            'id_product': self.__id_product,
            'BufferId': 1
        }
        payload = json.dumps(payload)

        res = self.__agua_iot.handle_webcall("POST", url, payload)
        if res is False:
            _LOGGER.debug("GETBUFFERREADING CALL FAILED!")
            raise Error("Error while fetching device information")

        _LOGGER.debug("GETBUFFERREADING SUCCEEDED!")

        id_request = res['idRequest']

        url = (self.__agua_iot.api_url + API_PATH_DEVICE_JOB_STATUS + id_request)

        payload = {}
        payload = json.dumps(payload)

        retry_count = 0
        res = self.__agua_iot.handle_webcall("GET", url, payload)
        while ((res is False or res['jobAnswerStatus'] != "completed") and retry_count < 10):
            time.sleep(1)
            res = self.__agua_iot.handle_webcall("GET", url, payload)
            retry_count = retry_count + 1

        if res is False or res['jobAnswerStatus'] != "completed":
            _LOGGER.debug("JOBANSWERSTATUS NOT COMPLETED!")
            raise Error("Error while fetching device information")

        _LOGGER.debug("JOBANSWERSTATUS COMPLETED!")

        current_i = 0
        information_dict = dict()
        try:
            for item in res['jobAnswerData']['Items']:
                information_dict.update({
                    item: res['jobAnswerData']['Values'][current_i]
                })
                current_i = current_i + 1
        except KeyError:
            _LOGGER.debug("NO ITEMS IN JOBANSWERDATA!")
            raise Error("Error while fetching device information")

        _LOGGER.debug("SUCCESSFULLY RETRIEVED ITEM IN JOBANSWERDATA!")

        _LOGGER.debug("INFORMATION MAP: %s", str(information_dict))

        self.__information_dict = information_dict

    def __get_information_item(self, item, format_string=False):
        formula = self.__register_map_dict[item]['formula']
        value = str(self.__information_dict[self.__register_map_dict[item]['offset']])
        _LOGGER.debug("GET '%s' FORMULA: %s", item, formula)
        _LOGGER.debug("GET '%s' ORIGINAL VALUE: %s", item, value)
        formula = formula.replace(
            "#",
            value
        )
        eval_formula = eval(formula)
        _LOGGER.debug("GET '%s' CALCULATED VALUE: %s", item, eval_formula)
        if format_string:
            return str.format(
                self.__register_map_dict[item]['format_string'],
                eval_formula
            )
        return eval_formula

    def __get_information_item_min(self, item):
        value = int(self.__register_map_dict[item]['set_min'])
        _LOGGER.debug("GET '%s' MIN: %s", item, value)
        return value

    def __get_information_item_max(self, item):
        value = int(self.__register_map_dict[item]['set_max'])
        _LOGGER.debug("GET '%s' MAX: %s", item, value)
        return value

    def __prepare_value_for_writing(self, item, value):
        value = float(value)
        set_min = self.__register_map_dict[item]['set_min']
        set_max = self.__register_map_dict[item]['set_max']

        if value < set_min or value > set_max:
            raise ValueError(
                "Value must be between {0} and {1}".format(
                    set_min, set_max
                )
            )

        formula = self.__register_map_dict[item]['formula_inverse']
        _LOGGER.debug("SET '%s' FORMULA: %s", item, formula)
        _LOGGER.debug("SET '%s' ORIGINAL VALUE: %s", item, value)
        formula = formula.replace(
            "#",
            str(value)
        )
        eval_formula = eval(formula)
        _LOGGER.debug("SET '%s' CALCULATED VALUE: %s", item, eval_formula)
        return int(eval_formula)

    def __request_writing(self, item, values):
        url = (self.__agua_iot.api_url + API_PATH_DEVICE_WRITING)

        items = [int(self.__register_map_dict[item]['offset'])]
        masks = [int(self.__register_map_dict[item]['mask'])]

        payload = {
            'id_device': self.__id_device,
            'id_product': self.__id_product,
            "Protocol": "RWMSmaster",
            "BitData": [8],
            "Endianess": ["L"],
            "Items": items,
            "Masks": masks,
            "Values": values
        }
        payload = json.dumps(payload)

        res = self.__agua_iot.handle_webcall("POST", url, payload)
        if res is False:
            raise Error("Error while request device writing")

        id_request = res['idRequest']

        url = (self.__agua_iot.api_url + API_PATH_DEVICE_JOB_STATUS + id_request)

        payload = {}
        payload = json.dumps(payload)

        retry_count = 0
        res = self.__agua_iot.handle_webcall("GET", url, payload)
        while ((res is False or res['jobAnswerStatus'] != "completed") and retry_count < 10):
            time.sleep(1)
            res = self.__agua_iot.handle_webcall("GET", url, payload)
            retry_count = retry_count + 1

        if res is False or res['jobAnswerStatus'] != "completed" or 'Cmd' not in res['jobAnswerData']:
            raise Error("Error while request device writing")

    @property
    def id(self):
        return self.__id

    @property
    def id_device(self):
        return self.__id_device

    @property
    def id_product(self):
        return self.__id_product

    @property
    def product_serial(self):
        return self.__product_serial

    @property
    def name(self):
        return self.__name

    @property
    def is_online(self):
        return self.__is_online

    @property
    def name_product(self):
        return self.__name_product

    @property
    def id_registers_map(self):
        return self.__id_registers_map

    @property
    def status_managed(self):
        return int(self.__get_information_item('status_managed_get'))

    @property
    def status_managed_enable(self):
        return int(self.__get_information_item('status_managed_on_enable'))

    @property
    def status(self):
        return int(self.__get_information_item('status_get'))

    @property
    def status_translated(self):
        return self.__agua_iot.statusTranslated[
            int(self.__get_information_item('status_get'))
        ]

    @property
    def alarms(self):
        return self.__get_information_item('alarms_get')

    @property
    def min_temp(self):
        return self.__get_information_item_min('temp_air_set')

    @property
    def max_temp(self):
        return self.__get_information_item_max('temp_air_set')

    @property
    def air_temperature(self):
        return float(self.__get_information_item('temp_air_get'))

    @property
    def set_air_temperature(self):
        return float(self.__get_information_item('temp_air_set'))

    @set_air_temperature.setter
    def set_air_temperature(self, value):
        item = 'temp_air_set'
        values = [self.__prepare_value_for_writing(item, value)]
        try:
            self.__request_writing(item, values)
        except Error:
            raise Error("Error while trying to set temperature")

    @property
    def gas_temperature(self):
        return float(self.__get_information_item('temp_gas_flue_get'))

    @property
    def real_power(self):
        return int(self.__get_information_item('real_power_get'))

    @property
    def min_power(self):
        return int(self.__get_information_item_min('power_set'))

    @property
    def max_power(self):
        return int(self.__get_information_item_max('power_set'))

    @property
    def set_power(self):
        return int(self.__get_information_item('power_set'))

    @set_power.setter
    def set_power(self, value):
        item = 'power_set'
        values = [self.__prepare_value_for_writing(item, value)]
        try:
            self.__request_writing(item, values)
        except Error:
            raise Error("Error while trying to set power")

    def turn_off(self):
        item = 'status_managed_get'
        values = [int(self.__register_map_dict[item]['value_off'])]
        try:
            self.__request_writing(item, values)
        except Error:
            raise Error("Error while trying to turn off device")

    def turn_on(self):
        item = 'status_managed_get'
        values = [
            int(self.__register_map_dict['status_managed_get']['value_on'])]
        try:
            self.__request_writing(item, values)
        except Error:
            raise Error("Error while trying to turn on device")


class Error(Exception):
    """Exception type for Agua IOT"""

    def __init__(self, message):
        Exception.__init__(self, message)


class UnauthorizedError(Error):
    """Unauthorized"""

    def __init__(self, message):
        super().__init__(message)


class ConnectionError(Error):
    """Connection error"""

    def __init__(self, message):
        super().__init__(message)
