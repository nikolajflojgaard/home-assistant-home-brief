"""HACS Template integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, ENABLE_FRONTEND, PLATFORMS
from .coordinator import HacsTemplateCoordinator
from .frontend import async_register_frontend
from .services import async_register as async_register_services
from .websocket_api import async_register as async_register_ws

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, _config: dict[str, Any]) -> bool:
    """Set up domain-level resources."""
    hass.data.setdefault(DOMAIN, {})
    if not hass.data[DOMAIN].get("ws_registered"):
        async_register_ws(hass)
        hass.data[DOMAIN]["ws_registered"] = True
    if not hass.data[DOMAIN].get("services_registered"):
        await async_register_services(hass)
        hass.data[DOMAIN]["services_registered"] = True
    if ENABLE_FRONTEND and not hass.data[DOMAIN].get("frontend_registered"):
        await async_register_frontend(hass)
        hass.data[DOMAIN]["frontend_registered"] = True
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from a config entry."""
    coordinator = HacsTemplateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    _LOGGER.debug("Setup complete for entry_id=%s", entry.entry_id)
    return True


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate old config entries.

    This is separate from storage migrations (see storage.py). Use it when you
    change config entry data/options or bump ConfigFlow.VERSION.
    """
    if entry.version < 2:
        data = dict(entry.data)
        # v1 only had name. v2 adds host/api_key (optional), default to empty.
        data.setdefault("host", "")
        data.setdefault("api_key", "")
        hass.config_entries.async_update_entry(entry, data=data, version=2)
        _LOGGER.debug("Migrated config entry %s to v2", entry.entry_id)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update by reloading."""
    await hass.config_entries.async_reload(entry.entry_id)
