from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import select

from multi_agent_platform.db.models.usage import UsageExportRequest
from multi_agent_platform.db.repositories.usage import UsageRepository
from multi_agent_platform.model_providers.models import (
    GatewayInvocationContext,
    GatewayResult,
    GatewayUsage,
    ProviderType,
    TestOutcome,
    UsageAvailability,
)
from multi_agent_platform.storage.base import ArtifactHandle, StorageProvider
from multi_agent_platform.usage.models import (
    UsageAccessScope,
    UsageEventStatus,
    UsageExportStatus,
    UsageFilters,
    UsageScopeType,
)
from multi_agent_platform.usage.service import (
    UsageAccessDeniedError,
    UsageAnalyticsService,
)


class FailingStorageProvider(StorageProvider):
    provider_name = "failing"

    async def put(self, key: str, payload: bytes) -> ArtifactHandle:
        raise OSError("storage offline")

    async def get(self, key: str) -> bytes:
        raise OSError("storage offline")


async def test_usage_service_records_safe_gateway_result(
    session, seeded_tenant
) -> None:
    service = UsageAnalyticsService(UsageRepository(session))
    event = await service.record_gateway_result(
        context=GatewayInvocationContext(
            tenant_id=seeded_tenant.tenant_id,
            initiating_principal_id="tenant-admin",
            workflow_run_id=uuid4(),
            workflow_run_step_id=uuid4(),
            agent_key="writer",
            sub_agent_key="critic",
            idempotency_key="usage-service-1",
            model_routing_provenance={"prompt": "never store this"},
            execution_mode="test",
        ),
        provider_key=ProviderType.OPENAI,
        model_id="gpt-test",
        result=GatewayResult(
            outcome=TestOutcome.SUCCESS,
            latency_ms=12,
            usage=GatewayUsage(
                availability=UsageAvailability.AVAILABLE,
                input_tokens=10,
                output_tokens=5,
                total_tokens=15,
            ),
            safe_audit_summary={"content": "redact me"},
        ),
    )

    assert event.total_tokens == 15
    assert event.estimated_cost_micros == 25
    assert event.usage_status is UsageEventStatus.CONFIRMED
    assert event.safe_attribution["model_routing_provenance"]["prompt"] == "[redacted]"
    assert event.safe_attribution["result"]["content"] == "[redacted]"


async def test_usage_service_summarizes_rollups(session, seeded_tenant) -> None:
    service = UsageAnalyticsService(UsageRepository(session))
    await service.record_gateway_result(
        context=GatewayInvocationContext(
            tenant_id=seeded_tenant.tenant_id,
            initiating_principal_id="tenant-admin",
            agent_key="writer",
            execution_mode="test",
            idempotency_key="rollup-1",
        ),
        provider_key="openai",
        model_id="gpt-test",
        result=GatewayResult(
            outcome=TestOutcome.SUCCESS,
            usage=GatewayUsage(
                availability=UsageAvailability.AVAILABLE,
                input_tokens=2,
                output_tokens=3,
                total_tokens=5,
            ),
        ),
    )

    summary = await service.summarize_usage(
        access_scope=UsageAccessScope(
            scope_type=UsageScopeType.TENANT,
            tenant_id=seeded_tenant.tenant_id,
            principal_id="tenant-admin",
        ),
        filters=UsageFilters(group_by="agent"),
    )

    assert summary.totals.total_events == 1
    assert summary.totals.total_tokens == 5
    assert summary.rollups[0].label == "writer"


