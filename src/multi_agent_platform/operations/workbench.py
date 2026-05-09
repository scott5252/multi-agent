from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from uuid import UUID

from multi_agent_platform.api.schemas.admin_patterns import (
    AdminAction,
    AdminActionMethod,
    EvidenceReferenceType,
    EvidenceSummary,
    FilterCriterion,
    FilterOption,
    FilterProfile,
    RefreshHint,
    SavedFilterSummary,
)
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminPageActionVariant,
    ReactAdminScope,
    ReactAdminScopeType,
)
from multi_agent_platform.api.schemas.admin_workbench import (
    ChannelDeliverySummary,
    GatewayAttemptSummary,
    GraphBranchSummary,
    HealthPressurePanel,
    LikelyCauseSummary,
    OperationsWorkbenchEnvelope,
    ReliabilityRecoveryItem,
    ReliabilityRecoverySummary,
    RunDebugEnvelope,
    TimelineEventSummary,
    ToolCallSummary,
    WorkbenchExportRequest,
    WorkbenchExportSnapshot,
    WorkbenchExportStatus,
    WorkbenchLink,
    WorkbenchLogSummary,
    WorkbenchMetric,
    WorkbenchSeverity,
    WorkbenchStatus,
    WorkbenchSummaryCard,
    WorkbenchTimeRange,
)
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.models.runtime_orchestration import (
    RunStepRecord,
    RuntimeTimelineEventRecord,
)
from multi_agent_platform.db.repositories.runtime_orchestration import (
    RuntimeOrchestrationRepository,
)
from multi_agent_platform.operations.models import (
    OperationalLogEvent,
    OperationsAccessScope,
    OperationsAuthorizationError,
    OperationsCapacitySummary,
    OperationsDashboardSnapshot,
    OperationsExportResult,
    OperationsLogFilters,
    OperationsRole,
)
from multi_agent_platform.operations.service import OperationsConsoleService
from multi_agent_platform.storage.base import StorageProvider

SUPPORTED_RANGE_PRESETS = frozenset({"60m"})
SUPPORTED_SEVERITIES = frozenset({"info", "warning", "critical"})
SUPPORTED_SUBSYSTEMS = frozenset(
    {"audit", "channel", "gateway", "reliability", "runtime", "telegram", "tool"}
)
TENANT_HIDDEN_CARDS = frozenset(
    {"Worker Capacity", "DB Pool Pressure", "Object Storage", "Model Providers"}
)
SAFE_REDACTION_SUMMARY = (
    "Secrets, prompts, completions, memory, provider details, channel messages, "
    "connector details, local paths, and unauthorized tenant details are redacted."
)


class RunDebugNotFoundError(LookupError):
    """Raised when a requested live run-debug projection is not visible."""


async def build_operations_workbench_envelope(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    service: OperationsConsoleService,
    range_preset: str = "60m",
    severity: str | None = None,
    subsystem: str | None = None,
    run_id: str | UUID | None = None,
) -> OperationsWorkbenchEnvelope:
    start, end = _range_window(range_preset)
    dashboard = await service.dashboard(
        access_scope=_access_scope(principal=principal),
        filters=_operations_filters(scope=scope, start=start, end=end),
    )
    visible_logs = _filter_visible_logs(
        dashboard.logs,
        severity=severity,
        subsystem=subsystem,
    )
    run_debug = None
    if run_id is not None:
        try:
            run_debug = await build_run_debug_envelope(
                scope=scope,
                principal=principal,
                service=service,
                workflow_run_id=run_id,
            )
        except RunDebugNotFoundError:
            run_debug = None
    if run_debug is None:
        run_debug = await _first_visible_run_debug(
            scope=scope,
            principal=principal,
            service=service,
            logs=visible_logs,
        )

    return OperationsWorkbenchEnvelope(
        page_id="react-operations-workbench",
        title="Operations workbench",
        description=(
            "Safe triage across health, reliability, runs, gateway attempts, "
            "tools, delivery, logs, and exports."
        ),
        scope=scope,
        generated_at_label=f"Generated from live evidence at {_clock_label(end)}",
        time_range=WorkbenchTimeRange(
            preset=range_preset,
            label="Last 60 minutes",
            start=start,
            end=end,
        ),
        summary_cards=_summary_cards(
            dashboard=dashboard, scope=scope, logs=visible_logs
        ),
        likely_causes=_likely_causes(
            dashboard=dashboard,
            logs=visible_logs,
            scope=scope,
        ),
        health_panels=_health_panels(
            dashboard=dashboard, scope=scope, logs=visible_logs
        ),
        run_debug=run_debug,
        reliability=_reliability(dashboard=dashboard, scope=scope),
        logs=tuple(_log_summary(event, scope=scope) for event in visible_logs[:50]),
        filters=_filters(scope=scope),
        actions=(
            AdminAction(
                action_id="workbench-export",
                label="Export workbench evidence",
                method=AdminActionMethod.POST,
                href=_with_tenant_query("/admin/app/operations/export", scope),
                variant=ReactAdminPageActionVariant.SECONDARY,
            ),
        ),
        exports=empty_workbench_export_snapshot(scope=scope),
        fallback_links=_fallback_links(is_platform=_is_platform(scope)),
        evidence=(
            EvidenceSummary(
                evidence_id="operations-live-source",
                label="Live operations source",
                summary=(
                    "Workbench data is derived from live operations, audit, "
                    "runtime, reliability, provider, usage, and storage evidence."
                ),
                reference_type=EvidenceReferenceType.VALIDATION,
            ),
        ),
        refresh=RefreshHint(mode="manual", interval_seconds=30),
    )


