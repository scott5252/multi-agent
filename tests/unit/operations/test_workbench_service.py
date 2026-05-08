from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from multi_agent_platform.api.schemas.admin_react import ReactAdminScope
from multi_agent_platform.auth.principal import (
    AuthMode,
    AuthProvider,
    PrincipalContext,
)
from multi_agent_platform.bootstrap.container import build_container
from multi_agent_platform.db.models.runtime_orchestration import (
    RunStepRecord,
    RuntimeExecutionBundleRecord,
    RuntimeRunStatus,
    RuntimeStepStatus,
    RuntimeTimelineEventRecord,
    WorkflowRunRecord,
)
from multi_agent_platform.operations import workbench
from multi_agent_platform.operations.models import (
    OperationalLogEvent,
    OperationsCapacitySummary,
    OperationsDashboardSnapshot,
    OperationsLink,
    OperationsProviderSummary,
    OperationsUsageSummary,
)
from multi_agent_platform.operations.service import OperationsConsoleService
from multi_agent_platform.operations.workbench import (
    RunDebugNotFoundError,
    build_operations_workbench_envelope,
    build_run_debug_envelope,
    create_workbench_export_snapshot,
)
from tests.fixtures.operations_workbench import seed_operations_workbench_live_data


def _principal(
    principal_id: str = "platform-admin",
    *,
    roles: tuple[str, ...] = ("platform_admin",),
    permissions: tuple[str, ...] = ("operations:read",),
) -> PrincipalContext:
    return PrincipalContext(
        principal_id=principal_id,
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        role_codes=roles,
        permission_codes=permissions,
        trace_id="trace-workbench-test",
    )


@pytest.mark.asyncio
async def test_platform_workbench_uses_live_seeded_evidence(session, settings) -> None:
    tenant_id = settings.local_principal_catalog_json["tenant-admin-acme"].tenant_id
    ids = await seed_operations_workbench_live_data(session, tenant_id=tenant_id)
    scope = ReactAdminScope(scope_type="platform", tenant_id=None, label="Platform")
    container = build_container(settings)
    try:
        envelope = await build_operations_workbench_envelope(
            scope=scope,
            principal=_principal(),
            service=OperationsConsoleService(session=session, container=container),
        )
    finally:
        await container.dispose()

    assert envelope.time_range.preset == "60m"
    assert envelope.refresh is not None
    assert envelope.refresh.interval_seconds == 30
    assert envelope.generated_at_label.startswith("Generated from live evidence")
    assert "Provider health" not in envelope.model_dump_json()
    assert "qa029" not in envelope.model_dump_json().lower()
    assert "Gateway attempt recorded retryable timeout category." in {
        log.summary for log in envelope.logs
    }
    assert envelope.run_debug is not None
    assert envelope.run_debug.workflow_run_id == str(ids["run_id"])


@pytest.mark.asyncio
async def test_tenant_workbench_hides_platform_pressure_and_empty_scope(
    session,
    settings,
) -> None:
    tenant_id = settings.local_principal_catalog_json["tenant-admin-acme"].tenant_id
    other_tenant_id = uuid4()
    await seed_operations_workbench_live_data(session, tenant_id=tenant_id)
    container = build_container(settings)
    try:
        acme = await build_operations_workbench_envelope(
            scope=ReactAdminScope(
                scope_type="tenant",
                tenant_id=tenant_id,
                label="Acme",
            ),
            principal=_principal("tenant-admin-acme", roles=("tenant_admin",)),
            service=OperationsConsoleService(session=session, container=container),
        )
        globex = await build_operations_workbench_envelope(
            scope=ReactAdminScope(
                scope_type="tenant",
                tenant_id=other_tenant_id,
                label="Globex",
            ),
            principal=_principal("tenant-admin-globex", roles=("tenant_admin",)),
            service=OperationsConsoleService(session=session, container=container),
        )
    finally:
        await container.dispose()

    acme_text = acme.model_dump_json()
    assert "Model Providers" not in acme_text
    assert "DB Pool Pressure" not in acme_text
    assert "OpenAI provider" not in acme_text
    assert "gpt-qa057-live" not in acme_text
    assert "/admin/app/governance/providers" not in acme_text
    assert acme.health_panels[0].partial_reason is not None
    assert acme.logs
    assert globex.logs == ()
    assert globex.summary_cards[0].status == "empty"


