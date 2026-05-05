from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminPageAction,
    ReactAdminPageActionVariant,
    ReactAdminScope,
    ReactAdminScopeOption,
    ReactAdminScopeType,
    ReactAdminShellState,
    ReactAdminShellStateKind,
)
from multi_agent_platform.api.schemas.admin_usage_react import (
    UsageReactConfidenceStatus,
    UsageReactDashboard,
    UsageReactDashboardQuery,
    UsageReactEventDrilldown,
    UsageReactEventQuery,
    UsageReactEventRow,
    UsageReactExportCreateRequest,
    UsageReactExportStatus,
    UsageReactExportSummary,
    UsageReactFilterMetadata,
    UsageReactFilterOption,
    UsageReactGroupBy,
    UsageReactProblem,
    UsageReactProblemReason,
    UsageReactRange,
    UsageReactRollupRow,
    UsageReactRollupSection,
    UsageReactSummaryCard,
    UsageReactTone,
    UsageReactTrendPoint,
)
from multi_agent_platform.auth.principal import PrincipalContext

ACME_TENANT_ID = "11111111-1111-1111-1111-111111111111"
GLOBEX_TENANT_ID = "22222222-2222-2222-2222-222222222222"
ACME_LABEL = "Acme"
GLOBEX_LABEL = "Globex"
QA_NOW = datetime(2026, 5, 5, 16, 0, tzinfo=UTC)
COMPLETED_EXPORT_ID = UUID("35000000-0000-0000-0000-000000000035")
DENIED_EXPORT_ID = UUID("35000000-0000-0000-0000-00000000d035")


@dataclass(frozen=True, slots=True)
class UsageActor:
    platform_admin: bool
    active_tenant_id: str | None
    active_tenant_label: str | None
    principal_label: str


@dataclass(frozen=True, slots=True)
class UsageFixtureEvent:
    event_id: UUID
    tenant_id: str
    tenant_label: str
    day_offset: int
    provider: str
    model: str
    workflow: str
    agent: str
    sub_agent: str
    prompt: str
    execution_mode: str
    principal: str
    graph_node: str
    gateway_operation: str
    physical_attempt: str
    governed_tool: str
    total_tokens: int
    input_tokens: int
    output_tokens: int
    estimated_cost_micros: int
    latency_ms: int
    status: UsageReactConfidenceStatus
    cost_status: UsageReactConfidenceStatus
    unavailable: bool = False
    archived: bool = False

    @property
    def recorded_at(self) -> datetime:
        return QA_NOW - timedelta(days=self.day_offset, hours=self.day_offset)


