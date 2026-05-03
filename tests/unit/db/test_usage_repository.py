from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from multi_agent_platform.db.models.usage import LlmUsageEvent
from multi_agent_platform.db.repositories.usage import (
    UsageAccessDeniedError,
    UsageRepository,
)
from multi_agent_platform.usage.models import (
    UsageAccessScope,
    UsageEventStatus,
    UsageExportStatus,
    UsageFilters,
    UsageScopeType,
)


async def test_usage_repository_filters_by_tenant_and_idempotency(
    session,
    seeded_tenant,
) -> None:
    repository = UsageRepository(session)
    event = await repository.record_usage_event(
        LlmUsageEvent(
            tenant_id=seeded_tenant.tenant_id,
            principal_id="tenant-admin",
            provider_key="openai",
            model_id="gpt-test",
            execution_mode="test",
            idempotency_key="idem-1",
            total_tokens=5,
            latency_ms=10,
            usage_status=UsageEventStatus.ESTIMATED,
        )
    )
    duplicate = await repository.record_usage_event(
        LlmUsageEvent(
            tenant_id=seeded_tenant.tenant_id,
            provider_key="openai",
            model_id="gpt-test",
            execution_mode="test",
            idempotency_key="idem-1",
            total_tokens=99,
            latency_ms=10,
            usage_status=UsageEventStatus.ESTIMATED,
        )
    )

    assert duplicate.llm_usage_event_id == event.llm_usage_event_id
    assert await repository.list_events(
        access_scope=UsageAccessScope(
            scope_type=UsageScopeType.TENANT,
            tenant_id=seeded_tenant.tenant_id,
            principal_id="tenant-admin",
        ),
        filters=UsageFilters(),
    ) == [event]
    assert (
        await repository.list_events(
            access_scope=UsageAccessScope(
                scope_type=UsageScopeType.TENANT,
                tenant_id=uuid4(),
                principal_id="other-admin",
            ),
            filters=UsageFilters(),
        )
        == []
    )


async def test_usage_repository_reconciles_event(session, seeded_tenant) -> None:
    repository = UsageRepository(session)
    event = await repository.record_usage_event(
        LlmUsageEvent(
            tenant_id=seeded_tenant.tenant_id,
            provider_key="openai",
            model_id="gpt-test",
            execution_mode="test",
            total_tokens=5,
            latency_ms=10,
            usage_status=UsageEventStatus.ESTIMATED,
        )
    )

    record = await repository.record_reconciliation(
        event=event,
        source="provider-late-usage",
        confirmed_values={"total_tokens": 7, "estimated_cost_micros": 21},
        reconciled_by_principal_id="system",
    )

    assert record.previous_values["total_tokens"] == 5
    assert event.total_tokens == 7
    assert event.usage_status is UsageEventStatus.CONFIRMED


async def test_usage_repository_reuses_active_pricing_version(session) -> None:
    repository = UsageRepository(session)

    pricing = await repository.get_or_create_pricing_version(
        provider_key="openai",
        model_id="gpt-test",
        actor_principal_id="creator",
    )
    reused = await repository.get_or_create_pricing_version(
        provider_key="openai",
        model_id="gpt-test",
        actor_principal_id="other",
    )

    assert reused.llm_pricing_version_id == pricing.llm_pricing_version_id
    assert reused.created_by_principal_id == "creator"


async def test_usage_repository_applies_all_event_filters(
    session,
    seeded_tenant,
) -> None:
    repository = UsageRepository(session)
    now = datetime.now(UTC)
    workflow_lineage_id = uuid4()
    workflow_version_id = uuid4()
    workflow_run_id = uuid4()
    workflow_run_step_id = uuid4()
    prompt_version_id = uuid4()
    event = await repository.record_usage_event(
        LlmUsageEvent(
            tenant_id=seeded_tenant.tenant_id,
            principal_id="tenant-admin",
            provider_key="openai",
            model_id="gpt-test",
            workflow_lineage_id=workflow_lineage_id,
            workflow_version_id=workflow_version_id,
            workflow_run_id=workflow_run_id,
            workflow_run_step_id=workflow_run_step_id,
            agent_key="writer",
            sub_agent_key="critic",
            prompt_version_id=prompt_version_id,
            execution_mode="test",
            total_tokens=5,
            latency_ms=10,
            usage_status=UsageEventStatus.ESTIMATED,
            recorded_at=now,
        )
    )
    await repository.record_usage_event(
        LlmUsageEvent(
            tenant_id=seeded_tenant.tenant_id,
            principal_id="other",
            provider_key="local",
            model_id="other-model",
            execution_mode="production",
            total_tokens=3,
            latency_ms=10,
            usage_status=UsageEventStatus.CONFIRMED,
            recorded_at=now,
        )
    )

    events = await repository.list_events_for_export(
        access_scope=UsageAccessScope(
            scope_type=UsageScopeType.PLATFORM,
            principal_id="platform-admin",
            platform_admin=True,
        ),
        filters=UsageFilters(
            tenant_id=seeded_tenant.tenant_id,
            start=now - timedelta(minutes=1),
            end=now + timedelta(minutes=1),
            provider_key="openai",
            model_id="gpt-test",
            workflow_lineage_id=workflow_lineage_id,
            workflow_version_id=workflow_version_id,
            workflow_run_id=workflow_run_id,
            workflow_run_step_id=workflow_run_step_id,
            agent_key="writer",
            sub_agent_key="critic",
            prompt_version_id=prompt_version_id,
            execution_mode="test",
            usage_status=UsageEventStatus.ESTIMATED,
            principal_id="tenant-admin",
        ),
    )

    assert events == [event]


async def test_usage_repository_export_access_scope(session, seeded_tenant) -> None:
    repository = UsageRepository(session)
    export = await repository.create_export_request(
        access_scope=UsageAccessScope(
            scope_type=UsageScopeType.TENANT,
            tenant_id=seeded_tenant.tenant_id,
            principal_id="tenant-admin",
        ),
        filters=UsageFilters(),
        status=UsageExportStatus.PENDING,
    )
    completed = await repository.complete_export_request(
        export,
        row_count=2,
        artifact_uri="file:///tmp/export.csv",
        artifact_sha256="a" * 64,
        artifact_size_bytes=200,
    )

    assert completed.completed_at is not None
    assert (
        await repository.get_export_request(
            completed.usage_export_request_id,
            access_scope=UsageAccessScope(
                scope_type=UsageScopeType.PLATFORM,
                principal_id="platform-admin",
                platform_admin=True,
            ),
        )
        == completed
    )
    assert (
        await repository.get_export_request(
            completed.usage_export_request_id,
            access_scope=UsageAccessScope(
                scope_type=UsageScopeType.TENANT,
                tenant_id=seeded_tenant.tenant_id,
                principal_id="tenant-admin",
            ),
        )
        == completed
    )
    assert (
        await repository.get_export_request(
            uuid4(),
            access_scope=UsageAccessScope(
                scope_type=UsageScopeType.PLATFORM,
                principal_id="platform-admin",
                platform_admin=True,
            ),
        )
        is None
    )
    with pytest.raises(UsageAccessDeniedError):
        await repository.get_export_request(
            completed.usage_export_request_id,
            access_scope=UsageAccessScope(
                scope_type=UsageScopeType.TENANT,
                tenant_id=uuid4(),
                principal_id="other-admin",
            ),
        )