async def build_run_debug_envelope(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    service: OperationsConsoleService,
    workflow_run_id: str | UUID,
) -> RunDebugEnvelope:
    run_id = _parse_run_id(workflow_run_id)
    tenant_id = (
        scope.tenant_id if scope.scope_type == ReactAdminScopeType.TENANT else None
    )
    repository = RuntimeOrchestrationRepository(service.session)
    persisted_run = await repository.get_run_by_id(workflow_run_id=run_id)
    if (
        scope.scope_type == ReactAdminScopeType.TENANT
        and persisted_run is not None
        and persisted_run.tenant_id != tenant_id
    ):
        raise RunDebugNotFoundError("run debug not found")

    logs = await service.query_logs(
        access_scope=_access_scope(principal=principal),
        filters=OperationsLogFilters(tenant_id=tenant_id, run_id=run_id, limit=100),
    )
    if persisted_run is None and not logs:
        raise RunDebugNotFoundError("run debug not found")

    runtime_events: Sequence[RuntimeTimelineEventRecord] = ()
    run_steps: Sequence[RunStepRecord] = ()
    bundle_summary = "No pinned execution bundle evidence was found for this run."
    if persisted_run is not None:
        runtime_events = await repository.list_timeline(
            workflow_run_id=run_id,
            tenant_id=persisted_run.tenant_id,
            limit=100,
        )
        run_steps = await repository.list_run_steps(
            workflow_run_id=run_id,
            tenant_id=persisted_run.tenant_id,
        )
        bundle = await repository.get_execution_bundle(
            run_bundle_id=persisted_run.run_bundle_id
        )
        if bundle is not None:
            bundle_summary = (
                "Pinned workflow, contract, prompt, model, and tool-policy "
                f"versions are recorded with digest {bundle.bundle_digest[:12]}."
            )

    timeline = _run_timeline(
        run_id=run_id,
        persisted_run=persisted_run,
        runtime_events=runtime_events,
        logs=logs,
        scope=scope,
    )
    return RunDebugEnvelope(
        workflow_run_id=str(run_id),
        tenant_scope=scope if scope.scope_type == ReactAdminScopeType.TENANT else None,
        run_status=_run_status(
            logs=logs, persisted_status=getattr(persisted_run, "status", None)
        ),
        safe_title=_run_title(run_id=run_id, persisted_run=persisted_run, logs=logs),
        timeline=timeline,
        branches=_branches_from_steps(run_steps=run_steps, logs=logs),
        gateway_attempts=tuple(
            _gateway_attempt(event)
            if _is_platform(scope)
            else _tenant_gateway_attempt(event)
            for event in logs
            if event.source == "gateway_attempt"
        ),
        tool_calls=tuple(
            _tool_call(event) for event in logs if _event_subsystem(event) == "tool"
        ),
        deliveries=tuple(
            _delivery(event)
            for event in logs
            if _event_subsystem(event) in {"telegram", "channel"}
        ),
        lineage=(
            WorkbenchLink(
                label="Run lineage",
                href=_with_tenant_query(
                    f"/admin/app/operations?run_id={run_id}&panel=lineage",
                    scope,
                ),
            ),
        ),
        replay_links=(
            WorkbenchLink(
                label="Open safe replay evidence",
                href=_with_tenant_query(
                    f"/admin/app/operations?run_id={run_id}&panel=replay",
                    scope,
                ),
            ),
        ),
        bundle_summary=bundle_summary,
        fallback_links=(
            WorkbenchLink(label="Operations workbench", href="/admin/app/operations"),
            WorkbenchLink(
                label="Run debug JSON",
                href=_with_tenant_query(
                    f"/admin/app/operations/runs/{run_id}.json",
                    scope,
                ),
            ),
        ),
    )


async def create_workbench_export_snapshot(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    service: OperationsConsoleService,
    storage_provider: StorageProvider,
    request: WorkbenchExportRequest | None = None,
) -> WorkbenchExportSnapshot:
    payload = request or WorkbenchExportRequest()
    if payload.range not in SUPPORTED_RANGE_PRESETS:
        return WorkbenchExportSnapshot(
            export_id="operations-export:validation",
            status=WorkbenchExportStatus.VALIDATION,
            summary=(
                "Workbench export was not created because the requested range "
                "is unsupported."
            ),
            artifact_reference_id=None,
            progress_label="Validation required",
            audit_reference_id=None,
            scope_label=scope.label,
            redaction_summary=SAFE_REDACTION_SUMMARY,
            row_count=0,
        )
    start, end = _range_window(payload.range)
    try:
        result = await service.export_logs(
            access_scope=_access_scope(principal=principal),
            filters=_operations_filters(scope=scope, start=start, end=end),
            storage_provider=storage_provider,
        )
    except OperationsAuthorizationError:
        return WorkbenchExportSnapshot(
            export_id="operations-export:denied",
            status=WorkbenchExportStatus.DENIED,
            summary="Workbench export was denied for the active principal and scope.",
            artifact_reference_id=None,
            progress_label="Denied",
            audit_reference_id=None,
            scope_label=scope.label,
            redaction_summary=SAFE_REDACTION_SUMMARY,
            row_count=0,
        )
    except Exception:
        return WorkbenchExportSnapshot(
            export_id="operations-export:unavailable",
            status=WorkbenchExportStatus.UNAVAILABLE,
            summary=(
                "Workbench export storage is unavailable; no fake artifact "
                "was returned."
            ),
            artifact_reference_id=None,
            progress_label="Unavailable",
            audit_reference_id=None,
            scope_label=scope.label,
            redaction_summary=SAFE_REDACTION_SUMMARY,
            row_count=0,
        )
    return _export_result_snapshot(scope=scope, result=result)


