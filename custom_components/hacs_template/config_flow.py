"""Config flow for HACS Template."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import CONF_API_KEY, CONF_HOST, CONF_NAME, DEFAULT_API_KEY, DEFAULT_HOST, DEFAULT_NAME, DOMAIN


class HacsTemplateConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HACS Template."""

    VERSION = 2

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            name = str(user_input.get(CONF_NAME, DEFAULT_NAME)).strip() or DEFAULT_NAME
            await self.async_set_unique_id(name.lower())
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=name,
                data={
                    CONF_NAME: name,
                    CONF_HOST: str(user_input.get(CONF_HOST, DEFAULT_HOST) or "").strip(),
                    CONF_API_KEY: str(user_input.get(CONF_API_KEY, DEFAULT_API_KEY) or "").strip(),
                },
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Optional(CONF_HOST, default=DEFAULT_HOST): str,
                vol.Optional(CONF_API_KEY, default=DEFAULT_API_KEY): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_reauth(self, user_input: dict[str, Any] | None = None):
        """Handle re-authentication (triggered by ConfigEntryAuthFailed)."""
        self._reauth_entry_id = self.context.get("entry_id")
        return await self.async_step_reauth_confirm(user_input)

    async def async_step_reauth_confirm(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            entry = self.hass.config_entries.async_get_entry(self._reauth_entry_id)
            if entry is not None:
                data = dict(entry.data)
                name = str(user_input.get(CONF_NAME, data.get(CONF_NAME, DEFAULT_NAME)) or "").strip() or DEFAULT_NAME
                data[CONF_NAME] = name
                data[CONF_API_KEY] = str(user_input.get(CONF_API_KEY, "")).strip()
                self.hass.config_entries.async_update_entry(entry, title=name, data=data)
                await self.hass.config_entries.async_reload(entry.entry_id)
            return self.async_abort(reason="reauth_successful")

        entry = self.hass.config_entries.async_get_entry(self._reauth_entry_id)
        current_name = (entry.data.get(CONF_NAME) if entry else None) or DEFAULT_NAME
        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=str(current_name)): str,
                vol.Required(CONF_API_KEY, default=""): str,
            }
        )
        return self.async_show_form(step_id="reauth_confirm", data_schema=schema)

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
            return self.async_create_entry(
                title="",
                data={
                    CONF_NAME: name,
                    CONF_HOST: str(user_input.get(CONF_HOST, DEFAULT_HOST) or "").strip(),
                    CONF_API_KEY: str(user_input.get(CONF_API_KEY, DEFAULT_API_KEY) or "").strip(),
                },
            )

        current = self.config_entry.options.get(
            CONF_NAME,
            self.config_entry.data.get(CONF_NAME, DEFAULT_NAME),
        )
        current_host = self.config_entry.options.get(CONF_HOST, self.config_entry.data.get(CONF_HOST, DEFAULT_HOST))
        current_api_key = self.config_entry.options.get(CONF_API_KEY, self.config_entry.data.get(CONF_API_KEY, DEFAULT_API_KEY))
        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=current): str,
                vol.Optional(CONF_HOST, default=str(current_host or "")): str,
                vol.Optional(CONF_API_KEY, default=str(current_api_key or "")): str,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
