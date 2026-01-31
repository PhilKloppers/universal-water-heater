"""Status sensor for universal_water_heater."""

from __future__ import annotations

import logging
from typing import Any

from custom_components.universal_water_heater.const import (
    CONF_BATTERY_AWARE,
    CONF_BATTERY_RESUME_THRESHOLD,
    CONF_BATTERY_THRESHOLD,
    CONF_ECO_MODE_END,
    CONF_ECO_MODE_START,
    CONF_ECO_TEMPERATURE,
    CONF_HYSTERESIS,
    CONF_MAX_TEMPERATURE,
    CONF_NORMAL_MODE_END,
    CONF_NORMAL_MODE_START,
    CONF_NORMAL_TEMPERATURE,
    CONF_SUN_ANGLE,
    CONF_TEMPERATURES,
    CONF_USE_SOLAR_CONTROL,
)
from custom_components.universal_water_heater.entity import UniversalWaterHeaterEntity
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.const import STATE_OFF, EntityCategory
from homeassistant.core import Event, EventStateChangedData
from homeassistant.helpers.event import async_track_state_change_event

LOGGER = logging.getLogger(__name__)

STATUS_STATES = ["Normal", "Overtemp", "Error", STATE_OFF]

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

    async def async_added_to_hass(self) -> None:
        """Register callbacks when entity is added to hass."""
        await super().async_added_to_hass()

        # Subscribe to temperature changes to update status
        temp_entity_id = self.coordinator.config_entry.options.get("temperature_source_entity_id")
        if temp_entity_id:
            self.async_on_remove(
                async_track_state_change_event(self.hass, temp_entity_id, self._async_temperature_changed)
            )

    async def _async_temperature_changed(self, event: Event[EventStateChangedData]) -> None:
        """Handle temperature entity state changes."""
        self.update_status()
        self.async_write_ha_state()

    def update_status(self) -> None:
        """Update the status based on current conditions."""
        temp_entity_id = self.coordinator.config_entry.options.get("temperature_source_entity_id")
        if temp_entity_id:
            temp_state = self.hass.states.get(temp_entity_id)
            if temp_state and temp_state.state not in ("unknown", "unavailable"):
                try:
                    current_temp = float(temp_state.state)
                    entry_data = self.coordinator.config_entry.data.get(CONF_TEMPERATURES, {})
                    max_temperature = entry_data.get(CONF_MAX_TEMPERATURE, 75.0)
                    normal_temperature = entry_data.get(CONF_NORMAL_TEMPERATURE, 65.0)

                    # Check if overtemperature condition exists
                    if current_temp >= max_temperature:
                        if self._attr_native_value != "Overtemp":
                            LOGGER.warning(
                                "Overtemperature detected! Temperature: %.1f°C (max: %.1f°C)",
                                current_temp,
                                max_temperature,
                            )
                        self._attr_native_value = "Overtemp"
                    # Auto-recover from Overtemp to Normal when temperature drops below normal temperature
                    elif self._attr_native_value == "Overtemp" and current_temp < normal_temperature:
                        self._attr_native_value = "Normal"
                        LOGGER.info(
                            "Status recovered from Overtemp to Normal - Temperature: %.1f°C (below normal: %.1f°C)",
                            current_temp,
                            normal_temperature,
                        )
                except (ValueError, TypeError):
                    pass

    @property
    def native_value(self) -> str:
        """Return the current status value."""
        return str(self._attr_native_value)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return temperature and battery configuration attributes."""
        entry_data = self.coordinator.config_entry.data.get(CONF_TEMPERATURES, {})
        options = self.coordinator.config_entry.options

        attributes = {
            CONF_NORMAL_TEMPERATURE: entry_data.get(CONF_NORMAL_TEMPERATURE),
            CONF_ECO_TEMPERATURE: entry_data.get(CONF_ECO_TEMPERATURE),
            CONF_MAX_TEMPERATURE: entry_data.get(CONF_MAX_TEMPERATURE),
            CONF_HYSTERESIS: entry_data.get(CONF_HYSTERESIS),
        }

        # Add battery thresholds if battery-aware is enabled
        if options.get(CONF_BATTERY_AWARE, False):
            attributes[CONF_BATTERY_THRESHOLD] = options.get(CONF_BATTERY_THRESHOLD)
            attributes[CONF_BATTERY_RESUME_THRESHOLD] = options.get(CONF_BATTERY_RESUME_THRESHOLD)

        # Add optimised mode configuration based on selected control type
        if options.get(CONF_USE_SOLAR_CONTROL, False):
            # Solar control is enabled - add solar control attributes
            attributes["optimised_control_type"] = "solar"
            attributes[CONF_SUN_ANGLE] = options.get(CONF_SUN_ANGLE)
        # Time-based control is enabled - add time range attributes
        # Only add if any time-based configuration exists
        elif any(
            options.get(key)
            for key in [CONF_NORMAL_MODE_START, CONF_NORMAL_MODE_END, CONF_ECO_MODE_START, CONF_ECO_MODE_END]
        ):
            attributes["optimised_control_type"] = "time_based"
            attributes[CONF_NORMAL_MODE_START] = options.get(CONF_NORMAL_MODE_START)
            attributes[CONF_NORMAL_MODE_END] = options.get(CONF_NORMAL_MODE_END)
            attributes[CONF_ECO_MODE_START] = options.get(CONF_ECO_MODE_START)
            attributes[CONF_ECO_MODE_END] = options.get(CONF_ECO_MODE_END)

        return attributes

    async def async_set_status(self, status: str) -> None:
        """Set the status value and update state."""
        if status in STATUS_STATES:
            old_status = self._attr_native_value
            self._attr_native_value = status
            self.async_write_ha_state()

            # Log status changes
            if old_status != status:
                if status == "Error":
                    LOGGER.error("Status changed from %s to Error due to unavailable entities", old_status)
                elif old_status == "Error":
                    LOGGER.info("Status recovered from Error to %s - all entities are now available", status)
                else:
                    LOGGER.debug("Status changed from %s to %s", old_status, status)
