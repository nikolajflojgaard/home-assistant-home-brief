"""Diagnostics support for Home Brief."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_DRYER_POWER_ENTITY,
    CONF_DRYER_STATUS_ENTITY,
    CONF_HOME_POWER_ENTITY,
    CONF_HUMIDITY_ENTITY,
    CONF_LIGHTS,
    CONF_OCCUPANCY_ENTITY,
    CONF_POWER_PRICE_ENTITY,
    CONF_SOLAR_POWER_ENTITY,
    CONF_WASHER_POWER_ENTITY,
    CONF_WASHER_STATUS_ENTITY,
    DOMAIN,
)
from .discovery import discover_defaults, effective_defaults, summarize_discovery

_TO_REDACT = {
    CONF_WASHER_STATUS_ENTITY,
    CONF_WASHER_POWER_ENTITY,
    CONF_DRYER_STATUS_ENTITY,
    CONF_DRYER_POWER_ENTITY,
    CONF_POWER_PRICE_ENTITY,
    CONF_SOLAR_POWER_ENTITY,
    CONF_HOME_POWER_ENTITY,
    CONF_OCCUPANCY_ENTITY,
    CONF_HUMIDITY_ENTITY,
    CONF_LIGHTS,
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    configured = dict(entry.data)
    configured.update(entry.options)
    defaults = discover_defaults(hass)

    payload: dict[str, Any] = {
        "entry": {
            "entry_id": entry.entry_id,
            "title": entry.title,
            "version": entry.version,
            "data": async_redact_data(dict(entry.data), _TO_REDACT),
            "options": async_redact_data(dict(entry.options), _TO_REDACT),
            "effective": async_redact_data(effective_defaults(configured=configured, discovered=defaults), _TO_REDACT),
        },
        "discovery": {
            "summary": summarize_discovery(defaults, configured),
            "defaults": async_redact_data(defaults, _TO_REDACT),
        },
    }

    if coordinator is not None:
        payload["coordinator"] = {
            "last_update_success": bool(getattr(coordinator, "last_update_success", False)),
            "last_exception": repr(getattr(coordinator, "last_exception", None)),
            "summary": getattr(getattr(coordinator, "data", None), "summary", None),
            "insights": getattr(getattr(coordinator, "data", None), "insights", None),
            "stats": async_redact_data(getattr(getattr(coordinator, "data", None), "stats", {}) or {}, {"missing_entities", "discovery_defaults", "effective_config"}),
            "stored_discovery": {
                "summary": getattr(coordinator, "discovery_summary", {}),
                "scanned_at": getattr(coordinator, "discovery_scanned_at", ""),
                "defaults": async_redact_data(getattr(coordinator, "discovery_defaults", {}), _TO_REDACT),
            },
        }

    return payload
