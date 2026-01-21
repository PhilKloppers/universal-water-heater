"""Select platform for universal_water_heater."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.universal_water_heater.const import PARALLEL_UPDATES as PARALLEL_UPDATES
from homeassistant.components.select import SelectEntityDescription

from .mode import ENTITY_DESCRIPTIONS as MODE_DESCRIPTIONS, UniversalWaterHeaterModeSelect

if TYPE_CHECKING:
    from custom_components.universal_water_heater.data import UniversalWaterHeaterConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

# Combine all entity descriptions from different modules
ENTITY_DESCRIPTIONS: tuple[SelectEntityDescription, ...] = (*MODE_DESCRIPTIONS,)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: UniversalWaterHeaterConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the select platform."""
    async_add_entities(
        UniversalWaterHeaterModeSelect(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in MODE_DESCRIPTIONS
    )
