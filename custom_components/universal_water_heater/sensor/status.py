"""Status sensor for universal_water_heater."""

from __future__ import annotations

from typing import Any

from custom_components.universal_water_heater.const import (
    CONF_ECO_TEMPERATURE,
    CONF_HYSTERESIS,
    CONF_MAX_TEMPERATURE,
    CONF_NORMAL_TEMPERATURE,
    CONF_TEMPERATURES,
)
from custom_components.universal_water_heater.entity import UniversalWaterHeaterEntity
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.const import STATE_OFF, EntityCategory

STATUS_STATES = ["Normal", "Error", STATE_OFF]

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="status",
        name="Status",
        icon="mdi:information-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


class UniversalWaterHeaterStatusSensor(SensorEntity, UniversalWaterHeaterEntity):
    """Status sensor for Universal Water Heater."""

    _attr_should_poll = False

    def __init__(
        self,
        coordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the status sensor."""
        super().__init__(coordinator, entity_description)
        self._attr_native_value = "Normal"  # Default state

    @property
    def native_value(self) -> str:
        """Return the current status value."""
        # TODO: Replace with real logic for status
        return str(self._attr_native_value)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return temperature and hysteresis attributes."""
        entry_data = self.coordinator.config_entry.data.get(CONF_TEMPERATURES, {})
        return {
            CONF_NORMAL_TEMPERATURE: entry_data.get(CONF_NORMAL_TEMPERATURE),
            CONF_ECO_TEMPERATURE: entry_data.get(CONF_ECO_TEMPERATURE),
            CONF_MAX_TEMPERATURE: entry_data.get(CONF_MAX_TEMPERATURE),
            CONF_HYSTERESIS: entry_data.get(CONF_HYSTERESIS),
        }

    async def async_set_status(self, status: str) -> None:
        """Set the status value and update state."""
        if status in STATUS_STATES:
            self._attr_native_value = status
            self.async_write_ha_state()
