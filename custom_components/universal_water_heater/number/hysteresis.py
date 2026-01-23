"""Hysteresis number for universal_water_heater."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.universal_water_heater.api import UniversalWaterHeaterApiClientError
from custom_components.universal_water_heater.const import LOGGER
from custom_components.universal_water_heater.entity import UniversalWaterHeaterEntity
from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.const import UnitOfTemperature
from homeassistant.exceptions import HomeAssistantError

if TYPE_CHECKING:
    from custom_components.universal_water_heater.coordinator import UniversalWaterHeaterDataUpdateCoordinator

ENTITY_DESCRIPTIONS = (
    NumberEntityDescription(
        key="hysteresis",
        translation_key="hysteresis",
        icon="mdi:thermometer-lines",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=0.1,
        native_max_value=5,
        native_step=1,
        mode=NumberMode.SLIDER,
        has_entity_name=True,
    ),
)


class UniversalWaterHeaterHysteresisNumber(NumberEntity, UniversalWaterHeaterEntity):
    """Hysteresis number class."""

    def __init__(
        self,
        coordinator: UniversalWaterHeaterDataUpdateCoordinator,
        entity_description: NumberEntityDescription,
    ) -> None:
        """Initialize the number."""
        super().__init__(coordinator, entity_description)
        # Default hysteresis
        self._attr_native_value: float = 4.0

    @property
    def native_value(self) -> float:
        """Return the current value."""
        return self._attr_native_value

    async def async_set_native_value(self, value: float) -> None:
        """Set new hysteresis."""
        try:
            # In production: Call API to set hysteresis
            # await self.coordinator.config_entry.runtime_data.client.async_set_hysteresis(float(value))

            self._attr_native_value = value
            self.async_write_ha_state()
            LOGGER.debug("Hysteresis set to %s°C", value)
        except UniversalWaterHeaterApiClientError as exception:
            LOGGER.exception("Failed to set hysteresis")
            raise HomeAssistantError(
                translation_domain="universal_water_heater",
                translation_key="number_set_failed",
            ) from exception
