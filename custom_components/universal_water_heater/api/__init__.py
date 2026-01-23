"""API package for universal_water_heater."""

from .client import (
    UniversalWaterHeaterApiClient,
    UniversalWaterHeaterApiClientCommunicationError,
    UniversalWaterHeaterApiClientError,
)

__all__ = [
    "UniversalWaterHeaterApiClient",
    "UniversalWaterHeaterApiClientCommunicationError",
    "UniversalWaterHeaterApiClientError",
]
