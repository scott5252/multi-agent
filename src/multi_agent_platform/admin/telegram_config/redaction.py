from __future__ import annotations

import hashlib
from collections.abc import Mapping

SENSITIVE_MARKERS = (
    "secret",
    "token",
    "password",
    "api_key",
    "authorization",
    "credential",
    "prompt",
    "message",
    "result",
    "payload",
    "chat_text",
    "webhook_secret",
    "bot",
)


def fingerprint_value(value: object) -> str:
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()


def fingerprint_prefix(value: object, *, length: int = 12) -> str:
    return fingerprint_value(value)[:length]


def mask_identifier(value: object, *, visible: int = 3) -> str:
    text = str(value or "").strip()
    if not text:
        return "masked"
    if len(text) <= visible * 2:
        return f"{text[:1]}***{text[-1:]}"
    return f"{text[:visible]}***{text[-visible:]}"


def safe_reference_label(value: str | None) -> str:
    if not value:
        return "not configured"
    if is_safe_secret_reference(value):
        return value.split(":", maxsplit=1)[0] + ":***"
    return "configured value redacted"


def is_safe_secret_reference(value: str | None) -> bool:
    return bool(
        value
        and value.startswith(
            (
                "env:",
                "secret-manager/",
                "static:",
                "local:",
                "test:",
                "fake:",
            )
        )
    )


def sanitize_text(
    value: object,
    *,
    fallback: str = "Protected detail redacted.",
    max_length: int = 240,
) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    lowered = text.lower()
    if any(marker in lowered for marker in SENSITIVE_MARKERS):
        return fallback
    if len(text) > max_length:
        return f"{text[: max_length - 1].rstrip()}..."
    return text


def sanitize_metadata(
    metadata: Mapping[str, object] | None,
) -> dict[str, str | int | bool | None]:
    safe: dict[str, str | int | bool | None] = {}
    for key, value in (metadata or {}).items():
        lowered = key.lower()
        if any(marker in lowered for marker in SENSITIVE_MARKERS):
            safe[key] = "redacted"
            continue
        if isinstance(value, bool | int) or value is None:
            safe[key] = value
        else:
            safe[key] = sanitize_text(value, max_length=120)
    return safe
