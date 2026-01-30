"""
Core DataUpdateCoordinator implementation for universal_water_heater.

This module contains the main coordinator class that manages data fetching
and updates for all entities in the integration. It handles refresh cycles
and error handling.

For more information on coordinators:
https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from custom_components.universal_water_heater.const import LOGGER
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

if TYPE_CHECKING:
    from custom_components.universal_water_heater.data import UniversalWaterHeaterConfigEntry


class UniversalWaterHeaterDataUpdateCoordinator(DataUpdateCoordinator):
    """
    Class to manage fetching data from the API.

    This coordinator handles all data fetching for the integration and distributes
    updates to all entities. It manages:
    - Periodic data updates based on update_interval
    - Error handling and recovery
    - Data distribution to all entities
    - Context-based data fetching (only fetch data for active entities)

    For more information:
    https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities

    Attributes:
        config_entry: The config entry for this integration instance.
    """

    config_entry: UniversalWaterHeaterConfigEntry

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the coordinator."""
        super().__init__(*args, **kwargs)
        self._temperature_monitor = None

    async def _async_setup(self) -> None:
        """
        Set up the coordinator.

        This method is called automatically during async_config_entry_first_refresh()
        and is the ideal place for one-time initialization tasks such as:
        - Loading device information
        - Setting up event listeners
        - Initializing caches

        This runs before the first data fetch, ensuring any required setup
        is complete before entities start requesting data.
        """
        # Set up temperature monitoring for real-time response
        from custom_components.universal_water_heater.coordinator.temperature_monitor import (  # noqa: PLC0415
            async_setup_temperature_monitoring,
        )

        self._temperature_monitor = await async_setup_temperature_monitoring(self)

        # Example: Fetch device info once at startup
        # device_info = await self.config_entry.runtime_data.client.get_device_info()
        # self._device_id = device_info["id"]
        LOGGER.debug("Coordinator setup complete for %s", self.config_entry.entry_id)

    async def _async_update_data(self) -> Any:
        """
        Fetch data from API endpoint.

        This is the only method that should be implemented in a DataUpdateCoordinator.
        It is called automatically based on the update_interval.

        Context-based fetching:
        The coordinator tracks which entities are currently listening via async_contexts().
        This allows optimizing API calls to only fetch data that's actually needed.
        For example, if only sensor entities are enabled, we can skip fetching switch data.

        Expected API response structure (example):
        {
            "userId": 1,      # Used as device identifier
            "id": 1,          # Data record ID
            "title": "...",   # Additional metadata
            "body": "...",    # Additional content
            # In production, would include:
            # "air_quality": {"aqi": 45, "pm25": 12.3},
            # "filter": {"life_remaining": 75, "runtime_hours": 324},
            # "settings": {"fan_speed": "medium", "humidity": 55}
        }

        Returns:
            A dictionary containing aggregated data from linked entities.

        Raises:
            UpdateFailed: If data aggregation fails for any reason.
        """
        try:
            # Optional: Get active entity contexts to optimize data processing
            # listening_contexts = set(self.async_contexts())
            # LOGGER.debug("Active entity contexts: %s", listening_contexts)

            # Aggregate data from linked entities
            # In a real implementation, this would:
            # 1. Read state from linked entities (temperature, power, etc.)
            # 2. Process and validate the data
            # 3. Return aggregated result
            # Example:
            # return {
            #     "temperature": self.hass.states.get("sensor.source_temperature"),
            #     "power": self.hass.states.get("sensor.source_power"),
            #     "switch_state": self.hass.states.get("switch.source_heater"),
            # }

            # Run control logic evaluation during data update
            # We'll implement this as a service call later

            # For now, return empty dict - entities will handle their own state
            return {}
        except Exception as exception:
            LOGGER.exception("Error aggregating entity data")
            raise UpdateFailed(
                translation_domain="universal_water_heater",
                translation_key="update_failed",
            ) from exception
            return await self.config_entry.runtime_data.client.async_get_data()

    async def async_shutdown(self) -> None:
        """Shut down the coordinator and clean up resources."""
        if self._temperature_monitor:
            self._temperature_monitor.stop_monitoring()
        await super().async_shutdown()
