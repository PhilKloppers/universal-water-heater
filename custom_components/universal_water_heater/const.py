"""Constants for universal_water_heater."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

# Integration metadata
DOMAIN = "universal_water_heater"

# Platform parallel updates - applied to all platforms
PARALLEL_UPDATES = 1

# Default configuration values
DEFAULT_ENABLE_DEBUGGING = False

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
