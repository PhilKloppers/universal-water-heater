"""Mode select for universal_water_heater."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from custom_components.universal_water_heater.const import DOMAIN, LOGGER
from custom_components.universal_water_heater.entity import UniversalWaterHeaterEntity
from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.helpers.restore_state import RestoreEntity

if TYPE_CHECKING:
    from custom_components.universal_water_heater.coordinator import UniversalWaterHeaterDataUpdateCoordinator


class Mode(StrEnum):
    """Mode enum."""

    NORMAL = "normal"
    OPTIMISED = "optimised"
    ECO = "eco"
    OFF = "off"


ENTITY_DESCRIPTIONS = (
    SelectEntityDescription(
        key="mode",
        translation_key="mode",
        icon="mdi:cog",
        options=[mode.value for mode in Mode],
        has_entity_name=True,
    ),
)


class UniversalWaterHeaterModeSelect(SelectEntity, UniversalWaterHeaterEntity, RestoreEntity):
    """Mode select class."""

    def __init__(
        self,
        coordinator: UniversalWaterHeaterDataUpdateCoordinator,
        entity_description: SelectEntityDescription,
    ) -> None:
        """Initialize the select."""
        super().__init__(coordinator, entity_description)
        # Don't set a default here - let Home Assistant restore the previous state
        self._attr_current_option = None

    @property
    def current_option(self) -> str | None:
        """Return the current selected mode."""
        # First check if mode has been set in coordinator data
        mode_value = self.coordinator.data.get("mode")
        if mode_value and mode_value in [mode.value for mode in Mode]:
            return mode_value

        # Return the current attribute value (will be restored by HA)
        if self._attr_current_option:
            return self._attr_current_option

        # Only use default if no state is available at all
        return Mode.NORMAL

    async def async_added_to_hass(self) -> None:
        """Handle entity added to Home Assistant."""
        await super().async_added_to_hass()

        # Restore the last known state if available
        if (last_state := await self.async_get_last_state()) is not None:
            if last_state.state in [mode.value for mode in Mode]:
                self._attr_current_option = last_state.state
                # Also update coordinator data with restored state
                if self.coordinator.data is None:
                    self.coordinator.data = {}
                self.coordinator.data["mode"] = last_state.state
                LOGGER.debug("Restored mode from last state: %s", last_state.state)
            else:
                LOGGER.warning("Invalid last state '%s', using default", last_state.state)
                self._attr_current_option = Mode.NORMAL
        else:
            # No previous state, use default
            self._attr_current_option = Mode.NORMAL
            if self.coordinator.data is None:
                self.coordinator.data = {}
            self.coordinator.data["mode"] = Mode.NORMAL
            LOGGER.debug("No previous state found, using default: %s", Mode.NORMAL)

    async def async_select_option(self, option: str) -> None:
        """Change the selected mode."""
        LOGGER.debug("Setting mode to %s", option)

        # Check if status is currently Overtemp and warn the user
        status_entity_id = f"sensor.{self.coordinator.config_entry.title.lower().replace(' ', '_')}_status"
        status_state = self.hass.states.get(status_entity_id)
        if status_state and status_state.state == "Overtemp":
            LOGGER.warning(
                "Mode change to '%s' requested while status is OVERTEMP. "
                "Ensure temperature is below maximum safe limit before enabling heating. "
                "Current status: %s",
                option,
                status_state.state,
            )

            # If user is trying to enable heating (not OFF mode) during overtemp, issue stronger warning
            if option != Mode.OFF:
                LOGGER.error(
                    "SAFETY WARNING: Attempting to enable heating mode '%s' while system is in OVERTEMP state. "
                    "Temperature may exceed safe limits. Mode change allowed but verify temperature before operation.",
                    option,
                )

        if option in [mode.value for mode in Mode]:
            self._attr_current_option = option
            # Update coordinator data
            if self.coordinator.data is None:
                self.coordinator.data = {}
            self.coordinator.data["mode"] = option
            self.async_write_ha_state()

            # Trigger control logic evaluation after mode change
            # BUT: Skip if we're setting mode to OFF during overtemp to prevent recursion
            if option == Mode.OFF and status_state and status_state.state == "Overtemp":
                LOGGER.debug("Skipping control logic trigger - mode set to OFF during overtemp condition")
            else:
                self.hass.async_create_task(self._async_trigger_control_logic())

    async def _async_trigger_control_logic(self) -> None:
        """Trigger control logic evaluation through service call."""
        try:
            await self.hass.services.async_call(
                DOMAIN,
                "evaluate_control_logic",
                blocking=False,
            )
        except Exception:  # noqa: BLE001
            LOGGER.debug("Failed to trigger control logic - service may not be registered yet")
