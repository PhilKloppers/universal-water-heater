"""Constants for universal_water_heater."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

# Integration metadata
DOMAIN = "universal_water_heater"
ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"

# Platform parallel updates - applied to all platforms
PARALLEL_UPDATES = 1

# Default configuration values
DEFAULT_UPDATE_INTERVAL_HOURS = 1
DEFAULT_ENABLE_DEBUGGING = False
