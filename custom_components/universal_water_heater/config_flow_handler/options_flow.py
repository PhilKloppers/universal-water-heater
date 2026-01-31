"""
Options flow for universal_water_heater.

This module implements the options flow that allows users to modify settings
after the initial configuration, such as update intervals and debug settings.

For more information:
https://developers.home-assistant.io/docs/config_entries_options_flow_handler
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from custom_components.universal_water_heater.config_flow_handler.schemas import (
    get_options_advanced_schema,
    get_options_battery_schema,
    get_options_optional_schema,
    get_options_required_schema,
    get_options_solar_control_schema,
    get_options_time_based_schema,
)
from custom_components.universal_water_heater.config_flow_handler.validators import validate_time_ranges_no_overlap
from homeassistant import config_entries
from homeassistant.helpers import entity_registry as er


class UniversalWaterHeaterOptionsFlow(config_entries.OptionsFlow):
    """
    Handle options flow for the integration.

    This class manages the options that users can modify after initial setup,
    using a multi-step flow to organize required, advanced, and optional settings.

    Flow steps:
    1. init: Required options (temperature source, switch source)
    2. advanced: Advanced options (debugging, custom icon, battery-aware)
    3. battery: Battery configuration (shown only if battery-aware is enabled)
    4. optional: Optional sensors (power, voltage, current)

    For more information:
    https://developers.home-assistant.io/docs/config_entries_options_flow_handler
    """

    def __init__(self) -> None:
        """Initialize the options flow."""
        super().__init__()
        self._options: dict[str, Any] = {}

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Handle required options (step 1 of 3).

        This step collects the required entity sources:
        - Temperature source entity
        - Switch source entity

        Args:
            user_input: The user input from the options form, or None for initial display.

        Returns:
            The config flow result, either showing a form or proceeding to next step.

        """
        if user_input is not None:
            # Store required options and proceed to advanced options
            self._options.update(user_input)
            return await self.async_step_advanced()

        return self.async_show_form(
            step_id="init",
            data_schema=get_options_required_schema(self.config_entry.options),
        )

    async def async_step_advanced(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Handle advanced options (step 2 of 5 or 4).

        This step collects advanced configuration:
        - Enable debugging
        - Custom icon
        - Battery-aware option
        - Solar control toggle (for optimized mode)

        Args:
            user_input: The user input from the options form, or None for initial display.

        Returns:
            The config flow result, either showing a form or proceeding to next step.

        """
        if user_input is not None:
            # Store advanced options
            self._options.update(user_input)

            # If battery-aware is enabled, proceed to battery configuration
            if user_input.get("battery_aware", False):
                return await self.async_step_battery()

            # Otherwise route to time-based or solar control configuration
            if user_input.get("use_solar_control", False):
                return await self.async_step_solar()
            return await self.async_step_time_based()

        return self.async_show_form(
            step_id="advanced",
            data_schema=get_options_advanced_schema(self.config_entry.options),
        )

    async def async_step_battery(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Handle battery configuration (step 3 of 4).

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
                self._options.update(user_input)

                # Route to time-based or solar control configuration
                if self._options.get("use_solar_control", False):
                    return await self.async_step_solar()
                return await self.async_step_time_based()

        return self.async_show_form(
            step_id="battery",
            data_schema=get_options_battery_schema(self.config_entry.options),
            errors=errors,
        )

    async def async_step_time_based(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Handle time-based control configuration during options flow (step 4 of 5).

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
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate time ranges don't overlap
            if not validate_time_ranges_no_overlap(
                str(user_input["normal_mode_start"]),
                str(user_input["normal_mode_end"]),
                str(user_input["eco_mode_start"]),
                str(user_input["eco_mode_end"]),
            ):
                errors["base"] = "time_ranges_overlap"
            else:
                # Store time-based options and proceed to optional sensors
                self._options.update(user_input)
                return await self.async_step_optional()

        return self.async_show_form(
            step_id="time_based",
            data_schema=get_options_time_based_schema(self.config_entry.options),
            errors=errors,
        )

    async def async_step_solar(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Handle solar control configuration during options flow (step 4 of 5).

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
            self._options.update(user_input)
            return await self.async_step_optional()

        return self.async_show_form(
            step_id="solar",
            data_schema=get_options_solar_control_schema(self.config_entry.options),
        )

    async def async_step_optional(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Handle optional sensors (step 4 of 4, or step 3 if battery step skipped).

        This step collects optional sensor entity sources:
        - Power source entity
        - Voltage source entity
        - Current source entity

        Args:
            user_input: The user input from the options form, or None for initial display.

        Returns:
            The config flow result, either showing a form or completing the flow.

        """
        if user_input is not None:
            # Merge all collected options
            self._options.update(user_input)

            # Check which optional sensor entities need to be removed
            old_options = self.config_entry.options
            await self._cleanup_removed_entities(old_options, self._options)

            # Update config entry options with all values (including empty strings)
            # so users can clear previously configured entity sources.
            # Empty strings are falsy, so the sensor platform will skip entity creation.
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                options=self._options,
            )
            # Reload the integration to apply the updated options
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_abort(reason="reconfigure_successful")

        return self.async_show_form(
            step_id="optional",
            data_schema=get_options_optional_schema(self.config_entry.options),
        )

    async def _cleanup_removed_entities(
        self,
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
                    self.config_entry.entry_id,
                )

                # Find matching entity by unique_id pattern
                for entity in entities:
                    if entity.unique_id.endswith(entity_key):
                        entity_registry.async_remove(entity.entity_id)


__all__ = ["UniversalWaterHeaterOptionsFlow"]
