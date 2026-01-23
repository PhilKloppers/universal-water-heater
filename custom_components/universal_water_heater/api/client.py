"""
API Client for universal_water_heater.

This module provides the API client for communicating with external services.
It handles HTTP requests and error handling.

For more information on creating API clients:
https://developers.home-assistant.io/docs/api_lib_index
"""

from __future__ import annotations

import asyncio
import socket
from typing import Any

import aiohttp


class UniversalWaterHeaterApiClientError(Exception):
    """Base exception to indicate a general API error."""


class UniversalWaterHeaterApiClientCommunicationError(
    UniversalWaterHeaterApiClientError,
):
    """Exception to indicate a communication error with the API."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """
    Verify that the API response is valid.

    Raises appropriate exceptions for HTTP errors.

    Args:
        response: The aiohttp ClientResponse to verify.

    Raises:
        aiohttp.ClientResponseError: For HTTP errors.

    """
    response.raise_for_status()


class UniversalWaterHeaterApiClient:
    """
    API Client for Universal Water Heater integration.

    This client demonstrates API communication patterns
    for Home Assistant integrations. It handles HTTP requests and error handling.

    For more information on API clients:
    https://developers.home-assistant.io/docs/api_lib_index

    Attributes:
        _device_name: The device name for identification.
        _session: The aiohttp ClientSession for making requests.

    """

    def __init__(
        self,
        device_name: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """
        Initialize the API Client with device name.

        Args:
            device_name: The device name for identification.
            session: The aiohttp ClientSession to use for requests.

        """
        self._device_name = device_name
        self._session = session

    async def async_get_data(self) -> Any:
        """
        Get data from the API.

        This method fetches the current state and sensor data from the device.

        Returns:
            A dictionary containing the device data.

        Raises:
            UniversalWaterHeaterApiClientCommunicationError: If communication fails.
            UniversalWaterHeaterApiClientError: For other API errors.

        """
        return await self._api_wrapper(
            method="get",
            url="https://jsonplaceholder.typicode.com/posts/1",
            # For demo purposes with JSONPlaceholder
            # In production, use device_name for device identification
        )

    async def async_set_fan_speed(self, speed: str) -> Any:
        """
        Set the fan speed on the device.

        Args:
            speed: The fan speed to set (low, medium, high, auto).

        Returns:
            A dictionary containing the API response.

        Raises:
            UniversalWaterHeaterApiClientCommunicationError: If communication fails.
            UniversalWaterHeaterApiClientError: For other API errors.

        """
        # In production: Send request to change fan speed
        return await self._api_wrapper(
            method="patch",
            url="https://jsonplaceholder.typicode.com/posts/1",
            data={"fan_speed": speed, "device": self._device_name},
            headers={"Content-type": "application/json; charset=UTF-8"},
        )

    async def async_set_target_humidity(self, humidity: int) -> Any:
        """
        Set the target humidity on the device.

        Args:
            humidity: The target humidity percentage (30-80).

        Returns:
            A dictionary containing the API response.

        Raises:
            UniversalWaterHeaterApiClientCommunicationError: If communication fails.
            UniversalWaterHeaterApiClientError: For other API errors.

        """
        # In production: Send request to change humidity setting
        return await self._api_wrapper(
            method="patch",
            url="https://jsonplaceholder.typicode.com/posts/1",
            data={"target_humidity": humidity, "device": self._device_name},
            headers={"Content-type": "application/json; charset=UTF-8"},
        )

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        """
        Wrapper for API requests with error handling.

        This method handles all HTTP requests and translates exceptions
        into integration-specific exceptions.

        Args:
            method: The HTTP method (get, post, patch, etc.).
            url: The URL to request.
            data: Optional data to send in the request body.
            headers: Optional headers to include in the request.

        Returns:
            The JSON response from the API.

        Raises:
            UniversalWaterHeaterApiClientCommunicationError: If communication fails.
            UniversalWaterHeaterApiClientError: For other API errors.

        """
        try:
            async with asyncio.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                _verify_response_or_raise(response)
                return await response.json()

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise UniversalWaterHeaterApiClientCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise UniversalWaterHeaterApiClientCommunicationError(
                msg,
            ) from exception
        except Exception as exception:
            msg = f"Something really wrong happened! - {exception}"
            raise UniversalWaterHeaterApiClientError(
                msg,
            ) from exception
