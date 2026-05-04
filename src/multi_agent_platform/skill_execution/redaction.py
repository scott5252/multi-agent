from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any
from urllib.parse import urlsplit, urlunsplit

SENSITIVE_KEY_MARKERS = (
    "access_token",
    "api_key",
    "authorization",
    "body",
    "credential",
    "password",
    "refresh_token",
    "secret",
    "token",
)

EMAIL_RE = re.compile(
    r"(?P<local>[A-Z0-9._%+-]+)@(?P<domain>[A-Z0-9.-]+\.[A-Z]{2,})", re.I
)
TOKEN_RE = re.compile(
    r"(Bearer\s+[A-Za-z0-9._~+/=-]+|sk-[A-Za-z0-9._-]+|ya29\.[A-Za-z0-9._-]+)",
    re.I,
)
URL_RE = re.compile(r"https?://[^\s<>\"]+")


def redact_text(value: object) -> str:
    text = str(value)
    text = URL_RE.sub(lambda match: _redact_url(match.group(0)), text)
    text = TOKEN_RE.sub("[redacted-token]", text)
    return EMAIL_RE.sub("[redacted-email]", text)


def redact_payload(value: Any) -> Any:
    if isinstance(value, Mapping):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key)
            if _is_sensitive_key(key_text):
                redacted[key_text] = "[redacted]"
            else:
                redacted[key_text] = redact_payload(item)
        return redacted
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return [redact_payload(item) for item in value]
    if isinstance(value, str):
        return redact_text(value)
    return value


def summarize_payload(tool_name: str, payload: Mapping[str, Any]) -> str:
    safe_payload = redact_payload(payload)
    if not isinstance(safe_payload, Mapping):
        return "Tool response was redacted."

    if tool_name == "google_calendar.events.read":
        events = _sequence(safe_payload.get("events"))
        return _count_summary("event", len(events), _first_title(events, "title"))
    if tool_name == "gmail.messages.read":
        messages = _sequence(safe_payload.get("messages"))
        return _count_summary(
            "message", len(messages), _first_title(messages, "subject")
        )
    if tool_name == "news.search":
        items = _sequence(safe_payload.get("items"))
        return _count_summary("news item", len(items), _first_title(items, "headline"))
    if tool_name == "weather.forecast.read":
        forecast = safe_payload.get("forecast")
        if isinstance(forecast, Mapping):
            condition = str(forecast.get("condition") or "forecast").strip()
            location = str(forecast.get("location") or "selected location").strip()
            return redact_text(f"Forecast for {location}: {condition}.")
    if tool_name == "commute.lookup":
        commute = safe_payload.get("commute")
        if isinstance(commute, Mapping):
            status = str(commute.get("status") or "available").strip()
            minutes = commute.get("estimated_minutes")
            return redact_text(f"Commute status {status}, estimated {minutes} minutes.")
    return "Tool response summary is available with protected details redacted."


def _is_sensitive_key(key: str) -> bool:
    lowered = key.lower()
    return any(marker in lowered for marker in SENSITIVE_KEY_MARKERS)


def _redact_url(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.query:
        return urlunsplit(
            (parsed.scheme, parsed.netloc, parsed.path, "redacted=true", "")
        )
    return url


def _sequence(value: object) -> Sequence[object]:
    if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
        return value
    return ()


def _first_title(items: Sequence[object], key: str) -> str | None:
    if not items:
        return None
    first = items[0]
    if not isinstance(first, Mapping):
        return None
    value = first.get(key)
    if value is None:
        return None
    return redact_text(value)


def _count_summary(noun: str, count: int, first_title: str | None) -> str:
    suffix = "" if count == 1 else "s"
    if first_title:
        return f"{count} {noun}{suffix}; first: {first_title}."
    return f"{count} {noun}{suffix} returned."
