from __future__ import annotations

import asyncio
from dataclasses import dataclass
import logging
import time
from typing import Any

import openai

from .client import HaosOpenAIClient
from .ha_client import client_config_from_data

TEST_PROMPT = "Reply with exactly: OK"
TEST_MAX_TOKENS = 64
LOGGER = logging.getLogger(__package__)


@dataclass(frozen=True)
class ConnectionTestResult:
    ok: bool
    detail: str


async def async_test_connection(data: dict[str, Any]) -> ConnectionTestResult:
    return await _async_test_connection(data)


async def async_test_connection_with_client(
    data: dict[str, Any],
    sdk_client: Any,
) -> ConnectionTestResult:
    return await _async_test_connection(data, sdk_client=sdk_client)


async def _async_test_connection(
    data: dict[str, Any],
    *,
    sdk_client: Any | None = None,
) -> ConnectionTestResult:
    started = time.monotonic()
    config = client_config_from_data(data, default_max_tokens=TEST_MAX_TOKENS)
    client = HaosOpenAIClient(config, sdk_client=sdk_client)

    try:
        LOGGER.info(
            "Connection test started for model %s at %s",
            config.model,
            config.base_url,
        )
        async with asyncio.timeout(config.timeout_seconds):
            result = await client.generate(TEST_PROMPT)
    except TimeoutError:
        LOGGER.error("Connection test timed out after %.1fs", config.timeout_seconds)
        return ConnectionTestResult(
            False,
            f"Timed out after {config.timeout_seconds:.1f}s",
        )
    except openai.AuthenticationError as err:
        LOGGER.error("Connection test authentication failed: %s", err)
        return ConnectionTestResult(False, f"Authentication failed: {err}")
    except openai.OpenAIError as err:
        LOGGER.error("Connection test provider request failed: %s", err)
        return ConnectionTestResult(False, f"Provider request failed: {err}")
    except Exception as err:
        LOGGER.exception("Connection test failed unexpectedly")
        return ConnectionTestResult(False, f"Test failed: {err}")

    elapsed = time.monotonic() - started
    content = result.content.strip().replace("\n", " ")
    if len(content) > 120:
        content = f"{content[:117]}..."
    if not content:
        detail = f"Received empty response in {elapsed:.1f}s"
        LOGGER.error("Connection test failed: %s", detail)
        return ConnectionTestResult(False, detail)
    if "OK" not in content.upper():
        detail = f"Received unexpected response in {elapsed:.1f}s: {content}"
        LOGGER.error("Connection test failed: %s", detail)
        return ConnectionTestResult(False, detail)
    detail = f"Received response in {elapsed:.1f}s: {content}"
    LOGGER.info("Connection test passed: %s", detail)
    return ConnectionTestResult(
        True,
        detail,
    )
