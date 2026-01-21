"""Custom types for universal_water_heater."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import UniversalWaterHeaterApiClient
    from .coordinator import UniversalWaterHeaterDataUpdateCoordinator


type UniversalWaterHeaterConfigEntry = ConfigEntry[UniversalWaterHeaterData]


@dataclass
class UniversalWaterHeaterData:
    """Data for universal_water_heater."""

    client: UniversalWaterHeaterApiClient
    coordinator: UniversalWaterHeaterDataUpdateCoordinator
    integration: Integration
