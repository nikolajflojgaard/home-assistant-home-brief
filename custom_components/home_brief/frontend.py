"""Frontend asset registration for Home Brief."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

CARD_STATIC_URL = "/home_brief_files/home-brief-card.js"
_MANIFEST_PATH = Path(__file__).parent / "manifest.json"


@lru_cache(maxsize=1)
def _frontend_resource_url() -> str:
    """Build a stable cache-busting URL for the card resource."""
    version = json.loads(_MANIFEST_PATH.read_text(encoding="utf-8")).get("version", "dev")
    return f"{CARD_STATIC_URL}?v={version}"


async def async_register_frontend(hass: HomeAssistant) -> None:
    card_path = Path(__file__).parent / "frontend" / "home-brief-card.js"
    await hass.http.async_register_static_paths(
        [StaticPathConfig(CARD_STATIC_URL, str(card_path), cache_headers=False)]
    )
    add_extra_js_url(hass, _frontend_resource_url())
