from __future__ import annotations

from multi_agent_platform.db.models.usage import LlmUsageEvent
from multi_agent_platform.db.repositories.usage import UsageRepository
from multi_agent_platform.usage.models import (
    UsageAccessScope,
    UsageEventStatus,
    UsageFilters,
    UsageScopeType,
)


async def test_usage_time_range_query_handles_seeded_volume(
    session,
    seeded_tenant,
) -> None:
    session.add_all(
        [
            LlmUsageEvent(
                tenant_id=seeded_tenant.tenant_id,
                provider_key="openai",
                model_id="gpt-test",
                execution_mode="test",
                total_tokens=i % 100,
                latency_ms=10,
                usage_status=UsageEventStatus.ESTIMATED,
            )
            for i in range(500)
        ]
    )
    await session.flush()

    rows = await UsageRepository(session).list_events(
        access_scope=UsageAccessScope(
            scope_type=UsageScopeType.TENANT,
            tenant_id=seeded_tenant.tenant_id,
            principal_id="tenant-admin",
        ),
        filters=UsageFilters(provider_key="openai"),
        limit=500,
    )

    assert len(rows) == 500