USAGE_EVENTS: tuple[UsageFixtureEvent, ...] = (
    UsageFixtureEvent(
        event_id=UUID("35000000-0000-0000-0000-000000000001"),
        tenant_id=ACME_TENANT_ID,
        tenant_label=ACME_LABEL,
        day_offset=0,
        provider="OpenAI",
        model="gpt-4.1-mini",
        workflow="Daily briefing workflow",
        agent="Briefing coordinator",
        sub_agent="Calendar summarizer",
        prompt="Briefing digest prompt v7",
        execution_mode="production",
        principal="tenant-admin-acme",
        graph_node="Collect calendar signals",
        gateway_operation="chat.completions primary route",
        physical_attempt="OpenAI attempt 1 succeeded",
        governed_tool="Daily briefing calendar list",
        total_tokens=12840,
        input_tokens=8120,
        output_tokens=4720,
        estimated_cost_micros=43680,
        latency_ms=820,
        status=UsageReactConfidenceStatus.CONFIRMED,
        cost_status=UsageReactConfidenceStatus.ESTIMATED,
    ),
    UsageFixtureEvent(
        event_id=UUID("35000000-0000-0000-0000-000000000002"),
        tenant_id=ACME_TENANT_ID,
        tenant_label=ACME_LABEL,
        day_offset=1,
        provider="OpenAI",
        model="gpt-4.1",
        workflow="Support triage workflow",
        agent="Triage analyst",
        sub_agent="Policy reviewer",
        prompt="Escalation policy prompt v3",
        execution_mode="production",
        principal="platform-admin",
        graph_node="Review escalation policy",
        gateway_operation="responses failover route",
        physical_attempt="OpenAI attempt 2 after retry",
        governed_tool="Daily briefing document search",
        total_tokens=22110,
        input_tokens=14800,
        output_tokens=7310,
        estimated_cost_micros=141900,
        latency_ms=1370,
        status=UsageReactConfidenceStatus.ESTIMATED,
        cost_status=UsageReactConfidenceStatus.ESTIMATED,
    ),
    UsageFixtureEvent(
        event_id=UUID("35000000-0000-0000-0000-000000000003"),
        tenant_id=ACME_TENANT_ID,
        tenant_label=ACME_LABEL,
        day_offset=2,
        provider="Local compatible",
        model="local-llama-qa",
        workflow="Workflow builder validation",
        agent="Validation reviewer",
        sub_agent="Graph planner",
        prompt="Builder validation prompt v2",
        execution_mode="test",
        principal="local-principal-admin",
        graph_node="Validate graph bundle",
        gateway_operation="local no-auth route",
        physical_attempt="Local attempt 1 completed",
        governed_tool="No connector tool",
        total_tokens=7310,
        input_tokens=6110,
        output_tokens=1200,
        estimated_cost_micros=0,
        latency_ms=430,
        status=UsageReactConfidenceStatus.PARTIAL,
        cost_status=UsageReactConfidenceStatus.UNAVAILABLE,
        archived=True,
    ),
    UsageFixtureEvent(
        event_id=UUID("35000000-0000-0000-0000-000000000004"),
        tenant_id=GLOBEX_TENANT_ID,
        tenant_label=GLOBEX_LABEL,
        day_offset=1,
        provider="OpenAI",
        model="gpt-4.1-mini",
        workflow="Invoice research workflow",
        agent="Finance analyst",
        sub_agent="Evidence collector",
        prompt="Invoice review prompt v5",
        execution_mode="production",
        principal="tenant-admin-globex",
        graph_node="Summarize invoice evidence",
        gateway_operation="chat.completions primary route",
        physical_attempt="OpenAI attempt 1 succeeded",
        governed_tool="Daily briefing mail search",
        total_tokens=18650,
        input_tokens=11950,
        output_tokens=6700,
        estimated_cost_micros=60450,
        latency_ms=910,
        status=UsageReactConfidenceStatus.CONFIRMED,
        cost_status=UsageReactConfidenceStatus.ESTIMATED,
    ),
    UsageFixtureEvent(
        event_id=UUID("35000000-0000-0000-0000-000000000005"),
        tenant_id=GLOBEX_TENANT_ID,
        tenant_label=GLOBEX_LABEL,
        day_offset=3,
        provider="OpenAI",
        model="gpt-4.1",
        workflow="Operations incident workflow",
        agent="Incident commander",
        sub_agent="Run debugger",
        prompt="Incident timeline prompt v4",
        execution_mode="production",
        principal="platform-admin",
        graph_node="Join branch evidence",
        gateway_operation="responses primary route",
        physical_attempt="Provider usage unavailable",
        governed_tool="Operations run lookup",
        total_tokens=0,
        input_tokens=0,
        output_tokens=0,
        estimated_cost_micros=0,
        latency_ms=1880,
        status=UsageReactConfidenceStatus.UNAVAILABLE,
        cost_status=UsageReactConfidenceStatus.UNAVAILABLE,
        unavailable=True,
    ),
)


def build_usage_dashboard(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    allowed_scope_options: tuple[ReactAdminScopeOption, ...],
    query: UsageReactDashboardQuery | None = None,
) -> UsageReactDashboard:
    actor = _actor(scope=scope, principal=principal)
    query = query or UsageReactDashboardQuery()
    safe_query = _scope_query(actor, query)
    events = _filtered_events(actor, safe_query)
    filters = _filter_metadata(actor, safe_query, events)
    rollup = _rollup_section(safe_query.group_by, events)
    drilldown = _drilldown(events[:100], total_rows=len(events))
    return UsageReactDashboard(
        page_id="qa035-usage-analytics",
        title="Usage and Cost Analytics",
        description=(
            "Review token usage, cost estimates, latency, confidence, "
            "attribution, and safe export evidence."
        ),
        scope=scope,
        allowed_scope_options=allowed_scope_options or _default_scope_options(actor),
        filters=filters,
        summary_cards=_summary_cards(events),
        trend=_trend_points(events, filters.selected_range),
        rollup=rollup,
        drilldown=drilldown,
        exports=(_export_summary(actor=actor, request=None),),
        states=_states(actor, events),
        common_states=_common_states(actor, events),
        updated_at=QA_NOW,
    )


