"""Voltage sensor that reads from another voltage sensor for universal_water_heater."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.universal_water_heater.entity import UniversalWaterHeaterEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import UnitOfElectricPotential
from homeassistant.core import callback

if TYPE_CHECKING:
    from custom_components.universal_water_heater.coordinator import UniversalWaterHeaterDataUpdateCoordinator


ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="voltage",
        translation_key="voltage",
        icon="mdi:lightning-bolt-circle",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=1,
        has_entity_name=True,
    ),
)


class UniversalWaterHeaterVoltageSensor(SensorEntity, UniversalWaterHeaterEntity):
    """Voltage sensor that reads from another voltage sensor."""

    def __init__(
        self,
        coordinator: UniversalWaterHeaterDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entity_description)
        self._unsub_state_updates: list = []

    @property
    def native_value(self) -> float | None:
        """Return the native value of the sensor."""
        if not self.coordinator.last_update_success:
            return None

        # Get the source entity ID from config entry options
        source_entity_id = self.coordinator.config_entry.options.get("voltage_source_entity_id")
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

        source_entity_id = self.coordinator.config_entry.options.get("voltage_source_entity_id")
        if not source_entity_id:
            return False

        source_state = self.hass.states.get(source_entity_id)
        return source_state is not None and source_state.state not in ("unknown", "unavailable")

    async def async_added_to_hass(self) -> None:
        """Handle entity added to hass."""
        await super().async_added_to_hass()
        self._setup_state_listener()
        self.async_on_remove(self._cleanup_state_listeners)

    def _setup_state_listener(self) -> None:
        """Set up the state change listener for the source entity."""
        source_entity_id = self.coordinator.config_entry.options.get("voltage_source_entity_id")
        if not source_entity_id:
            return

        unsub = self.hass.bus.async_listen(
            "state_changed",
            self._on_source_state_changed,
        )
        self._unsub_state_updates.append(unsub)

    @callback
    def _on_source_state_changed(self, event) -> None:
        """Handle source entity state changes."""
        source_entity_id = self.coordinator.config_entry.options.get("voltage_source_entity_id")
        if event.data.get("entity_id") == source_entity_id:
            self.async_write_ha_state()

    def _cleanup_state_listeners(self) -> None:
        """Clean up state change listeners."""
        for unsub in self._unsub_state_updates:
            unsub()
        self._unsub_state_updates.clear()
