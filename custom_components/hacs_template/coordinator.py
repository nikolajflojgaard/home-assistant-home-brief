"""Coordinator for HACS Template."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import HacsTemplateApi, HacsTemplateApiError, HacsTemplateAuthError
from .const import CONF_API_KEY, CONF_HOST
from .storage import HacsTemplateStore, StoredState

_LOGGER = logging.getLogger(__name__)


class HacsTemplateCoordinator(DataUpdateCoordinator[StoredState]):
    """Coordinates data fetching and storage."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.store = HacsTemplateStore(hass, entry.entry_id)
        host = entry.options.get(CONF_HOST, entry.data.get(CONF_HOST, ""))
        api_key = entry.options.get(CONF_API_KEY, entry.data.get(CONF_API_KEY, ""))
        self.api = HacsTemplateApi(hass, host=str(host or ""), api_key=str(api_key or ""))

        super().__init__(
            hass,
            logger=_LOGGER,
            name=f"hacs_template_{entry.entry_id}",
            update_interval=timedelta(minutes=30),
        )

    async def _async_update_data(self) -> StoredState:
        try:
            _ = await self.api.async_get_data()
        except HacsTemplateAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except HacsTemplateApiError as err:
            raise UpdateFailed(str(err)) from err
        except Exception as err:  # noqa: BLE001
            raise UpdateFailed(str(err)) from err

        # In real integrations you likely merge the new data into storage here.
        return await self.store.async_load()
