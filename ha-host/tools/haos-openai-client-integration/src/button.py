from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from .connection_test import async_test_connection_with_client
from .const import DEFAULT_NAME
from .ha_client import create_sdk_client

LOGGER = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([HaosOpenAIClientTestButton(entry)])


class HaosOpenAIClientTestButton(ButtonEntity):
    _attr_icon = "mdi:api"
    _attr_extra_state_attributes = {
        "last_test_status": "never_run",
        "last_test_detail": "",
    }

    def __init__(self, entry: ConfigEntry) -> None:
        self._entry = entry
        name = entry.data.get(CONF_NAME, DEFAULT_NAME)
        self._attr_name = f"{name} Test Connection"
        self._attr_unique_id = f"{entry.entry_id}_test_connection"

    async def async_press(self) -> None:
        data = dict(self._entry.data)
        title = f"{self._entry.data.get(CONF_NAME, DEFAULT_NAME)} test"
        self._set_test_state("running", "Connection test started.")
        LOGGER.warning("Manual connection test started for %s", title)
        await self._create_notification(title, "Connection test started.")

        result = await async_test_connection_with_client(
            data,
            create_sdk_client(self.hass, data),
        )
        message = result.detail
        if not result.ok:
            message = f"Failed. {message}"
            LOGGER.error(
                "Manual connection test failed for %s: %s",
                title,
                result.detail,
            )
            self._set_test_state("failed", result.detail)
        else:
            LOGGER.warning(
                "Manual connection test passed for %s: %s",
                title,
                result.detail,
            )
            self._set_test_state("passed", result.detail)

        await self._create_notification(title, message)

    async def _create_notification(self, title: str, message: str) -> None:
        try:
            await self.hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": title,
                    "message": message,
                    "notification_id": f"haos_openai_client_test_{self._entry.entry_id}",
                },
                blocking=True,
            )
        except Exception:
            LOGGER.exception("Failed to create persistent notification for %s", title)

    def _set_test_state(self, status: str, detail: str) -> None:
        self._attr_extra_state_attributes = {
            "last_test_status": status,
            "last_test_detail": detail,
            "last_test_at": dt_util.utcnow().isoformat(),
        }
        self.async_write_ha_state()
