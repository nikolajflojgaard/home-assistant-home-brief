"""Persistent storage for HACS Template.

Use this as your "database" for small-to-medium payloads stored in HA .storage.

Patterns included:
- Schema versioning
- Backward-compatible migrations
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DOMAIN

_STORAGE_VERSION = 2


@dataclass(slots=True)
class StoredState:
    """Example stored state payload."""

    counter: int = 0
    updated_at: str = ""


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _migrate_to_v2(raw: dict[str, Any]) -> dict[str, Any]:
    # v1: {"counter": int}
    # v2: {"schema": 2, "counter": int, "updated_at": str}
    counter = 0
    if isinstance(raw, dict):
        try:
            counter = int(raw.get("counter") or 0)
        except (TypeError, ValueError):
            counter = 0
    return {"schema": 2, "counter": max(0, counter), "updated_at": _now_iso()}


class HacsTemplateStore:
    """Store wrapper for one config entry."""

    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        self._store: Store[dict[str, Any]] = Store(hass, _STORAGE_VERSION, f"{DOMAIN}_{entry_id}")
        self._data: dict[str, Any] | None = None

    async def async_load(self) -> StoredState:
        if self._data is None:
            self._data = await self._store.async_load() or {}
            if not isinstance(self._data, dict):
                self._data = {}

            schema = int(self._data.get("schema") or 1)
            if schema < 2:
                self._data = _migrate_to_v2(self._data)
                await self._store.async_save(self._data)

        return StoredState(
            counter=int(self._data.get("counter") or 0),
            updated_at=str(self._data.get("updated_at") or ""),
        )

    async def async_increment(self) -> StoredState:
        state = await self.async_load()
        next_state = StoredState(counter=state.counter + 1, updated_at=_now_iso())
        self._data = {"schema": 2, "counter": next_state.counter, "updated_at": next_state.updated_at}
        await self._store.async_save(self._data)
        return next_state

    async def async_set_counter(self, value: int) -> StoredState:
        next_state = StoredState(counter=max(0, int(value)), updated_at=_now_iso())
        self._data = {"schema": 2, "counter": next_state.counter, "updated_at": next_state.updated_at}
        await self._store.async_save(self._data)
        return next_state

