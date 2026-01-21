"""API package for universal_water_heater."""

from .client import (
    UniversalWaterHeaterApiClient,
    UniversalWaterHeaterApiClientAuthenticationError,
    UniversalWaterHeaterApiClientCommunicationError,
    UniversalWaterHeaterApiClientError,
)

__all__ = [
    "UniversalWaterHeaterApiClient",
    "UniversalWaterHeaterApiClientAuthenticationError",
    "UniversalWaterHeaterApiClientCommunicationError",
    "UniversalWaterHeaterApiClientError",
]
