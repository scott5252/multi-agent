from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping

SENSITIVE_MARKERS = (
    "secret",
    "token",
    "password",
    "api_key",
    "authorization",
    "credential",
    "oauth",
    "bearer",
)


def fingerprint_value(value: object) -> str:
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()


def fingerprint_prefix(value: object, *, length: int = 12) -> str:
    return fingerprint_value(value)[:length]


def content_digest(payload: Mapping[str, object]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return f"sha256:{hashlib.sha256(encoded.encode('utf-8')).hexdigest()}"


def mask_identifier(value: object, *, visible: int = 3) -> str:
    text = str(value or "").strip()
    if not text:
        return "masked"
    if "@" in text:
        local, domain = text.split("@", maxsplit=1)
        if not local:
            return f"***@{domain}"
        return f"{local[:1]}***@{domain}"
    if len(text) <= visible * 2:
        return f"{text[:1]}***{text[-1:]}"
    return f"{text[:visible]}***{text[-visible:]}"


def safe_location_label(value: str | None) -> str:
    text = " ".join(str(value or "").strip().split())
    if not text:
        return "not configured"
    if any(character.isdigit() for character in text):
        return f"location:{fingerprint_prefix(text)}"
    return text[:80]


def safe_reference_label(value: str | None) -> str:
    text = str(value or "").strip()
    if not text or text == "none":
        return "none"
    prefix = text.split(":", maxsplit=1)[0]
    return f"{prefix}:***"


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


def sanitize_metadata(metadata: Mapping[str, object] | None) -> dict[str, object]:
    safe: dict[str, object] = {}
    for key, value in (metadata or {}).items():
        lowered_key = key.lower()
        if any(marker in lowered_key for marker in SENSITIVE_MARKERS):
            safe[key] = "redacted"
        elif isinstance(value, bool | int | float) or value is None:
            safe[key] = value
        else:
            safe[key] = sanitize_text(value, max_length=120)
    return safe


def safe_summary_for_payload(
    payload: Mapping[str, object],
    *,
    revision_id: object | None = None,
    content_hash: str | None = None,
) -> dict[str, object]:
    news_topics = _tuple_items(payload.get("news_topics"))
    vip_senders = _tuple_items(payload.get("vip_senders"))
    return {
        "profile_ready": True,
        "location_label": safe_location_label(str(payload.get("location_label") or "")),
        "timezone": str(payload.get("timezone") or ""),
        "topic_count": len(news_topics),
        "topic_preview": [
            sanitize_text(item, max_length=40) for item in news_topics[:3]
        ],
        "vip_sender_count": len(vip_senders),
        "vip_sender_preview": [mask_identifier(item) for item in vip_senders[:3]],
        "workday": f"{payload.get('workday_start')} - {payload.get('workday_end')}",
        "commute_mode": str(payload.get("commute_mode") or "none"),
        "calendar_account_label": safe_reference_label(
            str(payload.get("calendar_account_ref") or "")
        ),
        "email_account_label": safe_reference_label(
            str(payload.get("email_account_ref") or "")
        ),
        "output_style": str(payload.get("output_style") or "standard"),
        "scheduled_enabled": bool(payload.get("scheduled_enabled")),
        "scheduled_time": payload.get("scheduled_time") or "not scheduled",
        "revision_id": str(revision_id) if revision_id is not None else None,
        "content_digest": content_hash,
    }


def _tuple_items(value: object) -> tuple[object, ...]:
    if isinstance(value, (list, tuple)):
        return tuple(value)
    return ()
