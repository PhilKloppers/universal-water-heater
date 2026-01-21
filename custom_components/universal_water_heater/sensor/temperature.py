"""Temperature sensor that reads from another entity for universal_water_heater."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.universal_water_heater.entity import UniversalWaterHeaterEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import UnitOfTemperature

if TYPE_CHECKING:
    from custom_components.universal_water_heater.coordinator import UniversalWaterHeaterDataUpdateCoordinator


ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="water_temperature",
        translation_key="water_temperature",
        icon="mdi:thermometer",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        has_entity_name=True,
    ),
)


class UniversalWaterHeaterTemperatureSensor(SensorEntity, UniversalWaterHeaterEntity):
    """Temperature sensor that reads from another entity."""

    def __init__(
        self,
        coordinator: UniversalWaterHeaterDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entity_description)

    @property
    def native_value(self) -> float | None:
        """Return the native value of the sensor."""
        if not self.coordinator.last_update_success:
            return None

        # Get the source entity ID from config entry options
        source_entity_id = self.coordinator.config_entry.options.get("temperature_source_entity_id")
        if not source_entity_id:
            return None

        # Get the state of the source entity
        source_state = self.hass.states.get(source_entity_id)
        if source_state is None or source_state.state in ("unknown", "unavailable"):
            return None

        try:
            return float(source_state.state)
        except (ValueError, TypeError):
            return None

    @property
    def available(self) -> bool:
        """Return whether the entity is available."""
        if not self.coordinator.last_update_success:
            return False

        source_entity_id = self.coordinator.config_entry.options.get("temperature_source_entity_id")
        if not source_entity_id:
            return False

        source_state = self.hass.states.get(source_entity_id)
        return source_state is not None and source_state.state not in ("unknown", "unavailable")
