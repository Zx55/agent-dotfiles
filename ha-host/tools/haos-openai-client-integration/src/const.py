from __future__ import annotations

from typing import Final

DOMAIN: Final = "haos_openai_client"

CONF_API_MODE: Final = "api_mode"
CONF_BASE_URL: Final = "base_url"
CONF_MAX_TOKENS: Final = "max_tokens"
CONF_MODEL: Final = "model"
CONF_TEMPERATURE: Final = "temperature"
CONF_TIMEOUT_SECONDS: Final = "timeout_seconds"

DEFAULT_API_MODE: Final = "chat_completions"
DEFAULT_BASE_URL: Final = "https://api.openai.com/v1"
DEFAULT_MODEL: Final = "gpt-4o-mini"
DEFAULT_NAME: Final = "HAOS OpenAI Client"
DEFAULT_TIMEOUT_SECONDS: Final = 30.0

API_MODES: Final = ("chat_completions", "responses")