def empty_workbench_export_snapshot(
    *, scope: ReactAdminScope
) -> WorkbenchExportSnapshot:
    return WorkbenchExportSnapshot(
        export_id="operations-export:empty",
        status=WorkbenchExportStatus.EMPTY,
        summary="No workbench export has been requested for this live scope.",
        artifact_reference_id=None,
        progress_label="No export requested",
        audit_reference_id=None,
        scope_label=scope.label,
        redaction_summary=SAFE_REDACTION_SUMMARY,
        row_count=0,
    )


def _export_result_snapshot(
    *,
    scope: ReactAdminScope,
    result: OperationsExportResult,
) -> WorkbenchExportSnapshot:
    return WorkbenchExportSnapshot(
        export_id=f"operations-export:{result.export_id}",
        status=WorkbenchExportStatus.COMPLETE,
        summary="Workbench export persisted with safe artifact metadata.",
        artifact_reference_id=f"operations-export:{result.export_id}",
        progress_label="Complete",
        audit_reference_id=str(result.audit_event_id)
        if result.audit_event_id
        else None,
        scope_label=scope.label,
        redaction_summary=SAFE_REDACTION_SUMMARY,
        row_count=result.row_count,
    )


def _range_window(range_preset: str) -> tuple[datetime, datetime]:
    if range_preset not in SUPPORTED_RANGE_PRESETS:
        raise ValueError("unsupported workbench range")
    end = datetime.now(UTC)
    return end - timedelta(minutes=60), end


def _operations_filters(
    *,
    scope: ReactAdminScope,
    start: datetime,
    end: datetime,
) -> OperationsLogFilters:
    return OperationsLogFilters(
        tenant_id=scope.tenant_id
        if scope.scope_type == ReactAdminScopeType.TENANT
        else None,
        start=start,
        end=end,
        limit=100,
    )


def _access_scope(*, principal: PrincipalContext) -> OperationsAccessScope:
    roles = set(principal.role_codes)
    role = (
        OperationsRole.PLATFORM_ADMIN
        if "platform_admin" in roles
        else OperationsRole.AUDITOR
    )
    can_export = bool({"platform_admin", "tenant_admin"} & roles) or (
        "operations:export" in set(principal.permission_codes)
    )
    return OperationsAccessScope(
        principal_id=principal.principal_id,
        role=role,
        can_export=can_export,
        trace_id=principal.trace_id,
    )


def _summary_cards(
    *,
    dashboard: OperationsDashboardSnapshot,
    scope: ReactAdminScope,
    logs: tuple[OperationalLogEvent, ...],
) -> tuple[WorkbenchSummaryCard, ...]:
    cards: list[WorkbenchSummaryCard] = []
    if not _is_platform(scope):
        run_count = len({event.run_id for event in logs if event.run_id is not None})
        cards.append(
            WorkbenchSummaryCard(
                card_id="tenant-live-evidence",
                label="Tenant live evidence",
                value=str(len(logs)),
                status=WorkbenchStatus.READY if logs else WorkbenchStatus.EMPTY,
                severity=WorkbenchSeverity.INFO,
                summary=(
                    f"{scope.label} has {len(logs)} live operational rows and "
                    f"{run_count} visible runs in the selected range."
                ),
                freshness_label="Last 60 minutes",
                href=_with_tenant_query("/admin/app/operations?panel=logs", scope),
                evidence_reference_id="live:tenant-operations",
            )
        )
    for card in dashboard.status_cards:
        if not _is_platform(scope) and card.label in TENANT_HIDDEN_CARDS:
            continue
        cards.append(
            WorkbenchSummaryCard(
                card_id=_slug(card.label),
                label=card.label,
                value=card.value,
                status=_status(card.status),
                severity=_severity_from_status(card.status),
                summary=card.summary,
                freshness_label="Live source",
                href=_with_tenant_query(card.href, scope) if card.href else None,
                evidence_reference_id=f"live:{_slug(card.label)}",
            )
        )
    if cards:
        return tuple(cards)
    return (
        WorkbenchSummaryCard(
            card_id="empty-live-evidence",
            label="Live evidence",
            value="0",
            status=WorkbenchStatus.EMPTY,
            severity=WorkbenchSeverity.INFO,
            summary="No operational evidence matched the authorized scope and range.",
            freshness_label="Last 60 minutes",
            evidence_reference_id=None,
        ),
    )