async def test_usage_service_creates_csv_export(
    session,
    seeded_tenant,
    filesystem_storage_provider,
) -> None:
    service = UsageAnalyticsService(UsageRepository(session))
    await service.record_gateway_result(
        context=GatewayInvocationContext(
            tenant_id=seeded_tenant.tenant_id,
            initiating_principal_id="tenant-admin",
            agent_key="writer",
            idempotency_key="export-1",
        ),
        provider_key="openai",
        model_id="gpt-test",
        result=GatewayResult(
            outcome=TestOutcome.SUCCESS,
            usage=GatewayUsage(
                availability=UsageAvailability.AVAILABLE,
                input_tokens=1,
                output_tokens=2,
                total_tokens=3,
            ),
        ),
    )

    export = await service.create_csv_export(
        access_scope=UsageAccessScope(
            scope_type=UsageScopeType.PLATFORM,
            principal_id="platform-admin",
            platform_admin=True,
        ),
        filters=UsageFilters(tenant_id=seeded_tenant.tenant_id),
        storage_provider=filesystem_storage_provider,
    )

    assert export.status is UsageExportStatus.COMPLETED
    assert export.row_count == 1
    assert export.artifact_uri is not None
    assert export.artifact_uri.startswith("file:")
    assert export.artifact_sha256 is not None
    assert export.artifact_size_bytes is not None
    assert export.artifact_size_bytes > 0


async def test_usage_service_denies_cross_tenant_export(session, seeded_tenant) -> None:
    service = UsageAnalyticsService(UsageRepository(session))

    with pytest.raises(UsageAccessDeniedError, match="cross_tenant_scope"):
        await service.create_csv_export(
            access_scope=UsageAccessScope(
                scope_type=UsageScopeType.TENANT,
                tenant_id=seeded_tenant.tenant_id,
                principal_id="tenant-admin",
            ),
            filters=UsageFilters(tenant_id=uuid4()),
            storage_provider=FailingStorageProvider(),
        )

    export = (await session.execute(select(UsageExportRequest))).scalar_one()
    assert export.status is UsageExportStatus.DENIED
    assert export.denial_reason == "cross_tenant_scope"


async def test_usage_service_marks_export_failed_when_storage_fails(
    session,
    seeded_tenant,
) -> None:
    service = UsageAnalyticsService(UsageRepository(session))

    with pytest.raises(RuntimeError, match="usage export failed"):
        await service.create_csv_export(
            access_scope=UsageAccessScope(
                scope_type=UsageScopeType.TENANT,
                tenant_id=seeded_tenant.tenant_id,
                principal_id="tenant-admin",
            ),
            filters=UsageFilters(),
            storage_provider=FailingStorageProvider(),
        )

    export = (await session.execute(select(UsageExportRequest))).scalar_one()
    assert export.status is UsageExportStatus.FAILED
    assert export.failure_reason == "usage export failed"


async def test_usage_service_reconciles_allowed_values_only(
    session,
    seeded_tenant,
) -> None:
    service = UsageAnalyticsService(UsageRepository(session))
    event = await service.record_gateway_result(
        context=GatewayInvocationContext(
            tenant_id=seeded_tenant.tenant_id,
            initiating_principal_id="tenant-admin",
            idempotency_key="reconcile-1",
        ),
        provider_key="openai",
        model_id="gpt-test",
        result=GatewayResult(
            outcome=TestOutcome.SUCCESS,
            usage=GatewayUsage(
                availability=UsageAvailability.AVAILABLE,
                input_tokens=1,
                output_tokens=2,
                total_tokens=3,
            ),
        ),
    )

    record = await service.reconcile_usage_event(
        event_id=event.llm_usage_event_id,
        confirmed_values={"total_tokens": 4, "safe_attribution": {"prompt": "raw"}},
        source="provider-confirmation",
        reconciled_by_principal_id="system",
    )

    assert record.confirmed_values == {"total_tokens": 4}
    assert event.total_tokens == 4
    assert event.usage_status is UsageEventStatus.CONFIRMED


async def test_usage_service_reconcile_missing_event_raises(session) -> None:
    service = UsageAnalyticsService(UsageRepository(session))

    with pytest.raises(LookupError, match="usage event not found"):
        await service.reconcile_usage_event(
            event_id=uuid4(),
            confirmed_values={"total_tokens": 4},
            source="provider-confirmation",
        )
