"""Persistent storage for Home Brief."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DOMAIN

_STORAGE_VERSION = 6


@dataclass(slots=True)
class ApplianceState:
    """Persisted state for one appliance."""

    running: bool = False
    done: bool = False
    done_at: str = ""
    last_power: float | None = None


@dataclass(slots=True)
class DiscoveryState:
    """Persisted discovery snapshot."""

    defaults: dict[str, Any] = field(default_factory=dict)
    summary: dict[str, Any] = field(default_factory=dict)
    scanned_at: str = ""


@dataclass(slots=True)
class MorningBriefState:
    """Persisted structured morning brief payload."""

    payload: dict[str, Any] = field(default_factory=dict)
    published_at: str = ""
    source: str = ""


@dataclass(slots=True)
class PersonProfile:
    """Persisted person profile for personalized brief behavior."""

    id: str
    name: str
    aliases: list[str] = field(default_factory=list)
    interests: list[str] = field(default_factory=list)
    focus_mode: str = "balanced"
    show_household: bool = True
    show_personal: bool = True
    show_ambient: bool = True


@dataclass(slots=True)
class ProfileState:
    """Persisted profile model state."""

    active_profile_id: str = "nikolaj"
    profiles: list[PersonProfile] = field(default_factory=list)


@dataclass(slots=True)
class StoredState:
    """Stored Home Brief state."""

    washer: ApplianceState = field(default_factory=ApplianceState)
    dryer: ApplianceState = field(default_factory=ApplianceState)
    discovery: DiscoveryState = field(default_factory=DiscoveryState)
    morning_brief: MorningBriefState = field(default_factory=MorningBriefState)
    profiles: ProfileState = field(default_factory=ProfileState)
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


def _discovery_from_raw(raw: dict[str, Any] | None) -> dict[str, Any]:
    raw = raw or {}
    defaults = raw.get("defaults") if isinstance(raw.get("defaults"), dict) else {}
    summary = raw.get("summary") if isinstance(raw.get("summary"), dict) else {}
    return {
        "defaults": defaults,
        "summary": summary,
        "scanned_at": str(raw.get("scanned_at") or ""),
    }


def _morning_brief_from_raw(raw: dict[str, Any] | None) -> dict[str, Any]:
    raw = raw or {}
    payload = raw.get("payload") if isinstance(raw.get("payload"), dict) else {}
    return {
        "payload": payload,
        "published_at": str(raw.get("published_at") or ""),
        "source": str(raw.get("source") or ""),
    }


def _default_profile_state() -> dict[str, Any]:
    return {
        "active_profile_id": "nikolaj",
        "profiles": [
            {
                "id": "nikolaj",
                "name": "Nikolaj",
                "aliases": ["nikolaj"],
                "interests": ["chores", "energy", "weather"],
                "focus_mode": "balanced",
                "show_household": True,
                "show_personal": True,
                "show_ambient": True,
            }
        ],
    }


def _profiles_from_raw(raw: dict[str, Any] | None) -> dict[str, Any]:
    raw = raw or {}
    profiles_raw = raw.get("profiles") if isinstance(raw.get("profiles"), list) else []
    profiles: list[dict[str, Any]] = []
    for item in profiles_raw:
        if not isinstance(item, dict):
            continue
        profile_id = str(item.get("id") or "").strip()
        name = str(item.get("name") or "").strip()
        if not profile_id or not name:
            continue
        aliases = [str(alias).strip() for alias in item.get("aliases", []) if str(alias).strip()]
        interests = [str(interest).strip() for interest in item.get("interests", []) if str(interest).strip()]
        profiles.append(
            {
                "id": profile_id,
                "name": name,
                "aliases": aliases,
                "interests": interests,
                "focus_mode": str(item.get("focus_mode") or "balanced"),
                "show_household": bool(item.get("show_household", True)),
                "show_personal": bool(item.get("show_personal", True)),
                "show_ambient": bool(item.get("show_ambient", True)),
            }
        )

    if not profiles:
        return _default_profile_state()

    active_profile_id = str(raw.get("active_profile_id") or profiles[0]["id"])
    if active_profile_id not in {item["id"] for item in profiles}:
        active_profile_id = profiles[0]["id"]
    return {
        "active_profile_id": active_profile_id,
        "profiles": profiles,
    }


def _migrate(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": 6,
        "washer": _appliance_from_raw(raw.get("washer") if isinstance(raw, dict) else None),
        "dryer": _appliance_from_raw(raw.get("dryer") if isinstance(raw, dict) else None),
        "discovery": _discovery_from_raw(raw.get("discovery") if isinstance(raw, dict) else None),
        "morning_brief": _morning_brief_from_raw(raw.get("morning_brief") if isinstance(raw, dict) else None),
        "profiles": _profiles_from_raw(raw.get("profiles") if isinstance(raw, dict) else None),
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
            if schema < _STORAGE_VERSION:
                self._data = _migrate(self._data)
                await self._store.async_save(self._data)

        return StoredState(
            washer=ApplianceState(**_appliance_from_raw(self._data.get("washer"))),
            dryer=ApplianceState(**_appliance_from_raw(self._data.get("dryer"))),
            discovery=DiscoveryState(**_discovery_from_raw(self._data.get("discovery"))),
            morning_brief=MorningBriefState(**_morning_brief_from_raw(self._data.get("morning_brief"))),
            profiles=ProfileState(
                active_profile_id=_profiles_from_raw(self._data.get("profiles")).get("active_profile_id", "nikolaj"),
                profiles=[PersonProfile(**item) for item in _profiles_from_raw(self._data.get("profiles")).get("profiles", [])],
            ),
            updated_at=str(self._data.get("updated_at") or ""),
        )

    async def async_save_state(self, state: StoredState) -> StoredState:
        self._data = {
            "schema": _STORAGE_VERSION,
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
            "discovery": {
                "defaults": state.discovery.defaults,
                "summary": state.discovery.summary,
                "scanned_at": state.discovery.scanned_at,
            },
            "morning_brief": {
                "payload": state.morning_brief.payload,
                "published_at": state.morning_brief.published_at,
                "source": state.morning_brief.source,
            },
            "profiles": {
                "active_profile_id": state.profiles.active_profile_id,
                "profiles": [
                    {
                        "id": profile.id,
                        "name": profile.name,
                        "aliases": profile.aliases,
                        "interests": profile.interests,
                        "focus_mode": profile.focus_mode,
                        "show_household": profile.show_household,
                        "show_personal": profile.show_personal,
                        "show_ambient": profile.show_ambient,
                    }
                    for profile in state.profiles.profiles
                ],
            },
            "updated_at": _now_iso(),
        }
        await self._store.async_save(self._data)
        return await self.async_load()
