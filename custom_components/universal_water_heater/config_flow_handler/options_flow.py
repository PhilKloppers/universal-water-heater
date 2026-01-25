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

from custom_components.universal_water_heater.config_flow_handler.schemas import get_options_schema
from homeassistant import config_entries
from homeassistant.helpers import entity_registry as er


class UniversalWaterHeaterOptionsFlow(config_entries.OptionsFlow):
    """
    Handle options flow for the integration.

    This class manages the options that users can modify after initial setup,
    such as update intervals and debug settings.

    The options flow always starts with async_step_init and provides a single
    form for all configurable options.

    For more information:
    https://developers.home-assistant.io/docs/config_entries_options_flow_handler
    """

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """
        Manage the options for the integration.

        This is the entry point for the options flow, allowing users to
        configure advanced settings like update interval and debugging.

        Args:
            user_input: The user input from the options form, or None for initial display.

        Returns:
            The config flow result, either showing a form or creating an options entry.

        """
        if user_input is not None:
            # Check which optional sensor entities need to be removed
            old_options = self.config_entry.options
            await self._cleanup_removed_entities(old_options, user_input)

            # Update config entry options with all values (including empty strings)
            # so users can clear previously configured entity sources.
            # Empty strings are falsy, so the sensor platform will skip entity creation.
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                options=user_input,
            )
            # Reload the integration to apply the updated options
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_abort(reason="reconfigure_successful")

        return self.async_show_form(
            step_id="init",
            data_schema=get_options_schema(self.config_entry.options),
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
