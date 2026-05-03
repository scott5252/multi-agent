from __future__ import annotations

from multi_agent_platform.db.models.usage import LlmUsageEvent
from multi_agent_platform.usage.models import UsageEventStatus


async def test_usage_event_model_defaults(session, seeded_tenant) -> None:
    event = LlmUsageEvent(
        tenant_id=seeded_tenant.tenant_id,
        provider_key="openai",
        model_id="gpt-test",
        execution_mode="test",
        latency_ms=10,
        usage_status=UsageEventStatus.UNAVAILABLE,
    )
    session.add(event)
    await session.flush()

    assert event.currency == "USD"
    assert event.safe_attribution == {}
    assert event.llm_usage_event_id