def build_usage_events(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    query: UsageReactEventQuery,
) -> UsageReactEventDrilldown:
    actor = _actor(scope=scope, principal=principal)
    safe_query = _scope_query(actor, query)
    events = _filtered_events(actor, safe_query)
    if query.rollup_key:
        events = [
            event
            for event in events
            if _rollup_key(event, safe_query.group_by) == query.rollup_key
        ]
    return _drilldown(events[:100], total_rows=len(events))


def build_usage_export_result(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    request: UsageReactExportCreateRequest,
) -> UsageReactExportSummary:
    actor = _actor(scope=scope, principal=principal)
    tenant_id = request.filters.get("tenant_id")
    if tenant_id and not _tenant_allowed(actor, tenant_id):
        return _export_summary(
            actor=actor,
            request=request,
            status=UsageReactExportStatus.DENIED,
            export_id=DENIED_EXPORT_ID,
            denial_reason="tenant scope denied",
            row_count=0,
        )
    return _export_summary(actor=actor, request=request)


def build_usage_export_detail(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    usage_export_request_id: UUID,
) -> UsageReactExportSummary:
    actor = _actor(scope=scope, principal=principal)
    if usage_export_request_id == DENIED_EXPORT_ID:
        return _export_summary(
            actor=actor,
            request=None,
            status=UsageReactExportStatus.DENIED,
            export_id=usage_export_request_id,
            denial_reason="tenant scope denied",
            row_count=0,
        )
    return _export_summary(
        actor=actor,
        request=None,
        export_id=usage_export_request_id,
    )


def _actor(*, scope: ReactAdminScope, principal: PrincipalContext) -> UsageActor:
    active_tenant_id = str(scope.tenant_id) if scope.tenant_id is not None else None
    return UsageActor(
        platform_admin=scope.scope_type is ReactAdminScopeType.PLATFORM
        or "platform_admin" in principal.role_codes
        or "platform" in principal.role_codes,
        active_tenant_id=active_tenant_id,
        active_tenant_label=_tenant_label(active_tenant_id),
        principal_label=principal.principal_id,
    )


def _scope_query(
    actor: UsageActor,
    query: UsageReactDashboardQuery,
) -> UsageReactDashboardQuery:
    if not actor.platform_admin:
        data = query.model_dump()
        data["tenant_id"] = _canonical_tenant_id(
            actor.active_tenant_id,
            actor.active_tenant_label,
        )
        return type(query).model_validate(data)
    return query


def _filtered_events(
    actor: UsageActor,
    query: UsageReactDashboardQuery,
) -> list[UsageFixtureEvent]:
    start, end = _range_bounds(query)
    tenant_id = query.tenant_id or (
        None if actor.platform_admin else actor.active_tenant_id
    )
    events = [
        event
        for event in USAGE_EVENTS
        if _tenant_allowed(actor, event.tenant_id)
        and (tenant_id is None or event.tenant_id == tenant_id)
        and start <= event.recorded_at < end
        and (query.provider_key is None or event.provider == query.provider_key)
        and (query.model_id is None or event.model == query.model_id)
        and (query.usage_status is None or event.status is query.usage_status)
    ]
    return sorted(events, key=lambda event: event.recorded_at, reverse=True)


def _range_bounds(query: UsageReactDashboardQuery) -> tuple[datetime, datetime]:
    end = query.end or QA_NOW + timedelta(minutes=1)
    start = query.start or end - timedelta(days=7)
    return start, end


