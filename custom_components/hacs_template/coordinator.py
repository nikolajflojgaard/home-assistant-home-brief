"""Coordinator for HACS Template."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import HacsTemplateApi
from .storage import HacsTemplateStore, StoredState

_LOGGER = logging.getLogger(__name__)


class HacsTemplateCoordinator(DataUpdateCoordinator[StoredState]):
    """Coordinates data fetching and storage."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.api = HacsTemplateApi()
        self.store = HacsTemplateStore(hass, entry.entry_id)

        super().__init__(
            hass,
            logger=_LOGGER,
            name=f"hacs_template_{entry.entry_id}",
            update_interval=timedelta(minutes=30),
        )

    async def _async_update_data(self) -> StoredState:
        # Example:
        # - fetch from API
        # - merge into storage
        # - return a stable data object
        _ = await self.api.async_get_data()
        return await self.store.async_load()
