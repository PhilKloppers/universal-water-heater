"""Target humidity number for universal_water_heater."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.universal_water_heater.api import UniversalWaterHeaterApiClientError
from custom_components.universal_water_heater.const import LOGGER
from custom_components.universal_water_heater.entity import UniversalWaterHeaterEntity
from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.const import PERCENTAGE
from homeassistant.exceptions import HomeAssistantError

if TYPE_CHECKING:
    from custom_components.universal_water_heater.coordinator import UniversalWaterHeaterDataUpdateCoordinator

ENTITY_DESCRIPTIONS = (
    NumberEntityDescription(
        key="target_humidity",
        translation_key="target_humidity",
        icon="mdi:water-percent",
        device_class=NumberDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        native_min_value=30,
        native_max_value=80,
        native_step=5,
        mode=NumberMode.SLIDER,
        has_entity_name=True,
    ),
)


class UniversalWaterHeaterHumidityNumber(NumberEntity, UniversalWaterHeaterEntity):
    """Target humidity number class."""

    def __init__(
        self,
        coordinator: UniversalWaterHeaterDataUpdateCoordinator,
        entity_description: NumberEntityDescription,
    ) -> None:
        """Initialize the number."""
        super().__init__(coordinator, entity_description)
        # Default target humidity
        self._attr_native_value: float = 50.0

    @property
    def native_value(self) -> float:
        """Return the current value."""
        return self._attr_native_value

    async def async_set_native_value(self, value: float) -> None:
        """Set new target humidity."""
        try:
            # In production: Call API to set target humidity
            # await self.coordinator.config_entry.runtime_data.client.async_set_target_humidity(int(value))

            self._attr_native_value = value
            self.async_write_ha_state()
            LOGGER.debug("Target humidity set to %s%%", value)
        except UniversalWaterHeaterApiClientError as exception:
            LOGGER.exception("Failed to set target humidity")
            raise HomeAssistantError(
                translation_domain="universal_water_heater",
                translation_key="number_set_failed",
            ) from exception
