"""Client for the Zotero Add Local File plugin endpoint."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from zotero_mcp_wrapper.config import Config

TOOL_NAME = "zotero_add_from_file"


class LocalFilePluginError(Exception):
    """Raised when the local Zotero plugin request fails."""


@dataclass(frozen=True)
class LocalFilePluginResult:
    """A normalized result from the local Zotero plugin."""

    text: str


def is_add_from_file_tool_call(payload: object) -> bool:
    """Return whether an MCP JSON-RPC payload is a zotero_add_from_file call."""
    if not isinstance(payload, dict):
        return False
    if payload.get("method") != "tools/call":
        return False
    params = payload.get("params")
    return isinstance(params, dict) and params.get("name") == TOOL_NAME


def build_plugin_request(arguments: dict[str, Any]) -> dict[str, Any]:
    """Translate MCP zotero_add_from_file arguments into plugin endpoint input."""
    file_path = arguments.get("file_path")
    if not isinstance(file_path, str) or not file_path:
        raise LocalFilePluginError("file_path is required")
    if os.path.islink(file_path):
        raise LocalFilePluginError("Symlinks are not allowed for security reasons.")
    if not os.path.isabs(file_path):
        raise LocalFilePluginError("file_path must be an absolute path.")

    real_path = os.path.realpath(file_path)
    if not os.path.isfile(real_path):
        raise LocalFilePluginError(f"File not found: {real_path}")

    item_type = arguments.get("item_type")
    title = arguments.get("title")
    item: dict[str, Any] = {
        "itemType": item_type if isinstance(item_type, str) and item_type else "document",
        "title": title if isinstance(title, str) and title else os.path.basename(real_path),
    }

    collections = _normalize_string_list(arguments.get("collections"))
    tags = _normalize_string_list(arguments.get("tags"))
    if tags:
        item["tags"] = [{"tag": tag} for tag in tags]

    return {
        "filePath": real_path,
        "item": item,
        "collectionKeys": collections,
        "attachmentTitle": os.path.basename(real_path),
    }


def call_add_from_file_plugin(config: Config, arguments: dict[str, Any]) -> LocalFilePluginResult:
    """Call the local Zotero plugin and return a human-readable result."""
    if not config.add_local_file_token:
        raise LocalFilePluginError("ZOTERO_ADD_LOCAL_FILE_TOKEN is not configured")

    body = json.dumps(build_plugin_request(arguments)).encode("utf-8")
    url = f"http://{config.host}:{config.port}{config.add_local_file_path}"
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {config.add_local_file_token}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=config.add_local_file_timeout_sec) as response:
            response_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        error_body = error.read().decode("utf-8", errors="replace")
        raise LocalFilePluginError(f"Local Zotero add-from-file failed: HTTP {error.code}: {error_body}") from error
    except urllib.error.URLError as error:
        raise LocalFilePluginError(f"Local Zotero add-from-file endpoint is unavailable: {error}") from error

    try:
        data = json.loads(response_body)
    except json.JSONDecodeError as error:
        raise LocalFilePluginError(f"Local Zotero add-from-file returned invalid JSON: {response_body}") from error

    if not isinstance(data, dict) or data.get("ok") is not True:
        raise LocalFilePluginError(f"Local Zotero add-from-file returned an error: {response_body}")

    parent_key = data.get("parentKey")
    attachment_key = data.get("attachmentKey")
    attachment_title = data.get("attachmentTitle")
    stored_path = data.get("storedPath")
    lines = [
        f"Item key: `{parent_key}`",
        f"Attachment key: `{attachment_key}`",
        f"File attached: {attachment_title}",
        f"Stored path: {stored_path}",
        "",
        "_Note: To include this item in semantic search, run zotero_update_search_database._",
    ]
    return LocalFilePluginResult(text="\n".join(lines))


def _normalize_string_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    if isinstance(value, list):
        return [item.strip() for item in value if isinstance(item, str) and item.strip()]
    raise LocalFilePluginError("collections and tags must be strings or lists of strings")
