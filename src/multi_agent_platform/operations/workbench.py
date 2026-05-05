from __future__ import annotations

from uuid import UUID

from multi_agent_platform.api.schemas.admin_patterns import (
    AdminAction,
    AdminActionMethod,
    AdminExportStatus,
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
    WorkbenchLink,
    WorkbenchLogSummary,
    WorkbenchMetric,
    WorkbenchSeverity,
    WorkbenchStatus,
    WorkbenchSummaryCard,
    WorkbenchTimeRange,
)
from multi_agent_platform.auth.principal import PrincipalContext


def build_operations_workbench_envelope(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    range_preset: str = "60m",
    severity: str | None = None,
    subsystem: str | None = None,
) -> OperationsWorkbenchEnvelope:
    _ = principal
    is_platform = scope.scope_type == ReactAdminScopeType.PLATFORM
    cards = _platform_cards() if is_platform else _tenant_cards(scope)
    panels = _platform_panels() if is_platform else _tenant_panels(scope)
    fallback_links = _fallback_links(is_platform=is_platform)
    run_debug = build_run_debug_envelope(
        scope=scope,
        workflow_run_id="00000000-0000-0000-0000-000000000029",
    )
    logs = _logs(scope=scope, is_platform=is_platform)
    if severity:
        logs = tuple(log for log in logs if log.severity.value == severity)
    if subsystem:
        logs = tuple(log for log in logs if log.subsystem.lower() == subsystem.lower())
    return OperationsWorkbenchEnvelope(
        page_id="react-operations-workbench",
        title="Operations workbench",
        description=(
            "Safe triage across health, reliability, runs, gateway attempts, "
            "tools, delivery, logs, and exports."
        ),
        scope=scope,
        generated_at_label="Generated from deterministic QA029 summaries",
        time_range=WorkbenchTimeRange(preset=range_preset, label="Last 60 minutes"),
        summary_cards=cards,
        likely_causes=_likely_causes(is_platform=is_platform),
        health_panels=panels,
        run_debug=run_debug,
        reliability=_reliability(is_platform=is_platform),
        logs=logs,
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
        exports=build_workbench_export_snapshot(scope=scope),
        fallback_links=fallback_links,
        evidence=(
            EvidenceSummary(
                evidence_id="qa029-redaction",
                label="Redaction evidence",
                summary="Workbench contracts contain safe summaries only.",
                reference_type=EvidenceReferenceType.VALIDATION,
            ),
        ),
        refresh=RefreshHint(mode="manual", interval_seconds=30),
    )


