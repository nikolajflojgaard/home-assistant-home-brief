"""Diagnostics support for Home Brief."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = hass.data.get(DOMAIN, {}).get(entry.entry_id)

    payload: dict[str, Any] = {
        "entry": {
            "entry_id": entry.entry_id,
            "title": entry.title,
            "version": entry.version,
            "data": dict(entry.data),
            "options": dict(entry.options),
        }
    }

    if coordinator is not None:
        payload["coordinator"] = {
            "last_update_success": bool(getattr(coordinator, "last_update_success", False)),
            "last_exception": repr(getattr(coordinator, "last_exception", None)),
            "summary": getattr(getattr(coordinator, "data", None), "summary", None),
            "insights": getattr(getattr(coordinator, "data", None), "insights", None),
            "stats": getattr(getattr(coordinator, "data", None), "stats", None),
        }

    return payload
