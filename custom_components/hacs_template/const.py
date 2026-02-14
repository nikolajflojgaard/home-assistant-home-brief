"""Constants for HACS Template integration."""

from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "hacs_template"

PLATFORMS: list[Platform] = [Platform.SENSOR]

CONF_NAME = "name"

DEFAULT_NAME = "HACS Template"

# Dispatcher signals
SIGNAL_DATA_UPDATED = f"{DOMAIN}_data_updated"

