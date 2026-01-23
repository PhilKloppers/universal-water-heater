"""
Config flow for universal_water_heater.

This module implements the main configuration flow including:
- Initial user setup
- Reconfiguration of existing entries

For more information:
https://developers.home-assistant.io/docs/config_entries_config_flow_handler
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from slugify import slugify

from custom_components.universal_water_heater.config_flow_handler.schemas import (
    get_options_schema,
    get_reconfigure_schema,
    get_user_schema,
)
from custom_components.universal_water_heater.config_flow_handler.validators import validate_device_name
from custom_components.universal_water_heater.const import DOMAIN, LOGGER
from homeassistant import config_entries
from homeassistant.const import CONF_NAME

if TYPE_CHECKING:
    from custom_components.universal_water_heater.config_flow_handler.options_flow import (
        UniversalWaterHeaterOptionsFlow,
    )

# Map exception types to error keys for user-facing messages
ERROR_MAP = {
    "ValueError": "invalid_device_name",
}


class UniversalWaterHeaterConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """
    Handle a config flow for universal_water_heater.

    This class manages the configuration flow for the integration, including
    initial setup and reconfiguration.

    Supported flows:
    - user: Initial setup via UI
    - reconfigure: Update existing configuration

    For more details:
    https://developers.home-assistant.io/docs/config_entries_config_flow_handler
    """

    VERSION = 1

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> UniversalWaterHeaterOptionsFlow:
        """
        Get the options flow for this handler.

        Returns:
            The options flow instance for modifying integration options.

        """
        from custom_components.universal_water_heater.config_flow_handler.options_flow import (  # noqa: PLC0415
            UniversalWaterHeaterOptionsFlow,
        )

        return UniversalWaterHeaterOptionsFlow()

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Handle a flow initialized by the user.

        This is the entry point when a user adds the integration from the UI.

        Args:
            user_input: The user input from the config flow form, or None for initial display.

        Returns:
            The config flow result, either showing a form or creating an entry.

        """
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await validate_device_name(
                    self.hass,
                    device_name=user_input[CONF_NAME],
                )
            except Exception as exception:  # noqa: BLE001
                errors["base"] = self._map_exception_to_error(exception)
            else:
                # Set unique ID based on device name
                await self.async_set_unique_id(slugify(user_input[CONF_NAME]))
                self._abort_if_unique_id_configured()

                # Store device name and proceed to options configuration
                self.device_name = user_input[CONF_NAME]
                return await self.async_step_configure_entities()

        return self.async_show_form(
            step_id="user",
            data_schema=get_user_schema(user_input),
            errors=errors,
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Handle reconfiguration of the integration.

        Allows users to update their credentials without removing and re-adding
        the integration.

        Args:
            user_input: The user input from the reconfigure form, or None for initial display.

        Returns:
            The config flow result, either showing a form or updating the entry.

        """
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await validate_device_name(
                    self.hass,
                    device_name=user_input[CONF_NAME],
                )
            except Exception as exception:  # noqa: BLE001
                errors["base"] = self._map_exception_to_error(exception)
            else:
                return self.async_update_reload_and_abort(
                    entry,
                    data=user_input,
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=get_reconfigure_schema(entry.data.get(CONF_NAME, "")),
            errors=errors,
        )

    async def async_step_configure_entities(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Handle entity configuration after initial device setup.

        This step allows users to link source entities for water temperature,
        power consumption, etc. immediately after adding the device.

        Args:
            user_input: The user input from the options form, or None for initial display.

        Returns:
            The config flow result, either showing a form or creating the entry.

        """
        if user_input is not None:
            # User completed entity configuration, create the entry with options
            return self.async_create_entry(
                title=self.device_name,
                data={CONF_NAME: self.device_name},
                options=user_input,
            )

        # Show options form for entity configuration
        return self.async_show_form(
            step_id="configure_entities",
            data_schema=get_options_schema(),
            description_placeholders={"device_name": self.device_name},
        )

    def _map_exception_to_error(self, exception: Exception) -> str:
        """
        Map API exceptions to user-facing error keys.

        Args:
            exception: The exception that was raised.

        Returns:
            The error key for display in the config flow form.

        """
        LOGGER.warning("Error in config flow: %s", exception)
        exception_name = type(exception).__name__
        return ERROR_MAP.get(exception_name, "unknown")


__all__ = ["UniversalWaterHeaterConfigFlowHandler"]
