"""Set target temperature service action handler for universal_water_heater."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.universal_water_heater.const import LOGGER

if TYPE_CHECKING:
    from custom_components.universal_water_heater.data import UniversalWaterHeaterConfigEntry
    from homeassistant.core import HomeAssistant, ServiceCall


async def async_set_target_temperature(
    hass: HomeAssistant,
    entry: UniversalWaterHeaterConfigEntry,
    call: ServiceCall,
) -> None:
    """
    Handle the set_target_temperature service call.

    Args:
        hass: Home Assistant instance
        entry: Config entry for the integration
        call: Service call data containing the target temperature
    """
    temperature = call.data.get("temperature")

    if temperature is None:
        LOGGER.error("set_target_temperature service called without temperature parameter")
        return

    try:
        # Get the minimum and maximum temperature entities to validate bounds
        entry_id = entry.entry_id
        min_entity_id = f"number.{entry_id}_minimum_temperature"
        max_entity_id = f"number.{entry_id}_maximum_temperature"
        target_entity_id = f"number.{entry_id}_target_temperature"

        # Get current values from the number entities
        min_state = hass.states.get(min_entity_id)
        max_state = hass.states.get(max_entity_id)

        # Get the numeric values from the states
        min_temp = float(min_state.state) if min_state and min_state.state not in ("unknown", "unavailable") else 20
        max_temp = float(max_state.state) if max_state and max_state.state not in ("unknown", "unavailable") else 80

        # Validate temperature is within bounds
        if not min_temp <= temperature <= max_temp:
            LOGGER.error(
                "Target temperature %s°C is outside valid range [%s°C, %s°C]",
                temperature,
                min_temp,
                max_temp,
            )
            return

        # Call the service to set the target temperature
        await hass.services.async_call(
            "number",
            "set_value",
            {
                "entity_id": target_entity_id,
                "value": temperature,
            },
        )

        LOGGER.debug("Target temperature set to %s°C via service call", temperature)

    except (ValueError, Exception) as exception:  # noqa: BLE001
        LOGGER.exception("Failed to set target temperature via service call: %s", exception)