def _health_panels(
    *,
    dashboard: OperationsDashboardSnapshot,
    scope: ReactAdminScope,
    logs: tuple[OperationalLogEvent, ...],
) -> tuple[HealthPressurePanel, ...]:
    if not _is_platform(scope):
        run_count = len({event.run_id for event in logs if event.run_id is not None})
        return (
            HealthPressurePanel(
                panel_id="tenant-activity",
                title="Tenant activity",
                status=WorkbenchStatus.READY if logs else WorkbenchStatus.EMPTY,
                metrics=(
                    WorkbenchMetric(
                        label="Visible operational rows", value=str(len(logs))
                    ),
                    WorkbenchMetric(label="Visible runs", value=str(run_count)),
                    WorkbenchMetric(
                        label="Usage events",
                        value=str(dashboard.usage.total_events),
                        status=_status(dashboard.usage.usage_status),
                    ),
                ),
                dependencies=(),
                freshness_label=f"{scope.label} scope only",
                polling_allowed=True,
                partial_reason=(
                    "Platform-only database, provider, worker, queue, and storage "
                    "pressure details are hidden for tenant scope."
                ),
                links=(
                    WorkbenchLink(
                        label="Tenant logs",
                        href=_with_tenant_query(
                            "/admin/app/operations?panel=logs", scope
                        ),
                    ),
                ),
            ),
        )

    capacity = dashboard.capacity
    dependency_metrics = tuple(
        WorkbenchMetric(
            label=item.name,
            value=item.status,
            status=_status(item.status),
            summary=item.detail or None,
        )
        for item in dashboard.dependencies[:8]
    )
    provider_metrics = tuple(
        WorkbenchMetric(
            label=item.display_name,
            value=item.health_state,
            status=_status(item.health_state),
            summary=f"{item.model_count} models",
        )
        for item in dashboard.providers[:8]
    )
    return (
        HealthPressurePanel(
            panel_id="capacity",
            title="Capacity and dependencies",
            status=_capacity_status(capacity),
            metrics=(
                WorkbenchMetric(
                    label="Runnable queue",
                    value=str(capacity.runnable_depth),
                    status=WorkbenchStatus.WARNING
                    if capacity.runnable_depth
                    else WorkbenchStatus.READY,
                ),
                WorkbenchMetric(
                    label="Delayed queue", value=str(capacity.delayed_depth)
                ),
                WorkbenchMetric(
                    label="Active leases", value=str(capacity.active_leases)
                ),
                WorkbenchMetric(
                    label="Database pool wait p95",
                    value=f"{capacity.db_pool_wait_p95_ms} ms",
                    status=WorkbenchStatus.WARNING
                    if capacity.db_pool_wait_p95_ms
                    else WorkbenchStatus.READY,
                ),
                WorkbenchMetric(
                    label="Artifact operations",
                    value=str(capacity.artifact_inflight),
                ),
            ),
            dependencies=dependency_metrics,
            freshness_label="Live dependency and reliability state",
            polling_allowed=True,
            links=(
                WorkbenchLink(
                    label="Operations workbench",
                    href="/admin/app/operations",
                ),
            ),
        ),
        HealthPressurePanel(
            panel_id="providers",
            title="Provider, usage, and channel signals",
            status=_provider_panel_status(dashboard),
            metrics=(
                WorkbenchMetric(
                    label="Usage events",
                    value=str(dashboard.usage.total_events),
                    status=_status(dashboard.usage.usage_status),
                ),
                WorkbenchMetric(
                    label="Token throughput",
                    value=str(dashboard.usage.token_throughput),
                    status=_status(dashboard.usage.usage_status),
                ),
                WorkbenchMetric(
                    label="Model latency p95",
                    value=f"{dashboard.usage.model_latency_ms} ms",
                ),
            ),
            dependencies=provider_metrics,
            freshness_label="Last 60 minutes",
            polling_allowed=True,
            links=(
                WorkbenchLink(
                    label="Model providers",
                    href="/admin/app/governance/providers",
                ),
                WorkbenchLink(label="Usage analytics", href="/admin/app/usage"),
            ),
        ),
    )


def _likely_causes(
    *,
    dashboard: OperationsDashboardSnapshot,
    logs: tuple[OperationalLogEvent, ...],
    scope: ReactAdminScope,
) -> tuple[LikelyCauseSummary, ...]:
    is_platform = _is_platform(scope)
    causes: list[LikelyCauseSummary] = []
    if is_platform and dashboard.capacity.open_breaker_count:
        causes.append(
            LikelyCauseSummary(
                cause_id="live-open-breakers",
                severity=WorkbenchSeverity.WARNING,
                affected_subsystem="Reliability",
                symptom=(
                    f"{dashboard.capacity.open_breaker_count} breaker records are open."
                ),
                likely_cause_category="live_reliability_pressure",
                recommended_next_step="Open reliability recovery details.",
                href="/admin/app/operations?panel=reliability",
                evidence_reference_id="live:reliability",
            )
        )
    for event in logs:
        severity = _event_severity(event)
        if severity is WorkbenchSeverity.INFO and _status(event.status) in {
            WorkbenchStatus.READY,
            WorkbenchStatus.AVAILABLE,
        }:
            continue
        causes.append(
            LikelyCauseSummary(
                cause_id=f"cause-{_slug(event.event_id)}",
                severity=severity,
                affected_subsystem=_event_subsystem(event).title(),
                symptom=event.summary,
                likely_cause_category=_safe_category(event),
                recommended_next_step=_recommended_step(
                    event,
                    is_platform=is_platform,
                ),
                href=_first_link(event, scope=scope),
                evidence_reference_id=event.event_id,
            )
        )
        if len(causes) >= 3:
            break
    if causes:
        return tuple(causes)
    return (
        LikelyCauseSummary(
            cause_id="no-live-warning-symptoms",
            severity=WorkbenchSeverity.INFO,
            affected_subsystem="Live operations",
            symptom="No warning or critical symptoms matched the selected scope.",
            likely_cause_category="empty_live_evidence",
            recommended_next_step="Refresh or broaden the authorized filter.",
            href="/admin/app/operations",
            evidence_reference_id=None,
        ),
    )


