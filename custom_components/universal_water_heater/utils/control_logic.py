"""Control logic for universal water heater."""

from __future__ import annotations

from datetime import datetime, time
from typing import TYPE_CHECKING

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
    CONF_SUN_ENTITY_ID,
    CONF_TEMPERATURES,
    CONF_USE_SOLAR_CONTROL,
    DEFAULT_BATTERY_RESUME_THRESHOLD,
    DEFAULT_BATTERY_THRESHOLD,
    LOGGER,
)
from custom_components.universal_water_heater.select.mode import Mode
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.util import dt as dt_util

if TYPE_CHECKING:
    from custom_components.universal_water_heater.data import UniversalWaterHeaterConfigEntry
    from homeassistant.core import HomeAssistant


class WaterHeaterControlLogic:
    """Handle temperature-based control logic for the water heater."""

    def __init__(self, config_entry: UniversalWaterHeaterConfigEntry, hass: HomeAssistant | None = None) -> None:
        """Initialize the control logic."""
        self.config_entry = config_entry
        self.hass = hass

    def should_turn_on_heater(
        self,
        current_temp: float,
        current_mode: str,
        is_heater_on: bool,
        battery_soc: float | None = None,
        max_temperature: float | None = None,
    ) -> tuple[bool, bool]:
        """
        Determine if the heater should be turned on.

        Args:
            current_temp: Current water temperature in Celsius
            current_mode: Current operating mode (normal, eco, off, optimised)
            is_heater_on: Current state of the heater relay
            battery_soc: Current battery state of charge (percentage) if battery-aware is enabled
            max_temperature: Maximum allowed temperature (safety limit)

        Returns:
            Tuple of (should_turn_on: bool, is_overtemp: bool)

        """
        # CRITICAL SAFETY CHECK: Maximum temperature override
        # This check takes absolute priority over all other settings
        if max_temperature is not None and current_temp >= max_temperature:
            LOGGER.warning(
                "OVERTEMPERATURE DETECTED: Current temp (%.1f°C) >= max temp (%.1f°C), forcing heater OFF",
                current_temp,
                max_temperature,
            )
            return False, True  # Force off, overtemp detected

        # If mode is OFF, heater should always be off
        if current_mode == Mode.OFF:
            return False, False

        # Check battery-aware constraints
        battery_aware = self.config_entry.options.get(CONF_BATTERY_AWARE, False)
        if battery_aware and battery_soc is not None:
            battery_threshold = self.config_entry.options.get(CONF_BATTERY_THRESHOLD, DEFAULT_BATTERY_THRESHOLD)
            battery_resume_threshold = self.config_entry.options.get(
                CONF_BATTERY_RESUME_THRESHOLD, DEFAULT_BATTERY_RESUME_THRESHOLD
            )

            # Apply hysteresis to battery: turn off below threshold, turn on above resume threshold
            if is_heater_on:
                # If heater is on, keep it on unless battery drops below threshold
                if battery_soc < battery_threshold:
                    LOGGER.info(
                        "Battery SoC (%.1f%%) below threshold (%.1f%%), heater must be turned off",
                        battery_soc,
                        battery_threshold,
                    )
                    return False, False
            # If heater is off, don't turn it on unless battery is above resume threshold
            elif battery_soc < battery_resume_threshold:
                LOGGER.debug(
                    "Battery SoC (%.1f%%) below resume threshold (%.1f%%), heater remains off",
                    battery_soc,
                    battery_resume_threshold,
                )
                return False, False

        # Get temperature configuration
        temperatures = self.config_entry.data.get(CONF_TEMPERATURES, {})
        hysteresis = temperatures.get(CONF_HYSTERESIS, 4.0)

        # Get target temperature based on mode
        if current_mode == Mode.NORMAL:
            target_temp = temperatures.get(CONF_NORMAL_TEMPERATURE, 65.0)
        elif current_mode == Mode.ECO:
            target_temp = temperatures.get(CONF_ECO_TEMPERATURE, 55.0)
        elif current_mode == Mode.OPTIMISED:
            # For optimised mode, determine temperature based on configuration
            target_temp = self._get_optimised_target_temperature(temperatures)
            # If None returned, heater should be off (time outside configured ranges)
            if target_temp is None:
                LOGGER.debug("Optimised mode: outside configured time ranges, turning heater OFF")
                return False, False
        else:
            LOGGER.warning("Unknown mode: %s, defaulting to normal temperature", current_mode)
            target_temp = temperatures.get(CONF_NORMAL_TEMPERATURE, 65.0)

        # Apply hysteresis logic
        if is_heater_on:
            # If heater is currently on, turn off when temp reaches target + hysteresis
            should_be_on = current_temp < (target_temp + hysteresis)
        else:
            # If heater is currently off, turn on when temp drops below target - hysteresis
            should_be_on = current_temp < (target_temp - hysteresis)

        LOGGER.debug(
            "Control logic: temp=%.1f°C, target=%.1f°C, hysteresis=%.1f°C, mode=%s, heater_on=%s, should_be_on=%s, "
            "battery_soc=%s",
            current_temp,
            target_temp,
            hysteresis,
            current_mode,
            is_heater_on,
            should_be_on,
            f"{battery_soc:.1f}%" if battery_soc is not None else "N/A",
        )

        return should_be_on, False  # Not overtemp

    def _get_optimised_target_temperature(self, temperatures: dict) -> float | None:
        """
        Get target temperature for optimised mode based on configuration.

        Returns normal temperature if:
        - Time-based: Current time is within normal mode hours
        - Solar-based: Sun elevation is above configured angle

        Returns eco temperature if:
        - Time-based: Current time is within eco mode hours
        - Solar-based: Sun elevation is below configured angle

        Returns None if:
        - Time-based: Current time is outside both configured ranges (heater should be OFF)
        """
        use_solar_control = self.config_entry.options.get(CONF_USE_SOLAR_CONTROL, False)

        if use_solar_control:
            return self._get_solar_based_temperature(temperatures)
        return self._get_time_based_temperature(temperatures)

    def _get_time_based_temperature(self, temperatures: dict) -> float | None:
        """
        Get target temperature based on current time and configured schedules.

        Returns:
            Normal temperature if within normal mode hours, eco temperature if within eco hours,
            None if outside both configured ranges (heater should be off).
        """
        normal_mode_start = self.config_entry.options.get(CONF_NORMAL_MODE_START)
        normal_mode_end = self.config_entry.options.get(CONF_NORMAL_MODE_END)
        eco_mode_start = self.config_entry.options.get(CONF_ECO_MODE_START)
        eco_mode_end = self.config_entry.options.get(CONF_ECO_MODE_END)

        # If no time configuration is set, default to eco mode
        if not all([normal_mode_start, normal_mode_end, eco_mode_start, eco_mode_end]):
            LOGGER.debug("Time-based configuration incomplete, using eco temperature")
            return temperatures.get(CONF_ECO_TEMPERATURE, 55.0)

        # Get current time in Home Assistant's configured timezone
        now = dt_util.now().time()

        LOGGER.debug(
            "Time-based control check: now=%s, normal=%s-%s, eco=%s-%s (types: %s, %s, %s, %s)",
            now,
            normal_mode_start,
            normal_mode_end,
            eco_mode_start,
            eco_mode_end,
            type(normal_mode_start).__name__,
            type(normal_mode_end).__name__,
            type(eco_mode_start).__name__,
            type(eco_mode_end).__name__,
        )

        # Type narrowing: we've verified these are not None with the all() check above
        assert normal_mode_start is not None
        assert normal_mode_end is not None
        assert eco_mode_start is not None
        assert eco_mode_end is not None

        # Check if we're in normal mode period
        if self._is_time_in_range(now, normal_mode_start, normal_mode_end):
            LOGGER.debug("Current time in normal mode range, using normal temperature")
            return temperatures.get(CONF_NORMAL_TEMPERATURE, 65.0)

        # Check if we're in eco mode period
        if self._is_time_in_range(now, eco_mode_start, eco_mode_end):
            LOGGER.debug("Current time in eco mode range, using eco temperature")
            return temperatures.get(CONF_ECO_TEMPERATURE, 55.0)

        # Outside both ranges - heater should be OFF
        LOGGER.debug("Current time outside both configured ranges, heater should be OFF")
        return None

    def _get_solar_based_temperature(self, temperatures: dict) -> float:
        """
        Get target temperature based on sun elevation.

        Returns:
            Normal temperature if sun is above configured angle, eco temperature otherwise.
        """
        from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN  # noqa: PLC0415

        sun_entity_id = self.config_entry.options.get(CONF_SUN_ENTITY_ID)
        sun_angle_threshold = self.config_entry.options.get(CONF_SUN_ANGLE, 0)

        # If no sun entity configured or no hass instance, default to eco mode
        if not sun_entity_id or not self.hass:
            LOGGER.debug("No sun entity configured or no hass instance, using eco temperature")
            return temperatures.get(CONF_ECO_TEMPERATURE, 55.0)

        # Get sun entity state
        sun_state = self.hass.states.get(sun_entity_id)
        if not sun_state or sun_state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            LOGGER.debug("Sun entity %s unavailable, using eco temperature", sun_entity_id)
            return temperatures.get(CONF_ECO_TEMPERATURE, 55.0)

        # Get elevation attribute
        elevation = sun_state.attributes.get("elevation")
        if elevation is None:
            LOGGER.warning("Sun entity %s has no elevation attribute, using eco temperature", sun_entity_id)
            return temperatures.get(CONF_ECO_TEMPERATURE, 55.0)

        try:
            elevation_value = float(elevation)
            if elevation_value > sun_angle_threshold:
                LOGGER.debug(
                    "Sun elevation %.1f° > threshold %.1f°, using normal temperature",
                    elevation_value,
                    sun_angle_threshold,
                )
                return temperatures.get(CONF_NORMAL_TEMPERATURE, 65.0)
            LOGGER.debug(
                "Sun elevation %.1f° <= threshold %.1f°, using eco temperature",
                elevation_value,
                sun_angle_threshold,
            )
            return temperatures.get(CONF_ECO_TEMPERATURE, 55.0)
        except (ValueError, TypeError) as e:
            LOGGER.warning("Failed to parse sun elevation %s: %s, using eco temperature", elevation, e)
            return temperatures.get(CONF_ECO_TEMPERATURE, 55.0)

    @staticmethod
    def _is_time_in_range(current: time, start: time | str, end: time | str) -> bool:
        """
        Check if current time is within the given range.

        Handles ranges that cross midnight (e.g., 22:00-06:00).

        Args:
            current: Current time
            start: Start time as time object or string (HH:MM:SS or HH:MM)
            end: End time as time object or string (HH:MM:SS or HH:MM)

        Returns:
            True if current time is within range
        """
        try:
            # Convert to time objects if they're strings
            if isinstance(start, str):
                # Count colons to determine format
                if start.count(":") == 2:
                    start_time = datetime.strptime(start, "%H:%M:%S").time()
                else:
                    start_time = datetime.strptime(start, "%H:%M").time()
            else:
                start_time = start

            if isinstance(end, str):
                # Count colons to determine format
                if end.count(":") == 2:
                    end_time = datetime.strptime(end, "%H:%M:%S").time()
                else:
                    end_time = datetime.strptime(end, "%H:%M").time()
            else:
                end_time = end

            # Check if range crosses midnight
            if start_time <= end_time:
                # Normal range (e.g., 08:00 - 18:00)
                result = start_time <= current <= end_time
            else:
                # Range crosses midnight (e.g., 22:00 - 06:00)
                result = current >= start_time or current <= end_time

            LOGGER.debug(
                "Time range check: current=%s, range=%s-%s, in_range=%s",
                current,
                start_time,
                end_time,
                result,
            )
            return result  # noqa: TRY300
        except (ValueError, TypeError) as e:
            LOGGER.warning(
                "Failed to parse time range %s-%s (types: %s, %s): %s",
                start,
                end,
                type(start).__name__,
                type(end).__name__,
                e,
            )
            return False


