from __future__ import annotations

from dataclasses import dataclass, field
import os
from typing import Literal, Mapping
from urllib.parse import urlsplit, urlunsplit


ApiMode = Literal["chat_completions", "responses"]
_ENDPOINT_SUFFIXES = (
    "/chat/completions",
    "/responses",
    "/completions",
    "/models",
)


def normalize_base_url(base_url: str | None) -> str | None:
    if base_url is None:
        return None

    value = base_url.strip().rstrip("/")
    if not value:
        return None
    if "://" not in value:
        value = f"https://{value}"

    parsed = urlsplit(value)
    path = parsed.path.rstrip("/")

    for suffix in _ENDPOINT_SUFFIXES:
        if path.endswith(suffix):
            path = path[: -len(suffix)].rstrip("/")
            break

    if not path:
        path = "/v1"

    return urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            path,
            "",
            "",
        )
    )


@dataclass(frozen=True)
class OpenAIClientConfig:
    api_key: str = field(repr=False)
    model: str
    base_url: str | None = None
    api_mode: ApiMode = "chat_completions"
    timeout_seconds: float = 30.0
    temperature: float | None = None
    max_tokens: int | None = None
    extra_headers: Mapping[str, str] | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "base_url", normalize_base_url(self.base_url))

    @classmethod
    def from_env(
        cls,
        *,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        api_mode: ApiMode = "chat_completions",
        timeout_seconds: float = 30.0,
        temperature: float | None = None,
        max_tokens: int | None = None,
        extra_headers: Mapping[str, str] | None = None,
    ) -> "OpenAIClientConfig":
        resolved_api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not resolved_api_key:
            raise ValueError("api_key is required or OPENAI_API_KEY must be set")

        resolved_model = model or os.environ.get("OPENAI_MODEL")
        if not resolved_model:
            raise ValueError("model is required or OPENAI_MODEL must be set")

        return cls(
            api_key=resolved_api_key,
            model=resolved_model,
            base_url=base_url or os.environ.get("OPENAI_BASE_URL"),
            api_mode=api_mode,
            timeout_seconds=timeout_seconds,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_headers=extra_headers,
        )