def _reliability(
    *,
    dashboard: OperationsDashboardSnapshot,
    scope: ReactAdminScope,
) -> ReliabilityRecoverySummary:
    if not _is_platform(scope):
        return ReliabilityRecoverySummary(
            confirmations=(
                ReliabilityRecoveryItem(
                    item_id="tenant-recovery-empty",
                    label="Tenant recovery records",
                    status=WorkbenchStatus.EMPTY,
                    severity=WorkbenchSeverity.INFO,
                    summary=(
                        "No tenant-visible reliability recovery records matched "
                        "the selected range."
                    ),
                    href=_with_tenant_query(
                        "/admin/app/operations?panel=reliability",
                        scope,
                    ),
                ),
            ),
            partial_reason=(
                "Platform-only queue, breaker, and storage pressure is hidden "
                "for tenant scope."
            ),
        )
    capacity = dashboard.capacity
    return ReliabilityRecoverySummary(
        breakers=(
            ReliabilityRecoveryItem(
                item_id="live-breakers",
                label="Open breakers",
                status=WorkbenchStatus.WARNING
                if capacity.open_breaker_count
                else WorkbenchStatus.READY,
                severity=WorkbenchSeverity.WARNING
                if capacity.open_breaker_count
                else WorkbenchSeverity.INFO,
                summary=f"{capacity.open_breaker_count} open breaker records.",
                href="/admin/app/operations?panel=breakers",
            ),
        ),
        retries=(
            ReliabilityRecoveryItem(
                item_id="live-retries",
                label="Retry backlog",
                status=WorkbenchStatus.WARNING
                if capacity.retry_backlog
                else WorkbenchStatus.EMPTY,
                severity=WorkbenchSeverity.WARNING
                if capacity.retry_backlog
                else WorkbenchSeverity.INFO,
                summary=f"{capacity.retry_backlog} retry records are pending.",
                href="/admin/app/operations?panel=reliability",
            ),
        ),
        dead_letters=(
            ReliabilityRecoveryItem(
                item_id="live-dead-letters",
                label="Dead letters",
                status=WorkbenchStatus.CRITICAL
                if capacity.dead_letter_count
                else WorkbenchStatus.EMPTY,
                severity=WorkbenchSeverity.CRITICAL
                if capacity.dead_letter_count
                else WorkbenchSeverity.INFO,
                summary=(
                    f"{capacity.dead_letter_count} dead-letter records match "
                    "the live state."
                ),
                href="/admin/app/operations?panel=dead-letters",
            ),
        ),
        confirmations=(
            ReliabilityRecoveryItem(
                item_id="live-compensation",
                label="Compensation backlog",
                status=WorkbenchStatus.WARNING
                if capacity.compensation_backlog
                else WorkbenchStatus.EMPTY,
                severity=WorkbenchSeverity.WARNING
                if capacity.compensation_backlog
                else WorkbenchSeverity.INFO,
                summary=(
                    f"{capacity.compensation_backlog} compensation records are pending."
                ),
                href="/admin/app/operations?panel=compensation",
            ),
        ),
    )


def _log_summary(
    event: OperationalLogEvent,
    *,
    scope: ReactAdminScope,
) -> WorkbenchLogSummary:
    return WorkbenchLogSummary(
        log_id=event.event_id,
        occurred_at_label=_relative_label(event.occurred_at),
        source=event.source,
        severity=_event_severity(event),
        status=_status(event.status),
        subsystem=_event_subsystem(event),
        tenant_scope="tenant" if event.tenant_id is not None else None,
        run_reference=str(event.run_id) if event.run_id else None,
        correlation_reference=event.trace_id,
        summary=event.summary,
        safe_details=_scoped_details(event.details, scope=scope),
        links=_scoped_links(event.links, scope=scope),
    )


async def _first_visible_run_debug(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    service: OperationsConsoleService,
    logs: tuple[OperationalLogEvent, ...],
) -> RunDebugEnvelope | None:
    for event in logs:
        if event.run_id is None:
            continue
        try:
            return await build_run_debug_envelope(
                scope=scope,
                principal=principal,
                service=service,
                workflow_run_id=event.run_id,
            )
        except RunDebugNotFoundError:
            continue
    return None