def _filter_metadata(
    actor: UsageActor,
    query: UsageReactDashboardQuery,
    events: list[UsageFixtureEvent],
) -> UsageReactFilterMetadata:
    start, end = _range_bounds(query)
    tenant_values = [
        (ACME_TENANT_ID, ACME_LABEL),
        (GLOBEX_TENANT_ID, GLOBEX_LABEL),
    ]
    if not actor.platform_admin:
        tenant_values = [
            (
                actor.active_tenant_id or ACME_TENANT_ID,
                actor.active_tenant_label or ACME_LABEL,
            )
        ]
    providers = sorted({event.provider for event in _visible_events(actor)})
    models = sorted({event.model for event in _visible_events(actor)})
    workflows = sorted({event.workflow for event in _visible_events(actor)})
    agents = sorted({event.agent for event in _visible_events(actor)})
    prompts = sorted({event.prompt for event in _visible_events(actor)})
    return UsageReactFilterMetadata(
        selected_range=UsageReactRange(label="Last 7 days", start=start, end=end),
        range_options=(
            _option("7d", "Last 7 days", selected=True),
            _option("24h", "Last 24 hours"),
            _option("30d", "Last 30 days"),
        ),
        selected_group_by=query.group_by,
        group_by_options=tuple(
            _option(group.value, _group_label(group), selected=group is query.group_by)
            for group in UsageReactGroupBy
            if actor.platform_admin or group is not UsageReactGroupBy.TENANT
        ),
        tenant_options=tuple(
            _option(
                tenant_id,
                label,
                selected=query.tenant_id == tenant_id
                or (not actor.platform_admin and actor.active_tenant_id == tenant_id),
                disabled=not _tenant_allowed(actor, tenant_id),
                disabled_reason=(
                    None
                    if _tenant_allowed(actor, tenant_id)
                    else "Tenant scope is not available."
                ),
            )
            for tenant_id, label in tenant_values
        ),
        provider_options=tuple(
            _option(provider, provider, selected=query.provider_key == provider)
            for provider in providers
        ),
        model_options=tuple(
            _option(model, model, selected=query.model_id == model) for model in models
        ),
        workflow_options=tuple(_option(value, value) for value in workflows),
        agent_options=tuple(_option(value, value) for value in agents),
        prompt_options=tuple(_option(value, value) for value in prompts),
        confidence_options=tuple(
            _option(
                status.value,
                status.value.title(),
                selected=query.usage_status is status,
            )
            for status in UsageReactConfidenceStatus
        ),
        availability_options=(
            _option("all", "All usage"),
            _option("available", "Available usage"),
            _option("unavailable", "Unavailable usage"),
        ),
        disabled_reasons=(
            {} if events else {"events": "No usage events match the selected filters."}
        ),
    )


def _summary_cards(
    events: list[UsageFixtureEvent],
) -> tuple[UsageReactSummaryCard, ...]:
    total_tokens = sum(event.total_tokens for event in events)
    total_cost = sum(event.estimated_cost_micros for event in events)
    total_latency = sum(event.latency_ms for event in events)
    unavailable = sum(1 for event in events if event.unavailable)
    confirmed = sum(
        1 for event in events if event.status is UsageReactConfidenceStatus.CONFIRMED
    )
    estimated = sum(
        1 for event in events if event.status is UsageReactConfidenceStatus.ESTIMATED
    )
    average_latency = int(total_latency / len(events)) if events else 0
    coverage_status = (
        UsageReactConfidenceStatus.CONFIRMED
        if events and confirmed == len(events)
        else UsageReactConfidenceStatus.PARTIAL
        if events
        else UsageReactConfidenceStatus.UNAVAILABLE
    )
    return (
        _card(
            "tokens",
            "Total tokens",
            f"{total_tokens:,}",
            "tokens",
            coverage_status,
            "Confirmed and estimated token counts for the selected scope.",
        ),
        _card(
            "cost",
            "Estimated cost",
            _money(total_cost),
            "USD",
            UsageReactConfidenceStatus.ESTIMATED if events else coverage_status,
            "Cost is estimated from active pricing metadata.",
        ),
        _card(
            "events",
            "Usage events",
            str(len(events)),
            "events",
            coverage_status,
            "Bounded normalized usage records included in this view.",
        ),
        _card(
            "latency",
            "Average latency",
            f"{average_latency:,}",
            "ms",
            coverage_status,
            "Mean gateway latency for visible usage events.",
        ),
        _card(
            "unavailable",
            "Unavailable usage",
            str(unavailable),
            "events",
            UsageReactConfidenceStatus.UNAVAILABLE if unavailable else coverage_status,
            "Provider usage that could not be confirmed remains visible safely.",
            tone=UsageReactTone.WARNING if unavailable else UsageReactTone.SUCCESS,
        ),
        _card(
            "coverage",
            "Confidence coverage",
            f"{confirmed} confirmed · {estimated} estimated",
            "events",
            coverage_status,
            "Confirmed, estimated, partial, and unavailable states stay separate.",
        ),
    )