def build_run_debug_envelope(
    *,
    scope: ReactAdminScope,
    workflow_run_id: str | UUID,
) -> RunDebugEnvelope:
    run_id = str(workflow_run_id)
    return RunDebugEnvelope(
        workflow_run_id=run_id,
        tenant_scope=scope if scope.scope_type == ReactAdminScopeType.TENANT else None,
        run_status=WorkbenchStatus.DEGRADED,
        safe_title="Daily briefing graph run",
        timeline=(
            TimelineEventSummary(
                event_id="timeline-run-started",
                occurred_at_label="5 minutes ago",
                sequence=1,
                category="run",
                severity=WorkbenchSeverity.INFO,
                status=WorkbenchStatus.READY,
                summary="Run started with pinned execution bundle.",
                details={
                    "bundle": (
                        "Workflow, prompt, profile, and provider versions pinned."
                    )
                },
                trace_id="trace-qa029-run",
                audit_reference_id="audit-run-qa029",
                links=(WorkbenchLink(label="Open run inspection", href="/admin/runs"),),
            ),
            TimelineEventSummary(
                event_id="timeline-join-waiting",
                occurred_at_label="2 minutes ago",
                sequence=2,
                category="graph_join",
                severity=WorkbenchSeverity.WARNING,
                status=WorkbenchStatus.WARNING,
                summary="Join is waiting for one branch retry.",
                details={"join": "Weather branch retry is scheduled."},
                audit_reference_id="audit-join-qa029",
            ),
        ),
        branches=(
            GraphBranchSummary(
                branch_id="branch-calendar",
                label="Calendar branch",
                status=WorkbenchStatus.READY,
                node_count=2,
                completed_count=2,
                summary="Calendar context completed with safe connector output.",
            ),
            GraphBranchSummary(
                branch_id="branch-weather",
                label="Weather branch",
                status=WorkbenchStatus.WARNING,
                node_count=2,
                completed_count=1,
                waiting_count=1,
                join_policy="Wait for required branches",
                join_decision="Retry scheduled before join",
                manual_resolution_required=False,
                summary="Weather connector retry is pending before the join completes.",
            ),
        ),
        gateway_attempts=(
            GatewayAttemptSummary(
                attempt_id="gateway-attempt-qa029",
                provider_label="OpenAI provider",
                model_label="Pinned briefing model",
                status=WorkbenchStatus.DEGRADED,
                latency_ms=840,
                retry_category="retryable_timeout",
                breaker_category="closed",
                credential_diagnostic_category="resolved_reference",
                usage_reference_id="usage-qa029",
                safe_summary="Gateway attempt retried after a timeout category.",
                evidence_reference_id="gateway-evidence-qa029",
            ),
        ),
        tool_calls=(
            ToolCallSummary(
                tool_call_id="tool-call-qa029",
                tool_label="Daily briefing weather",
                connector_label="Weather connector",
                readiness_status=WorkbenchStatus.READY,
                policy_outcome="allowed_read_only",
                side_effect_classification="read_only",
                result_category="safe_summary",
                safe_summary="Connector returned a redacted weather summary.",
                evidence_reference_id="tool-evidence-qa029",
            ),
        ),
        deliveries=(
            ChannelDeliverySummary(
                delivery_id="delivery-qa029",
                channel="telegram",
                alias_label="Morning briefing alias",
                identity_status=WorkbenchStatus.READY,
                receipt_status=WorkbenchStatus.READY,
                notification_status=WorkbenchStatus.WARNING,
                delivery_status=WorkbenchStatus.WARNING,
                failure_category="mock_delivery_retry",
                safe_summary=(
                    "Delivery is queued for a mocked retry without private message "
                    "text."
                ),
                evidence_reference_id="delivery-evidence-qa029",
            ),
        ),
        lineage=(
            WorkbenchLink(
                label="Parent run lineage",
                href=f"/admin/runs/{run_id}/lineage",
            ),
        ),
        replay_links=(
            WorkbenchLink(
                label="Open safe replay",
                href=f"/admin/runs/{run_id}/replay",
            ),
        ),
        bundle_summary=(
            "Pinned workflow, prompt, profile, provider, and tool policy versions."
        ),
        fallback_links=(
            WorkbenchLink(label="Run search", href="/admin/runs"),
            WorkbenchLink(label="Operations console", href="/admin/operations"),
        ),
    )


def build_workbench_export_snapshot(
    *,
    scope: ReactAdminScope,
    request: WorkbenchExportRequest | None = None,
) -> WorkbenchExportSnapshot:
    _ = request
    scope_label = (
        "platform" if scope.scope_type == ReactAdminScopeType.PLATFORM else "tenant"
    )
    return WorkbenchExportSnapshot(
        export_id=f"workbench-export-qa029-{scope_label}",
        status=AdminExportStatus.COMPLETE,
        summary="Workbench export is ready as a safe artifact reference.",
        artifact_reference_id=f"artifact-ref-qa029-{scope_label}",
        progress_label="Complete",
        audit_reference_id=f"audit-workbench-export-qa029-{scope_label}",
        scope_label=scope.label,
        redaction_summary=(
            "Secrets, prompt output, memory references, provider responses, "
            "channel message text, and connector outputs are redacted."
        ),
        row_count=12 if scope.scope_type == ReactAdminScopeType.PLATFORM else 5,
    )


def _platform_cards() -> tuple[WorkbenchSummaryCard, ...]:
    return (
        WorkbenchSummaryCard(
            card_id="health",
            label="Health",
            value="degraded",
            status=WorkbenchStatus.DEGRADED,
            severity=WorkbenchSeverity.WARNING,
            summary="One dependency is degraded while core API readiness is available.",
            freshness_label="Checked within 1 minute",
            trend="stable",
            href="/admin/operations",
            evidence_reference_id="health-qa029",
        ),
        WorkbenchSummaryCard(
            card_id="queue-pressure",
            label="Queue pressure",
            value="18 runnable",
            status=WorkbenchStatus.WARNING,
            severity=WorkbenchSeverity.WARNING,
            summary="Runnable work is elevated and retries are accumulating.",
            freshness_label="Last 60 minutes",
            href="/admin/reliability/ui/",
            evidence_reference_id="queue-qa029",
        ),
        WorkbenchSummaryCard(
            card_id="provider-health",
            label="Provider health",
            value="1 degraded",
            status=WorkbenchStatus.DEGRADED,
            severity=WorkbenchSeverity.WARNING,
            summary="A model provider has retryable timeout evidence.",
            freshness_label="Last probe 4 minutes ago",
            href="/admin/model-providers",
            evidence_reference_id="provider-qa029",
        ),
    )


