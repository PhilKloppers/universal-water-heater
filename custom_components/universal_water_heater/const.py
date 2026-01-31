"""Constants for universal_water_heater."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

# Integration metadata
DOMAIN = "universal_water_heater"

# Platform parallel updates - applied to all platforms
PARALLEL_UPDATES = 1

# Default configuration values
DEFAULT_ENABLE_DEBUGGING = False

# Battery configuration keys
CONF_BATTERY_AWARE = "battery_aware"
CONF_BATTERY_THRESHOLD = "battery_threshold"
CONF_BATTERY_RESUME_THRESHOLD = "battery_resume_threshold"
CONF_BATTERY_SOC_ENTITY_ID = "battery_soc_entity_id"

# Battery defaults
DEFAULT_BATTERY_AWARE = False
DEFAULT_BATTERY_THRESHOLD = 20
DEFAULT_BATTERY_RESUME_THRESHOLD = 35  # Default: Resume at 35% (20% + 15%)

# Temperature configuration keys
CONF_TEMPERATURES = "temperatures"
CONF_NORMAL_TEMPERATURE = "normal_temperature"
CONF_ECO_TEMPERATURE = "eco_temperature"
CONF_MAX_TEMPERATURE = "max_temperature"
CONF_HYSTERESIS = "hysteresis"

# Temperature defaults
DEFAULT_NORMAL_TEMPERATURE = 65.0
DEFAULT_ECO_TEMPERATURE = 55.0
DEFAULT_MAX_TEMPERATURE = 75.0
DEFAULT_HYSTERESIS = 4.0

# Optimized mode configuration keys
CONF_USE_SOLAR_CONTROL = "use_solar_control"
CONF_NORMAL_MODE_START = "normal_mode_start"
CONF_NORMAL_MODE_END = "normal_mode_end"
CONF_ECO_MODE_START = "eco_mode_start"
CONF_ECO_MODE_END = "eco_mode_end"
CONF_SUN_ENTITY_ID = "sun_entity_id"
CONF_SUN_ANGLE = "sun_angle"

# Optimized mode defaults
DEFAULT_USE_SOLAR_CONTROL = False
DEFAULT_SUN_ANGLE = 0
