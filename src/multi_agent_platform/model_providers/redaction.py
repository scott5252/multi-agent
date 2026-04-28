from __future__ import annotations

import re
from collections.abc import Mapping
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

SENSITIVE_KEYS = frozenset(
    {
        "api_key",
        "apikey",
        "authorization",
        "bearer",
        "credential",
        "password",
        "prompt",
        "completion",
        "secret",
        "token",
    }
)

SECRET_PATTERN = re.compile(
    r"(sk-[A-Za-z0-9_-]{12,}|Bearer\s+[A-Za-z0-9._-]+|[A-Za-z0-9_-]{32,})"
)


def redact_text(value: object, *, fallback: str = "Protected detail") -> str:
    text = str(value or "").strip()
    if not text:
        return fallback
    lowered = text.lower()
    if any(marker in lowered for marker in SENSITIVE_KEYS):
        return fallback
    return SECRET_PATTERN.sub("[redacted]", text)[:500]


def safe_url(value: str | None) -> str | None:
    if not value:
        return None
    parsed = urlsplit(value)
    netloc = parsed.hostname or ""
    if parsed.port is not None:
        netloc = f"{netloc}:{parsed.port}"
    safe_query = []
    for key, item in parse_qsl(parsed.query, keep_blank_values=True):
        if key.lower() in SENSITIVE_KEYS:
            safe_query.append((key, "[redacted]"))
        else:
            safe_query.append((key, item))
    return urlunsplit(
        (
            parsed.scheme,
            netloc,
            parsed.path.rstrip("/") or "/",
            urlencode(safe_query),
            "",
        )
    )


def safe_mapping_summary(mapping: Mapping[str, object]) -> dict[str, object]:
    summary: dict[str, object] = {}
    for key, value in mapping.items():
        lowered = key.lower()
        if any(marker in lowered for marker in SENSITIVE_KEYS):
            summary[key] = "[redacted]"
        elif isinstance(value, str):
            summary[key] = redact_text(value)
        elif isinstance(value, int | float | bool) or value is None:
            summary[key] = value
        else:
            summary[key] = redact_text(value)
    return summary
