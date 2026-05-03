from __future__ import annotations

from collections.abc import Mapping
from hashlib import sha256
from typing import Any

SENSITIVE_KEYS = {
    "password",
    "token",
    "secret",
    "credential",
    "authorization",
    "raw_email",
}


def normalize_email(email: str) -> str:
    return " ".join(email.strip().lower().split())


def email_fingerprint(email: str) -> str:
    return sha256(normalize_email(email).encode("utf-8")).hexdigest()


def mask_email(email: str) -> str:
    normalized = normalize_email(email)
    if "@" not in normalized:
        return mask_identifier(normalized)
    local, domain = normalized.split("@", 1)
    if len(local) <= 2:
        safe_local = local[:1] + "***"
    else:
        safe_local = f"{local[:2]}***{local[-1:]}"
    domain_parts = domain.split(".")
    if len(domain_parts) >= 2:
        safe_domain = f"{domain_parts[0][:1]}***.{domain_parts[-1]}"
    else:
        safe_domain = mask_identifier(domain)
    return f"{safe_local}@{safe_domain}"


def mask_identifier(value: str | None) -> str:
    if not value:
        return "unavailable"
    clean = sanitize_text(value, max_length=96) or "unavailable"
    if len(clean) <= 8:
        return f"{clean[:2]}***"
    return f"{clean[:4]}***{clean[-4:]}"


def sanitize_text(value: object | None, *, max_length: int = 255) -> str | None:
    if value is None:
        return None
    text = str(value).replace("\x00", "").strip()
    text = " ".join(text.split())
    if not text:
        return None
    return text[:max_length]


def sanitize_metadata(metadata: Mapping[str, Any] | None) -> dict[str, object]:
    if not metadata:
        return {}
    safe: dict[str, object] = {}
    for key, value in metadata.items():
        normalized_key = sanitize_text(key, max_length=64) or "field"
        if any(sensitive in normalized_key.lower() for sensitive in SENSITIVE_KEYS):
            safe[normalized_key] = "[redacted]"
        elif isinstance(value, str):
            safe[normalized_key] = sanitize_text(value, max_length=255) or ""
        elif isinstance(value, bool | int | float) or value is None:
            safe[normalized_key] = value
        elif isinstance(value, list | tuple):
            safe[normalized_key] = [
                sanitize_text(item, max_length=120) or "" for item in value[:20]
            ]
        else:
            safe[normalized_key] = sanitize_text(value, max_length=255) or ""
    return safe
