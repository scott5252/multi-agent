from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

_SAFE_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]*$")


@dataclass(slots=True, frozen=True)
class QueryWindow:
    tenant_id: UUID | None
    start: datetime
    end: datetime
    limit: int = 100


@dataclass(slots=True, frozen=True)
class PartitionPlan:
    table_name: str
    partition_name: str
    detach_after: datetime
    drop_after: datetime


def month_floor(value: datetime) -> datetime:
    value = value.astimezone(UTC) if value.tzinfo else value.replace(tzinfo=UTC)
    return value.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def next_month(value: datetime) -> datetime:
    start = month_floor(value)
    if start.month == 12:
        return start.replace(year=start.year + 1, month=1)
    return start.replace(month=start.month + 1)


def partition_name(table_name: str, window_start: datetime) -> str:
    if not _SAFE_IDENTIFIER.match(table_name):
        raise ValueError("table name must be a safe lowercase SQL identifier")
    start = month_floor(window_start)
    return f"{table_name}_y{start.year:04d}m{start.month:02d}"


def tenant_hash_partition_name(
    table_name: str, *, tenant_id: UUID, modulus: int = 16
) -> str:
    if modulus <= 0:
        raise ValueError("modulus must be positive")
    bucket = tenant_id.int % modulus
    return f"{partition_name(table_name, datetime.now(UTC))}_t{bucket:02d}"


def validate_query_window(window: QueryWindow) -> QueryWindow:
    if window.end <= window.start:
        raise ValueError("query window end must be after start")
    if window.limit < 1 or window.limit > 500:
        raise ValueError("query window limit must be between 1 and 500")
    return window


def retention_plan(
    table_name: str,
    *,
    now: datetime,
    retention_days: int,
    detach_grace_days: int = 7,
) -> PartitionPlan:
    if retention_days <= 0:
        raise ValueError("retention_days must be positive")
    boundary = month_floor(now - timedelta(days=retention_days))
    return PartitionPlan(
        table_name=table_name,
        partition_name=partition_name(table_name, boundary),
        detach_after=boundary + timedelta(days=retention_days),
        drop_after=boundary + timedelta(days=retention_days + detach_grace_days),
    )