@pytest.mark.asyncio
async def test_run_debug_and_export_are_live_and_safe(session, settings) -> None:
    tenant_id = settings.local_principal_catalog_json["tenant-admin-acme"].tenant_id
    ids = await seed_operations_workbench_live_data(session, tenant_id=tenant_id)
    scope = ReactAdminScope(scope_type="tenant", tenant_id=tenant_id, label="Acme")
    container = build_container(settings)
    try:
        service = OperationsConsoleService(session=session, container=container)
        run_debug = await build_run_debug_envelope(
            scope=scope,
            principal=_principal("tenant-admin-acme", roles=("tenant_admin",)),
            service=service,
            workflow_run_id=ids["run_id"],
        )
        export = await create_workbench_export_snapshot(
            scope=scope,
            principal=_principal("tenant-admin-acme", roles=("tenant_admin",)),
            service=service,
            storage_provider=container.storage_provider,
        )
    finally:
        await container.dispose()

    assert run_debug.gateway_attempts[0].credential_diagnostic_category
    assert run_debug.tool_calls[0].policy_outcome == "allowed_read_only"
    assert run_debug.deliveries[0].failure_category == "telegram-retry-scheduled"
    assert "OpenAI provider" not in run_debug.model_dump_json()
    assert "gpt-qa057-live" not in run_debug.model_dump_json()
    assert "/admin/app/governance/providers" not in run_debug.model_dump_json()
    assert export.status == "complete"
    assert export.artifact_reference_id is not None
    assert export.artifact_reference_id.startswith("operations-export:")
    assert not export.artifact_reference_id.startswith("/")
    assert "/Users/" not in export.model_dump_json()


@pytest.mark.asyncio
async def test_missing_run_debug_is_not_found(session, settings) -> None:
    container = build_container(settings)
    try:
        with pytest.raises(RunDebugNotFoundError):
            await build_run_debug_envelope(
                scope=ReactAdminScope(
                    scope_type="platform", tenant_id=None, label="Platform"
                ),
                principal=_principal(),
                service=OperationsConsoleService(session=session, container=container),
                workflow_run_id="00000000-0000-0000-0000-000000000057",
            )
    finally:
        await container.dispose()


@pytest.mark.asyncio
async def test_persisted_run_debug_uses_runtime_bundle_steps_and_events(
    session,
    settings,
) -> None:
    tenant_id = settings.local_principal_catalog_json["tenant-admin-acme"].tenant_id
    run_id = uuid4()
    bundle = RuntimeExecutionBundleRecord(
        tenant_id=tenant_id,
        workflow_run_id=run_id,
        published_workflow_version_id=uuid4(),
        bundle_digest="b" * 64,
    )
    session.add(bundle)
    await session.flush()
    session.add(
        WorkflowRunRecord(
            workflow_run_id=run_id,
            tenant_id=tenant_id,
            scope_type="tenant",
            initiating_principal_id="tenant-admin-acme",
            run_bundle_id=bundle.run_bundle_id,
            status=RuntimeRunStatus.RUNNING,
            idempotency_key="qa057-runtime-run",
            trace_id="trace-runtime-run",
            started_at=datetime.now(UTC) - timedelta(minutes=9),
        )
    )
    session.add(
        RuntimeTimelineEventRecord(
            tenant_id=tenant_id,
            workflow_run_id=run_id,
            event_type="node_started",
            severity="warning",
            payload={
                "summary": "Runtime node started safely.",
                "count": 2,
                "ignored": {"nested": True},
            },
            trace_id="trace-runtime-run",
        )
    )
    session.add(
        RunStepRecord(
            workflow_run_id=run_id,
            tenant_id=tenant_id,
            step_key="collect_live_evidence",
            step_type="task",
            status=RuntimeStepStatus.SUCCEEDED,
        )
    )
    await session.flush()
    container = build_container(settings)
    try:
        service = OperationsConsoleService(session=session, container=container)
        debug = await build_run_debug_envelope(
            scope=ReactAdminScope(
                scope_type="platform", tenant_id=None, label="Platform"
            ),
            principal=_principal(),
            service=service,
            workflow_run_id=run_id,
        )
        with pytest.raises(RunDebugNotFoundError):
            await build_run_debug_envelope(
                scope=ReactAdminScope(
                    scope_type="tenant",
                    tenant_id=uuid4(),
                    label="Other tenant",
                ),
                principal=_principal("tenant-admin-other", roles=("tenant_admin",)),
                service=service,
                workflow_run_id=run_id,
            )
    finally:
        await container.dispose()

    assert debug.safe_title == f"Workflow run {str(run_id)[:8]} (running)"
    assert "bbbbbbbbbbbb" in debug.bundle_summary
    assert debug.timeline[0].category == "runtime_run"
    assert any(event.category == "node_started" for event in debug.timeline)
    assert debug.branches[0].label == "Collect Live Evidence"


