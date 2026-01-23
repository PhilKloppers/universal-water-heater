"""Diagnostic sensors for universal_water_heater."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.universal_water_heater.entity import UniversalWaterHeaterEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import EntityCategory, UnitOfTime

if TYPE_CHECKING:
    from datetime import datetime

    from custom_components.universal_water_heater.coordinator import UniversalWaterHeaterDataUpdateCoordinator

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="runtime",
        translation_key="runtime",
        icon="mdi:timer-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=0,
        has_entity_name=True,
    ),
)


class UniversalWaterHeaterRuntimeSensor(SensorEntity, UniversalWaterHeaterEntity):
    """Runtime diagnostic sensor class."""

    def __init__(
        self,
        coordinator: UniversalWaterHeaterDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entity_description)

    @property
    def native_value(self) -> int | float | datetime | None:
        """Return the native value of the sensor."""
        if not self.coordinator.last_update_success:
            return None

        user_id = self.coordinator.data.get("userId", 0)

        # Total runtime in hours
        if self.entity_description.key == "runtime":
            return (user_id * 12) % 10000

        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Diagnostic entities should always be available to show status
        return True
