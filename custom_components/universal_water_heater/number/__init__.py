"""Number platform for universal_water_heater."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.universal_water_heater.const import PARALLEL_UPDATES as PARALLEL_UPDATES
from homeassistant.components.number import NumberEntityDescription

from .hysteresis import ENTITY_DESCRIPTIONS as HYSTERESIS_DESCRIPTIONS, UniversalWaterHeaterHysteresisNumber
from .maximum_temperature import (
    ENTITY_DESCRIPTIONS as MAXIMUM_TEMPERATURE_DESCRIPTIONS,
    UniversalWaterHeaterMaximumTemperatureNumber,
)
from .minimum_temperature import (
    ENTITY_DESCRIPTIONS as MINIMUM_TEMPERATURE_DESCRIPTIONS,
    UniversalWaterHeaterMinimumTemperatureNumber,
)
from .target_humidity import ENTITY_DESCRIPTIONS as HUMIDITY_DESCRIPTIONS, UniversalWaterHeaterHumidityNumber
from .target_temperature import (
    ENTITY_DESCRIPTIONS as TARGET_TEMPERATURE_DESCRIPTIONS,
    UniversalWaterHeaterTargetTemperatureNumber,
)

if TYPE_CHECKING:
    from custom_components.universal_water_heater.data import UniversalWaterHeaterConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

# Combine all entity descriptions from different modules
ENTITY_DESCRIPTIONS: tuple[NumberEntityDescription, ...] = (
    *HUMIDITY_DESCRIPTIONS,
    *TARGET_TEMPERATURE_DESCRIPTIONS,
    *MINIMUM_TEMPERATURE_DESCRIPTIONS,
    *MAXIMUM_TEMPERATURE_DESCRIPTIONS,
    *HYSTERESIS_DESCRIPTIONS,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: UniversalWaterHeaterConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    async_add_entities(
        UniversalWaterHeaterHumidityNumber(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in HUMIDITY_DESCRIPTIONS
    )
    async_add_entities(
        UniversalWaterHeaterTargetTemperatureNumber(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in TARGET_TEMPERATURE_DESCRIPTIONS
    )
    async_add_entities(
        UniversalWaterHeaterMinimumTemperatureNumber(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in MINIMUM_TEMPERATURE_DESCRIPTIONS
    )
    async_add_entities(
        UniversalWaterHeaterMaximumTemperatureNumber(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in MAXIMUM_TEMPERATURE_DESCRIPTIONS
    )
    async_add_entities(
        UniversalWaterHeaterHysteresisNumber(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in HYSTERESIS_DESCRIPTIONS
    )
