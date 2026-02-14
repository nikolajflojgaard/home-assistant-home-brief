"""API layer for HACS Template.

Patterns included:
- aiohttp session injection via HA's shared session
- typed exceptions you can map to config flow / reauth
- a simple `async_validate()` hook

Replace this with your real IO (local device, cloud, etc).
"""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.helpers.aiohttp_client import async_get_clientsession


class HacsTemplateError(Exception):
    """Base error for the integration."""


class HacsTemplateAuthError(HacsTemplateError):
    """Raised when authentication fails or is missing."""


class HacsTemplateApiError(HacsTemplateError):
    """Raised for non-auth API failures."""


@dataclass(slots=True)
class ExampleData:
    """Data returned by the API."""

    value: int


class HacsTemplateApi:
    """Example API client.

    This is intentionally minimal. Use `async_get_clientsession(hass)` and keep IO here.
    """

    def __init__(self, hass, *, host: str, api_key: str) -> None:
        self._hass = hass
        self._host = (host or "").strip()
        self._api_key = (api_key or "").strip()
        self._session = async_get_clientsession(hass)

    async def async_validate(self) -> None:
        """Validate current credentials/settings.

        In real integrations, do a cheap request here. For the template we only
        enforce: if a host is set, an api_key must also be set.
        """
        if self._host and not self._api_key:
            raise HacsTemplateAuthError("Missing API key")

    async def async_get_data(self) -> ExampleData:
        """Fetch data from the API."""
        await self.async_validate()

        # Replace this with real IO using `self._session`.
        # Example:
        # async with self._session.get(f\"http://{self._host}/status\", headers={...}) as resp:
        #   ...
        return ExampleData(value=1)