def _run_timeline(
    *,
    run_id: UUID,
    persisted_run: object | None,
    runtime_events: Sequence[RuntimeTimelineEventRecord],
    logs: tuple[OperationalLogEvent, ...],
    scope: ReactAdminScope,
) -> tuple[TimelineEventSummary, ...]:
    timeline: list[TimelineEventSummary] = []
    if persisted_run is not None:
        status_value = getattr(
            getattr(persisted_run, "status", None), "value", "recorded"
        )
        updated_at = getattr(persisted_run, "updated_at", None)
        created_at = getattr(persisted_run, "created_at", None)
        timeline.append(
            TimelineEventSummary(
                event_id=f"runtime-run-{run_id}",
                occurred_at_label=_relative_label(
                    updated_at or created_at or datetime.now(UTC)
                ),
                sequence=0,
                category="runtime_run",
                severity=_severity_from_status(status_value),
                status=_status(status_value),
                summary=f"Runtime run is {status_value}.",
                details={"source": "runtime_workflow_runs"},
                trace_id=getattr(persisted_run, "trace_id", None),
                audit_reference_id=None,
            )
        )
    for index, event in enumerate(
        sorted(runtime_events, key=lambda item: item.created_at), 1
    ):
        timeline.append(
            TimelineEventSummary(
                event_id=f"runtime-timeline-{event.runtime_timeline_event_id}",
                occurred_at_label=_relative_label(event.created_at),
                sequence=index,
                category=event.event_type,
                severity=_severity_from_status(event.severity),
                status=_status(event.severity),
                summary=_payload_summary(event.payload, fallback=event.event_type),
                details=_string_details(event.payload),
                trace_id=event.trace_id,
                audit_reference_id=None,
            )
        )
    offset = len(timeline)
    for index, log_event in enumerate(
        sorted(logs, key=lambda item: item.occurred_at), 1
    ):
        timeline.append(
            TimelineEventSummary(
                event_id=f"run-log-{_slug(log_event.event_id)}",
                occurred_at_label=_relative_label(log_event.occurred_at),
                sequence=offset + index,
                category=log_event.component,
                severity=_event_severity(log_event),
                status=_status(log_event.status),
                summary=log_event.summary,
                details=_scoped_details(log_event.details, scope=scope),
                trace_id=log_event.trace_id,
                audit_reference_id=log_event.event_id,
                links=_scoped_links(log_event.links, scope=scope),
            )
        )
    return tuple(timeline)


def _branches_from_steps(
    *,
    run_steps: Sequence[RunStepRecord],
    logs: tuple[OperationalLogEvent, ...],
) -> tuple[GraphBranchSummary, ...]:
    if run_steps:
        return tuple(
            GraphBranchSummary(
                branch_id=f"step-{step.step_key}",
                label=step.step_key.replace("_", " ").title(),
                status=_status(getattr(step.status, "value", str(step.status))),
                node_count=1,
                completed_count=1
                if getattr(step.status, "value", str(step.status)) == "succeeded"
                else 0,
                failed_count=1
                if getattr(step.status, "value", str(step.status)) == "failed"
                else 0,
                waiting_count=1
                if getattr(step.status, "value", str(step.status))
                in {"pending", "runnable", "retry_scheduled", "waiting_child"}
                else 0,
                join_policy=None,
                join_decision=None,
                manual_resolution_required=getattr(
                    step.status, "value", str(step.status)
                )
                == "paused",
                summary=(
                    "Live step status is "
                    f"{getattr(step.status, 'value', str(step.status))}."
                ),
            )
            for step in run_steps[:12]
        )
    counts = Counter(_event_subsystem(event) for event in logs)
    return tuple(
        GraphBranchSummary(
            branch_id=f"evidence-{subsystem}",
            label=f"{subsystem.title()} evidence",
            status=WorkbenchStatus.READY,
            node_count=count,
            completed_count=count,
            summary=f"{count} live evidence rows are associated with this subsystem.",
        )
        for subsystem, count in counts.items()
    )


def _gateway_attempt(event: OperationalLogEvent) -> GatewayAttemptSummary:
    return GatewayAttemptSummary(
        attempt_id=event.event_id,
        provider_label=event.details.get(
            "provider", event.dependency or "Model provider"
        ),
        model_label=event.details.get("model", "Recorded model"),
        status=_status(event.status),
        latency_ms=event.latency_ms,
        retry_category=event.details.get("retry_category") or _safe_category(event),
        breaker_category=event.details.get("breaker_category"),
        credential_diagnostic_category=event.details.get(
            "credential", "safe_reference"
        ),
        usage_reference_id=event.details.get("usage_reference_id"),
        safe_summary=event.summary,
        evidence_reference_id=event.event_id,
    )


def _tenant_gateway_attempt(event: OperationalLogEvent) -> GatewayAttemptSummary:
    return GatewayAttemptSummary(
        attempt_id=event.event_id,
        provider_label="Model provider",
        model_label="Recorded model",
        status=_status(event.status),
        latency_ms=event.latency_ms,
        retry_category=event.details.get("retry_category") or _safe_category(event),
        breaker_category=None,
        credential_diagnostic_category="safe_reference",
        usage_reference_id=event.details.get("usage_reference_id"),
        safe_summary=event.summary,
        evidence_reference_id=event.event_id,
    )


def _tool_call(event: OperationalLogEvent) -> ToolCallSummary:
    return ToolCallSummary(
        tool_call_id=event.event_id,
        tool_label=event.dependency or event.details.get("tool", "Tool execution"),
        connector_label=event.details.get("connector", "First-party connector"),
        readiness_status=_status(event.status),
        policy_outcome=event.details.get("policy_outcome", event.severity),
        side_effect_classification=event.details.get("side_effect", "read_only"),
        result_category=event.details.get("result_category", event.status),
        safe_summary=event.summary,
        evidence_reference_id=event.event_id,
    )


def _delivery(event: OperationalLogEvent) -> ChannelDeliverySummary:
    return ChannelDeliverySummary(
        delivery_id=event.event_id,
        channel="telegram" if _event_subsystem(event) == "telegram" else "channel",
        alias_label=event.details.get("alias", "Delivery attempt"),
        identity_status=WorkbenchStatus.READY,
        receipt_status=_status(event.status),
        notification_status=_status(event.status),
        delivery_status=_status(event.status),
        failure_category=None
        if _status(event.status) is WorkbenchStatus.READY
        else _safe_category(event),
        safe_summary=event.summary,
        evidence_reference_id=event.event_id,
    )


