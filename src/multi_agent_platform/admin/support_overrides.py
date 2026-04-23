from __future__ import annotations

from datetime import UTC, datetime, timedelta


def build_override_expiration(*, hours: int) -> datetime:
    return datetime.now(UTC) + timedelta(hours=hours)
