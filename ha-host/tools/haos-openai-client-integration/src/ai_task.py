from __future__ import annotations

from json import JSONDecodeError
import logging
from typing import Any

import openai
import voluptuous as vol
from voluptuous_openapi import convert

from homeassistant.components import ai_task, conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import llm
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import slugify

from .client import HaosOpenAIClient
from .const import (
    DEFAULT_NAME,
)
from .ha_client import client_config_from_data, create_sdk_client
LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([HaosOpenAIClientTaskEntity(entry)])


class HaosOpenAIClientTaskEntity(ai_task.AITaskEntity):
    _attr_supported_features = ai_task.AITaskEntityFeature.GENERATE_DATA

    def __init__(self, entry: ConfigEntry) -> None:
        self._entry = entry
        self._attr_unique_id = entry.entry_id
        self._attr_name = entry.data.get(CONF_NAME, DEFAULT_NAME)

    async def _async_generate_data(
        self,
        task: ai_task.GenDataTask,
        chat_log: conversation.ChatLog,
    ) -> ai_task.GenDataTaskResult:
        client = HaosOpenAIClient(
            client_config_from_data(dict(self._entry.data)),
            sdk_client=create_sdk_client(self.hass, dict(self._entry.data)),
        )
        json_schema = (
            _format_structured_output(task.structure, task.llm_api)
            if task.structure
            else None
        )

        try:
            result = await client.generate(
                task.instructions,
                json_schema=json_schema,
                schema_name=slugify(task.name),
            )
        except openai.AuthenticationError as err:
            self._entry.async_start_reauth(self.hass)
            raise HomeAssistantError("Authentication error") from err
        except openai.RateLimitError as err:
            raise HomeAssistantError("Rate limited or insufficient funds") from err
        except openai.OpenAIError as err:
            LOGGER.error("Error talking to OpenAI-compatible endpoint: %s", err)
            raise HomeAssistantError("Error talking to OpenAI-compatible endpoint") from err
        except (JSONDecodeError, ValueError) as err:
            LOGGER.error("Error parsing OpenAI-compatible response: %s", err)
            raise HomeAssistantError("Error parsing OpenAI-compatible response") from err

        return ai_task.GenDataTaskResult(
            conversation_id=chat_log.conversation_id,
            data=result.data if json_schema else result.content,
        )

def _format_structured_output(
    schema: vol.Schema,
    llm_api: llm.APIInstance | None,
) -> dict[str, Any]:
    return convert(
        schema,
        custom_serializer=(
            llm_api.custom_serializer if llm_api else llm.selector_serializer
        ),
    )
