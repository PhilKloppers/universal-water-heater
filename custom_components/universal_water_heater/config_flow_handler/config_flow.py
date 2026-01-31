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
    get_options_advanced_schema,
    get_options_battery_schema,
    get_options_optional_schema,
    get_options_required_schema,
    get_options_schema,
    get_options_solar_control_schema,
    get_options_time_based_schema,
    get_reconfigure_schema,
    get_user_schema,
)
from custom_components.universal_water_heater.config_flow_handler.validators import validate_device_name
from custom_components.universal_water_heater.config_flow_handler.validators.time_range import (
    validate_time_ranges_no_overlap,
)
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
        self.entity_options: dict[str, Any] = {}

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
        Handle required entity configuration after initial device setup (step 1 of 3).

        This step collects the required entity sources:
        - Temperature source entity
        - Switch source entity

        Args:
            user_input: The user input from the form, or None for initial display.

        Returns:
            The config flow result, either showing a form or proceeding to next step.

        """
        if user_input is not None:
            # Store required entity options and proceed to advanced settings
            self.entity_options.update(user_input)
            return await self.async_step_configure_advanced()

        # Show options form for required entity configuration
        return self.async_show_form(
            step_id="configure_entities",
            data_schema=get_options_required_schema({}),
            description_placeholders={"device_name": self.device_name or ""},
        )

    async def async_step_configure_advanced(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Handle advanced settings during initial setup (step 2 of 5).

        This step collects advanced configuration:
        - Enable debugging
        - Custom icon
        - Battery-aware mode toggle
        - Solar control toggle (for optimized mode)

        Args:
            user_input: The user input from the form, or None for initial display.

        Returns:
            The config flow result, either showing a form or proceeding to next step.

        """
        if user_input is not None:
            # Store advanced options
            self.entity_options.update(user_input)

            # Check if battery-aware is enabled
            if user_input.get("battery_aware", False):
                return await self.async_step_configure_battery()

            # Otherwise route to time-based or solar control configuration
            if user_input.get("use_solar_control", False):
                return await self.async_step_configure_solar()
            return await self.async_step_configure_time_based()

        return self.async_show_form(
            step_id="configure_advanced",
            data_schema=get_options_advanced_schema({}),
            description_placeholders={"device_name": self.device_name or ""},
        )

    async def async_step_configure_optional(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Handle optional sensor configuration during initial setup (step 4 of 4).

        This step collects optional sensor entity sources:
        - Power source entity
        - Voltage source entity
        - Current source entity

        Args:
            user_input: The user input from the form, or None for initial display.

        Returns:
            The config flow result, either showing a form or creating the entry.

        """
        device_name = self.device_name or ""

        if user_input is not None:
            # Merge all collected entity options
            self.entity_options.update(user_input)

            # Pass all values as-is, including empty strings for optional fields.
            # The sensor platform will skip entity creation for any empty/falsy values.
            return self.async_create_entry(
                title=device_name,
                data={
                    CONF_NAME: device_name,
                    CONF_TEMPERATURES: self.temperature_settings,
                },
                options=self.entity_options,
            )

        return self.async_show_form(
            step_id="configure_optional",
            data_schema=get_options_optional_schema({}),
            description_placeholders={"device_name": device_name},
        )

    async def async_step_configure_time_based(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Handle time-based control configuration during initial setup (step 4 of 5).

        This step collects time-based control settings:
        - Normal mode start time
        - Normal mode end time
        - Eco mode start time
        - Eco mode end time

        Args:
            user_input: The user input from the form, or None for initial display.

        Returns:
            The config flow result, either showing a form or proceeding to next step.

        """
        errors = {}

        if user_input is not None:
            # Validate that time ranges don't overlap
            normal_start = user_input.get("normal_mode_start")
            normal_end = user_input.get("normal_mode_end")
            eco_start = user_input.get("eco_mode_start")
            eco_end = user_input.get("eco_mode_end")

            if all([normal_start, normal_end, eco_start, eco_end]):
                if not validate_time_ranges_no_overlap(
                    str(normal_start), str(normal_end), str(eco_start), str(eco_end)
                ):
                    errors["base"] = "time_ranges_overlap"

            if not errors:
                # Store time-based options and proceed to optional sensors
                self.entity_options.update(user_input)
                return await self.async_step_configure_optional()

        return self.async_show_form(
            step_id="configure_time_based",
            data_schema=get_options_time_based_schema({}),
            description_placeholders={"device_name": self.device_name or ""},
            errors=errors,
        )

    async def async_step_configure_solar(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Handle solar control configuration during initial setup (step 4 of 5).

        This step collects solar control settings:
        - Sun entity selector
        - Sun angle above horizon

        Args:
            user_input: The user input from the form, or None for initial display.

        Returns:
            The config flow result, either showing a form or proceeding to next step.

        """
        if user_input is not None:
            # Store solar control options and proceed to optional sensors
            self.entity_options.update(user_input)
            return await self.async_step_configure_optional()

        return self.async_show_form(
            step_id="configure_solar",
            data_schema=get_options_solar_control_schema({}),
            description_placeholders={"device_name": self.device_name or ""},
        )

    async def async_step_configure_battery(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Handle battery configuration during initial setup (step 3 of 5).

        This step collects battery-aware configuration:
        - Battery threshold percentage (stop heating below this)
        - Battery resume threshold (resume heating above this)
        - Battery SoC sensor entity

        Args:
            user_input: The user input from the options form, or None for initial display.

        Returns:
            The config flow result, either showing a form or proceeding to next step.

        """
        errors = {}

        if user_input is not None:
            # Validate that resume threshold is higher than stop threshold
            battery_threshold = user_input.get("battery_threshold", 20)
            battery_resume_threshold = user_input.get("battery_resume_threshold", 35)

            if battery_resume_threshold <= battery_threshold:
                errors["battery_resume_threshold"] = "resume_threshold_too_low"

            if not errors:
                # Store battery options
                self.entity_options.update(user_input)

                # Route to time-based or solar control configuration
                if self.entity_options.get("use_solar_control", False):
                    return await self.async_step_configure_solar()
                return await self.async_step_configure_time_based()

        return self.async_show_form(
            step_id="configure_battery",
            data_schema=get_options_battery_schema({}),
            description_placeholders={"device_name": self.device_name or ""},
            errors=errors,
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
