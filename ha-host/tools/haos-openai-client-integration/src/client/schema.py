from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


JsonSchema = Mapping[str, Any]


def make_strict_json_schema(schema: JsonSchema) -> dict[str, Any]:
    normalized = deepcopy(dict(schema))
    _make_object_fields_required(normalized)
    return normalized


def _make_object_fields_required(schema: dict[str, Any]) -> None:
    schema_type = schema.get("type")

    if schema_type == "object":
        schema.setdefault("additionalProperties", False)
        properties = schema.get("properties")
        if not isinstance(properties, dict):
            return

        required = schema.setdefault("required", [])
        for prop_name, prop_schema in properties.items():
            if isinstance(prop_schema, dict):
                _make_object_fields_required(prop_schema)
            if prop_name not in required:
                required.append(prop_name)
        return

    if schema_type == "array":
        items = schema.get("items")
        if isinstance(items, dict):
            _make_object_fields_required(items)
