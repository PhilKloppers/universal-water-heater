"""Linked switch that mirrors and controls another switch for universal_water_heater."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from custom_components.universal_water_heater.entity import UniversalWaterHeaterEntity
from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity, SwitchEntityDescription
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import async_track_state_change_event

if TYPE_CHECKING:
    from custom_components.universal_water_heater.coordinator import UniversalWaterHeaterDataUpdateCoordinator


ENTITY_DESCRIPTIONS = (
    SwitchEntityDescription(
        key="linked_switch",
        translation_key="linked_switch",
        icon="mdi:link-variant",
        device_class=SwitchDeviceClass.SWITCH,
        has_entity_name=True,
        entity_registry_enabled_default=True,
    ),
)


class UniversalWaterHeaterLinkedSwitch(SwitchEntity, UniversalWaterHeaterEntity):
    """Switch that mirrors and controls another switch entity."""

    _remove_state_listener: Callable[[], None] | None = None

    def __init__(
        self,
        coordinator: UniversalWaterHeaterDataUpdateCoordinator,
        entity_description: SwitchEntityDescription,
    ) -> None:
        """Initialize the linked switch."""
        super().__init__(coordinator, entity_description)
        self._attr_is_on: bool = False
        self._remove_state_listener = None

    async def async_added_to_hass(self) -> None:
        """Handle entity added to Home Assistant."""
        await super().async_added_to_hass()
        self._update_state_from_source()
        self._setup_state_listener()

    async def async_will_remove_from_hass(self) -> None:
        """Handle entity removal from Home Assistant."""
        if self._remove_state_listener:
            self._remove_state_listener()
        await super().async_will_remove_from_hass()

    def _setup_state_listener(self) -> None:
        """Set up listener for source entity state changes."""
        source_entity_id = self.coordinator.config_entry.options.get("switch_source_entity_id")
        if not source_entity_id:
            return

        # Remove existing listener if any
        if self._remove_state_listener:
            self._remove_state_listener()

        # Add new listener for state changes
        self._remove_state_listener = async_track_state_change_event(
            self.hass,
            [source_entity_id],
            self._on_source_entity_state_changed,
        )

    @callback
    def _on_source_entity_state_changed(self, event: Any) -> None:
        """Handle source entity state change."""
        self._update_state_from_source()
        self.async_write_ha_state()

    def _update_state_from_source(self) -> None:
        """Update the switch state from the source entity."""
        source_entity_id = self.coordinator.config_entry.options.get("switch_source_entity_id")
        if not source_entity_id:
            self._attr_is_on = False
            return

        source_state = self.hass.states.get(source_entity_id)
        if source_state is None:
            self._attr_is_on = False
            return

        self._attr_is_on = source_state.state == "on"

    @property
    def available(self) -> bool:
        """Return whether the entity is available."""
        if not self.coordinator.last_update_success:
            return False

        source_entity_id = self.coordinator.config_entry.options.get("switch_source_entity_id")
        if not source_entity_id:
            return False

        source_state = self.hass.states.get(source_entity_id)
        return source_state is not None and source_state.state != "unavailable"

    async def async_turn_on(self, **_: Any) -> None:
        """Turn on the linked switch."""
        source_entity_id = self.coordinator.config_entry.options.get("switch_source_entity_id")
        if not source_entity_id:
            raise HomeAssistantError(
                translation_domain="universal_water_heater",
                translation_key="linked_switch_no_source",
            )

        try:
            # Call the service to turn on the source entity
            await self.hass.services.async_call(
                "homeassistant",
                "turn_on",
                {"entity_id": source_entity_id},
                blocking=True,
            )
            # Update local state
            self._attr_is_on = True
            self.async_write_ha_state()
        except HomeAssistantError:
            raise
        except Exception as exception:
            raise HomeAssistantError(
                translation_domain="universal_water_heater",
                translation_key="linked_switch_turn_on_failed",
            ) from exception

    async def async_turn_off(self, **_: Any) -> None:
        """Turn off the linked switch."""
        source_entity_id = self.coordinator.config_entry.options.get("switch_source_entity_id")
        if not source_entity_id:
            raise HomeAssistantError(
                translation_domain="universal_water_heater",
                translation_key="linked_switch_no_source",
            )

        try:
            # Call the service to turn off the source entity
            await self.hass.services.async_call(
                "homeassistant",
                "turn_off",
                {"entity_id": source_entity_id},
                blocking=True,
            )
            # Update local state
            self._attr_is_on = False
            self.async_write_ha_state()
        except HomeAssistantError:
            raise
        except Exception as exception:
            raise HomeAssistantError(
                translation_domain="universal_water_heater",
                translation_key="linked_switch_turn_off_failed",
            ) from exception
