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
from .discovery import discover_defaults, effective_defaults, summarize_discovery

_SIGNAL_FIELDS: tuple[str, ...] = (
    CONF_WASHER_STATUS_ENTITY,
    CONF_WASHER_POWER_ENTITY,
    CONF_DRYER_STATUS_ENTITY,
    CONF_DRYER_POWER_ENTITY,
    CONF_POWER_PRICE_ENTITY,
    CONF_SOLAR_POWER_ENTITY,
    CONF_HOME_POWER_ENTITY,
    CONF_OCCUPANCY_ENTITY,
    CONF_HUMIDITY_ENTITY,
)


def _optional_with_default(key: str, defaults: dict[str, Any]) -> Any:
    value = defaults.get(key)
    if value is None:
        return vol.Optional(key)
    return vol.Optional(key, default=value)


def _schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=defaults.get(CONF_NAME, DEFAULT_NAME)): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
            ),
            _optional_with_default(CONF_WASHER_STATUS_ENTITY, defaults): selector.EntitySelector(
                selector.EntitySelectorConfig(multiple=False)
            ),
            _optional_with_default(CONF_WASHER_POWER_ENTITY, defaults): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", multiple=False)
            ),
            vol.Optional(CONF_WASHER_DONE_THRESHOLD, default=defaults.get(CONF_WASHER_DONE_THRESHOLD, DEFAULT_WASHER_DONE_THRESHOLD)): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0, max=50, mode=selector.NumberSelectorMode.BOX, unit_of_measurement="W")
            ),
            _optional_with_default(CONF_DRYER_STATUS_ENTITY, defaults): selector.EntitySelector(
                selector.EntitySelectorConfig(multiple=False)
            ),
            _optional_with_default(CONF_DRYER_POWER_ENTITY, defaults): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", multiple=False)
            ),
            vol.Optional(CONF_DRYER_DONE_THRESHOLD, default=defaults.get(CONF_DRYER_DONE_THRESHOLD, DEFAULT_DRYER_DONE_THRESHOLD)): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0, max=50, mode=selector.NumberSelectorMode.BOX, unit_of_measurement="W")
            ),
            _optional_with_default(CONF_POWER_PRICE_ENTITY, defaults): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", multiple=False)
            ),
            _optional_with_default(CONF_SOLAR_POWER_ENTITY, defaults): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", multiple=False)
            ),
            _optional_with_default(CONF_HOME_POWER_ENTITY, defaults): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", multiple=False)
            ),
            _optional_with_default(CONF_OCCUPANCY_ENTITY, defaults): selector.EntitySelector(
                selector.EntitySelectorConfig(multiple=False)
            ),
            _optional_with_default(CONF_HUMIDITY_ENTITY, defaults): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", multiple=False)
            ),
            vol.Optional(CONF_LIGHTS, default=defaults.get(CONF_LIGHTS, [])): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="light", multiple=True)
            ),
            vol.Optional(CONF_HUMIDITY_THRESHOLD, default=defaults.get(CONF_HUMIDITY_THRESHOLD, DEFAULT_HUMIDITY_THRESHOLD)): selector.NumberSelector(
                selector.NumberSelectorConfig(min=40, max=95, mode=selector.NumberSelectorMode.BOX, unit_of_measurement="%")
            ),
            vol.Optional(CONF_AWAY_POWER_THRESHOLD, default=defaults.get(CONF_AWAY_POWER_THRESHOLD, DEFAULT_AWAY_POWER_THRESHOLD)): selector.NumberSelector(
                selector.NumberSelectorConfig(min=100, max=5000, mode=selector.NumberSelectorMode.BOX, unit_of_measurement="W")
            ),
        }
    )


def _normalize_input(user_input: dict[str, Any]) -> dict[str, Any]:
    data = dict(user_input)
    data[CONF_NAME] = str(data.get(CONF_NAME, DEFAULT_NAME)).strip() or DEFAULT_NAME
    data[CONF_LIGHTS] = list(data.get(CONF_LIGHTS) or [])
    return data


def _validate_input(data: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = {}
    if not any(data.get(field) for field in _SIGNAL_FIELDS) and not data.get(CONF_LIGHTS):
        errors["base"] = "no_signals"
    return errors


class HomeBriefConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            data = _normalize_input(user_input)
            errors = _validate_input(data)
            if not errors:
                await self.async_set_unique_id(data[CONF_NAME].lower())
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=data[CONF_NAME], data=data)

        discovered = discover_defaults(self.hass)
        defaults = effective_defaults(configured={CONF_NAME: DEFAULT_NAME}, discovered=discovered)
        defaults[CONF_NAME] = DEFAULT_NAME
        discovery = summarize_discovery(discovered, {CONF_NAME: DEFAULT_NAME})
        description_placeholders = {
            "matched": str(discovery["matched_count"]),
            "autofilled": str(discovery["autofilled_count"]),
            "lights": str(discovery["lights_count"]),
        }
        return self.async_show_form(
            step_id="user",
            data_schema=_schema(defaults),
            errors=errors,
            description_placeholders=description_placeholders,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return HomeBriefOptionsFlow(config_entry)


class HomeBriefOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            data = _normalize_input(user_input)
            errors = _validate_input(data)
            if not errors:
                return self.async_create_entry(title="", data=data)

        configured = dict(self.config_entry.data)
        configured.update(self.config_entry.options)
        discovered = discover_defaults(self.hass)
        current = effective_defaults(configured=configured, discovered=discovered)
        discovery = summarize_discovery(discovered, configured)
        description_placeholders = {
            "matched": str(discovery["matched_count"]),
            "autofilled": str(discovery["autofilled_count"]),
            "lights": str(discovery["lights_count"]),
        }
        return self.async_show_form(
            step_id="init",
            data_schema=_schema(current),
            errors=errors,
            description_placeholders=description_placeholders,
        )