def _scoped_links(
    links: tuple[object, ...],
    *,
    scope: ReactAdminScope,
) -> tuple[WorkbenchLink, ...]:
    scoped: list[WorkbenchLink] = []
    for link in links:
        href = getattr(link, "href", "")
        label = getattr(link, "label", "Details")
        if scope.scope_type == ReactAdminScopeType.TENANT and (
            "governance/providers" in href or "model" in label.lower()
        ):
            continue
        scoped.append(WorkbenchLink(label=label, href=href))
    return tuple(scoped)


def _scoped_details(
    details: dict[str, str],
    *,
    scope: ReactAdminScope,
) -> dict[str, str]:
    if _is_platform(scope):
        return details
    hidden_fragments = ("provider", "model", "credential", "breaker")
    return {
        key: value
        for key, value in details.items()
        if not any(fragment in key.lower() for fragment in hidden_fragments)
    }


def _filter_visible_logs(
    logs: tuple[OperationalLogEvent, ...],
    *,
    severity: str | None,
    subsystem: str | None,
) -> tuple[OperationalLogEvent, ...]:
    visible = logs
    if severity:
        visible = tuple(
            event for event in visible if _event_severity(event).value == severity
        )
    if subsystem:
        visible = tuple(
            event for event in visible if _event_subsystem(event) == subsystem
        )
    return visible


def _run_status(
    *,
    logs: tuple[OperationalLogEvent, ...],
    persisted_status: object | None,
) -> WorkbenchStatus:
    if persisted_status is not None:
        return _status(getattr(persisted_status, "value", str(persisted_status)))
    if any(_event_severity(event) is WorkbenchSeverity.CRITICAL for event in logs):
        return WorkbenchStatus.CRITICAL
    if any(_event_severity(event) is WorkbenchSeverity.WARNING for event in logs):
        return WorkbenchStatus.WARNING
    return WorkbenchStatus.READY


def _run_title(
    *,
    run_id: UUID,
    persisted_run: object | None,
    logs: tuple[OperationalLogEvent, ...],
) -> str:
    if persisted_run is not None:
        status_value = getattr(
            getattr(persisted_run, "status", None), "value", "recorded"
        )
        return f"Workflow run {str(run_id)[:8]} ({status_value})"
    if logs:
        return f"Workflow run {str(run_id)[:8]} from live audit evidence"
    return f"Workflow run {str(run_id)[:8]}"


def _status(value: str | None) -> WorkbenchStatus:
    normalized = (value or "").lower()
    if normalized in {"ready", "healthy", "succeeded", "success", "closed", "allowed"}:
        return WorkbenchStatus.READY
    if normalized in {"available", "complete", "completed", "recorded"}:
        return WorkbenchStatus.AVAILABLE
    if normalized in {"empty", "none"}:
        return WorkbenchStatus.EMPTY
    if normalized in {"queued", "pending", "runnable", "running", "leased"}:
        return WorkbenchStatus.QUEUED
    if normalized in {"denied", "forbidden", "unauthorized"}:
        return WorkbenchStatus.DENIED
    if normalized in {"validation", "validation_error", "invalid"}:
        return WorkbenchStatus.VALIDATION
    if normalized in {"conflict", "stale_conflict"}:
        return WorkbenchStatus.CONFLICT
    if normalized in {"not_found", "missing"}:
        return WorkbenchStatus.NOT_FOUND
    if normalized in {"unavailable", "not_ready"}:
        return WorkbenchStatus.UNAVAILABLE
    if normalized in {"critical", "failed", "failure"}:
        return WorkbenchStatus.CRITICAL
    if normalized in {"degraded", "warning", "retry_scheduled", "recoverable_failed"}:
        return WorkbenchStatus.WARNING
    return WorkbenchStatus.READY


def _event_severity(event: OperationalLogEvent) -> WorkbenchSeverity:
    combined = f"{event.severity} {event.status}".lower()
    if any(
        token in combined for token in ("critical", "failed", "failure", "unavailable")
    ):
        return WorkbenchSeverity.CRITICAL
    if any(
        token in combined
        for token in ("warning", "retry", "timeout", "degraded", "runtime_required")
    ):
        return WorkbenchSeverity.WARNING
    return WorkbenchSeverity.INFO


def _severity_from_status(value: str | None) -> WorkbenchSeverity:
    status = _status(value)
    if status in {
        WorkbenchStatus.CRITICAL,
        WorkbenchStatus.DENIED,
        WorkbenchStatus.UNAVAILABLE,
    }:
        return WorkbenchSeverity.CRITICAL
    if status in {
        WorkbenchStatus.WARNING,
        WorkbenchStatus.DEGRADED,
        WorkbenchStatus.QUEUED,
    }:
        return WorkbenchSeverity.WARNING
    return WorkbenchSeverity.INFO


def _capacity_status(capacity: OperationsCapacitySummary) -> WorkbenchStatus:
    if capacity.dead_letter_count or capacity.open_breaker_count:
        return WorkbenchStatus.WARNING
    if capacity.retry_backlog or capacity.runnable_depth or capacity.delayed_depth:
        return WorkbenchStatus.WARNING
    return WorkbenchStatus.READY


