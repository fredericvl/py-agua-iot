"""Support for Agua IOT heating devices."""
import logging

from py_agua_iot import (  # pylint: disable=redefined-builtin
    ConnectionError,
    Error as AguaIOTError,
    UnauthorizedError,
    agua_iot,
)

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE,
    CURRENT_HVAC_OFF,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    SUPPORT_FAN_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    CONF_EMAIL,
    CONF_PASSWORD,
    PRECISION_HALVES,
    TEMP_CELSIUS,
)

from .const import (
    ATTR_DEVICE_ALARM,
    ATTR_DEVICE_STATUS,
    ATTR_HUMAN_DEVICE_STATUS,
    ATTR_REAL_POWER,
    ATTR_SMOKE_TEMP,
    CONF_API_URL,
    CONF_BRAND_ID,
    CONF_CUSTOMER_CODE,
    CONF_LOGIN_API_URL,
    CONF_API_LOGIN_APPLICATION_VERSION,
    CONF_UUID,
    DOMAIN,
    AGUA_STATUS_CLEANING,
    AGUA_STATUS_FLAME,
    AGUA_STATUS_OFF,
    AGUA_STATUS_ON,
)

_LOGGER = logging.getLogger(__name__)

CURRENT_HVAC_MAP_AGUA_HEAT = {
    AGUA_STATUS_ON: CURRENT_HVAC_HEAT,
    AGUA_STATUS_CLEANING: CURRENT_HVAC_HEAT,
    AGUA_STATUS_FLAME: CURRENT_HVAC_HEAT,
    AGUA_STATUS_OFF: CURRENT_HVAC_OFF,
}


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up Agua IOT climate, nothing to do."""


async def async_setup_entry(hass, entry, async_add_entities):
    """Add Agua IOT device entry."""
    api_url = entry.data[CONF_API_URL]
    customer_code = entry.data[CONF_CUSTOMER_CODE]
    brand_id = entry.data[CONF_BRAND_ID]
    email = entry.data[CONF_EMAIL]
    password = entry.data[CONF_PASSWORD]
    gen_uuid = entry.data[CONF_UUID]
    login_api_url = entry.data.get(CONF_LOGIN_API_URL) if entry.data.get(CONF_LOGIN_API_URL) != "" else None
    api_login_application_version= entry.data.get(CONF_API_LOGIN_APPLICATION_VERSION) if entry.data.get(CONF_API_LOGIN_APPLICATION_VERSION) != "" else "1.6.0"

    try:
        debug = False
        agua = await hass.async_add_executor_job(agua_iot, api_url, customer_code, email, password, gen_uuid, login_api_url, brand_id, debug, api_login_application_version)
        device = agua.devices[0]
    except UnauthorizedError:
        _LOGGER.error("Wrong credentials for Agua IOT")
        return False
    except ConnectionError:
        _LOGGER.error("Connection to Agua IOT not possible")
        return False
    except AguaIOTError as err:
        _LOGGER.error("Unknown Agua IOT error: %s", err)
        return False

    async_add_entities(
        [AguaIOTHeatingDevice(device)], True,
    )

    return True


class AguaIOTHeatingDevice(ClimateEntity):
    """Representation of an Agua IOT heating device."""

    def __init__(self, device):
        """Initialize the thermostat."""
        self._device = device

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_TARGET_TEMPERATURE | SUPPORT_FAN_MODE

    @property
    def device_state_attributes(self):
        """Return the device specific state attributes."""
        return {
            ATTR_DEVICE_ALARM: self._device.alarms,
            ATTR_DEVICE_STATUS: self._device.status,
            ATTR_HUMAN_DEVICE_STATUS: self._device.status_translated,
            ATTR_SMOKE_TEMP: self._device.gas_temperature,
            ATTR_REAL_POWER: self._device.real_power,
        }

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._device.id_device

    @property
    def name(self):
        """Return the name of the device, if any."""
        return self._device.name

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.name,
            "manufacturer": "Micronova",
            "model": self._device.name_product,
        }

    @property
    def precision(self):
        """Return the precision of the system."""
        return PRECISION_HALVES

    @property
    def target_temperature_step(self):
        """Return the supported step of target temperature."""
        return PRECISION_HALVES

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def min_temp(self):
        """Return the minimum temperature to set."""
        return self._device.min_temp

    @property
    def max_temp(self):
        """Return the maximum temperature to set."""
        return self._device.max_temp

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._device.air_temperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._device.set_air_temperature

    @property
    def hvac_mode(self):
        """Return hvac operation ie. heat, cool mode."""
        if self._device.status != 0:
            return HVAC_MODE_HEAT
        return HVAC_MODE_OFF

    @property
    def hvac_modes(self):
        """Return the list of available hvac operation modes."""
        return [HVAC_MODE_HEAT, HVAC_MODE_OFF]

    @property
    def fan_mode(self):
        """Return fan mode."""
        return str(self._device.set_power)

    @property
    def fan_modes(self):
        """Return the list of available fan modes."""
        fan_modes = []
        for x in range(self._device.min_power, (self._device.max_power + 1)):
            fan_modes.append(str(x))
        return fan_modes

    @property
    def hvac_action(self):
        """Return the current running hvac operation."""
        if self._device.status_translated in CURRENT_HVAC_MAP_AGUA_HEAT:
            return CURRENT_HVAC_MAP_AGUA_HEAT.get(self._device.status_translated)
        return CURRENT_HVAC_IDLE

    def turn_off(self):
        """Turn device off."""
        try:
            self._device.turn_off()
        except AguaIOTError as err:
            _LOGGER.error("Failed to turn off device, error: %s", err)

    def turn_on(self):
        """Turn device on."""
        try:
            self._device.turn_on()
        except AguaIOTError as err:
            _LOGGER.error("Failed to turn on device, error: %s", err)

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return

        try:
            self._device.set_air_temperature = temperature
        except (ValueError, AguaIOTError) as err:
            _LOGGER.error("Failed to set temperature, error: %s", err)

    def set_fan_mode(self, fan_mode):
        """Set new target fan mode."""
        if fan_mode is None or not fan_mode.isdigit():
            return

        try:
            self._device.set_power = int(fan_mode)
        except AguaIOTError as err:
            _LOGGER.error("Failed to set fan mode, error: %s", err)

    def set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        if hvac_mode == HVAC_MODE_OFF:
            self.turn_off()
        elif hvac_mode == HVAC_MODE_HEAT:
            self.turn_on()

    def update(self):
        """Get the latest data."""
        try:
            self._device.update()
        except UnauthorizedError:
            _LOGGER.error(
                "Wrong credentials for device %s (%s)",
                self.name,
                self._device.id_device,
            )
            return False
        except ConnectionError:
            _LOGGER.error("Connection to Agua IOT not possible")
            return False
        except AguaIOTError as err:
            _LOGGER.error(
                "Failed to update %s (%s), error: %s",
                self.name,
                self._device.id_device,
                err,
            )
            return False

        return True
