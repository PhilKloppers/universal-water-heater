"""Linked switch that mirrors and controls another switch for universal_water_heater."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from custom_components.universal_water_heater.entity import UniversalWaterHeaterEntity
from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity, SwitchEntityDescription
from homeassistant.exceptions import HomeAssistantError

if TYPE_CHECKING:
    from custom_components.universal_water_heater.coordinator import UniversalWaterHeaterDataUpdateCoordinator


ENTITY_DESCRIPTIONS = (
    SwitchEntityDescription(
        key="linked_switch",
        translation_key="linked_switch",
        icon="mdi:link-variant",
        device_class=SwitchDeviceClass.SWITCH,
        has_entity_name=True,
        entity_registry_enabled_default=False,
    ),
)


class UniversalWaterHeaterLinkedSwitch(SwitchEntity, UniversalWaterHeaterEntity):
    """Switch that mirrors and controls another switch entity."""

    def __init__(
        self,
        coordinator: UniversalWaterHeaterDataUpdateCoordinator,
        entity_description: SwitchEntityDescription,
    ) -> None:
        """Initialize the linked switch."""
        super().__init__(coordinator, entity_description)

    @property
    def is_on(self) -> bool:
        """Return true if the linked switch is on."""
        # Get the source entity ID from config entry options
        source_entity_id = self.coordinator.config_entry.options.get("switch_source_entity_id")
        if not source_entity_id:
            return False

        # Get the state of the source entity
        source_state = self.hass.states.get(source_entity_id)
        if source_state is None:
            return False

        return source_state.state == "on"

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
        except HomeAssistantError:
            raise
        except Exception as exception:
            raise HomeAssistantError(
                translation_domain="universal_water_heater",
                translation_key="linked_switch_turn_off_failed",
            ) from exception
