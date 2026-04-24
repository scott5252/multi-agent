from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping, Sequence

type JsonValue = (
    None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]
)

REMOVAL_MARKER_KEY = "$memory_removed"


class CanonicalJsonError(ValueError):
    """Raised when memory content cannot be represented as canonical JSON."""


def validate_json_value(value: object, *, path: str = "$") -> JsonValue:
    if value is None or isinstance(value, bool | str):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise CanonicalJsonError(f"{path} contains a non-finite number")
        return value
    if isinstance(value, Mapping):
        normalized: dict[str, JsonValue] = {}
        for key, nested in value.items():
            if not isinstance(key, str):
                raise CanonicalJsonError(f"{path} contains a non-string object key")
            normalized[key] = validate_json_value(nested, path=f"{path}.{key}")
        _validate_removal_marker(normalized, path=path)
        return normalized
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return [
            validate_json_value(nested, path=f"{path}[{index}]")
            for index, nested in enumerate(value)
        ]
    raise CanonicalJsonError(f"{path} contains unsupported JSON value {type(value)!r}")


def canonical_dumps(value: object) -> str:
    normalized = validate_json_value(value)
    return json.dumps(
        normalized,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def canonical_bytes(value: object) -> bytes:
    return canonical_dumps(value).encode("utf-8")


def content_sha256(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def content_size_bytes(value: object) -> int:
    return len(canonical_bytes(value))


def _validate_removal_marker(value: dict[str, JsonValue], *, path: str) -> None:
    marker = value.get(REMOVAL_MARKER_KEY)
    if marker is None:
        return
    if not isinstance(marker, list) or not all(
        isinstance(item, str) for item in marker
    ):
        raise CanonicalJsonError(
            f"{path}.{REMOVAL_MARKER_KEY} must be a list of removed field names"
        )
