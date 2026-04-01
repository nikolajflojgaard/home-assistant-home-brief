"""Services for Home Brief."""

from __future__ import annotations

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse

from .const import DOMAIN

SERVICE_GET_BRIEF = "get_brief"
SERVICE_GET_ACTIONS = "get_actions"
SERVICE_RESCAN = "rescan"

_GET_BRIEF_SCHEMA = vol.Schema({vol.Required("entry_id"): str})
_RESCAN_SCHEMA = vol.Schema({vol.Optional("entry_id"): str})


async def async_register(hass: HomeAssistant) -> None:
    async def _async_get_brief(call: ServiceCall) -> ServiceResponse:
        entry_id = str(call.data["entry_id"])
        coordinator = hass.data.get(DOMAIN, {}).get(entry_id)
        if coordinator is None:
            return {"ok": False, "error": "entry_not_found"}
        data = coordinator.data
        return {
            "ok": True,
            "summary": data.summary,
            "insights": data.insights,
            "stats": data.stats,
        }

    async def _async_get_actions(call: ServiceCall) -> ServiceResponse:
        entry_id = str(call.data["entry_id"])
        coordinator = hass.data.get(DOMAIN, {}).get(entry_id)
        if coordinator is None:
            return {"ok": False, "error": "entry_not_found"}
        data = coordinator.data
        stats = data.stats or {}
        return {
            "ok": True,
            "entry_id": entry_id,
            "top_action": stats.get("top_action"),
            "recommended_actions": stats.get("recommended_actions", []),
            "recommended_action_count": stats.get("recommended_action_count", 0),
        }

    async def _async_rescan(call: ServiceCall) -> ServiceResponse:
        entry_id = call.data.get("entry_id")
        coordinators = hass.data.get(DOMAIN, {})
        targets = []
        if entry_id:
            coordinator = coordinators.get(str(entry_id))
            if coordinator is None:
                return {"ok": False, "error": "entry_not_found"}
            targets = [coordinator]
        else:
            targets = [value for key, value in coordinators.items() if key not in {"ws_registered", "services_registered", "frontend_registered"}]

        results: list[dict[str, object]] = []
        for coordinator in targets:
            await coordinator.async_refresh_discovery()
            await coordinator.async_request_refresh()
            results.append(
                {
                    "entry_id": coordinator.entry.entry_id,
                    "title": coordinator.entry.title,
                    "discovery": coordinator.discovery_summary,
                    "scanned_at": coordinator.discovery_scanned_at,
                }
            )

        return {"ok": True, "entries": results, "count": len(results)}

    if not hass.services.has_service(DOMAIN, SERVICE_GET_BRIEF):
        hass.services.async_register(
            DOMAIN,
            SERVICE_GET_BRIEF,
            _async_get_brief,
            schema=_GET_BRIEF_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_GET_ACTIONS):
        hass.services.async_register(
            DOMAIN,
            SERVICE_GET_ACTIONS,
            _async_get_actions,
            schema=_GET_BRIEF_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_RESCAN):
        hass.services.async_register(
            DOMAIN,
            SERVICE_RESCAN,
            _async_rescan,
            schema=_RESCAN_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )
