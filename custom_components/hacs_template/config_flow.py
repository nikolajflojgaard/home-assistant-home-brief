"""Config flow for HACS Template."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import CONF_NAME, DEFAULT_NAME, DOMAIN


class HacsTemplateConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HACS Template."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            name = str(user_input.get(CONF_NAME, DEFAULT_NAME)).strip() or DEFAULT_NAME
            await self.async_set_unique_id(name.lower())
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=name, data={CONF_NAME: name})

        schema = vol.Schema({vol.Required(CONF_NAME, default=DEFAULT_NAME): str})
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return HacsTemplateOptionsFlow(config_entry)


class HacsTemplateOptionsFlow(config_entries.OptionsFlow):
    """Handle options for HACS Template."""

    def __init__(self, config_entry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            name = str(user_input.get(CONF_NAME, DEFAULT_NAME)).strip() or DEFAULT_NAME
            return self.async_create_entry(title="", data={CONF_NAME: name})

        current = self.config_entry.options.get(
            CONF_NAME,
            self.config_entry.data.get(CONF_NAME, DEFAULT_NAME),
        )
        schema = vol.Schema({vol.Required(CONF_NAME, default=current): str})
        return self.async_show_form(step_id="init", data_schema=schema)