def _tenant_cards(scope: ReactAdminScope) -> tuple[WorkbenchSummaryCard, ...]:
    return (
        WorkbenchSummaryCard(
            card_id="tenant-runs",
            label="Tenant run health",
            value="attention needed",
            status=WorkbenchStatus.WARNING,
            severity=WorkbenchSeverity.WARNING,
            summary=f"{scope.label} has one run waiting for a safe retry.",
            freshness_label="Last 60 minutes",
            href=_with_tenant_query("/admin/runs", scope),
            evidence_reference_id="tenant-run-qa029",
        ),
        WorkbenchSummaryCard(
            card_id="tenant-delivery",
            label="Tenant delivery",
            value="retry queued",
            status=WorkbenchStatus.WARNING,
            severity=WorkbenchSeverity.WARNING,
            summary="A mocked Telegram delivery attempt is queued for retry.",
            freshness_label="Updated 2 minutes ago",
            href=_with_tenant_query("/admin/telegram", scope),
            evidence_reference_id="tenant-delivery-qa029",
        ),
    )


def _platform_panels() -> tuple[HealthPressurePanel, ...]:
    return (
        HealthPressurePanel(
            panel_id="capacity",
            title="Capacity and dependencies",
            status=WorkbenchStatus.DEGRADED,
            metrics=(
                WorkbenchMetric(
                    label="Runnable queue",
                    value="18",
                    status=WorkbenchStatus.WARNING,
                ),
                WorkbenchMetric(label="Database pool wait p95", value="42 ms"),
                WorkbenchMetric(label="Artifact operations", value="3 inflight"),
            ),
            dependencies=(
                WorkbenchMetric(label="PostgreSQL", value="ready"),
                WorkbenchMetric(
                    label="Telegram",
                    value="degraded",
                    status=WorkbenchStatus.DEGRADED,
                ),
            ),
            freshness_label="Checked within 1 minute",
            polling_allowed=True,
            links=(
                WorkbenchLink(
                    label="Existing operations console",
                    href="/admin/operations",
                ),
            ),
        ),
    )


def _tenant_panels(scope: ReactAdminScope) -> tuple[HealthPressurePanel, ...]:
    return (
        HealthPressurePanel(
            panel_id="tenant-activity",
            title="Tenant activity",
            status=WorkbenchStatus.WARNING,
            metrics=(
                WorkbenchMetric(
                    label="Runs needing attention",
                    value="1",
                    status=WorkbenchStatus.WARNING,
                ),
                WorkbenchMetric(
                    label="Deliveries queued",
                    value="1",
                    status=WorkbenchStatus.WARNING,
                ),
            ),
            freshness_label=f"{scope.label} scope only",
            polling_allowed=True,
            partial_reason=(
                "Platform-only provider, queue, and database pressure details are "
                "hidden for tenant scope."
            ),
            links=(
                WorkbenchLink(
                    label="Run search",
                    href=_with_tenant_query("/admin/runs", scope),
                ),
            ),
        ),
    )


def _likely_causes(*, is_platform: bool) -> tuple[LikelyCauseSummary, ...]:
    if not is_platform:
        return (
            LikelyCauseSummary(
                cause_id="tenant-delivery-retry",
                severity=WorkbenchSeverity.WARNING,
                affected_subsystem="Tenant delivery",
                symptom="One delivery attempt is queued for retry.",
                likely_cause_category="mock_delivery_retry",
                recommended_next_step="Open Telegram diagnostics for the tenant.",
                href="/admin/telegram",
                evidence_reference_id="delivery-evidence-qa029",
            ),
        )
    return (
        LikelyCauseSummary(
            cause_id="provider-timeout",
            severity=WorkbenchSeverity.WARNING,
            affected_subsystem="Model gateway",
            symptom="Provider attempt latency and retry counts increased.",
            likely_cause_category="retryable_timeout",
            recommended_next_step="Open provider health and gateway diagnostics.",
            href="/admin/model-providers",
            evidence_reference_id="gateway-evidence-qa029",
        ),
    )


