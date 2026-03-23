"""Websocket API for Home Brief."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant

from .const import DOMAIN


@websocket_api.websocket_command(
    {
        vol.Required("type"): "home_brief/get_brief",
        vol.Required("entry_id"): str,
    }
)
@websocket_api.async_response
async def ws_get_brief(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    entry_id = msg["entry_id"]
    coordinator = hass.data.get(DOMAIN, {}).get(entry_id)
    if coordinator is None:
        connection.send_error(msg["id"], "entry_not_found", f"No entry found for entry_id={entry_id}")
        return
    data = coordinator.data
    connection.send_result(
        msg["id"],
        {
            "entry_id": entry_id,
            "summary": data.summary,
            "insights": data.insights,
            "stats": data.stats,
        },
    )


@websocket_api.websocket_command({vol.Required("type"): "home_brief/list_entries"})
@websocket_api.async_response
async def ws_list_entries(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    entries = hass.config_entries.async_entries(DOMAIN)
    payload = [{"entry_id": entry.entry_id, "title": entry.title} for entry in entries]
    connection.send_result(msg["id"], {"entries": payload})


def async_register(hass: HomeAssistant) -> None:
    websocket_api.async_register_command(hass, ws_get_brief)
    websocket_api.async_register_command(hass, ws_list_entries)
