"""WeatherWizz data coordinator."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    WeatherWizzApiClient,
    WeatherWizzAuthenticationError,
    WeatherWizzConnectionError,
)

LOGGER = logging.getLogger(__name__)


class WeatherWizzCoordinator(DataUpdateCoordinator[dict]):
    """Coordinate WeatherWizz cloud updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: WeatherWizzApiClient,
        scan_interval: int,
    ) -> None:
        super().__init__(
            hass,
            LOGGER,
            name="WeatherWizz",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client

    async def _async_update_data(self) -> dict:
        try:
            return await self.client.async_stations()
        except WeatherWizzAuthenticationError as error:
            raise ConfigEntryAuthFailed from error
        except WeatherWizzConnectionError as error:
            raise UpdateFailed(str(error)) from error