def _provider_panel_status(dashboard: OperationsDashboardSnapshot) -> WorkbenchStatus:
    if any(
        _status(item.health_state) is WorkbenchStatus.CRITICAL
        for item in dashboard.providers
    ):
        return WorkbenchStatus.WARNING
    if dashboard.usage.usage_status == "unavailable":
        return WorkbenchStatus.UNAVAILABLE
    return WorkbenchStatus.READY


def _event_subsystem(event: OperationalLogEvent) -> str:
    haystack = f"{event.source} {event.component} {event.dependency or ''}".lower()
    if "gateway" in haystack or "model_provider" in haystack:
        return "gateway"
    if "telegram" in haystack:
        return "telegram"
    if "delivery" in haystack or "channel" in haystack:
        return "channel"
    if "tool" in haystack or "connector" in haystack:
        return "tool"
    if "reliability" in haystack or "retry" in haystack or "breaker" in haystack:
        return "reliability"
    if "runtime" in haystack or "run" in haystack:
        return "runtime"
    return "audit"


def _safe_category(event: OperationalLogEvent) -> str:
    if event.details.get("category"):
        return event.details["category"]
    return _slug(f"{_event_subsystem(event)} {event.status or event.severity}")


def _recommended_step(event: OperationalLogEvent, *, is_platform: bool) -> str:
    subsystem = _event_subsystem(event)
    if subsystem == "gateway":
        if not is_platform:
            return "Open gateway diagnostics."
        return "Open provider health and gateway diagnostics."
    if subsystem in {"telegram", "channel"}:
        return "Open channel delivery diagnostics."
    if subsystem == "tool":
        return "Open skill tool diagnostics."
    if subsystem == "reliability":
        return "Open reliability recovery details."
    return "Open the run debug timeline."


def _first_link(event: OperationalLogEvent, *, scope: ReactAdminScope) -> str | None:
    links = _scoped_links(event.links, scope=scope)
    return links[0].href if links else None


def _payload_summary(payload: dict[str, object], *, fallback: str) -> str:
    value = (
        payload.get("summary") or payload.get("safe_summary") or payload.get("message")
    )
    return str(value)[:160] if value else f"Runtime event recorded: {fallback}."


def _string_details(payload: dict[str, object]) -> dict[str, str]:
    details: dict[str, str] = {}
    for key, value in payload.items():
        if isinstance(value, (str, int, float, bool)) and len(details) < 8:
            details[str(key)] = str(value)
    return details


def _relative_label(value: datetime) -> str:
    aware = value if value.tzinfo is not None else value.replace(tzinfo=UTC)
    seconds = int((datetime.now(UTC) - aware).total_seconds())
    if seconds < 60:
        return "moments ago"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} minutes ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} hours ago"
    return aware.date().isoformat()


def _clock_label(value: datetime) -> str:
    return value.astimezone(UTC).strftime("%H:%M UTC")


def _filters(*, scope: ReactAdminScope) -> FilterProfile:
    base_href = _with_tenant_query("/admin/app/operations", scope)
    return FilterProfile(
        profile_id="operations-workbench-filters",
        criteria=(
            FilterCriterion(
                key="range",
                label="Time range",
                options=(FilterOption(value="60m", label="Last 60 minutes"),),
            ),
            FilterCriterion(
                key="severity",
                label="Severity",
                options=tuple(
                    FilterOption(value=value, label=value.title())
                    for value in sorted(SUPPORTED_SEVERITIES)
                ),
            ),
            FilterCriterion(
                key="subsystem",
                label="Subsystem",
                options=tuple(
                    FilterOption(value=value, label=value.title())
                    for value in sorted(SUPPORTED_SUBSYSTEMS)
                ),
            ),
        ),
        saved_filters=(
            SavedFilterSummary(
                filter_id="operations-last-hour",
                label="Last hour pressure",
                href=f"{base_href}{'&' if '?' in base_href else '?'}range=60m",
            ),
        ),
    )


def _fallback_links(*, is_platform: bool) -> tuple[WorkbenchLink, ...]:
    links = [
        WorkbenchLink(label="Operations workbench", href="/admin/app/operations"),
        WorkbenchLink(label="Run inspection", href="/admin/app/operations?panel=runs"),
        WorkbenchLink(
            label="Reliability controls",
            href="/admin/app/operations?panel=reliability",
        ),
        WorkbenchLink(
            label="Skill tool diagnostics",
            href="/admin/app/skills/diagnostics",
        ),
    ]
    if is_platform:
        links.extend(
            [
                WorkbenchLink(
                    label="Model providers",
                    href="/admin/app/governance/providers",
                ),
                WorkbenchLink(label="Usage analytics", href="/admin/app/usage"),
            ]
        )
    return tuple(links)


def _with_tenant_query(path: str, scope: ReactAdminScope) -> str:
    if scope.scope_type != ReactAdminScopeType.TENANT or scope.tenant_id is None:
        return path
    separator = "&" if "?" in path else "?"
    return f"{path}{separator}tenant_id={scope.tenant_id}"


def _is_platform(scope: ReactAdminScope) -> bool:
    return scope.scope_type == ReactAdminScopeType.PLATFORM


def _parse_run_id(value: str | UUID) -> UUID:
    try:
        return value if isinstance(value, UUID) else UUID(str(value))
    except ValueError as exc:
        raise RunDebugNotFoundError("run debug not found") from exc


def _slug(value: str) -> str:
    chars = [char.lower() if char.isalnum() else "-" for char in value]
    collapsed = "-".join(part for part in "".join(chars).split("-") if part)
    return collapsed[:96] or "live"
