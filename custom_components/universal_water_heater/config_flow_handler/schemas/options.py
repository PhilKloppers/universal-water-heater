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

from custom_components.universal_water_heater.const import DEFAULT_ENABLE_DEBUGGING
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

    # Build schema dynamically to handle optional fields correctly
    schema_dict = {
        vol.Required(
            "temperature_source_entity_id",
            default=defaults.get("temperature_source_entity_id"),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(
                domain=["sensor"],
            ),
        ),
        vol.Required(
            "switch_source_entity_id",
            default=defaults.get("switch_source_entity_id"),
        ): selector.EntitySelector(
            selector.EntitySelectorConfig(
                domain=["switch"],
            ),
        ),
        vol.Optional(
            "enable_debugging",
            default=defaults.get("enable_debugging", DEFAULT_ENABLE_DEBUGGING),
        ): selector.BooleanSelector(),
        vol.Optional(
            "custom_icon",
            default=defaults.get("custom_icon", ""),
        ): selector.IconSelector(),
    }

    # Add optional sensor fields without defaults to allow clearing
    # Use suggested_value to show current value but allow clearing
    for field in ["power_source_entity_id", "voltage_source_entity_id", "current_source_entity_id"]:
        schema_dict[vol.Optional(field, description={"suggested_value": defaults.get(field, "")})] = (
            selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain=["sensor"],
                    multiple=False,
                ),
            )
        )

    return vol.Schema(schema_dict)


__all__ = [
    "get_options_schema",
]
