"""Sensor platform for universal_water_heater."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.universal_water_heater.const import PARALLEL_UPDATES as PARALLEL_UPDATES
from homeassistant.components.sensor import SensorEntityDescription

from .current import ENTITY_DESCRIPTIONS as CURRENT_DESCRIPTIONS, UniversalWaterHeaterCurrentSensor
from .power import ENTITY_DESCRIPTIONS as POWER_DESCRIPTIONS, UniversalWaterHeaterPowerSensor
from .status import ENTITY_DESCRIPTIONS as STATUS_DESCRIPTIONS, UniversalWaterHeaterStatusSensor
from .temperature import ENTITY_DESCRIPTIONS as TEMPERATURE_DESCRIPTIONS, UniversalWaterHeaterTemperatureSensor
from .voltage import ENTITY_DESCRIPTIONS as VOLTAGE_DESCRIPTIONS, UniversalWaterHeaterVoltageSensor

if TYPE_CHECKING:
    from custom_components.universal_water_heater.data import UniversalWaterHeaterConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

# Combine all entity descriptions from different modules
ENTITY_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    *CURRENT_DESCRIPTIONS,
    *POWER_DESCRIPTIONS,
    *TEMPERATURE_DESCRIPTIONS,
    *VOLTAGE_DESCRIPTIONS,
    *STATUS_DESCRIPTIONS,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: UniversalWaterHeaterConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    # Conditionally add current sensors if configured
    if entry.options.get("current_source_entity_id"):
        async_add_entities(
            UniversalWaterHeaterCurrentSensor(
                coordinator=entry.runtime_data.coordinator,
                entity_description=entity_description,
            )
            for entity_description in CURRENT_DESCRIPTIONS
        )
    # Conditionally add power sensors if configured
    if entry.options.get("power_source_entity_id"):
        async_add_entities(
            UniversalWaterHeaterPowerSensor(
                coordinator=entry.runtime_data.coordinator,
                entity_description=entity_description,
            )
            for entity_description in POWER_DESCRIPTIONS
        )
    # Always add temperature sensors (required)
    async_add_entities(
        UniversalWaterHeaterTemperatureSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in TEMPERATURE_DESCRIPTIONS
    )
    # Conditionally add voltage sensors if configured
    if entry.options.get("voltage_source_entity_id"):
        async_add_entities(
            UniversalWaterHeaterVoltageSensor(
                coordinator=entry.runtime_data.coordinator,
                entity_description=entity_description,
            )
            for entity_description in VOLTAGE_DESCRIPTIONS
        )
    # Always add status sensor
    async_add_entities(
        UniversalWaterHeaterStatusSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in STATUS_DESCRIPTIONS
    )
