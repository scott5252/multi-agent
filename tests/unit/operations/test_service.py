from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import cast
from uuid import uuid4

import pytest
from sqlalchemy import func, select

from multi_agent_platform.bootstrap.container import Container, build_container
from multi_agent_platform.config.settings import AppEnvironment
from multi_agent_platform.db.models.audit_debugging import (
    AuditRuntimeTraceRecord,
    AuditTimelineEventRecord,
    InspectionAccessAuditEventRecord,
)
from multi_agent_platform.db.models.model_providers import GatewayInvocationAttempt
from multi_agent_platform.db.models.reliability import CapacitySnapshotRecord
from multi_agent_platform.operations.models import (
    OperationalLogEvent,
    OperationsAccessScope,
    OperationsAuthorizationError,
    OperationsLogFilters,
    OperationsRole,
)
from multi_agent_platform.operations.service import (
    OperationsConsoleService,
    _apply_common_gateway_filters,
    _apply_common_timeline_filters,
    _apply_common_trace_filters,
    _dependency_from_details,
    _ensure_aware,
    _matches_filters,
    _p95,
    _run_href,
    _telegram_ready,
    _usage_href,
)


def test_operations_console_requires_no_new_migration_file() -> None:
    migration_names = {path.name for path in Path("alembic/versions").glob("*.py")}

    assert not any("operations_console" in name for name in migration_names)


@pytest.mark.asyncio
async def test_operations_service_aggregates_capacity_and_filters_logs(
    session,
    settings,
) -> None:
    tenant_id = settings.local_principal_catalog_json["tenant-admin-acme"].tenant_id
    run_id = uuid4()
    session.add(
        CapacitySnapshotRecord(
            tenant_id=None,
            runnable_depth=4,
            delayed_depth=1,
            active_leases=2,
            retry_backlog=3,
            dead_letter_count=1,
            db_pool_wait_p95_ms=12,
            db_pool_in_use=2,
            db_pool_available=8,
            open_breaker_count=1,
        )
    )
    session.add(
        AuditTimelineEventRecord(
            tenant_id=tenant_id,
            workflow_run_id=run_id,
            sequence=1,
            event_category="runtime",
            run_status_after="running",
            origin_type="system",
            actor_principal_id="platform-admin",
            trace_id="trace-ops",
            source_event_id="source-1",
            criticality="diagnostic",
            safe_summary="Worker capacity recorded",
            safe_details={"dependency": "postgres", "secret": "should-redact"},
            occurred_at=datetime(2026, 5, 3, tzinfo=UTC),
        )
    )
    await session.flush()
    container = build_container(settings)
    try:
        service = OperationsConsoleService(session=session, container=container)
        access_scope = OperationsAccessScope(
            principal_id="platform-admin",
            role=OperationsRole.PLATFORM_ADMIN,
            can_export=True,
        )
        filters = OperationsLogFilters(trace_id="trace-ops", component="runtime")

        dashboard = await service.dashboard(
            access_scope=access_scope,
            filters=filters,
        )

        assert dashboard.capacity.runnable_depth == 4
        assert dashboard.logs[0].summary == "Worker capacity recorded"
        assert dashboard.logs[0].details["secret"] == "[redacted]"
        assert any(card.label == "Reliability State" for card in dashboard.status_cards)
    finally:
        await container.dispose()


@pytest.mark.asyncio
async def test_operations_service_filters_trace_events_and_audits_export_denial(
    session,
    settings,
) -> None:
    run_id = uuid4()
    timeline = AuditTimelineEventRecord(
        tenant_id=None,
        workflow_run_id=run_id,
        sequence=1,
        event_category="runtime",
        run_status_after="running",
        origin_type="system",
        actor_principal_id="platform-admin",
        trace_id="trace-denied",
        source_event_id="source-denied",
        criticality="diagnostic",
        safe_summary="Trace created",
        safe_details={"dependency": "queue"},
        occurred_at=datetime(2026, 5, 3, tzinfo=UTC),
    )
    session.add(timeline)
    await session.flush()
    session.add(
        AuditRuntimeTraceRecord(
            tenant_id=None,
            workflow_run_id=run_id,
            timeline_event_id=timeline.timeline_event_id,
            trace_type="tool_call",
            trace_id="trace-denied",
            outcome="failed",
            duration_ms=42,
            policy_outcome="runtime_required",
            subject_ref="queue-worker",
            metadata_json={"message": "must redact", "safe": "kept"},
            occurred_at=datetime(2026, 5, 3, 0, 0, 1, tzinfo=UTC),
        )
    )
    await session.flush()
    container = build_container(settings)
    try:
        service = OperationsConsoleService(session=session, container=container)
        access_scope = OperationsAccessScope(
            principal_id="auditor",
            role=OperationsRole.AUDITOR,
            can_export=False,
            trace_id="trace-denied",
        )
        filters = OperationsLogFilters(
            trace_id="trace-denied",
            severity="runtime",
            status="fail",
            dependency="queue",
            limit=10,
        )

        rows = await service.query_logs(access_scope=access_scope, filters=filters)

        assert rows[0].source == "runtime_trace"
        assert rows[0].latency_ms == 42
        assert rows[0].details["message"] == "[redacted]"
        with pytest.raises(OperationsAuthorizationError):
            await service.export_logs(
                access_scope=access_scope,
                filters=filters,
                storage_provider=container.storage_provider,
            )
        audit_count = await session.scalar(
            select(func.count()).select_from(InspectionAccessAuditEventRecord)
        )
        assert audit_count == 1
    finally:
        await container.dispose()