def _trend_points(
    events: list[UsageFixtureEvent],
    selected_range: UsageReactRange,
) -> tuple[UsageReactTrendPoint, ...]:
    start = selected_range.start
    buckets: dict[datetime, list[UsageFixtureEvent]] = defaultdict(list)
    for event in events:
        bucket = event.recorded_at.replace(hour=0, minute=0, second=0, microsecond=0)
        buckets[bucket].append(event)
    points: list[UsageReactTrendPoint] = []
    for index in range(7):
        bucket_start = (start + timedelta(days=index)).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        bucket_events = buckets.get(bucket_start, [])
        confirmed_tokens = sum(
            event.total_tokens
            for event in bucket_events
            if event.status is UsageReactConfidenceStatus.CONFIRMED
        )
        estimated_tokens = sum(
            event.total_tokens
            for event in bucket_events
            if event.status
            in {
                UsageReactConfidenceStatus.ESTIMATED,
                UsageReactConfidenceStatus.PARTIAL,
            }
        )
        unavailable_events = sum(1 for event in bucket_events if event.unavailable)
        average_latency = (
            int(sum(event.latency_ms for event in bucket_events) / len(bucket_events))
            if bucket_events
            else 0
        )
        points.append(
            UsageReactTrendPoint(
                bucket_start=bucket_start,
                bucket_end=bucket_start + timedelta(days=1),
                label=bucket_start.strftime("%b %-d"),
                confirmed_tokens=confirmed_tokens,
                estimated_tokens=estimated_tokens,
                unavailable_events=unavailable_events,
                estimated_cost_display=_money(
                    sum(event.estimated_cost_micros for event in bucket_events)
                ),
                estimated_cost_micros=sum(
                    event.estimated_cost_micros for event in bucket_events
                ),
                average_latency_ms=average_latency,
                event_count=len(bucket_events),
                confidence_status=_confidence(bucket_events),
            )
        )
    return tuple(points)


def _rollup_section(
    group_by: UsageReactGroupBy,
    events: list[UsageFixtureEvent],
) -> UsageReactRollupSection:
    grouped: dict[str, list[UsageFixtureEvent]] = defaultdict(list)
    for event in events:
        grouped[_rollup_key(event, group_by)].append(event)
    rows = [
        _rollup_row(group_by, key, bucket)
        for key, bucket in sorted(
            grouped.items(),
            key=lambda item: sum(event.total_tokens for event in item[1]),
            reverse=True,
        )
    ]
    return UsageReactRollupSection(
        group_by=group_by,
        rows=tuple(rows[:25]),
        limit=25,
        total_rows=len(rows),
    )


def _rollup_row(
    group_by: UsageReactGroupBy,
    key: str,
    events: list[UsageFixtureEvent],
) -> UsageReactRollupRow:
    total_tokens = sum(event.total_tokens for event in events)
    average_latency = int(sum(event.latency_ms for event in events) / len(events))
    first = events[0]
    return UsageReactRollupRow(
        row_id=f"{group_by.value}:{key}",
        group_by=group_by,
        safe_label=key,
        safe_summary=_rollup_summary(group_by, first),
        event_count=len(events),
        total_tokens=total_tokens,
        input_tokens=sum(event.input_tokens for event in events),
        output_tokens=sum(event.output_tokens for event in events),
        estimated_cost_display=_money(
            sum(event.estimated_cost_micros for event in events)
        ),
        estimated_cost_micros=sum(event.estimated_cost_micros for event in events),
        average_latency_ms=average_latency,
        unavailable_event_count=sum(1 for event in events if event.unavailable),
        confidence_status=_confidence(events),
        attempt_summary=(
            first.physical_attempt
            if group_by
            in {UsageReactGroupBy.GATEWAY_OPERATION, UsageReactGroupBy.PHYSICAL_ATTEMPT}
            else None
        ),
        tool_summary=(
            first.governed_tool if group_by is UsageReactGroupBy.GOVERNED_TOOL else None
        ),
        drilldown_href=(
            f"/admin/app/usage/events.json?group_by={group_by.value}&rollup_key={key}"
        ),
    )


