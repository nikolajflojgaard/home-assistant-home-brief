"""Persistent storage for Home Brief."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DOMAIN

_STORAGE_VERSION = 3


@dataclass(slots=True)
class ApplianceState:
    """Persisted state for one appliance."""

    running: bool = False
    done: bool = False
    done_at: str = ""
    last_power: float | None = None


@dataclass(slots=True)
class StoredState:
    """Stored Home Brief state."""

    washer: ApplianceState = field(default_factory=ApplianceState)
    dryer: ApplianceState = field(default_factory=ApplianceState)
    updated_at: str = ""


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _appliance_from_raw(raw: dict[str, Any] | None) -> dict[str, Any]:
    raw = raw or {}
    return {
        "running": bool(raw.get("running", False)),
        "done": bool(raw.get("done", False)),
        "done_at": str(raw.get("done_at") or ""),
        "last_power": raw.get("last_power"),
    }


def _migrate(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": 3,
        "washer": _appliance_from_raw(raw.get("washer") if isinstance(raw, dict) else None),
        "dryer": _appliance_from_raw(raw.get("dryer") if isinstance(raw, dict) else None),
        "updated_at": _now_iso(),
    }


class HomeBriefStore:
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
            if schema < 3:
                self._data = _migrate(self._data)
                await self._store.async_save(self._data)

        return StoredState(
            washer=ApplianceState(**_appliance_from_raw(self._data.get("washer"))),
            dryer=ApplianceState(**_appliance_from_raw(self._data.get("dryer"))),
            updated_at=str(self._data.get("updated_at") or ""),
        )

    async def async_save_state(self, state: StoredState) -> StoredState:
        self._data = {
            "schema": 3,
            "washer": {
                "running": state.washer.running,
                "done": state.washer.done,
                "done_at": state.washer.done_at,
                "last_power": state.washer.last_power,
            },
            "dryer": {
                "running": state.dryer.running,
                "done": state.dryer.done,
                "done_at": state.dryer.done_at,
                "last_power": state.dryer.last_power,
            },
            "updated_at": _now_iso(),
        }
        await self._store.async_save(self._data)
        return await self.async_load()
