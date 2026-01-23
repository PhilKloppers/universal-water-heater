"""Mode select for universal_water_heater."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from custom_components.universal_water_heater.const import LOGGER
from custom_components.universal_water_heater.entity import UniversalWaterHeaterEntity
from homeassistant.components.select import SelectEntity, SelectEntityDescription

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


class UniversalWaterHeaterModeSelect(SelectEntity, UniversalWaterHeaterEntity):
    """Mode select class."""

    def __init__(
        self,
        coordinator: UniversalWaterHeaterDataUpdateCoordinator,
        entity_description: SelectEntityDescription,
    ) -> None:
        """Initialize the select."""
        super().__init__(coordinator, entity_description)
        # Initialize with optimised mode
        self._attr_current_option = Mode.OPTIMISED

    @property
    def current_option(self) -> str | None:
        """Return the current selected mode."""
        # Check if mode has been set in coordinator data
        mode_value = self.coordinator.data.get("mode")
        if mode_value and mode_value in [mode.value for mode in Mode]:
            return mode_value
        return self._attr_current_option

    async def async_select_option(self, option: str) -> None:
        """Change the selected mode."""
        LOGGER.debug("Setting mode to %s", option)
        if option in [mode.value for mode in Mode]:
            self._attr_current_option = option
            # Update coordinator data
            if self.coordinator.data is None:
                self.coordinator.data = {}
            self.coordinator.data["mode"] = option
            self.async_write_ha_state()
