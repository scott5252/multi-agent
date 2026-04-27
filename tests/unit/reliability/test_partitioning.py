from __future__ import annotations

from datetime import UTC, datetime

import pytest

from multi_agent_platform.reliability.partitioning import (
    QueryWindow,
    month_floor,
    next_month,
    partition_name,
    retention_plan,
    validate_query_window,
)


def test_partition_names_are_month_scoped() -> None:
    value = datetime(2026, 4, 26, 12, tzinfo=UTC)
    assert month_floor(value) == datetime(2026, 4, 1, tzinfo=UTC)
    assert next_month(value) == datetime(2026, 5, 1, tzinfo=UTC)
    assert partition_name("reliability_admission_decisions", value).endswith(
        "_y2026m04"
    )


def test_query_window_validation_rejects_unbounded_requests() -> None:
    start = datetime(2026, 4, 26, tzinfo=UTC)
    with pytest.raises(ValueError):
        validate_query_window(QueryWindow(None, start, start, limit=50))
    with pytest.raises(ValueError):
        validate_query_window(QueryWindow(None, start, next_month(start), limit=501))


def test_retention_plan_names_detached_partition() -> None:
    plan = retention_plan(
        "reliability_retry_schedules",
        now=datetime(2026, 4, 26, tzinfo=UTC),
        retention_days=30,
    )
    assert plan.partition_name == "reliability_retry_schedules_y2026m03"
    assert plan.drop_after > plan.detach_after
