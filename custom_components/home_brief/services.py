"""Services for Home Brief."""

from __future__ import annotations

from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse

from .const import DOMAIN

SERVICE_GET_BRIEF = "get_brief"


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

    if not hass.services.has_service(DOMAIN, SERVICE_GET_BRIEF):
        hass.services.async_register(
            DOMAIN,
            SERVICE_GET_BRIEF,
            _async_get_brief,
            supports_response=SupportsResponse.ONLY,
        )
