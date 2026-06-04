from __future__ import annotations

from typing import Any, cast

import openai

from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.httpx_client import get_async_client

from .client import ApiMode, OpenAIClientConfig, normalize_base_url
from .const import (
    CONF_API_MODE,
    CONF_BASE_URL,
    CONF_MAX_TOKENS,
    CONF_MODEL,
    CONF_TEMPERATURE,
    CONF_TIMEOUT_SECONDS,
    DEFAULT_API_MODE,
    DEFAULT_MODEL,
    DEFAULT_TIMEOUT_SECONDS,
)


def client_config_from_data(
    data: dict[str, Any],
    *,
    default_max_tokens: int | None = None,
) -> OpenAIClientConfig:
    max_tokens = _optional_int(data.get(CONF_MAX_TOKENS))
    if max_tokens is None:
        max_tokens = default_max_tokens

    return OpenAIClientConfig(
        api_key=data[CONF_API_KEY],
        base_url=data.get(CONF_BASE_URL),
        model=data.get(CONF_MODEL, DEFAULT_MODEL),
        api_mode=cast(ApiMode, data.get(CONF_API_MODE, DEFAULT_API_MODE)),
        timeout_seconds=_optional_float(data.get(CONF_TIMEOUT_SECONDS))
        or DEFAULT_TIMEOUT_SECONDS,
        temperature=_optional_float(data.get(CONF_TEMPERATURE)),
        max_tokens=max_tokens,
    )


def create_sdk_client(
    hass: HomeAssistant,
    data: dict[str, Any],
) -> openai.AsyncOpenAI:
    kwargs: dict[str, Any] = {
        "api_key": data[CONF_API_KEY],
        "http_client": get_async_client(hass),
        "timeout": _optional_float(data.get(CONF_TIMEOUT_SECONDS))
        or DEFAULT_TIMEOUT_SECONDS,
    }
    if data.get(CONF_BASE_URL):
        kwargs["base_url"] = normalize_base_url(data[CONF_BASE_URL])
    return openai.AsyncOpenAI(**kwargs)


def _optional_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def _optional_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    return int(value)
