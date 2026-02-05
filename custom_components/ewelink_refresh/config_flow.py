"""Config flow for eWeLink Refresh integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, CONF_SCAN_INTERVAL
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_REGION,
    CONF_AUTO_DISCOVER,
    CONF_COUNTRY_CODE,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_REGION,
    DEFAULT_COUNTRY_CODE,
    REGIONS,
    COUNTRY_CODES,
)
from .ewelink_api import EWeLinkRefreshAPI

_LOGGER = logging.getLogger(__name__)


class EWeLinkRefreshConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for eWeLink Refresh."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validar credenciales
            api = EWeLinkRefreshAPI(
                email=user_input[CONF_EMAIL],
                password=user_input[CONF_PASSWORD],
                region=user_input.get(CONF_REGION, DEFAULT_REGION),
                country_code=user_input.get(CONF_COUNTRY_CODE, DEFAULT_COUNTRY_CODE),
                hass=self.hass,
            )

            # Intentar login
            login_result = await self.hass.async_add_executor_job(api.login)
            if login_result:
                # Login exitoso
                _LOGGER.info("eWeLink authentication successful")
                
                # Auto-descubrir si está habilitado
                devices = []
                if user_input.get(CONF_AUTO_DISCOVER, False):
                    devices = await self.hass.async_add_executor_job(
                        api.detect_power_meters
                    )
                    _LOGGER.info(f"Auto-discovered {len(devices)} power meter(s)")
                
                # Crear entrada
                return self.async_create_entry(
                    title=f"eWeLink ({user_input[CONF_EMAIL]})",
                    data={
                        **user_input,
                        "devices": devices,
                    },
                )
            else:
                errors["base"] = "invalid_auth"
                _LOGGER.error("Authentication failed - check credentials, region, and country code")

        # Mostrar formulario
        country_options = [
            selector.SelectOptionDict(value=code, label=f"{name} ({code})")
            for code, name in COUNTRY_CODES.items()
        ]
        data_schema = vol.Schema(
            {
                vol.Required(CONF_EMAIL): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Optional(CONF_REGION, default=DEFAULT_REGION): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=REGIONS,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(
                    CONF_COUNTRY_CODE, default=DEFAULT_COUNTRY_CODE
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=country_options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(CONF_AUTO_DISCOVER, default=True): bool,
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): cv.positive_int,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "region_help": "Región del servidor eWeLink (Europa: eu, América: us)",
                "country_help": "Código del país donde registraste tu cuenta eWeLink",
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return EWeLinkRefreshOptionsFlow(config_entry)


class EWeLinkRefreshOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for eWeLink Refresh."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.data.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): cv.positive_int,
                }
            ),
        )
