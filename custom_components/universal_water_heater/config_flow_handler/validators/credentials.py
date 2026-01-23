"""
Device name validators.

Validation functions for device name configuration.

When this file grows, consider splitting into:
- device.py: Device name validation
- api_connection.py: API connection testing
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


async def validate_device_name(hass: HomeAssistant, device_name: str) -> None:
    """
    Validate device name.

    Args:
        hass: Home Assistant instance.
        device_name: The device name to validate.

    Raises:
        ValueError: If device name is invalid (empty, too long, etc.).

    """
    if not device_name or not device_name.strip():
        msg = "Device name cannot be empty"
        raise ValueError(msg)

    if len(device_name) > 100:
        msg = "Device name must be less than 100 characters"
        raise ValueError(msg)


__all__ = [
    "validate_device_name",
]
