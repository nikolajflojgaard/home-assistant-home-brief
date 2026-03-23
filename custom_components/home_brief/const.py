"""Constants for Home Brief integration."""

from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "home_brief"

PLATFORMS: list[Platform] = [Platform.SENSOR]

CONF_NAME = "name"
CONF_WASHER_STATUS_ENTITY = "washer_status_entity"
CONF_WASHER_POWER_ENTITY = "washer_power_entity"
CONF_WASHER_DONE_THRESHOLD = "washer_done_threshold"
CONF_DRYER_STATUS_ENTITY = "dryer_status_entity"
CONF_DRYER_POWER_ENTITY = "dryer_power_entity"
CONF_DRYER_DONE_THRESHOLD = "dryer_done_threshold"
CONF_POWER_PRICE_ENTITY = "power_price_entity"
CONF_SOLAR_POWER_ENTITY = "solar_power_entity"
CONF_HOME_POWER_ENTITY = "home_power_entity"
CONF_OCCUPANCY_ENTITY = "occupancy_entity"
CONF_LIGHTS = "lights"
CONF_HUMIDITY_ENTITY = "humidity_entity"
CONF_HUMIDITY_THRESHOLD = "humidity_threshold"
CONF_AWAY_POWER_THRESHOLD = "away_power_threshold"

DEFAULT_NAME = "Home Brief"
DEFAULT_HUMIDITY_THRESHOLD = 70
DEFAULT_WASHER_DONE_THRESHOLD = 5
DEFAULT_DRYER_DONE_THRESHOLD = 5
DEFAULT_AWAY_POWER_THRESHOLD = 500

ENABLE_FRONTEND = True
