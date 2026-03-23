"""Entity helpers for Home Brief."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo

from .const import CONF_NAME, DEFAULT_NAME, DOMAIN


def device_info_from_entry(entry) -> DeviceInfo:
    """Create a stable DeviceInfo for entities in this integration."""
    name = entry.options.get(CONF_NAME, entry.data.get(CONF_NAME, DEFAULT_NAME))

    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=str(name),
        manufacturer="Nikolaj Fløjgaard",
        model="Home Brief",
    )
