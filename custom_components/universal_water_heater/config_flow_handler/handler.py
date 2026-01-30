"""
Config flow handler for universal_water_heater.

This module provides backwards compatibility by re-exporting the flow handlers
from their respective modules. The actual implementation is split across:

- config_flow.py: Main config flow (user, reconfigure)
- options_flow.py: Options flow for post-setup configuration
- subentry_flow.py: Template for future subentry flows
- schemas/: Voluptuous schemas for all forms
- validators/: Validation logic for user inputs

This structure keeps the code organized while allowing complex flows to grow
without becoming monolithic.

For more information:
https://developers.home-assistant.io/docs/config_entries_config_flow_handler
"""

from __future__ import annotations

from custom_components.universal_water_heater.config_flow_handler.config_flow import (
    UniversalWaterHeaterConfigFlowHandler,
)
from custom_components.universal_water_heater.config_flow_handler.options_flow import UniversalWaterHeaterOptionsFlow

# Re-export for backwards compatibility and external imports
__all__ = [
    "UniversalWaterHeaterConfigFlowHandler",
    "UniversalWaterHeaterOptionsFlow",
]
