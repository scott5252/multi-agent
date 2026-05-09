from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from typing import Any

MAX_SAFE_TEXT_LENGTH = 4_000
PROHIBITED_SAFE_TEXT_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"authorization\s*:", re.IGNORECASE),
    re.compile(r"bearer\s+[A-Za-z0-9._-]{12,}", re.IGNORECASE),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bpassword\s*=", re.IGNORECASE),
    re.compile(r"\bapi[_-]?key\s*=", re.IGNORECASE),
    re.compile(r"raw_prompt", re.IGNORECASE),
    re.compile(r"raw_completion", re.IGNORECASE),
)


class UnsafeDesignReviewContentError(ValueError):
    pass


def validate_safe_text(value: str, *, field_name: str) -> str:
    cleaned = " ".join(value.strip().split())
    if not cleaned:
        raise UnsafeDesignReviewContentError(f"{field_name} is required")
    if len(cleaned) > MAX_SAFE_TEXT_LENGTH:
        raise UnsafeDesignReviewContentError(
            f"{field_name} exceeds the safe summary length limit"
        )
    for pattern in PROHIBITED_SAFE_TEXT_PATTERNS:
        if pattern.search(cleaned):
            raise UnsafeDesignReviewContentError(
                f"{field_name} appears to contain protected raw content"
            )
    return cleaned


def digest_safe_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def safe_metadata(value: Mapping[str, Any] | None) -> dict[str, object]:
    metadata: dict[str, object] = {}
    for key, item in (value or {}).items():
        key_text = validate_safe_text(str(key), field_name="metadata key")
        if item is None or isinstance(item, (bool, int, float)):
            metadata[key_text] = item
        elif isinstance(item, str):
            metadata[key_text] = validate_safe_text(
                item,
                field_name=f"metadata.{key_text}",
            )
        else:
            metadata[key_text] = validate_safe_text(
                str(item),
                field_name=f"metadata.{key_text}",
            )
    return metadata
