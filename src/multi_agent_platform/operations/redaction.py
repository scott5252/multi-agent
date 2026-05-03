from __future__ import annotations

from collections.abc import Mapping

SENSITIVE_MARKERS = (
    "prompt",
    "completion",
    "response",
    "content",
    "message",
    "messages",
    "secret",
    "token",
    "password",
    "api_key",
    "apikey",
    "authorization",
    "credential",
    "memory",
    "payload",
    "transcript",
    "traceback",
    "stack trace",
    "stacktrace",
    "raw",
)


def is_sensitive_key(key: object) -> bool:
    lowered = str(key).lower().replace("-", "_")
    return any(marker in lowered for marker in SENSITIVE_MARKERS)


def sanitize_operations_text(
    value: object,
    *,
    fallback: str = "Protected detail",
    max_length: int = 240,
) -> str:
    text = str(value or "").strip()
    if not text:
        return fallback
    lowered = text.lower()
    if any(marker in lowered for marker in SENSITIVE_MARKERS):
        return fallback
    if len(text) > max_length:
        return f"{text[: max_length - 1].rstrip()}..."
    return text


def sanitize_operations_metadata(
    metadata: Mapping[str, object] | None,
    *,
    max_items: int = 20,
) -> dict[str, str]:
    if not metadata:
        return {}
    sanitized: dict[str, str] = {}
    for index, (key, value) in enumerate(metadata.items()):
        if index >= max_items:
            break
        safe_key = _safe_metadata_key(key)
        if is_sensitive_key(key):
            sanitized[safe_key] = "[redacted]"
            continue
        if isinstance(value, Mapping):
            nested = {
                str(nested_key): nested_value
                for nested_key, nested_value in value.items()
                if not is_sensitive_key(nested_key)
            }
            sanitized[safe_key] = sanitize_operations_text(nested, max_length=240)
        elif isinstance(value, list | tuple):
            sanitized[safe_key] = sanitize_operations_text(
                ", ".join(str(item) for item in value[:5]),
                max_length=240,
            )
        else:
            sanitized[safe_key] = sanitize_operations_text(value, max_length=240)
    return sanitized


def _safe_metadata_key(key: object) -> str:
    text = str(key or "").strip()
    if not text:
        return "field"
    if len(text) > 80:
        return f"{text[:79].rstrip()}..."
    return text


def redaction_notice() -> str:
    return (
        "Operations console data is built from persisted safe metadata. Raw "
        "prompts, model responses, channel messages, secrets, credentials, "
        "payloads, memory content, and stack traces are not rendered or exported."
    )