def _drilldown(
    events: list[UsageFixtureEvent],
    *,
    total_rows: int,
) -> UsageReactEventDrilldown:
    return UsageReactEventDrilldown(
        rows=tuple(_event_row(event) for event in events[:100]),
        limit=100,
        total_rows=total_rows,
        truncated=total_rows > 100,
    )


def _event_row(event: UsageFixtureEvent) -> UsageReactEventRow:
    return UsageReactEventRow(
        event_id=event.event_id,
        recorded_at=event.recorded_at,
        tenant_label=event.tenant_label,
        provider_label=event.provider,
        model_label=event.model,
        workflow_label=event.workflow,
        agent_label=event.agent,
        prompt_label=event.prompt,
        graph_node_label=event.graph_node,
        gateway_operation_label=event.gateway_operation,
        physical_attempt_label=event.physical_attempt,
        tool_label=event.governed_tool,
        total_tokens=event.total_tokens,
        input_tokens=event.input_tokens,
        output_tokens=event.output_tokens,
        estimated_cost_display=_money(event.estimated_cost_micros),
        latency_ms=event.latency_ms,
        usage_status=event.status,
        cost_status=event.cost_status,
        safe_attribution_summary=(
            "Archived reference rendered as a safe label."
            if event.archived
            else "Safe runtime attribution summary."
        ),
        audit_reference=f"audit-usage-qa035-{str(event.event_id)[-4:]}",
        trace_reference=f"trace-qa035-{str(event.event_id)[-4:]}",
    )


def _export_summary(
    *,
    actor: UsageActor,
    request: UsageReactExportCreateRequest | None,
    status: UsageReactExportStatus = UsageReactExportStatus.COMPLETED,
    export_id: UUID = COMPLETED_EXPORT_ID,
    denial_reason: str | None = None,
    row_count: int | None = None,
) -> UsageReactExportSummary:
    snapshot = request.filters if request is not None else {"range": "last_7_days"}
    completed = QA_NOW if status is UsageReactExportStatus.COMPLETED else None
    rows = row_count
    if rows is None:
        rows = len(
            [
                event
                for event in _visible_events(actor)
                if _tenant_allowed(actor, event.tenant_id)
            ]
        )
    return UsageReactExportSummary(
        usage_export_request_id=export_id,
        status=status,
        scope_label=(
            "Platform"
            if actor.platform_admin and not snapshot.get("tenant_id")
            else actor.active_tenant_label
            or _tenant_label(snapshot.get("tenant_id"))
            or "Active tenant"
        ),
        requested_by_label=actor.principal_label,
        filter_snapshot=snapshot,
        row_count=rows,
        artifact_reference=(
            "usage-export-artifact-qa035"
            if status is UsageReactExportStatus.COMPLETED
            else None
        ),
        artifact_size_label=(
            "18 KB" if status is UsageReactExportStatus.COMPLETED else None
        ),
        checksum_prefix=(
            "sha256:qa035d" if status is UsageReactExportStatus.COMPLETED else None
        ),
        created_at=QA_NOW - timedelta(minutes=4),
        completed_at=completed,
        expires_at=QA_NOW + timedelta(days=7),
        audit_reference=(
            "audit-usage-qa035-export-denied"
            if status is UsageReactExportStatus.DENIED
            else "audit-usage-qa035-export-created"
        ),
        denial_reason=denial_reason,
        failure_reason=None,
        next_step=(
            "Review the safe denial and adjust tenant scope."
            if status is UsageReactExportStatus.DENIED
            else "Use the artifact reference from the governed export store."
        ),
    )


def _visible_events(actor: UsageActor) -> tuple[UsageFixtureEvent, ...]:
    return tuple(
        event for event in USAGE_EVENTS if _tenant_allowed(actor, event.tenant_id)
    )


def _tenant_allowed(actor: UsageActor, tenant_id: str | None) -> bool:
    if actor.platform_admin:
        return True
    return tenant_id is not None and tenant_id == _canonical_tenant_id(
        actor.active_tenant_id,
        actor.active_tenant_label,
    )


