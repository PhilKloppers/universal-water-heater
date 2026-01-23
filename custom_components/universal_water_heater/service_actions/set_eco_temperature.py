"""Set eco temperature service action handler for universal_water_heater."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.universal_water_heater.const import LOGGER

if TYPE_CHECKING:
    from custom_components.universal_water_heater.data import UniversalWaterHeaterConfigEntry
    from homeassistant.core import HomeAssistant, ServiceCall


async def async_set_eco_temperature(
    hass: HomeAssistant,
    entry: UniversalWaterHeaterConfigEntry,
    call: ServiceCall,
) -> None:
    """
    Handle the set_eco_temperature service call.

    Args:
        hass: Home Assistant instance
        entry: Config entry for the integration
        call: Service call data containing the eco temperature
    """
    temperature = call.data.get("temperature")

    if temperature is None:
        LOGGER.error("set_eco_temperature service called without temperature parameter")
        return

    try:
        # Get the maximum and normal temperature entities to validate bounds
        entry_id = entry.entry_id
        max_entity_id = f"number.{entry_id}_max_temperature"
        normal_entity_id = f"number.{entry_id}_normal_temperature"
        eco_entity_id = f"number.{entry_id}_eco_temperature"

        # Get current values from the maximum and normal temperature entities
        max_state = hass.states.get(max_entity_id)
        normal_state = hass.states.get(normal_entity_id)

        # Get the numeric values from the states
        max_temp = float(max_state.state) if max_state and max_state.state not in ("unknown", "unavailable") else 80
        normal_temp = (
            float(normal_state.state) if normal_state and normal_state.state not in ("unknown", "unavailable") else 65
        )

        # Validate temperature is within bounds (40 to max_temperature)
        min_temp = 40
        if not min_temp <= temperature <= max_temp:
            LOGGER.error(
                "Eco temperature %s°C is outside valid range [%s°C, %s°C]",
                temperature,
                min_temp,
                max_temp,
            )
            return

        # Validate eco temperature is not more than normal temperature
        if temperature > normal_temp:
            LOGGER.error(
                "Eco temperature %s°C cannot exceed normal temperature %s°C",
                temperature,
                normal_temp,
            )
            return

        # Call the service to set the eco temperature
        await hass.services.async_call(
            "number",
            "set_value",
            {
                "entity_id": eco_entity_id,
                "value": temperature,
            },
        )

        LOGGER.debug("Eco temperature set to %s°C via service call", temperature)

    except (ValueError, Exception) as exception:  # noqa: BLE001
        LOGGER.exception("Failed to set eco temperature via service call: %s", exception)