@pytest.mark.asyncio
async def test_first_visible_run_debug_skips_logs_without_visible_runs(
    session,
    settings,
) -> None:
    container = build_container(settings)
    try:
        service = OperationsConsoleService(session=session, container=container)
        result = await workbench._first_visible_run_debug(
            scope=ReactAdminScope(
                scope_type="platform", tenant_id=None, label="Platform"
            ),
            principal=_principal(),
            service=service,
            logs=(
                _event(
                    event_id="log-without-run",
                    source="audit",
                    component="runtime",
                    status="ready",
                    severity="info",
                    run_id=None,
                ),
                _event(
                    event_id="log-missing-run",
                    source="audit",
                    component="runtime",
                    status="ready",
                    severity="info",
                    run_id=uuid4(),
                ),
            ),
        )
    finally:
        await container.dispose()

    assert result is None


@pytest.mark.asyncio
async def test_export_validation_denied_and_unavailable_states(settings) -> None:
    scope = ReactAdminScope(scope_type="platform", tenant_id=None, label="Platform")
    container = build_container(settings)
    try:
        validation = await create_workbench_export_snapshot(
            scope=scope,
            principal=_principal(),
            service=_ExportService("ok"),
            storage_provider=container.storage_provider,
            request=workbench.WorkbenchExportRequest(range="24h"),
        )
        denied = await create_workbench_export_snapshot(
            scope=scope,
            principal=_principal(),
            service=_ExportService("denied"),
            storage_provider=container.storage_provider,
        )
        unavailable = await create_workbench_export_snapshot(
            scope=scope,
            principal=_principal(),
            service=_ExportService("unavailable"),
            storage_provider=container.storage_provider,
        )
    finally:
        await container.dispose()

    assert validation.status == "validation"
    assert denied.status == "denied"
    assert unavailable.status == "unavailable"


def test_workbench_helper_branches_cover_empty_and_status_states() -> None:
    platform = ReactAdminScope(scope_type="platform", tenant_id=None, label="Platform")
    tenant = ReactAdminScope(scope_type="tenant", tenant_id=uuid4(), label="Acme")
    dashboard = OperationsDashboardSnapshot(
        health_status="ready",
        status_cards=(),
        dependencies=(),
        capacity=OperationsCapacitySummary(),
        redaction_notice="redacted",
    )
    empty_cards = workbench._summary_cards(dashboard=dashboard, scope=platform, logs=())
    assert empty_cards[0].card_id == "empty-live-evidence"
    causes = workbench._likely_causes(
        dashboard=dashboard,
        logs=(
            _event(
                event_id="ready-log",
                source="audit",
                component="runtime",
                status="ready",
                severity="info",
            ),
        ),
        scope=platform,
    )
    assert causes[0].cause_id == "no-live-warning-symptoms"
    assert workbench._first_link(_event(links=()), scope=tenant) is None

    for value, expected in {
        "empty": "empty",
        "pending": "queued",
        "denied": "denied",
        "validation_error": "validation",
        "conflict": "conflict",
        "not_found": "not_found",
        "unavailable": "unavailable",
        "failed": "critical",
        "retry_scheduled": "warning",
        "mystery": "ready",
    }.items():
        assert workbench._status(value) == expected
    assert workbench._run_status(logs=(), persisted_status=RuntimeRunStatus.RUNNING)
    assert (
        workbench._run_status(
            logs=(_event(status="failed", severity="critical"),),
            persisted_status=None,
        )
        == "critical"
    )
    assert (
        workbench._run_status(
            logs=(_event(status="retry_scheduled", severity="warning"),),
            persisted_status=None,
        )
        == "warning"
    )
    assert workbench._run_title(run_id=uuid4(), persisted_run=None, logs=())[:12]

    with pytest.raises(ValueError):
        workbench._range_window("24h")

    assert workbench._capacity_status(OperationsCapacitySummary(dead_letter_count=1))
    assert workbench._capacity_status(OperationsCapacitySummary(retry_backlog=1))
    assert workbench._capacity_status(OperationsCapacitySummary()) == "ready"
    assert (
        workbench._provider_panel_status(
            OperationsDashboardSnapshot(
                health_status="ready",
                status_cards=(),
                dependencies=(),
                capacity=OperationsCapacitySummary(),
                providers=(
                    OperationsProviderSummary(
                        provider_connection_id=uuid4(),
                        display_name="Provider",
                        provider_type="openai",
                        active=True,
                        health_state="failed",
                        model_count=1,
                        href="/admin/app/governance/providers",
                    ),
                ),
                redaction_notice="redacted",
            )
        )
        == "warning"
    )
    assert (
        workbench._provider_panel_status(
            OperationsDashboardSnapshot(
                health_status="ready",
                status_cards=(),
                dependencies=(),
                capacity=OperationsCapacitySummary(),
                usage=OperationsUsageSummary(usage_status="unavailable"),
                redaction_notice="redacted",
            )
        )
        == "unavailable"
    )


