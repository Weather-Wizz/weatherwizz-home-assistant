"""Async client for the WeatherWizz Home Assistant API."""

from __future__ import annotations

from typing import Any

import aiohttp


class WeatherWizzApiError(Exception):
    """Base WeatherWizz API error."""


class WeatherWizzAuthenticationError(WeatherWizzApiError):
    """The WeatherWizz key was rejected."""


class WeatherWizzConnectionError(WeatherWizzApiError):
    """WeatherWizz could not be reached."""


class WeatherWizzApiClient:
    """Small API client using Home Assistant's shared HTTP session."""

    def __init__(self, session: aiohttp.ClientSession, api_url: str, api_key: str) -> None:
        self._session = session
        self._api_url = api_url.rstrip("/")
        self._headers = {"Authorization": f"Bearer {api_key}"}

    async def _get(self, path: str) -> dict[str, Any]:
        try:
            async with self._session.get(
                f"{self._api_url}/{path.lstrip('/')}",
                headers=self._headers,
                timeout=aiohttp.ClientTimeout(total=20),
            ) as response:
                if response.status in (401, 403):
                    raise WeatherWizzAuthenticationError("The WeatherWizz key was rejected")
                if response.status >= 400:
                    raise WeatherWizzConnectionError(
                        f"WeatherWizz returned HTTP {response.status}"
                    )
                payload = await response.json()
        except WeatherWizzApiError:
            raise
        except (aiohttp.ClientError, TimeoutError, ValueError) as error:
            raise WeatherWizzConnectionError(str(error)) from error

        if not isinstance(payload, dict) or payload.get("ok") is not True:
            raise WeatherWizzConnectionError("WeatherWizz returned an invalid response")
        return payload

    async def async_account(self) -> dict[str, Any]:
        """Validate credentials and return the account identity."""
        return await self._get("account")

    async def async_stations(self) -> dict[str, Any]:
        """Return the stations and sensors permitted by the key."""
        return await self._get("stations")
