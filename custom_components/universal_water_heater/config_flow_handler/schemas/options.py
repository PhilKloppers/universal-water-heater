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

from custom_components.universal_water_heater.const import (
    DEFAULT_BATTERY_AWARE,
    DEFAULT_BATTERY_RESUME_THRESHOLD,
    DEFAULT_BATTERY_THRESHOLD,
    DEFAULT_ENABLE_DEBUGGING,
    DEFAULT_SUN_ANGLE,
    DEFAULT_USE_SOLAR_CONTROL,
)
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

    Collects advanced configuration settings like debugging, custom icons,
    and battery-aware features.

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
            vol.Optional(
                "battery_aware",
                default=defaults.get("battery_aware", DEFAULT_BATTERY_AWARE),
            ): selector.BooleanSelector(),
            vol.Optional(
                "use_solar_control",
                default=defaults.get("use_solar_control", DEFAULT_USE_SOLAR_CONTROL),
            ): selector.BooleanSelector(),
        }
    )


def get_options_battery_schema(defaults: Mapping[str, Any] | None = None) -> vol.Schema:
    """
    Get schema for battery-aware options (step 2b of 3).

    This schema is shown when battery_aware is enabled and collects:
    - Battery threshold percentage
    - Battery SoC entity selector

    Args:
        defaults: Optional dictionary of current option values.

    Returns:
        Voluptuous schema for battery configuration.

    """
    defaults = defaults or {}

    return vol.Schema(
        {
            vol.Optional(
                "battery_threshold",
                default=defaults.get("battery_threshold", DEFAULT_BATTERY_THRESHOLD),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=5,
                    max=95,
                    step=1,
                    unit_of_measurement="%",
                    mode=selector.NumberSelectorMode.SLIDER,
                ),
            ),
            vol.Optional(
                "battery_resume_threshold",
                default=defaults.get("battery_resume_threshold", DEFAULT_BATTERY_RESUME_THRESHOLD),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=10,
                    max=100,
                    step=1,
                    unit_of_measurement="%",
                    mode=selector.NumberSelectorMode.SLIDER,
                ),
            ),
            vol.Optional(
                "battery_soc_entity_id",
                default=defaults.get("battery_soc_entity_id"),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain=["sensor"],
                    device_class=["battery"],
                ),
            ),
        }
    )


def get_options_time_based_schema(defaults: Mapping[str, Any] | None = None) -> vol.Schema:
    """
    Get schema for time-based optimized mode configuration.

    This schema is shown when use_solar_control is disabled (default) and collects:
    - Normal mode start time
    - Normal mode end time
    - Eco mode start time
    - Eco mode end time

    Args:
        defaults: Optional dictionary of current option values.

    Returns:
        Voluptuous schema for time-based control configuration.

    """
    defaults = defaults or {}

    return vol.Schema(
        {
            vol.Optional(
                "normal_mode_start",
                default=defaults.get("normal_mode_start"),
            ): selector.TimeSelector(),
            vol.Optional(
                "normal_mode_end",
                default=defaults.get("normal_mode_end"),
            ): selector.TimeSelector(),
            vol.Optional(
                "eco_mode_start",
                default=defaults.get("eco_mode_start"),
            ): selector.TimeSelector(),
            vol.Optional(
                "eco_mode_end",
                default=defaults.get("eco_mode_end"),
            ): selector.TimeSelector(),
        }
    )


def get_options_solar_control_schema(defaults: Mapping[str, Any] | None = None) -> vol.Schema:
    """
    Get schema for solar-based optimized mode configuration.

    This schema is shown when use_solar_control is enabled and collects:
    - Sun entity selector
    - Sun angle above horizon (0-80 degrees)

    Args:
        defaults: Optional dictionary of current option values.

    Returns:
        Voluptuous schema for solar control configuration.

    """
    defaults = defaults or {}

    return vol.Schema(
        {
            vol.Optional(
                "sun_entity_id",
                default=defaults.get("sun_entity_id"),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(
                    domain=["sun"],
                ),
            ),
            vol.Optional(
                "sun_angle",
                default=defaults.get("sun_angle", DEFAULT_SUN_ANGLE),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=80,
                    step=1,
                    unit_of_measurement="°",
                    mode=selector.NumberSelectorMode.SLIDER,
                ),
            ),
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
    "get_options_battery_schema",
    "get_options_optional_schema",
    "get_options_required_schema",
    "get_options_schema",
    "get_options_solar_control_schema",
    "get_options_time_based_schema",
]
