"""Config flow for Home Brief."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_AWAY_POWER_THRESHOLD,
    CONF_DRYER_DONE_THRESHOLD,
    CONF_DRYER_POWER_ENTITY,
    CONF_DRYER_STATUS_ENTITY,
    CONF_HOME_POWER_ENTITY,
    CONF_HUMIDITY_ENTITY,
    CONF_HUMIDITY_THRESHOLD,
    CONF_LIGHTS,
    CONF_NAME,
    CONF_OCCUPANCY_ENTITY,
    CONF_POWER_PRICE_ENTITY,
    CONF_SOLAR_POWER_ENTITY,
    CONF_WASHER_DONE_THRESHOLD,
    CONF_WASHER_POWER_ENTITY,
    CONF_WASHER_STATUS_ENTITY,
    DEFAULT_AWAY_POWER_THRESHOLD,
    DEFAULT_DRYER_DONE_THRESHOLD,
    DEFAULT_HUMIDITY_THRESHOLD,
    DEFAULT_NAME,
    DEFAULT_WASHER_DONE_THRESHOLD,
    DOMAIN,
)
from .discovery import discover_defaults


def _schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=defaults.get(CONF_NAME, DEFAULT_NAME)): str,
            vol.Optional(CONF_WASHER_STATUS_ENTITY, default=defaults.get(CONF_WASHER_STATUS_ENTITY)): selector.EntitySelector(selector.EntitySelectorConfig()),
            vol.Optional(CONF_WASHER_POWER_ENTITY, default=defaults.get(CONF_WASHER_POWER_ENTITY)): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
            vol.Optional(CONF_WASHER_DONE_THRESHOLD, default=defaults.get(CONF_WASHER_DONE_THRESHOLD, DEFAULT_WASHER_DONE_THRESHOLD)): selector.NumberSelector(selector.NumberSelectorConfig(min=0, max=50, mode=selector.NumberSelectorMode.BOX)),
            vol.Optional(CONF_DRYER_STATUS_ENTITY, default=defaults.get(CONF_DRYER_STATUS_ENTITY)): selector.EntitySelector(selector.EntitySelectorConfig()),
            vol.Optional(CONF_DRYER_POWER_ENTITY, default=defaults.get(CONF_DRYER_POWER_ENTITY)): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
            vol.Optional(CONF_DRYER_DONE_THRESHOLD, default=defaults.get(CONF_DRYER_DONE_THRESHOLD, DEFAULT_DRYER_DONE_THRESHOLD)): selector.NumberSelector(selector.NumberSelectorConfig(min=0, max=50, mode=selector.NumberSelectorMode.BOX)),
            vol.Optional(CONF_POWER_PRICE_ENTITY, default=defaults.get(CONF_POWER_PRICE_ENTITY)): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
            vol.Optional(CONF_SOLAR_POWER_ENTITY, default=defaults.get(CONF_SOLAR_POWER_ENTITY)): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
            vol.Optional(CONF_HOME_POWER_ENTITY, default=defaults.get(CONF_HOME_POWER_ENTITY)): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
            vol.Optional(CONF_OCCUPANCY_ENTITY, default=defaults.get(CONF_OCCUPANCY_ENTITY)): selector.EntitySelector(selector.EntitySelectorConfig()),
            vol.Optional(CONF_HUMIDITY_ENTITY, default=defaults.get(CONF_HUMIDITY_ENTITY)): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
            vol.Optional(CONF_LIGHTS, default=defaults.get(CONF_LIGHTS, [])): selector.EntitySelector(selector.EntitySelectorConfig(domain="light", multiple=True)),
            vol.Optional(CONF_HUMIDITY_THRESHOLD, default=defaults.get(CONF_HUMIDITY_THRESHOLD, DEFAULT_HUMIDITY_THRESHOLD)): selector.NumberSelector(selector.NumberSelectorConfig(min=40, max=95, mode=selector.NumberSelectorMode.BOX)),
            vol.Optional(CONF_AWAY_POWER_THRESHOLD, default=defaults.get(CONF_AWAY_POWER_THRESHOLD, DEFAULT_AWAY_POWER_THRESHOLD)): selector.NumberSelector(selector.NumberSelectorConfig(min=100, max=5000, mode=selector.NumberSelectorMode.BOX)),
        }
    )


class HomeBriefConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            name = str(user_input.get(CONF_NAME, DEFAULT_NAME)).strip() or DEFAULT_NAME
            await self.async_set_unique_id(name.lower())
            self._abort_if_unique_id_configured()
            data = dict(user_input)
            data[CONF_NAME] = name
            return self.async_create_entry(title=name, data=data)

        defaults = discover_defaults(self.hass)
        defaults[CONF_NAME] = DEFAULT_NAME
        return self.async_show_form(step_id="user", data_schema=_schema(defaults))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return HomeBriefOptionsFlow(config_entry)


class HomeBriefOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            name = str(user_input.get(CONF_NAME, DEFAULT_NAME)).strip() or DEFAULT_NAME
            user_input[CONF_NAME] = name
            return self.async_create_entry(title="", data=user_input)

        current = discover_defaults(self.hass)
        current.update(dict(self.config_entry.data))
        current.update(self.config_entry.options)
        return self.async_show_form(step_id="init", data_schema=_schema(current))
