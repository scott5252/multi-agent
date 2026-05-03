from __future__ import annotations

from collections.abc import Mapping
from typing import Any

SENSITIVE_KEYS = {
    "api_key",
    "authorization",
    "credential",
    "credentials",
    "memory",
    "password",
    "payload",
    "prompt",
    "provider_message",
    "raw",
    "secret",
    "token",
    "transcript",
}
REDACTED = "[redacted]"


def redact_value(value: Any, *, max_string_length: int = 180) -> Any:
    if isinstance(value, Mapping):
        return redact_mapping(value, max_string_length=max_string_length)
    if isinstance(value, list):
        return [
            redact_value(item, max_string_length=max_string_length) for item in value
        ]
    if isinstance(value, tuple):
        return [
            redact_value(item, max_string_length=max_string_length) for item in value
        ]
    if isinstance(value, str):
        lowered = value.lower()
        if any(marker in lowered for marker in SENSITIVE_KEYS):
            return REDACTED
        if len(value) > max_string_length:
            return f"{value[: max_string_length - 1].rstrip()}..."
    return value


def redact_mapping(
    payload: Mapping[str, Any],
    *,
    max_string_length: int = 180,
) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in payload.items():
        lowered = str(key).lower()
        if any(marker in lowered for marker in SENSITIVE_KEYS):
            redacted[str(key)] = REDACTED
        else:
            redacted[str(key)] = redact_value(
                value,
                max_string_length=max_string_length,
            )
    return redacted


def safe_fixture_summary(fixture: Mapping[str, Any] | None) -> dict[str, Any]:
    if not fixture:
        return {"fields": [], "redacted": False}
    redacted = redact_mapping(fixture)
    return {
        "fields": sorted(str(key) for key in fixture),
        "preview": redacted,
        "redacted": redacted != dict(fixture),
    }


def safe_transcript_summary(messages: list[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "message_count": len(messages),
        "messages": [redact_mapping(message) for message in messages[:5]],
        "truncated": len(messages) > 5,
    }


def safe_artifact_summary(
    *,
    artifact_type: str,
    storage_uri: str | None,
    checksum_sha256: str | None,
    size_bytes: int | None,
) -> dict[str, Any]:
    return {
        "artifact_type": artifact_type,
        "storage_ref": "available" if storage_uri else "inline",
        "checksum_sha256": checksum_sha256,
        "size_bytes": size_bytes,
    }
