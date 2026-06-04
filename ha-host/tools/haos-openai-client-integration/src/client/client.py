from __future__ import annotations

import json
from typing import Any, Mapping

from .config import OpenAIClientConfig
from .result import GenerateResult
from .schema import make_strict_json_schema


DEFAULT_SYSTEM_PROMPT = "You are a concise assistant for Home Assistant tasks."


class HaosOpenAIClient:
    def __init__(
        self,
        config: OpenAIClientConfig,
        *,
        sdk_client: Any | None = None,
    ) -> None:
        self._config = config
        self._client = sdk_client or self._create_sdk_client(config)

    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        json_schema: Mapping[str, Any] | None = None,
        schema_name: str = "haos_response",
    ) -> GenerateResult:
        if self._config.api_mode == "chat_completions":
            return await self._generate_chat_completion(
                prompt,
                system_prompt=system_prompt,
                json_schema=json_schema,
                schema_name=schema_name,
            )
        if self._config.api_mode == "responses":
            return await self._generate_response(
                prompt,
                system_prompt=system_prompt,
                json_schema=json_schema,
                schema_name=schema_name,
            )
        raise ValueError(f"Unsupported api_mode: {self._config.api_mode}")

    def _create_sdk_client(self, config: OpenAIClientConfig) -> Any:
        from openai import AsyncOpenAI

        kwargs: dict[str, Any] = {
            "api_key": config.api_key,
            "timeout": config.timeout_seconds,
        }
        if config.base_url:
            kwargs["base_url"] = config.base_url
        if config.extra_headers:
            kwargs["default_headers"] = dict(config.extra_headers)
        return AsyncOpenAI(**kwargs)

    async def _generate_chat_completion(
        self,
        prompt: str,
        *,
        system_prompt: str | None,
        json_schema: Mapping[str, Any] | None,
        schema_name: str,
    ) -> GenerateResult:
        model_args: dict[str, Any] = {
            "model": self._config.model,
            "messages": [
                {"role": "system", "content": system_prompt or DEFAULT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        }
        if self._config.temperature is not None:
            model_args["temperature"] = self._config.temperature
        if self._config.max_tokens is not None:
            model_args["max_tokens"] = self._config.max_tokens
        if json_schema is not None:
            model_args["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": schema_name,
                    "schema": make_strict_json_schema(json_schema),
                    "strict": True,
                },
            }

        response = await self._client.chat.completions.create(**model_args)
        content = _extract_chat_completion_text(response)
        return _result_from_content(
            content,
            json_schema=json_schema,
            raw_response=response,
        )

    async def _generate_response(
        self,
        prompt: str,
        *,
        system_prompt: str | None,
        json_schema: Mapping[str, Any] | None,
        schema_name: str,
    ) -> GenerateResult:
        model_args: dict[str, Any] = {
            "model": self._config.model,
            "input": [
                {
                    "type": "message",
                    "role": "system",
                    "content": system_prompt or DEFAULT_SYSTEM_PROMPT,
                },
                {"type": "message", "role": "user", "content": prompt},
            ],
        }
        if self._config.temperature is not None:
            model_args["temperature"] = self._config.temperature
        if self._config.max_tokens is not None:
            model_args["max_output_tokens"] = self._config.max_tokens
        if json_schema is not None:
            model_args["text"] = {
                "format": {
                    "type": "json_schema",
                    "name": schema_name,
                    "schema": make_strict_json_schema(json_schema),
                    "strict": True,
                },
            }

        response = await self._client.responses.create(**model_args)
        content = _extract_response_text(response)
        return _result_from_content(content, json_schema=json_schema, raw_response=response)


def _result_from_content(
    content: str,
    *,
    json_schema: Mapping[str, Any] | None,
    raw_response: Any,
) -> GenerateResult:
    if json_schema is None:
        return GenerateResult(content=content, raw_response=raw_response)
    return GenerateResult(
        content=content,
        data=json.loads(content),
        raw_response=raw_response,
        is_structured=True,
    )


def _extract_chat_completion_text(response: Any) -> str:
    try:
        content = response.choices[0].message.content
    except (AttributeError, IndexError) as err:
        raise ValueError("Chat Completions response did not contain message content") from err
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    return str(content)


def _extract_response_text(response: Any) -> str:
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str):
        return output_text

    output = getattr(response, "output", None)
    if isinstance(output, list):
        parts: list[str] = []
        for item in output:
            for content_item in getattr(item, "content", []) or []:
                text = getattr(content_item, "text", None)
                if isinstance(text, str):
                    parts.append(text)
        if parts:
            return "".join(parts)

    raise ValueError("Responses API response did not contain output text")