def _canonical_tenant_id(tenant_id: str | None, tenant_label: str | None) -> str | None:
    if tenant_id in {ACME_TENANT_ID, GLOBEX_TENANT_ID}:
        return tenant_id
    if tenant_label == ACME_LABEL:
        return ACME_TENANT_ID
    if tenant_label == GLOBEX_LABEL:
        return GLOBEX_TENANT_ID
    return tenant_id


def _tenant_label(tenant_id: str | None) -> str | None:
    if tenant_id == ACME_TENANT_ID:
        return ACME_LABEL
    if tenant_id == GLOBEX_TENANT_ID:
        return GLOBEX_LABEL
    return None


def _default_scope_options(actor: UsageActor) -> tuple[ReactAdminScopeOption, ...]:
    if actor.platform_admin:
        return (
            ReactAdminScopeOption(
                scope=ReactAdminScope(
                    scope_type=ReactAdminScopeType.PLATFORM,
                    tenant_id=None,
                    label="Platform",
                ),
                label="Platform",
                href="/admin/app/usage",
                selected=True,
            ),
        )
    return ()


def _states(
    actor: UsageActor,
    events: list[UsageFixtureEvent],
) -> tuple[UsageReactProblem, ...]:
    states: list[UsageReactProblem] = []
    if not events:
        states.append(
            UsageReactProblem(
                reason=UsageReactProblemReason.EMPTY,
                title="No usage events",
                detail="No safe usage events match the selected filters.",
                next_action="Adjust the range or grouping filters.",
            )
        )
    if any(event.status is UsageReactConfidenceStatus.PARTIAL for event in events):
        states.append(
            UsageReactProblem(
                reason=UsageReactProblemReason.PARTIAL,
                title="Partial usage",
                detail="Some provider values are estimated or incomplete.",
                next_action="Review confidence labels before exporting.",
            )
        )
    if any(event.unavailable for event in events):
        states.append(
            UsageReactProblem(
                reason=UsageReactProblemReason.UNAVAILABLE,
                title="Unavailable usage",
                detail="Some provider usage was unavailable and is counted separately.",
                next_action="Use event drilldown for safe attempt evidence.",
            )
        )
    if not actor.platform_admin:
        states.append(
            UsageReactProblem(
                reason=UsageReactProblemReason.DENIED,
                title="Tenant scope enforced",
                detail="This view is limited to the active tenant.",
                next_action="Ask a platform administrator for cross-tenant analysis.",
                audit_reference="audit-usage-qa035-tenant-scope",
            )
        )
    return tuple(states)


def _common_states(
    actor: UsageActor,
    events: list[UsageFixtureEvent],
) -> tuple[ReactAdminShellState, ...]:
    states = [
        ReactAdminShellState(
            state=ReactAdminShellStateKind.PARTIAL_DATA
            if events
            else ReactAdminShellStateKind.EMPTY,
            title="Usage analytics ready" if events else "No usage events",
            summary=(
                "Summary, trend, rollups, drilldown, and export evidence are bounded."
                if events
                else "No usage events match the active filters."
            ),
            trace_id=None,
        )
    ]
    if not actor.platform_admin:
        states.append(
            ReactAdminShellState(
                state=ReactAdminShellStateKind.DENIED,
                title="Platform scope hidden",
                summary="Tenant administrators see only their active tenant usage.",
                action=ReactAdminPageAction(
                    action_id="usage-tenant-scope",
                    label="Stay in tenant scope",
                    href="/admin/app/usage",
                    variant=ReactAdminPageActionVariant.SECONDARY,
                ),
                trace_id=None,
            )
        )
    return tuple(states)


def _card(
    card_id: str,
    label: str,
    value: str,
    unit: str,
    status: UsageReactConfidenceStatus,
    detail: str,
    *,
    tone: UsageReactTone = UsageReactTone.NEUTRAL,
) -> UsageReactSummaryCard:
    return UsageReactSummaryCard(
        card_id=card_id,
        label=label,
        value=value,
        unit=unit,
        status=status,
        tone=tone,
        detail=detail,
        comparison="Selected range",
    )


