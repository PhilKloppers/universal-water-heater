"""
Config flow schemas.

Schemas for the main configuration flow steps:
- User setup
- Reconfiguration

When this file grows too large (>300 lines), consider splitting into:
- user.py: User setup schemas
- reconfigure.py: Reconfiguration schemas
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from custom_components.universal_water_heater.const import (
    CONF_ECO_TEMPERATURE,
    CONF_HYSTERESIS,
    CONF_MAX_TEMPERATURE,
    CONF_NORMAL_TEMPERATURE,
    CONF_TEMPERATURES,
    DEFAULT_ECO_TEMPERATURE,
    DEFAULT_HYSTERESIS,
    DEFAULT_MAX_TEMPERATURE,
    DEFAULT_NORMAL_TEMPERATURE,
)
from homeassistant.const import CONF_NAME
from homeassistant.helpers import selector
from homeassistant.helpers.selector import NumberSelectorMode


def _get_temperature_defaults(defaults: Mapping[str, Any]) -> dict[str, float]:
    """Extract temperature defaults from existing data."""

    temperature_defaults = defaults.get(CONF_TEMPERATURES, {}) if isinstance(defaults, Mapping) else {}
    return {
        CONF_NORMAL_TEMPERATURE: float(
            temperature_defaults.get(CONF_NORMAL_TEMPERATURE, DEFAULT_NORMAL_TEMPERATURE),
        ),
        CONF_ECO_TEMPERATURE: float(
            temperature_defaults.get(CONF_ECO_TEMPERATURE, DEFAULT_ECO_TEMPERATURE),
        ),
        CONF_MAX_TEMPERATURE: float(
            temperature_defaults.get(CONF_MAX_TEMPERATURE, DEFAULT_MAX_TEMPERATURE),
        ),
        CONF_HYSTERESIS: float(
            temperature_defaults.get(CONF_HYSTERESIS, DEFAULT_HYSTERESIS),
        ),
    }


def get_user_schema(defaults: Mapping[str, Any] | None = None) -> vol.Schema:
    """
    Get schema for user step (initial setup).

    Args:
        defaults: Optional dictionary of default values to pre-populate the form.

    Returns:
        Voluptuous schema for device name input.

    """
    defaults = defaults or {}
    temperature_defaults = _get_temperature_defaults(defaults)

    return vol.Schema(
        {
            vol.Required(
                CONF_NAME,
                default=defaults.get(CONF_NAME, vol.UNDEFINED),
            ): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.TEXT,
                ),
            ),
            vol.Required(
                CONF_NORMAL_TEMPERATURE,
                default=temperature_defaults[CONF_NORMAL_TEMPERATURE],
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=40,
                    max=80,
                    step=1,
                    unit_of_measurement="°C",
                    mode=NumberSelectorMode.SLIDER,
                ),
            ),
            vol.Required(
                CONF_ECO_TEMPERATURE,
                default=temperature_defaults[CONF_ECO_TEMPERATURE],
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=40,
                    max=80,
                    step=1,
                    unit_of_measurement="°C",
                    mode=NumberSelectorMode.SLIDER,
                ),
            ),
            vol.Required(
                CONF_MAX_TEMPERATURE,
                default=temperature_defaults[CONF_MAX_TEMPERATURE],
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=50,
                    max=85,
                    step=1,
                    unit_of_measurement="°C",
                    mode=NumberSelectorMode.SLIDER,
                ),
            ),
            vol.Required(
                CONF_HYSTERESIS,
                default=temperature_defaults[CONF_HYSTERESIS],
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0.1,
                    max=5,
                    step=1,
                    unit_of_measurement="°C",
                    mode=NumberSelectorMode.SLIDER,
                ),
            ),
        },
    )


def get_reconfigure_schema(name: str, defaults: Mapping[str, Any]) -> vol.Schema:
    """
    Get schema for reconfigure step.

    Args:
        name: Current device name to pre-fill in the form.

    Returns:
        Voluptuous schema for reconfiguration.

    """
    temperature_defaults = _get_temperature_defaults(defaults)

    return vol.Schema(
        {
            vol.Required(
                CONF_NAME,
                default=name,
            ): selector.TextSelector(
                selector.TextSelectorConfig(
                    type=selector.TextSelectorType.TEXT,
                ),
            ),
            vol.Required(
                CONF_NORMAL_TEMPERATURE,
                default=temperature_defaults[CONF_NORMAL_TEMPERATURE],
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=40,
                    max=80,
                    step=1,
                    unit_of_measurement="°C",
                    mode=NumberSelectorMode.SLIDER,
                ),
            ),
            vol.Required(
                CONF_ECO_TEMPERATURE,
                default=temperature_defaults[CONF_ECO_TEMPERATURE],
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=40,
                    max=80,
                    step=1,
                    unit_of_measurement="°C",
                    mode=NumberSelectorMode.SLIDER,
                ),
            ),
            vol.Required(
                CONF_MAX_TEMPERATURE,
                default=temperature_defaults[CONF_MAX_TEMPERATURE],
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=50,
                    max=85,
                    step=1,
                    unit_of_measurement="°C",
                    mode=NumberSelectorMode.SLIDER,
                ),
            ),
            vol.Required(
                CONF_HYSTERESIS,
                default=temperature_defaults[CONF_HYSTERESIS],
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0.1,
                    max=5,
                    step=1,
                    unit_of_measurement="°C",
                    mode=NumberSelectorMode.SLIDER,
                ),
            ),
        },
    )


__all__ = [
    "get_reconfigure_schema",
    "get_user_schema",
]
