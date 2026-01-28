"""
Config flow for universal_water_heater.

This module implements the main configuration flow including:
- Initial user setup
- Reconfiguration of existing entries

For more information:
https://developers.home-assistant.io/docs/config_entries_config_flow_handler
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from slugify import slugify

from custom_components.universal_water_heater.config_flow_handler.schemas import (
    get_options_schema,
    get_reconfigure_schema,
    get_user_schema,
)
from custom_components.universal_water_heater.config_flow_handler.validators import validate_device_name
from custom_components.universal_water_heater.const import (
    CONF_ECO_TEMPERATURE,
    CONF_HYSTERESIS,
    CONF_MAX_TEMPERATURE,
    CONF_NORMAL_TEMPERATURE,
    CONF_TEMPERATURES,
    DOMAIN,
    LOGGER,
)
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.helpers import entity_registry as er

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

    def __init__(self) -> None:
        """Initialize flow state."""

        super().__init__()
        self.device_name: str | None = None
        self.temperature_settings: dict[str, float] = {}

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

                # Store device configuration and proceed to entity linking
                self.device_name = user_input[CONF_NAME]
                self.temperature_settings = self._build_temperature_settings(user_input)
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

        Allows users to update their configuration without removing and re-adding
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
                # Store device configuration and proceed to entity reconfiguration
                self.device_name = user_input[CONF_NAME]
                self.temperature_settings = self._build_temperature_settings(user_input)
                return await self.async_step_reconfigure_entities()

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=get_reconfigure_schema(
                entry.data.get(CONF_NAME, ""),
                entry.data,
            ),
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
        device_name = self.device_name or ""

        if user_input is not None:
            # Pass all values as-is, including empty strings for optional fields.
            # The sensor platform will skip entity creation for any empty/falsy values.
            return self.async_create_entry(
                title=device_name,
                data={
                    CONF_NAME: device_name,
                    CONF_TEMPERATURES: self.temperature_settings,
                },
                options=user_input,
            )

        # Show options form for entity configuration
        # Pass empty dict explicitly to avoid any state carryover
        return self.async_show_form(
            step_id="configure_entities",
            data_schema=get_options_schema({}),
            description_placeholders={"device_name": device_name},
        )

    async def async_step_reconfigure_entities(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Handle entity source reconfiguration during reconfigure flow.

        This step allows users to modify entity sources (power, voltage, current)
        during reconfiguration. Unlike initial setup, empty values are preserved
        to allow clearing previously configured options.

        Args:
            user_input: The user input from the options form, or None for initial display.

        Returns:
            The config flow result, either showing a form or updating the entry.

        """
        entry = self._get_reconfigure_entry()
        device_name = self.device_name or ""

        if user_input is not None:
            # Check which optional sensor entities need to be removed
            await self._cleanup_removed_entities(entry, entry.options, user_input)

            # During reconfiguration, preserve empty values so users can clear
            # previously configured entity sources. The sensor platform will
            # skip entity creation for any empty/falsy values.
            updated_data = {
                CONF_NAME: device_name,
                CONF_TEMPERATURES: self.temperature_settings,
            }

            return self.async_update_reload_and_abort(
                entry,
                data=updated_data,
                options=user_input,
            )

        # Show options form for entity reconfiguration
        return self.async_show_form(
            step_id="reconfigure_entities",
            data_schema=get_options_schema(entry.options),
            description_placeholders={"device_name": device_name},
        )

    async def _cleanup_removed_entities(
        self,
        entry: config_entries.ConfigEntry,
        old_options: Mapping[str, Any],
        new_options: Mapping[str, Any],
    ) -> None:
        """Remove entities whose source entity configuration was cleared."""
        entity_registry = er.async_get(self.hass)

        # Map of option keys to their entity key suffixes
        sensor_mappings = {
            "power_source_entity_id": "power_consumption",
            "voltage_source_entity_id": "voltage",
            "current_source_entity_id": "current",
        }

        for option_key, entity_key in sensor_mappings.items():
            # If the option was previously set but is now empty/unset, remove the entity
            if old_options.get(option_key) and not new_options.get(option_key):
                # Get all entities for this config entry
                entities = er.async_entries_for_config_entry(
                    entity_registry,
                    entry.entry_id,
                )

                # Find matching entity by unique_id pattern
                for entity in entities:
                    if entity.unique_id.endswith(entity_key):
                        entity_registry.async_remove(entity.entity_id)

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

    def _build_temperature_settings(self, data: dict[str, Any]) -> dict[str, float]:
        """Extract temperature settings from user input."""

        return {
            CONF_NORMAL_TEMPERATURE: float(data[CONF_NORMAL_TEMPERATURE]),
            CONF_ECO_TEMPERATURE: float(data[CONF_ECO_TEMPERATURE]),
            CONF_MAX_TEMPERATURE: float(data[CONF_MAX_TEMPERATURE]),
            CONF_HYSTERESIS: float(data[CONF_HYSTERESIS]),
        }


__all__ = ["UniversalWaterHeaterConfigFlowHandler"]
