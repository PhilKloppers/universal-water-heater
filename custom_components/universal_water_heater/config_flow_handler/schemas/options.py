"""
Options flow schemas.

Schemas for the multi-step options flow that allows users to modify settings
after initial configuration.

The flow is organized into three steps:
1. Required options (temperature source, switch source)
2. Advanced options (debugging, custom icon)
3. Optional sensors (power, voltage, current)
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from custom_components.universal_water_heater.const import DEFAULT_ENABLE_DEBUGGING
from homeassistant.helpers import selector


def get_options_required_schema(defaults: Mapping[str, Any] | None = None) -> vol.Schema:
    """
    Get schema for required options (step 1 of 3).

    Collects the required entity sources that must be configured.

    Args:
        defaults: Optional dictionary of current option values.

    Returns:
        Voluptuous schema for required options configuration.

    """
    defaults = defaults or {}

    return vol.Schema(
        {
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
        }
    )


def get_options_advanced_schema(defaults: Mapping[str, Any] | None = None) -> vol.Schema:
    """
    Get schema for advanced options (step 2 of 3).

    Collects advanced configuration settings like debugging and custom icons.

    Args:
        defaults: Optional dictionary of current option values.

    Returns:
        Voluptuous schema for advanced options configuration.

    """
    defaults = defaults or {}

    return vol.Schema(
        {
            vol.Optional(
                "enable_debugging",
                default=defaults.get("enable_debugging", DEFAULT_ENABLE_DEBUGGING),
            ): selector.BooleanSelector(),
            vol.Optional(
                "custom_icon",
                default=defaults.get("custom_icon", ""),
            ): selector.IconSelector(),
        }
    )


def get_options_optional_schema(defaults: Mapping[str, Any] | None = None) -> vol.Schema:
    """
    Get schema for optional sensor sources (step 3 of 3).

    Collects optional sensor entity sources. Uses suggested_value to show
    current value but allows clearing by leaving the field empty.

    Args:
        defaults: Optional dictionary of current option values.

    Returns:
        Voluptuous schema for optional sensor configuration.

    """
    defaults = defaults or {}

    schema_dict = {}

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


# Legacy function for backward compatibility (used in config_flow.py)
def get_options_schema(defaults: Mapping[str, Any] | None = None) -> vol.Schema:
    """
    Get combined schema for single-step options flow (legacy).

    This function combines all option schemas into a single form.
    Used by config_flow.py for entity configuration during initial setup.

    Args:
        defaults: Optional dictionary of current option values.

    Returns:
        Voluptuous schema for all options configuration.

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
    "get_options_advanced_schema",
    "get_options_optional_schema",
    "get_options_required_schema",
    "get_options_schema",
]