def _reliability(*, is_platform: bool) -> ReliabilityRecoverySummary:
    return ReliabilityRecoverySummary(
        breakers=(
            ReliabilityRecoveryItem(
                item_id="breaker-model-gateway",
                label="Model gateway breaker",
                status=(
                    WorkbenchStatus.READY
                    if is_platform
                    else WorkbenchStatus.UNAVAILABLE
                ),
                severity=WorkbenchSeverity.INFO,
                summary="Breaker is closed with retryable timeout evidence summarized.",
                href="/admin/reliability/ui/breakers" if is_platform else None,
            ),
        ),
        retries=(
            ReliabilityRecoveryItem(
                item_id="retry-weather-branch",
                label="Weather branch retry",
                status=WorkbenchStatus.WARNING,
                severity=WorkbenchSeverity.WARNING,
                summary="Retry is scheduled before the graph join completes.",
                href="/admin/reliability/ui/",
            ),
        ),
        dead_letters=(
            ReliabilityRecoveryItem(
                item_id="dead-letters",
                label="Dead letters",
                status=WorkbenchStatus.READY,
                severity=WorkbenchSeverity.INFO,
                summary="No dead-letter records match the active workbench scope.",
                href="/admin/reliability/ui/dead-letters" if is_platform else None,
            ),
        ),
        confirmations=(
            ReliabilityRecoveryItem(
                item_id="replay-confirmation",
                label="Replay requires confirmation",
                status=WorkbenchStatus.WARNING,
                severity=WorkbenchSeverity.WARNING,
                summary="Replay-style remediation must be confirmed and audited.",
                confirmation="Confirm safe replay preview",
            ),
        ),
    )


def _logs(
    *,
    scope: ReactAdminScope,
    is_platform: bool,
) -> tuple[WorkbenchLogSummary, ...]:
    tenant_scope = None if is_platform else scope.label
    return (
        WorkbenchLogSummary(
            log_id="log-gateway-timeout",
            occurred_at_label="4 minutes ago",
            source="gateway_attempt",
            severity=WorkbenchSeverity.WARNING,
            status=WorkbenchStatus.DEGRADED,
            subsystem="gateway",
            tenant_scope=tenant_scope,
            run_reference="run-qa029",
            correlation_reference="trace-qa029-run",
            summary="Gateway attempt recorded retryable timeout category.",
            safe_details={
                "provider": "OpenAI provider",
                "diagnostic": "resolved_reference",
            },
            links=(
                WorkbenchLink(
                    label="Provider diagnostics",
                    href="/admin/model-providers",
                ),
            ),
        ),
        WorkbenchLogSummary(
            log_id="log-delivery-retry",
            occurred_at_label="2 minutes ago",
            source="channel_delivery",
            severity=WorkbenchSeverity.WARNING,
            status=WorkbenchStatus.WARNING,
            subsystem="telegram",
            tenant_scope=tenant_scope,
            run_reference="run-qa029",
            correlation_reference="trace-qa029-delivery",
            summary="Telegram delivery attempt is queued for mocked retry.",
            safe_details={"alias": "Morning briefing alias"},
            links=(
                WorkbenchLink(
                    label="Telegram diagnostics",
                    href="/admin/telegram",
                ),
            ),
        ),
    )


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
                options=(
                    FilterOption(value="warning", label="Warning"),
                    FilterOption(value="critical", label="Critical"),
                ),
            ),
            FilterCriterion(
                key="subsystem",
                label="Subsystem",
                options=(
                    FilterOption(value="gateway", label="Gateway"),
                    FilterOption(value="telegram", label="Telegram"),
                    FilterOption(value="reliability", label="Reliability"),
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
        WorkbenchLink(label="Existing operations console", href="/admin/operations"),
        WorkbenchLink(label="Run inspection", href="/admin/runs"),
        WorkbenchLink(label="Reliability controls", href="/admin/reliability/ui/"),
        WorkbenchLink(
            label="Skill tool diagnostics",
            href="/admin/skill-execution/ui/diagnostics",
        ),
    ]
    if is_platform:
        links.extend(
            [
                WorkbenchLink(label="Model providers", href="/admin/model-providers"),
                WorkbenchLink(label="Usage analytics", href="/admin/usage"),
            ]
        )
    return tuple(links)


def _with_tenant_query(path: str, scope: ReactAdminScope) -> str:
    if scope.scope_type != ReactAdminScopeType.TENANT or scope.tenant_id is None:
        return path
    separator = "&" if "?" in path else "?"
    return f"{path}{separator}tenant_id={scope.tenant_id}"
