from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from multi_agent_platform.runtime.orchestration.contracts import sha256_digest

SENSITIVE_KEY_FRAGMENTS = (
    "authorization",
    "credential",
    "message",
    "password",
    "payload",
    "prompt",
    "raw",
    "response",
    "secret",
    "token",
    "traceback",
)

MAX_SAFE_STRING_LENGTH = 500


def is_sensitive_key(key: str) -> bool:
    normalized = key.lower().replace("-", "_")
    return any(fragment in normalized for fragment in SENSITIVE_KEY_FRAGMENTS)


def redact_graph_value(value: object) -> object:
    if isinstance(value, Mapping):
        redacted: dict[str, object] = {}
        for key, item in value.items():
            key_text = str(key)
            if is_sensitive_key(key_text):
                redacted[key_text] = {
                    "redacted": True,
                    "payload_digest": sha256_digest(item),
                }
            else:
                redacted[key_text] = redact_graph_value(item)
        return redacted
    if isinstance(value, str):
        if len(value) > MAX_SAFE_STRING_LENGTH:
            return {
                "redacted": True,
                "payload_digest": sha256_digest(value),
                "reason": "string_too_large_for_inline_graph_output",
            }
        return value
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        return [redact_graph_value(item) for item in value]
    if isinstance(value, bytes | bytearray):
        return {
            "redacted": True,
            "payload_digest": sha256_digest(value.hex()),
            "reason": "binary_payload",
        }
    return value


def graph_payload_digest(value: object) -> str:
    return sha256_digest(value)


def safe_graph_ref(
    *,
    source: str,
    payload: Mapping[str, Any] | None,
    safe_summary: str,
) -> dict[str, object]:
    safe_payload = redact_graph_value(dict(payload or {}))
    return {
        "source": source,
        "safe_summary": safe_summary,
        "payload_digest": graph_payload_digest(payload or {}),
        "structured_output": safe_payload,
    }


def contains_sensitive_key(value: object) -> bool:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if is_sensitive_key(str(key)) or contains_sensitive_key(item):
                return True
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        return any(contains_sensitive_key(item) for item in value)
    return False
