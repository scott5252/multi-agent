from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.usage.export import usage_events_to_csv
from multi_agent_platform.usage.models import UsageEventStatus, UsageEventView, utc_now


def test_usage_export_contains_only_safe_columns() -> None:
    payload = usage_events_to_csv(
        [
            UsageEventView(
                llm_usage_event_id=uuid4(),
                tenant_id=uuid4(),
                principal_id="tenant-admin",
                provider_key="openai",
                model_id="gpt-test",
                execution_mode="test",
                total_tokens=5,
                latency_ms=12,
                estimated_cost_micros=10,
                usage_status=UsageEventStatus.ESTIMATED,
                recorded_at=utc_now(),
            )
        ]
    ).decode()

    assert "usage_event_id,tenant_id,principal_id" in payload
    assert "raw prompt" not in payload.lower()
    assert "raw completion" not in payload.lower()
    assert "secret" not in payload.lower()
