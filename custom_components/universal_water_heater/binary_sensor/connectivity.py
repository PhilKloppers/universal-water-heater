"""Connectivity binary sensor for universal_water_heater."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.universal_water_heater.entity import UniversalWaterHeaterEntity
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory

if TYPE_CHECKING:
    from custom_components.universal_water_heater.coordinator import UniversalWaterHeaterDataUpdateCoordinator

ENTITY_DESCRIPTIONS = (
    BinarySensorEntityDescription(
        key="api_connectivity",
        translation_key="api_connectivity",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:api",
        has_entity_name=True,
    ),
)


class UniversalWaterHeaterConnectivitySensor(BinarySensorEntity, UniversalWaterHeaterEntity):
    """Connectivity sensor for universal_water_heater."""

    def __init__(
        self,
        coordinator: UniversalWaterHeaterDataUpdateCoordinator,
        entity_description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entity_description)

    @property
    def is_on(self) -> bool:
        """Return true if the API connection is established."""
        # Connection is considered established if coordinator has valid data
        return self.coordinator.last_update_success

    @property
    def extra_state_attributes(self) -> dict[str, str | None]:
        """Return additional state attributes."""
        return {
            "update_interval": str(self.coordinator.update_interval),
            "api_endpoint": "JSONPlaceholder (Demo)",
        }
