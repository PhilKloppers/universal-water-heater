"""Service action for evaluating and controlling the heater."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.universal_water_heater.const import LOGGER

if TYPE_CHECKING:
    from custom_components.universal_water_heater.data import UniversalWaterHeaterConfigEntry
    from homeassistant.core import HomeAssistant, ServiceCall


async def async_evaluate_control_logic(
    hass: HomeAssistant,
    config_entry: UniversalWaterHeaterConfigEntry,
    call: ServiceCall,
) -> None:
    """
    Evaluate control logic and control heater as needed.

    This service action implements the main control logic for the water heater,
    reading the current temperature and mode, then controlling the heater relay
    based on the configured temperature thresholds and hysteresis values.

    Args:
        hass: Home Assistant instance
        config_entry: Configuration entry for this integration
        call: The service call data (not used for this service)

    """
    # Import here to avoid circular imports during startup
    from custom_components.universal_water_heater.utils.control_logic import (  # noqa: PLC0415
        async_evaluate_and_control_heater,
    )

    try:
        await async_evaluate_and_control_heater(hass, config_entry)
        LOGGER.debug("Control logic evaluation completed successfully")
    except Exception:  # noqa: BLE001
        LOGGER.exception("Failed to evaluate control logic")
        # Don't re-raise to prevent service call failures from breaking HA
