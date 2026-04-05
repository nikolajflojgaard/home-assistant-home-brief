"""Home Brief integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, ENABLE_FRONTEND, PLATFORMS
from .coordinator import HomeBriefCoordinator
from .frontend import async_register_frontend
from .services import async_register as async_register_services
from .websocket_api import async_register as async_register_ws

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class HomeBriefRuntimeData:
    entries: dict[str, HomeBriefCoordinator] = field(default_factory=dict)
    ws_registered: bool = False
    services_registered: bool = False
    frontend_registered: bool = False


async def async_setup(hass: HomeAssistant, _config: dict[str, Any]) -> bool:
    """Set up domain-level resources."""
    runtime = hass.data.setdefault(DOMAIN, HomeBriefRuntimeData())
    if not runtime.ws_registered:
        async_register_ws(hass)
        runtime.ws_registered = True
    if not runtime.services_registered:
        await async_register_services(hass)
        runtime.services_registered = True
    if ENABLE_FRONTEND and not runtime.frontend_registered:
        await async_register_frontend(hass)
        runtime.frontend_registered = True
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from a config entry."""
    coordinator = HomeBriefCoordinator(hass, entry)
    await coordinator.async_load_discovery_state()
    await coordinator.async_refresh_discovery()
    await coordinator.async_config_entry_first_refresh()
    runtime = hass.data.setdefault(DOMAIN, HomeBriefRuntimeData())
    runtime.entries[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    _LOGGER.debug("Setup complete for entry_id=%s", entry.entry_id)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        runtime = hass.data.get(DOMAIN)
        if runtime is not None:
            runtime.entries.pop(entry.entry_id, None)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update by reloading."""
    await hass.config_entries.async_reload(entry.entry_id)