async def async_evaluate_and_control_heater(
    hass: HomeAssistant,
    config_entry: UniversalWaterHeaterConfigEntry,
) -> None:
    """
    Evaluate current conditions and control the heater relay.

    This function reads the current temperature, mode, and heater state,
    then applies control logic to determine if the heater should be turned on or off.

    Args:
        hass: Home Assistant instance
        config_entry: The config entry for this integration

    """
    try:
        # Get source entity IDs from config
        temp_entity_id = config_entry.options.get("temperature_source_entity_id")
        switch_entity_id = config_entry.options.get("switch_source_entity_id")

        if not temp_entity_id or not switch_entity_id:
            LOGGER.warning("Temperature or switch entity not configured, skipping control logic")
            return

        # Get current states
        temp_state = hass.states.get(temp_entity_id)
        switch_state = hass.states.get(switch_entity_id)

        if not temp_state or temp_state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            LOGGER.warning("Temperature sensor %s is unavailable", temp_entity_id)
            return

        if not switch_state or switch_state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            LOGGER.warning("Switch %s is unavailable", switch_entity_id)
            return

        # Parse current temperature
        try:
            current_temp = float(temp_state.state)
        except (ValueError, TypeError):
            LOGGER.warning("Invalid temperature value from %s: %s", temp_entity_id, temp_state.state)
            return

        # Get current mode from coordinator data
        coordinator = config_entry.runtime_data.coordinator
        current_mode = coordinator.data.get("mode", Mode.OPTIMISED)
        is_heater_on = switch_state.state == "on"

        # Get maximum temperature for safety check
        temperatures = config_entry.data.get(CONF_TEMPERATURES, {})
        max_temperature = temperatures.get(CONF_MAX_TEMPERATURE, 75.0)

        # Get battery SoC if battery-aware is enabled
        battery_soc = None
        battery_aware = config_entry.options.get("battery_aware", False)
        if battery_aware:
            battery_soc_entity_id = config_entry.options.get("battery_soc_entity_id")
            if battery_soc_entity_id:
                battery_state = hass.states.get(battery_soc_entity_id)
                if battery_state and battery_state.state not in ("unknown", "unavailable"):
                    try:
                        battery_soc = float(battery_state.state)
                    except (ValueError, TypeError):
                        LOGGER.warning(
                            "Invalid battery SoC value from %s: %s", battery_soc_entity_id, battery_state.state
                        )

        # Apply control logic
        control_logic = WaterHeaterControlLogic(config_entry, hass)
        should_turn_on, is_overtemp = control_logic.should_turn_on_heater(
            current_temp, current_mode, is_heater_on, battery_soc, max_temperature
        )

        # Handle overtemperature condition
        if is_overtemp:
            # Force heater off
            if is_heater_on:
                LOGGER.error(
                    "OVERTEMPERATURE: Forcing heater OFF - Temp: %.1f°C, Max: %.1f°C", current_temp, max_temperature
                )
                await hass.services.async_call(
                    "homeassistant",
                    "turn_off",
                    {"entity_id": switch_entity_id},
                    blocking=False,
                )

            # Set status to Overtemp
            status_entity_id = f"sensor.{config_entry.title.lower().replace(' ', '_')}_status"
            status_entity = hass.states.get(status_entity_id)
            if status_entity:
                await hass.services.async_call(
                    "homeassistant",
                    "update_entity",
                    {"entity_id": status_entity_id},
                    blocking=False,
                )
            return

        # Control the heater if needed
        if should_turn_on and not is_heater_on:
            LOGGER.info("Turning on heater - Temperature: %.1f°C, Mode: %s", current_temp, current_mode)
            await hass.services.async_call(
                "homeassistant",
                "turn_on",
                {"entity_id": switch_entity_id},
                blocking=False,
            )
        elif not should_turn_on and is_heater_on:
            LOGGER.info("Turning off heater - Temperature: %.1f°C, Mode: %s", current_temp, current_mode)
            await hass.services.async_call(
                "homeassistant",
                "turn_off",
                {"entity_id": switch_entity_id},
                blocking=False,
            )

    except Exception:  # noqa: BLE001
        LOGGER.exception("Error in control logic evaluation")
