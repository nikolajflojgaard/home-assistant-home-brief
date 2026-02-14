"""Entity helpers for HACS Template."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo

from .const import CONF_HOST, CONF_NAME, DEFAULT_NAME, DOMAIN


def device_info_from_entry(entry) -> DeviceInfo:
    """Create a stable DeviceInfo for entities in this integration."""
    name = entry.options.get(CONF_NAME, entry.data.get(CONF_NAME, DEFAULT_NAME))
    host = str(entry.options.get(CONF_HOST, entry.data.get(CONF_HOST, "")) or "").strip()

    identifiers = {(DOMAIN, entry.entry_id)}
    if host:
        identifiers.add((DOMAIN, host))

    return DeviceInfo(
        identifiers=identifiers,
        name=str(name),
        manufacturer="Template",
        model="HACS Template Integration",
        configuration_url=f"http://{host}" if host else None,
    )

