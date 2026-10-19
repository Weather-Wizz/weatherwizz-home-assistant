"""Config flow for WeatherWizz."""

from __future__ import annotations

from typing import Any

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import voluptuous as vol

from .api import (
    WeatherWizzApiClient,
    WeatherWizzAuthenticationError,
    WeatherWizzConnectionError,
)
from .const import (
    CONF_API_KEY,
    CONF_API_URL,
    CONF_SCAN_INTERVAL,
    DEFAULT_API_URL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)


async def validate_input(hass, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the API URL and key."""
    client = WeatherWizzApiClient(
        async_get_clientsession(hass),
        str(data[CONF_API_URL]).strip().rstrip("/"),
        str(data[CONF_API_KEY]).strip(),
    )
    return await client.async_account()


class WeatherWizzConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a WeatherWizz config flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Set up WeatherWizz from the UI."""
        errors: dict[str, str] = {}
        if user_input is not None:
            normalized = {
                CONF_API_URL: str(user_input[CONF_API_URL]).strip().rstrip("/"),
                CONF_API_KEY: str(user_input[CONF_API_KEY]).strip(),
            }
            try:
                account = await validate_input(self.hass, normalized)
            except WeatherWizzAuthenticationError:
                errors["base"] = "invalid_auth"
            except WeatherWizzConnectionError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(str(account["account_id"]))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="WeatherWizz", data=normalized)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_API_URL,
                        default=(user_input or {}).get(CONF_API_URL, DEFAULT_API_URL),
                    ): str,
                    vol.Required(CONF_API_KEY): str,
                }
            ),
            errors=errors,
        )

    async def async_step_reauth(self, entry_data: dict[str, Any]):
        """Start key reauthentication."""
        self._reauth_entry = self._get_reauth_entry()
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input: dict[str, Any] | None = None):
        """Replace a revoked or invalid key."""
        errors: dict[str, str] = {}
        if user_input is not None:
            updated_data = {
                **self._reauth_entry.data,
                CONF_API_KEY: str(user_input[CONF_API_KEY]).strip(),
            }
            try:
                await validate_input(self.hass, updated_data)
            except WeatherWizzAuthenticationError:
                errors["base"] = "invalid_auth"
            except WeatherWizzConnectionError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_update_reload_and_abort(
                    self._reauth_entry,
                    data_updates=updated_data,
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return WeatherWizzOptionsFlow()


class WeatherWizzOptionsFlow(config_entries.OptionsFlow):
    """Configure the WeatherWizz refresh interval."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): vol.All(int, vol.Range(min=30, max=3600))
                }
            ),
        )