@pytest.mark.asyncio
async def test_operations_service_returns_safe_fallbacks_for_unavailable_sources(
    monkeypatch,
    session,
    settings,
) -> None:
    class BrokenHealthService:
        def __init__(self, container: object) -> None:
            self.container = container

        async def dependency_status(self) -> object:
            raise RuntimeError("health offline")

    class BrokenUsageService:
        def __init__(self, repository: object) -> None:
            self.repository = repository

        async def summarize_usage(self, **kwargs: object) -> object:
            raise ValueError("usage offline")

    monkeypatch.setattr(
        "multi_agent_platform.operations.service.HealthService",
        BrokenHealthService,
    )
    monkeypatch.setattr(
        "multi_agent_platform.operations.service.UsageAnalyticsService",
        BrokenUsageService,
    )
    container = build_container(settings)
    try:
        service = OperationsConsoleService(session=session, container=container)
        access_scope = OperationsAccessScope(
            principal_id="platform-admin",
            role=OperationsRole.PLATFORM_ADMIN,
        )

        dependencies = await service._dependency_views()
        capacity = await service._capacity_summary()
        usage = await service._usage_summary(
            access_scope=access_scope,
            filters=OperationsLogFilters(),
        )

        assert dependencies[0].status == "unavailable"
        assert dependencies[0].detail == "RuntimeError"
        assert capacity.runnable_depth == 0
        assert usage.usage_status == "unavailable"
    finally:
        await container.dispose()


def test_operations_service_helpers_cover_filter_and_reference_edges(settings) -> None:
    tenant_id = uuid4()
    run_id = uuid4()
    event = OperationalLogEvent(
        event_id="event-1",
        source="audit_timeline",
        occurred_at=datetime(2026, 5, 3, tzinfo=UTC),
        tenant_id=tenant_id,
        trace_id="trace-1",
        run_id=run_id,
        component="runtime",
        severity="diagnostic",
        status="running",
        dependency="postgres",
        summary="safe",
    )

    assert _matches_filters(event, OperationsLogFilters(component="run"))
    assert not _matches_filters(event, OperationsLogFilters(component="gateway"))
    assert not _matches_filters(event, OperationsLogFilters(severity="security"))
    assert not _matches_filters(event, OperationsLogFilters(status="failed"))
    assert not _matches_filters(event, OperationsLogFilters(dependency="redis"))
    assert _dependency_from_details({"component": "queue"}) == "queue"
    assert _dependency_from_details({"other": "value"}) is None
    assert _ensure_aware(datetime(2026, 5, 3)).tzinfo is UTC
    assert _ensure_aware(datetime(2026, 5, 3, tzinfo=UTC)).tzinfo is UTC
    assert _run_href(run_id, tenant_id) == (
        f"/admin/app/operations?run_id={run_id}&tenant_id={tenant_id}"
    )
    assert _usage_href(None) == "/admin/app/usage"
    assert _usage_href(tenant_id).endswith(f"?tenant_id={tenant_id}")
    assert _p95([None, 10, 20, 30]) == 30

    unsafe_production = settings.model_copy(
        update={
            "app_env": AppEnvironment.PRODUCTION,
            "telegram_provider_token_ref": "plain-token",
            "telegram_webhook_secret": "static:qa019/webhook",
        }
    )
    safe_production = settings.model_copy(
        update={
            "app_env": AppEnvironment.PRODUCTION,
            "telegram_provider_token_ref": "static:qa019/token",
            "telegram_webhook_secret": "env:TELEGRAM_WEBHOOK_SECRET",
        }
    )

    assert not _telegram_ready(
        cast(Container, SimpleNamespace(settings=unsafe_production))
    )
    assert _telegram_ready(cast(Container, SimpleNamespace(settings=safe_production)))


def test_operations_filter_builders_apply_all_common_dimensions() -> None:
    filters = OperationsLogFilters(
        tenant_id=uuid4(),
        run_id=uuid4(),
        trace_id="trace-1",
        start=datetime(2026, 5, 3, tzinfo=UTC),
        end=datetime(2026, 5, 4, tzinfo=UTC),
    )

    timeline_stmt = _apply_common_timeline_filters(
        select(AuditTimelineEventRecord), filters
    )
    trace_stmt = _apply_common_trace_filters(select(AuditRuntimeTraceRecord), filters)
    gateway_stmt = _apply_common_gateway_filters(
        select(GatewayInvocationAttempt), filters
    )

    assert timeline_stmt.whereclause is not None
    assert trace_stmt.whereclause is not None
    assert gateway_stmt.whereclause is not None
