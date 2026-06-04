from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY, CONF_NAME
from homeassistant.helpers import selector

from .client import normalize_base_url
from .const import (
    API_MODES,
    CONF_API_MODE,
    CONF_BASE_URL,
    CONF_MAX_TOKENS,
    CONF_MODEL,
    CONF_TEMPERATURE,
    CONF_TIMEOUT_SECONDS,
    DEFAULT_API_MODE,
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    DEFAULT_NAME,
    DEFAULT_TIMEOUT_SECONDS,
    DOMAIN,
)
from .connection_test import async_test_connection_with_client
from .ha_client import create_sdk_client


def _user_schema(user_input: dict[str, Any] | None = None) -> vol.Schema:
    suggested = user_input or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_NAME,
                default=suggested.get(CONF_NAME, DEFAULT_NAME),
            ): str,
            vol.Required(CONF_API_KEY): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
            ),
            vol.Required(
                CONF_BASE_URL,
                default=suggested.get(CONF_BASE_URL, DEFAULT_BASE_URL),
            ): str,
            vol.Required(
                CONF_MODEL,
                default=suggested.get(CONF_MODEL, DEFAULT_MODEL),
            ): str,
            vol.Required(
                CONF_API_MODE,
                default=suggested.get(CONF_API_MODE, DEFAULT_API_MODE),
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=list(API_MODES),
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Optional(
                CONF_TIMEOUT_SECONDS,
                default=suggested.get(CONF_TIMEOUT_SECONDS, DEFAULT_TIMEOUT_SECONDS),
            ): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    max=300,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Optional(CONF_TEMPERATURE): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=2,
                    step=0.1,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Optional(CONF_MAX_TOKENS): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    max=128000,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
        }
    )


class HaosOpenAIClientConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._pending_data: dict[str, Any] | None = None
        self._test_placeholders: dict[str, str] | None = None

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._pending_data = _normalize_user_input(user_input)
            return await self.async_step_connection_test()

        return self.async_show_form(
            step_id="user",
            data_schema=_user_schema(user_input),
        )

    async def async_step_connection_test(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        if self._pending_data is None:
            return await self.async_step_user()

        if user_input is not None:
            data = self._pending_data
            await self.async_set_unique_id(data[CONF_NAME])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=data[CONF_NAME], data=data)

        if self._test_placeholders is None:
            result = await async_test_connection_with_client(
                self._pending_data,
                create_sdk_client(self.hass, self._pending_data),
            )
            self._test_placeholders = {
                "test_status": "Passed" if result.ok else "Failed",
                "test_detail": result.detail,
            }

        return self.async_show_form(
            step_id="connection_test",
            data_schema=vol.Schema({}),
            description_placeholders=self._test_placeholders,
        )

    async def async_step_reauth(
        self,
        entry_data: dict[str, Any],
    ) -> ConfigFlowResult:
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        if user_input is not None:
            entry = self._get_reauth_entry()
            data = dict(entry.data)
            data[CONF_API_KEY] = user_input[CONF_API_KEY]
            return self.async_update_reload_and_abort(
                entry,
                data_updates=data,
                reason="reauth_successful",
            )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD
                        )
                    )
                }
            ),
        )


def _normalize_user_input(user_input: dict[str, Any]) -> dict[str, Any]:
    data = dict(user_input)
    data[CONF_BASE_URL] = normalize_base_url(data.get(CONF_BASE_URL))
    for key in (CONF_TEMPERATURE, CONF_MAX_TOKENS):
        if data.get(key) in ("", None):
            data.pop(key, None)
    return data
