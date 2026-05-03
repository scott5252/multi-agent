from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from multi_agent_platform.operations.export import operation_log_events_to_csv
from multi_agent_platform.operations.models import OperationalLogEvent


def test_operation_log_events_to_csv_contains_only_safe_columns() -> None:
    event = OperationalLogEvent(
        event_id="audit:1",
        source="audit_timeline",
        occurred_at=datetime(2026, 5, 3, tzinfo=UTC),
        tenant_id=uuid4(),
        trace_id="trace-safe",
        run_id=uuid4(),
        component="runtime",
        severity="diagnostic",
        status="running",
        dependency="postgres",
        summary="Safe summary",
        details={"secret": "[redacted]"},
        latency_ms=42,
    )

    payload = operation_log_events_to_csv([event]).decode("utf-8")

    assert "Safe summary" in payload
    assert "postgres" in payload
    assert "secret" not in payload
    assert "details" not in payload
