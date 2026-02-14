"""Persistent storage for HACS Template.

Use this as your "database" for small-to-medium payloads stored in HA .storage.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DOMAIN

_STORAGE_VERSION = 1


@dataclass(slots=True)
class StoredState:
    """Example stored state payload."""

    counter: int = 0


class HacsTemplateStore:
    """Store wrapper for one config entry."""

    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        self._store: Store[dict[str, Any]] = Store(hass, _STORAGE_VERSION, f"{DOMAIN}_{entry_id}")
        self._data: dict[str, Any] | None = None

    async def async_load(self) -> StoredState:
        if self._data is None:
            self._data = await self._store.async_load() or {}
        return StoredState(counter=int(self._data.get("counter") or 0))

    async def async_increment(self) -> StoredState:
        state = await self.async_load()
        next_state = StoredState(counter=state.counter + 1)
        self._data = {"counter": next_state.counter}
        await self._store.async_save(self._data)
        return next_state

    async def async_set_counter(self, value: int) -> StoredState:
        next_state = StoredState(counter=max(0, int(value)))
        self._data = {"counter": next_state.counter}
        await self._store.async_save(self._data)
        return next_state

