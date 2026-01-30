"""Temperature monitoring and control integration for coordinator."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from custom_components.universal_water_heater.const import CONF_BATTERY_AWARE, LOGGER
from custom_components.universal_water_heater.utils.control_logic import async_evaluate_and_control_heater
from homeassistant.core import callback
from homeassistant.helpers.event import async_track_state_change_event

if TYPE_CHECKING:
    from collections.abc import Callable

    from custom_components.universal_water_heater.coordinator import UniversalWaterHeaterDataUpdateCoordinator
    from homeassistant.core import HomeAssistant


class TemperatureMonitor:
    """Monitor temperature changes and trigger control logic."""

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: UniversalWaterHeaterDataUpdateCoordinator,
    ) -> None:
        """Initialize the temperature monitor."""
        self.hass = hass
        self.coordinator = coordinator
        self._unsubscribe_listeners: list[Callable[[], None]] = []

    def start_monitoring(self) -> None:
        """Start monitoring temperature, switch state, and battery SoC changes."""
        config_entry = self.coordinator.config_entry

        # Get entity IDs to monitor
        temp_entity_id = config_entry.options.get("temperature_source_entity_id")
        switch_entity_id = config_entry.options.get("switch_source_entity_id")
        battery_soc_entity_id = (
            config_entry.options.get("battery_soc_entity_id")
            if config_entry.options.get("battery_aware", False)
            else None
        )

        entities_to_monitor = []
        if temp_entity_id:
            entities_to_monitor.append(temp_entity_id)
        if switch_entity_id:
            entities_to_monitor.append(switch_entity_id)
        if battery_soc_entity_id:
            entities_to_monitor.append(battery_soc_entity_id)

        if not entities_to_monitor:
            LOGGER.warning("No entities configured to monitor")
            return

        LOGGER.debug("Starting temperature monitoring for entities: %s", entities_to_monitor)

        # Set up state change listener
        unsubscribe = async_track_state_change_event(
            self.hass,
            entities_to_monitor,
            self._handle_state_change,
        )
        self._unsubscribe_listeners.append(unsubscribe)

    def stop_monitoring(self) -> None:
        """Stop all monitoring."""
        for unsubscribe in self._unsubscribe_listeners:
            unsubscribe()
        self._unsubscribe_listeners.clear()
        LOGGER.debug("Stopped temperature monitoring")

    @callback
    def _handle_state_change(self, event: Any) -> None:
        """Handle state change event and trigger control logic."""
        entity_id = event.data["entity_id"]
        old_state = event.data["old_state"]
        new_state = event.data["new_state"]

        if new_state is None:
            return

        # Check if entity became unavailable or unknown
        if new_state.state in ("unavailable", "unknown"):
            LOGGER.warning(
                "Entity %s became %s - triggering error handling",
                entity_id,
                new_state.state,
            )
            # Trigger error handling which will check all entities and update status
            self.hass.async_create_task(self._check_entity_availability())
            return

        # Check if entity recovered from unavailable/unknown
        if (
            old_state
            and old_state.state in ("unavailable", "unknown")
            and new_state.state
            not in (
                "unavailable",
                "unknown",
            )
        ):
            LOGGER.info("Entity %s recovered from %s - checking system status", entity_id, old_state.state)
            # Trigger recovery check which will verify all entities and potentially recover
            self.hass.async_create_task(self._check_entity_availability())
            return

        # Skip if state hasn't actually changed
        if old_state and old_state.state == new_state.state:
            return

        # For temperature sensors, only trigger if change is significant (>= 0.5°C)
        temp_entity_id = self.coordinator.config_entry.options.get("temperature_source_entity_id")
        battery_soc_entity_id = self.coordinator.config_entry.options.get("battery_soc_entity_id")

        if entity_id == temp_entity_id:
            try:
                old_temp = (
                    float(old_state.state) if old_state and old_state.state not in ("unknown", "unavailable") else None
                )
                new_temp = float(new_state.state) if new_state.state not in ("unknown", "unavailable") else None

                if old_temp is not None and new_temp is not None:
                    temp_change = abs(new_temp - old_temp)
                    LOGGER.debug(
                        "Temperature change detected: %.1f°C -> %.1f°C (Δ%.1f°C)",
                        old_temp,
                        new_temp,
                        temp_change,
                    )
            except (ValueError, TypeError):
                # If we can't parse temperatures, just proceed with control logic
                pass

        # For battery SoC, log all changes
        elif entity_id == battery_soc_entity_id:
            try:
                old_soc = (
                    float(old_state.state) if old_state and old_state.state not in ("unknown", "unavailable") else None
                )
                new_soc = float(new_state.state) if new_state.state not in ("unknown", "unavailable") else None

                if old_soc is not None and new_soc is not None:
                    soc_change = abs(new_soc - old_soc)
                    LOGGER.debug(
                        "Battery SoC change detected: %.1f%% -> %.1f%% (Δ%.1f%%)",
                        old_soc,
                        new_soc,
                        soc_change,
                    )
            except (ValueError, TypeError):
                # If we can't parse SoC, just proceed with control logic
                pass

        LOGGER.debug(
            "State change detected for %s: %s -> %s",
            entity_id,
            old_state.state if old_state else "unknown",
            new_state.state,
        )

        # Schedule control logic evaluation
        self.hass.async_create_task(async_evaluate_and_control_heater(self.hass, self.coordinator.config_entry))

    async def _check_entity_availability(self) -> None:
        """Check availability of all monitored entities and update status accordingly."""
        temp_entity_id = self.coordinator.config_entry.options.get("temperature_source_entity_id")
        switch_entity_id = self.coordinator.config_entry.options.get("heater_switch_entity_id")
        battery_soc_entity_id = self.coordinator.config_entry.options.get("battery_soc_entity_id")
        battery_aware = self.coordinator.config_entry.options.get(CONF_BATTERY_AWARE, False)

        unavailable_entities = []

        # Check temperature entity (required)
        if temp_entity_id:
            temp_state = self.hass.states.get(temp_entity_id)
            if not temp_state or temp_state.state in ("unavailable", "unknown"):
                unavailable_entities.append(temp_entity_id)

        # Check switch entity (required)
        if switch_entity_id:
            switch_state = self.hass.states.get(switch_entity_id)
            if not switch_state or switch_state.state in ("unavailable", "unknown"):
                unavailable_entities.append(switch_entity_id)

        # Check battery SoC entity (only if battery-aware is enabled)
        if battery_aware and battery_soc_entity_id:
            battery_state = self.hass.states.get(battery_soc_entity_id)
            if not battery_state or battery_state.state in ("unavailable", "unknown"):
                unavailable_entities.append(battery_soc_entity_id)

        # Get status sensor
        status_entity = None
        for entity_id in self.hass.states.async_entity_ids("sensor"):
            if entity_id.startswith(f"sensor.{self.coordinator.config_entry.entry_id}") and "_status" in entity_id:
                status_entity = self.hass.states.get(entity_id)
                break

        if unavailable_entities:
            # Entities are unavailable - set error status and turn off heater
            LOGGER.error(
                "One or more entities unavailable: %s - Setting status to Error and turning off heater",
                ", ".join(unavailable_entities),
            )

            # Turn off heater for safety
            if switch_entity_id:
                switch_state = self.hass.states.get(switch_entity_id)
                if switch_state and switch_state.state == "on":
                    await self.hass.services.async_call(
                        "switch",
                        "turn_off",
                        {"entity_id": switch_entity_id},
                        blocking=True,
                    )
                    LOGGER.warning("Heater turned off due to unavailable entities")

            # Set status to Error
            if status_entity:
                # Find the actual entity object from the coordinator
                for entity in self.coordinator.hass.data.get("sensor", {}).values():
                    if hasattr(entity, "entity_id") and entity.entity_id == status_entity.entity_id:
                        await entity.async_set_status("Error")
                        break
        elif status_entity and status_entity.state == "Error":
            # All entities are available and status is Error - recover
            LOGGER.info("All entities are now available - recovering from Error to Normal status")
            for entity in self.coordinator.hass.data.get("sensor", {}).values():
                if hasattr(entity, "entity_id") and entity.entity_id == status_entity.entity_id:
                    await entity.async_set_status("Normal")
                    break

            # Resume normal operation by triggering control logic
            await async_evaluate_and_control_heater(self.hass, self.coordinator.config_entry)


async def async_setup_temperature_monitoring(
    coordinator: UniversalWaterHeaterDataUpdateCoordinator,
) -> TemperatureMonitor:
    """
    Set up temperature monitoring for the coordinator.

    Args:
        coordinator: The coordinator instance

    Returns:
        TemperatureMonitor instance

    """
    monitor = TemperatureMonitor(coordinator.hass, coordinator)
    monitor.start_monitoring()

    # Also run initial control logic evaluation
    await async_evaluate_and_control_heater(coordinator.hass, coordinator.config_entry)

    return monitor
