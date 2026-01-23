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
        # Get the maximum temperature entity to validate bounds
        entry_id = entry.entry_id
        max_entity_id = f"number.{entry_id}_max_temperature"
        target_entity_id = f"number.{entry_id}_normal_temperature"

        # Get current value from the maximum temperature entity
        max_state = hass.states.get(max_entity_id)

        # Get the numeric value from the state
        max_temp = float(max_state.state) if max_state and max_state.state not in ("unknown", "unavailable") else 80

        # Validate temperature is within bounds (40 to max_temperature)
        min_temp = 40
        if not min_temp <= temperature <= max_temp:
            LOGGER.error(
                "Normal temperature %s°C is outside valid range [%s°C, %s°C]",
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