def test_workbench_text_helper_branches_cover_subsystems_and_labels() -> None:
    assert workbench._event_subsystem(_event(source="gateway_attempt")) == "gateway"
    assert (
        workbench._event_subsystem(_event(component="telegram_delivery")) == "telegram"
    )
    assert workbench._event_subsystem(_event(component="channel_delivery")) == "channel"
    assert workbench._event_subsystem(_event(component="tool_call")) == "tool"
    assert workbench._event_subsystem(_event(component="retry")) == "reliability"
    assert workbench._event_subsystem(_event(component="runtime")) == "runtime"
    assert workbench._event_subsystem(_event(component="audit")) == "audit"
    assert (
        workbench._recommended_step(_event(source="gateway_attempt"), is_platform=False)
        == "Open gateway diagnostics."
    )
    assert (
        workbench._recommended_step(_event(component="tool_call"), is_platform=True)
        == "Open skill tool diagnostics."
    )
    assert (
        workbench._recommended_step(_event(component="retry"), is_platform=True)
        == "Open reliability recovery details."
    )
    assert workbench._payload_summary({}, fallback="fallback") == (
        "Runtime event recorded: fallback."
    )
    assert workbench._string_details({"a": 1, "b": True, "c": {"hidden": True}}) == {
        "a": "1",
        "b": "True",
    }
    assert workbench._relative_label(datetime.now(UTC)) == "moments ago"
    assert "minutes ago" in workbench._relative_label(
        datetime.now(UTC) - timedelta(minutes=5)
    )
    assert "hours ago" in workbench._relative_label(
        datetime.now(UTC) - timedelta(hours=2)
    )
    assert workbench._relative_label(datetime.now(UTC) - timedelta(days=2)).count("-")
    with pytest.raises(RunDebugNotFoundError):
        workbench._parse_run_id("not-a-uuid")


class _ExportService:
    def __init__(self, mode: str) -> None:
        self.mode = mode

    async def export_logs(self, **kwargs):
        if self.mode == "denied":
            raise workbench.OperationsAuthorizationError("denied")
        if self.mode == "unavailable":
            raise RuntimeError("storage failed")
        raise AssertionError("validation should return before export")


def _event(
    *,
    event_id: str = "event-1",
    source: str = "audit_timeline",
    component: str = "runtime",
    status: str = "ready",
    severity: str = "info",
    run_id=None,
    links: tuple[OperationsLink, ...] = (
        OperationsLink(label="Run", href="/admin/app/operations"),
    ),
) -> OperationalLogEvent:
    return OperationalLogEvent(
        event_id=event_id,
        source=source,
        occurred_at=datetime.now(UTC) - timedelta(minutes=1),
        run_id=run_id,
        component=component,
        severity=severity,
        status=status,
        summary="Safe summary",
        links=links,
    )
