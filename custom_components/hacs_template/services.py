"""Services for HACS Template."""

from __future__ import annotations

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse

from .const import DOMAIN

SERVICE_INCREMENT = "increment_counter"
SERVICE_SET = "set_counter"

_SET_SCHEMA = vol.Schema({vol.Required("entry_id"): str, vol.Required("value"): vol.Coerce(int)})
_INCREMENT_SCHEMA = vol.Schema({vol.Required("entry_id"): str})


async def async_register(hass: HomeAssistant) -> None:
    async def _async_increment(call: ServiceCall) -> ServiceResponse:
        entry_id = str(call.data["entry_id"])
        coordinator = hass.data.get(DOMAIN, {}).get(entry_id)
        if coordinator is None:
            return {"ok": False, "error": "entry_not_found"}
        state = await coordinator.store.async_increment()
        await coordinator.async_request_refresh()
        return {"ok": True, "counter": state.counter}

    async def _async_set(call: ServiceCall) -> ServiceResponse:
        entry_id = str(call.data["entry_id"])
        value = int(call.data["value"])
        coordinator = hass.data.get(DOMAIN, {}).get(entry_id)
        if coordinator is None:
            return {"ok": False, "error": "entry_not_found"}
        state = await coordinator.store.async_set_counter(value)
        await coordinator.async_request_refresh()
        return {"ok": True, "counter": state.counter}

    if not hass.services.has_service(DOMAIN, SERVICE_INCREMENT):
        hass.services.async_register(
            DOMAIN,
            SERVICE_INCREMENT,
            _async_increment,
            schema=_INCREMENT_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )
    if not hass.services.has_service(DOMAIN, SERVICE_SET):
        hass.services.async_register(
            DOMAIN,
            SERVICE_SET,
            _async_set,
            schema=_SET_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )

