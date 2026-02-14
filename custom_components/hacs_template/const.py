"""Constants for HACS Template integration."""

from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "hacs_template"

PLATFORMS: list[Platform] = [Platform.SENSOR]

CONF_NAME = "name"
CONF_HOST = "host"
CONF_API_KEY = "api_key"

DEFAULT_NAME = "HACS Template"
DEFAULT_HOST = ""
DEFAULT_API_KEY = ""

# Optional: set to True if you want to auto-register frontend resources from frontend.py.
ENABLE_FRONTEND = False

# Dispatcher signals
SIGNAL_DATA_UPDATED = f"{DOMAIN}_data_updated"
