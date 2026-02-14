"""Websocket API for HACS Template."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant

from .const import DOMAIN


@websocket_api.websocket_command(
    {
        vol.Required("type"): "hacs_template/get_state",
        vol.Required("entry_id"): str,
    }
)
@websocket_api.async_response
async def ws_get_state(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    entry_id = msg["entry_id"]
    coordinator = hass.data.get(DOMAIN, {}).get(entry_id)
    if coordinator is None:
        connection.send_error(msg["id"], "entry_not_found", f"No entry found for entry_id={entry_id}")
        return
    state = await coordinator.store.async_load()
    connection.send_result(msg["id"], {"entry_id": entry_id, "counter": state.counter})


@websocket_api.websocket_command(
    {
        vol.Required("type"): "hacs_template/set_counter",
        vol.Required("entry_id"): str,
        vol.Required("value"): vol.Coerce(int),
    }
)
@websocket_api.async_response
async def ws_set_counter(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    entry_id = msg["entry_id"]
    coordinator = hass.data.get(DOMAIN, {}).get(entry_id)
    if coordinator is None:
        connection.send_error(msg["id"], "entry_not_found", f"No entry found for entry_id={entry_id}")
        return
    state = await coordinator.store.async_set_counter(int(msg["value"]))
    await coordinator.async_request_refresh()
    connection.send_result(msg["id"], {"entry_id": entry_id, "counter": state.counter})


@websocket_api.websocket_command({vol.Required("type"): "hacs_template/list_entries"})
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
    websocket_api.async_register_command(hass, ws_get_state)
    websocket_api.async_register_command(hass, ws_set_counter)
    websocket_api.async_register_command(hass, ws_list_entries)