def _option(
    value: str,
    label: str,
    *,
    selected: bool = False,
    disabled: bool = False,
    disabled_reason: str | None = None,
) -> UsageReactFilterOption:
    return UsageReactFilterOption(
        value=value,
        label=label,
        selected=selected,
        disabled=disabled,
        disabled_reason=disabled_reason,
    )


def _money(micros: int) -> str:
    amount = micros / 1_000_000
    if amount == 0:
        return "$0.0000"
    if amount < 0.01:
        return f"${amount:.4f}"
    return f"${amount:.2f}"


def _confidence(events: list[UsageFixtureEvent]) -> UsageReactConfidenceStatus:
    statuses = {event.status for event in events}
    if not events:
        return UsageReactConfidenceStatus.UNAVAILABLE
    if statuses == {UsageReactConfidenceStatus.CONFIRMED}:
        return UsageReactConfidenceStatus.CONFIRMED
    if UsageReactConfidenceStatus.UNAVAILABLE in statuses:
        return UsageReactConfidenceStatus.UNAVAILABLE
    if UsageReactConfidenceStatus.PARTIAL in statuses:
        return UsageReactConfidenceStatus.PARTIAL
    return UsageReactConfidenceStatus.ESTIMATED


def _group_label(group: UsageReactGroupBy) -> str:
    labels = {
        UsageReactGroupBy.DAY: "Day",
        UsageReactGroupBy.TENANT: "Tenant",
        UsageReactGroupBy.PROVIDER: "Provider",
        UsageReactGroupBy.MODEL: "Model",
        UsageReactGroupBy.WORKFLOW: "Workflow",
        UsageReactGroupBy.AGENT: "Agent",
        UsageReactGroupBy.SUB_AGENT: "Sub-agent",
        UsageReactGroupBy.PROMPT: "Prompt",
        UsageReactGroupBy.EXECUTION_MODE: "Execution mode",
        UsageReactGroupBy.PRINCIPAL: "Principal",
        UsageReactGroupBy.GRAPH_NODE: "Graph node",
        UsageReactGroupBy.GATEWAY_OPERATION: "Gateway operation",
        UsageReactGroupBy.PHYSICAL_ATTEMPT: "Physical attempt",
        UsageReactGroupBy.GOVERNED_TOOL: "Governed tool",
    }
    return labels[group]


def _rollup_key(event: UsageFixtureEvent, group_by: UsageReactGroupBy) -> str:
    values = {
        UsageReactGroupBy.DAY: event.recorded_at.strftime("%Y-%m-%d"),
        UsageReactGroupBy.TENANT: event.tenant_label,
        UsageReactGroupBy.PROVIDER: event.provider,
        UsageReactGroupBy.MODEL: event.model,
        UsageReactGroupBy.WORKFLOW: event.workflow,
        UsageReactGroupBy.AGENT: event.agent,
        UsageReactGroupBy.SUB_AGENT: event.sub_agent,
        UsageReactGroupBy.PROMPT: event.prompt,
        UsageReactGroupBy.EXECUTION_MODE: event.execution_mode,
        UsageReactGroupBy.PRINCIPAL: event.principal,
        UsageReactGroupBy.GRAPH_NODE: event.graph_node,
        UsageReactGroupBy.GATEWAY_OPERATION: event.gateway_operation,
        UsageReactGroupBy.PHYSICAL_ATTEMPT: event.physical_attempt,
        UsageReactGroupBy.GOVERNED_TOOL: event.governed_tool,
    }
    return values[group_by]


def _rollup_summary(group_by: UsageReactGroupBy, event: UsageFixtureEvent) -> str:
    if group_by is UsageReactGroupBy.PHYSICAL_ATTEMPT:
        return "Physical attempt evidence is summarized without raw provider details."
    if group_by is UsageReactGroupBy.GATEWAY_OPERATION:
        return "Logical gateway operation, distinct from physical attempts."
    if group_by is UsageReactGroupBy.GOVERNED_TOOL:
        return "Governed connector attribution excludes request and response payloads."
    if group_by is UsageReactGroupBy.GRAPH_NODE:
        return "Graph node attribution uses safe node labels only."
    if event.archived:
        return "Archived reference is retained as a safe label."
    return f"Grouped by {_group_label(group_by).lower()}."
