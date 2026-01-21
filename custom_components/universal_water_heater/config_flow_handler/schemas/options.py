"""
Options flow schemas.

Schemas for the options flow that allows users to modify settings
after initial configuration.

When adding many options, consider grouping them:
- basic_options.py: Common settings (update interval, debug mode)
- advanced_options.py: Advanced settings
- device_options.py: Device-specific settings
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from custom_components.universal_water_heater.const import DEFAULT_ENABLE_DEBUGGING, DEFAULT_UPDATE_INTERVAL_HOURS
from homeassistant.helpers import selector


def get_options_schema(defaults: Mapping[str, Any] | None = None) -> vol.Schema:
    """
    Get schema for options flow.

    Args:
        defaults: Optional dictionary of current option values.

    Returns:
        Voluptuous schema for options configuration.

    """
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Optional(
                "update_interval_hours",
                default=defaults.get("update_interval_hours", DEFAULT_UPDATE_INTERVAL_HOURS),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0.25,
                    max=24,
                    step=0.25,
                    unit_of_measurement="h",
                    mode=selector.NumberSelectorMode.BOX,
                ),
            ),
            vol.Optional(
                "enable_debugging",
                default=defaults.get("enable_debugging", DEFAULT_ENABLE_DEBUGGING),
            ): selector.BooleanSelector(),
            vol.Optional(
                "custom_icon",
                default=defaults.get("custom_icon"),
            ): selector.IconSelector(),
            vol.Optional(
                "current_source_entity_id",
                default=defaults.get("current_source_entity_id"),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain=["sensor"],
                ),
            ),
            vol.Optional(
                "temperature_source_entity_id",
                default=defaults.get("temperature_source_entity_id"),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain=["sensor", "binary_sensor", "weather"],
                ),
            ),
            vol.Optional(
                "power_source_entity_id",
                default=defaults.get("power_source_entity_id"),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain=["sensor"],
                ),
            ),
            vol.Optional(
                "voltage_source_entity_id",
                default=defaults.get("voltage_source_entity_id"),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain=["sensor"],
                ),
            ),
            vol.Optional(
                "switch_source_entity_id",
                default=defaults.get("switch_source_entity_id"),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain=["switch"],
                ),
            ),
        },
    )


__all__ = [
    "get_options_schema",
]
