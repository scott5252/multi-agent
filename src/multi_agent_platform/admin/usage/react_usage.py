from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime, timedelta
from typing import Any, cast
from urllib.parse import urlencode
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
    safe_usage_text,
)
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.models.usage import LlmUsageEvent, UsageExportRequest
from multi_agent_platform.db.repositories.usage import (
    UsageAccessDeniedError,
    UsageRepository,
)
from multi_agent_platform.model_providers.models import UsageValueStatus
from multi_agent_platform.storage.base import StorageProvider
from multi_agent_platform.usage.models import (
    UsageAccessScope,
    UsageEventStatus,
    UsageExportStatus,
    UsageFilters,
    UsageGroupBy,
    UsageScopeType,
)
from multi_agent_platform.usage.service import UsageAnalyticsService

DEFAULT_RANGE_DAYS = 30
DRILLDOWN_LIMIT = 100
ROLLUP_LIMIT = 25
DASHBOARD_EVENT_LIMIT = 200
EXPORT_LIMIT = 10


class UsageReactExportNotFoundError(LookupError):
    pass


async def build_usage_dashboard(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    allowed_scope_options: tuple[ReactAdminScopeOption, ...],
    repository: UsageRepository,
    service: UsageAnalyticsService,
    query: UsageReactDashboardQuery | None = None,
) -> UsageReactDashboard:
    query = query or UsageReactDashboardQuery()
    access_scope = _access_scope(scope=scope, principal=principal)
    filters = _filters(query=query, access_scope=access_scope)
    events = await repository.list_events(
        access_scope=access_scope,
        filters=filters,
        limit=DASHBOARD_EVENT_LIMIT,
    )
    summary = await service.summarize_usage(
        access_scope=access_scope,
        filters=_service_filters(filters, query.group_by),
        limit=DASHBOARD_EVENT_LIMIT,
    )
    tenant_labels = await repository.list_tenant_labels(
        access_scope=access_scope,
        tenant_ids={event.tenant_id for event in events},
    )
    export_requests = await repository.list_export_requests(
        access_scope=access_scope,
        filters=filters,
        limit=EXPORT_LIMIT,
    )
    selected_range = _selected_range(filters)
    filter_metadata = _filter_metadata(
        scope=scope,
        access_scope=access_scope,
        query=query,
        events=events,
        tenant_labels=tenant_labels,
        selected_range=selected_range,
    )
    return UsageReactDashboard(
        page_id="usage-analytics-live",
        title="Usage and Cost Analytics",
        description=(
            "Review token usage, cost estimates, latency, confidence, "
            "attribution, and safe export evidence."
        ),
        scope=scope,
        allowed_scope_options=allowed_scope_options,
        filters=filter_metadata,
        summary_cards=_summary_cards(summary.totals, events),
        trend=_trend_points(events, selected_range),
        rollup=_rollup_section(query.group_by, events, tenant_labels),
        drilldown=_drilldown(
            events[:DRILLDOWN_LIMIT],
            total_rows=len(events),
            tenant_labels=tenant_labels,
        ),
        exports=tuple(_export_summary(export) for export in export_requests),
        states=_states(access_scope, events, export_requests),
        common_states=_common_states(events),
        updated_at=datetime.now(UTC),
    )


async def build_usage_events(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    repository: UsageRepository,
    query: UsageReactEventQuery,
) -> UsageReactEventDrilldown:
    access_scope = _access_scope(scope=scope, principal=principal)
    filters = _filters(query=query, access_scope=access_scope)
    events = await repository.list_events(
        access_scope=access_scope,
        filters=filters,
        limit=DASHBOARD_EVENT_LIMIT,
    )
    tenant_labels = await repository.list_tenant_labels(
        access_scope=access_scope,
        tenant_ids={event.tenant_id for event in events},
    )
    if query.rollup_key:
        events = [
            event
            for event in events
            if _rollup_key(event, query.group_by, tenant_labels) == query.rollup_key
        ]
    return _drilldown(
        events[:DRILLDOWN_LIMIT],
        total_rows=len(events),
        tenant_labels=tenant_labels,
    )


async def build_usage_export_result(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    repository: UsageRepository,
    service: UsageAnalyticsService,
    storage_provider: StorageProvider,
    request: UsageReactExportCreateRequest,
) -> UsageReactExportSummary:
    access_scope = _access_scope(scope=scope, principal=principal)
    filters = _filters_from_snapshot(
        request.filters,
        access_scope=access_scope,
        group_by=request.requested_group_by,
    )
    try:
        return _export_summary(
            await service.create_csv_export(
                access_scope=access_scope,
                filters=filters,
                storage_provider=storage_provider,
            )
        )
    except UsageAccessDeniedError:
        latest = await _latest_export(repository, access_scope, filters)
        if latest is not None:
            return _export_summary(latest)
        return _synthetic_export_summary(
            access_scope=access_scope,
            filters=filters,
            status=UsageReactExportStatus.DENIED,
            reason="tenant scope denied",
        )
    except RuntimeError as exc:
        latest = await _latest_export(repository, access_scope, filters)
        if latest is not None:
            return _export_summary(latest)
        return _synthetic_export_summary(
            access_scope=access_scope,
            filters=filters,
            status=UsageReactExportStatus.UNAVAILABLE,
            reason=str(exc),
        )


async def build_usage_export_detail(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
    repository: UsageRepository,
    usage_export_request_id: UUID,
) -> UsageReactExportSummary:
    access_scope = _access_scope(scope=scope, principal=principal)
    try:
        export = await repository.get_export_request(
            usage_export_request_id,
            access_scope=access_scope,
        )
    except UsageAccessDeniedError as exc:
        raise exc
    if export is None:
        raise UsageReactExportNotFoundError("usage export not found")
    return _export_summary(export)


def _access_scope(
    *,
    scope: ReactAdminScope,
    principal: PrincipalContext,
) -> UsageAccessScope:
    platform_admin = (
        scope.scope_type is ReactAdminScopeType.PLATFORM
        or "platform_admin" in principal.role_codes
        or "platform" in principal.role_codes
    )
    if platform_admin and scope.scope_type is ReactAdminScopeType.PLATFORM:
        return UsageAccessScope(
            scope_type=UsageScopeType.PLATFORM,
            principal_id=principal.principal_id,
            platform_admin=True,
        )
    tenant_id = scope.tenant_id or principal.tenant_id
    if tenant_id is None:
        return UsageAccessScope(
            scope_type=UsageScopeType.PLATFORM,
            principal_id=principal.principal_id,
            platform_admin=platform_admin,
        )
    return UsageAccessScope(
        scope_type=UsageScopeType.TENANT,
        tenant_id=tenant_id,
        principal_id=principal.principal_id,
        platform_admin=platform_admin,
    )


def _filters(
    *,
    query: UsageReactDashboardQuery,
    access_scope: UsageAccessScope,
) -> UsageFilters:
    now = datetime.now(UTC)
    end = query.end or now
    start = query.start or end - timedelta(days=DEFAULT_RANGE_DAYS)
    tenant_id = _query_tenant(query.tenant_id)
    if access_scope.scope_type is UsageScopeType.TENANT and tenant_id is None:
        tenant_id = access_scope.tenant_id
    return UsageFilters(
        tenant_id=tenant_id,
        start=start,
        end=end,
        provider_key=query.provider_key,
        model_id=query.model_id,
        usage_status=_usage_filter_status(query.usage_status),
        group_by=_service_group_by(query.group_by),
    )


def _filters_from_snapshot(
    snapshot: dict[str, str],
    *,
    access_scope: UsageAccessScope,
    group_by: UsageReactGroupBy | None,
) -> UsageFilters:
    start = _parse_datetime(snapshot.get("start"))
    end = _parse_datetime(snapshot.get("end"))
    if start is None or end is None:
        now = datetime.now(UTC)
        end = end or now
        start = start or end - timedelta(days=DEFAULT_RANGE_DAYS)
    tenant_id = _query_tenant(snapshot.get("tenant_id"))
    if access_scope.scope_type is UsageScopeType.TENANT and tenant_id is None:
        tenant_id = access_scope.tenant_id
    return UsageFilters(
        tenant_id=tenant_id,
        start=start,
        end=end,
        provider_key=snapshot.get("provider_key") or None,
        model_id=snapshot.get("model_id") or None,
        usage_status=_usage_filter_status_text(snapshot.get("usage_status")),
        group_by=_service_group_by(group_by or UsageReactGroupBy.DAY),
    )


def _service_filters(
    filters: UsageFilters,
    group_by: UsageReactGroupBy,
) -> UsageFilters:
    data = filters.model_dump()
    data["group_by"] = _service_group_by(group_by)
    return UsageFilters.model_validate(data)


def _service_group_by(group_by: UsageReactGroupBy) -> UsageGroupBy:
    if group_by in {
        UsageReactGroupBy.DAY,
        UsageReactGroupBy.TENANT,
        UsageReactGroupBy.PROVIDER,
        UsageReactGroupBy.MODEL,
        UsageReactGroupBy.WORKFLOW,
        UsageReactGroupBy.AGENT,
        UsageReactGroupBy.SUB_AGENT,
        UsageReactGroupBy.PROMPT,
        UsageReactGroupBy.EXECUTION_MODE,
        UsageReactGroupBy.PRINCIPAL,
    }:
        return cast(UsageGroupBy, group_by.value)
    return "day"


def _query_tenant(raw: str | None) -> UUID | None:
    if not raw:
        return None
    try:
        return UUID(raw)
    except ValueError:
        return None


def _parse_datetime(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed


def _usage_filter_status(
    status: UsageReactConfidenceStatus | None,
) -> UsageEventStatus | None:
    if status is None:
        return None
    return _usage_filter_status_text(status.value)


def _usage_filter_status_text(raw: str | None) -> UsageEventStatus | None:
    if raw == UsageReactConfidenceStatus.CONFIRMED.value:
        return UsageEventStatus.CONFIRMED
    if raw == UsageReactConfidenceStatus.ESTIMATED.value:
        return UsageEventStatus.ESTIMATED
    if raw in {
        UsageReactConfidenceStatus.PARTIAL.value,
        UsageReactConfidenceStatus.RECONCILIATION_PENDING.value,
    }:
        return UsageEventStatus.PARTIAL
    if raw in {
        UsageReactConfidenceStatus.MISSING.value,
        UsageReactConfidenceStatus.UNAVAILABLE.value,
    }:
        return UsageEventStatus.UNAVAILABLE
    return None


def _selected_range(filters: UsageFilters) -> UsageReactRange:
    end = filters.end or datetime.now(UTC)
    start = filters.start or end - timedelta(days=DEFAULT_RANGE_DAYS)
    label = (
        "Last 30 days"
        if end - start <= timedelta(days=DEFAULT_RANGE_DAYS, minutes=1)
        else "Custom range"
    )
    return UsageReactRange(label=label, start=start, end=end)


def _filter_metadata(
    *,
    scope: ReactAdminScope,
    access_scope: UsageAccessScope,
    query: UsageReactDashboardQuery,
    events: list[LlmUsageEvent],
    tenant_labels: dict[UUID, str],
    selected_range: UsageReactRange,
) -> UsageReactFilterMetadata:
    tenant_options: list[UsageReactFilterOption] = []
    active_tenants = {scope.tenant_id} if scope.tenant_id else set()
    visible_tenants = sorted(
        {event.tenant_id for event in events} | active_tenants,
        key=lambda value: _tenant_label(value, tenant_labels),
    )
    for tenant_id in visible_tenants:
        tenant_options.append(
            _option(
                str(tenant_id),
                _tenant_label(tenant_id, tenant_labels),
                selected=query.tenant_id == str(tenant_id)
                or (
                    access_scope.scope_type is UsageScopeType.TENANT
                    and access_scope.tenant_id == tenant_id
                ),
            )
        )
    providers = sorted({event.provider_key for event in events})
    models = sorted({event.model_id for event in events})
    workflows = sorted({_workflow_label(event) for event in events})
    agents = sorted(
        value
        for value in {_safe_optional(event.agent_key) for event in events}
        if value
    )
    prompts = sorted({_prompt_label(event) for event in events})
    return UsageReactFilterMetadata(
        selected_range=selected_range,
        range_options=(
            _option("30d", "Last 30 days", selected=True),
            _option("7d", "Last 7 days"),
            _option("24h", "Last 24 hours"),
        ),
        selected_group_by=query.group_by,
        group_by_options=tuple(
            _option(group.value, _group_label(group), selected=group is query.group_by)
            for group in UsageReactGroupBy
            if access_scope.scope_type is UsageScopeType.PLATFORM
            or group is not UsageReactGroupBy.TENANT
        ),
        tenant_options=tuple(tenant_options),
        provider_options=tuple(
            _option(provider, provider, selected=query.provider_key == provider)
            for provider in providers
        ),
        model_options=tuple(
            _option(model, model, selected=query.model_id == model) for model in models
        ),
        workflow_options=tuple(_option(value, value) for value in workflows if value),
        agent_options=tuple(_option(value, value) for value in agents if value),
        prompt_options=tuple(_option(value, value) for value in prompts if value),
        confidence_options=tuple(
            _option(
                status.value,
                _status_label(status.value),
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
    totals: Any,
    events: list[LlmUsageEvent],
) -> tuple[UsageReactSummaryCard, ...]:
    average_latency = (
        int(sum(event.latency_ms for event in events) / len(events)) if events else 0
    )
    coverage_status = _confidence(events)
    estimated = sum(
        1
        for event in events
        if _event_confidence(event) is UsageReactConfidenceStatus.ESTIMATED
    )
    confirmed = sum(
        1
        for event in events
        if _event_confidence(event) is UsageReactConfidenceStatus.CONFIRMED
    )
    unavailable = sum(
        1
        for event in events
        if _event_confidence(event) is UsageReactConfidenceStatus.UNAVAILABLE
    )
    return (
        _card(
            "tokens",
            "Total tokens",
            f"{totals.total_tokens:,}",
            "tokens",
            coverage_status,
            "Live token counts for the selected scope and range.",
        ),
        _card(
            "cost",
            "Estimated cost",
            _money(totals.estimated_cost_micros),
            totals.currency,
            _cost_confidence(events),
            "Cost is shown only from persisted pricing and usage evidence.",
        ),
        _card(
            "events",
            "Usage events",
            str(totals.total_events),
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
            str(totals.unavailable_event_count or unavailable),
            "events",
            UsageReactConfidenceStatus.UNAVAILABLE
            if totals.unavailable_event_count
            else coverage_status,
            "Provider usage that could not be confirmed remains visible safely.",
            tone=UsageReactTone.WARNING
            if totals.unavailable_event_count
            else UsageReactTone.SUCCESS,
        ),
        _card(
            "coverage",
            "Confidence coverage",
            f"{confirmed} confirmed, {estimated} estimated",
            "events",
            coverage_status,
            "Confirmed, estimated, partial, missing, and unavailable states "
            "stay separate.",
        ),
    )


def _trend_points(
    events: list[LlmUsageEvent],
    selected_range: UsageReactRange,
) -> tuple[UsageReactTrendPoint, ...]:
    start = selected_range.start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = selected_range.end
    bucket_count = max(1, min(31, (end.date() - start.date()).days + 1))
    buckets: dict[datetime, list[LlmUsageEvent]] = defaultdict(list)
    for event in events:
        bucket = event.recorded_at.replace(hour=0, minute=0, second=0, microsecond=0)
        buckets[bucket].append(event)
    points: list[UsageReactTrendPoint] = []
    for index in range(bucket_count):
        bucket_start = start + timedelta(days=index)
        bucket_events = buckets.get(bucket_start, [])
        confirmed_tokens = sum(
            event.total_tokens or 0
            for event in bucket_events
            if _event_confidence(event) is UsageReactConfidenceStatus.CONFIRMED
        )
        estimated_tokens = sum(
            event.total_tokens or 0
            for event in bucket_events
            if _event_confidence(event)
            in {
                UsageReactConfidenceStatus.ESTIMATED,
                UsageReactConfidenceStatus.PARTIAL,
                UsageReactConfidenceStatus.RECONCILIATION_PENDING,
            }
        )
        unavailable_events = sum(
            1
            for event in bucket_events
            if _event_confidence(event)
            in {
                UsageReactConfidenceStatus.MISSING,
                UsageReactConfidenceStatus.UNAVAILABLE,
            }
        )
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
                    sum(event.estimated_cost_micros or 0 for event in bucket_events)
                ),
                estimated_cost_micros=sum(
                    event.estimated_cost_micros or 0 for event in bucket_events
                ),
                currency=_currency(bucket_events),
                average_latency_ms=average_latency,
                event_count=len(bucket_events),
                confidence_status=_confidence(bucket_events),
            )
        )
    return tuple(points)


def _rollup_section(
    group_by: UsageReactGroupBy,
    events: list[LlmUsageEvent],
    tenant_labels: dict[UUID, str],
) -> UsageReactRollupSection:
    grouped: dict[str, list[LlmUsageEvent]] = defaultdict(list)
    for event in events:
        grouped[_rollup_key(event, group_by, tenant_labels)].append(event)
    rows = [
        _rollup_row(group_by, key, bucket)
        for key, bucket in sorted(
            grouped.items(),
            key=lambda item: sum(event.total_tokens or 0 for event in item[1]),
            reverse=True,
        )
    ]
    return UsageReactRollupSection(
        group_by=group_by,
        rows=tuple(rows[:ROLLUP_LIMIT]),
        limit=ROLLUP_LIMIT,
        total_rows=len(rows),
    )


def _rollup_row(
    group_by: UsageReactGroupBy,
    key: str,
    events: list[LlmUsageEvent],
) -> UsageReactRollupRow:
    average_latency = int(sum(event.latency_ms for event in events) / len(events))
    first = events[0]
    return UsageReactRollupRow(
        row_id=f"{group_by.value}:{key}",
        group_by=group_by,
        safe_label=key,
        safe_summary=_rollup_summary(group_by, first),
        event_count=len(events),
        total_tokens=sum(event.total_tokens or 0 for event in events),
        input_tokens=sum(event.input_tokens or 0 for event in events),
        output_tokens=sum(event.output_tokens or 0 for event in events),
        estimated_cost_display=_money(
            sum(event.estimated_cost_micros or 0 for event in events)
        ),
        estimated_cost_micros=sum(event.estimated_cost_micros or 0 for event in events),
        currency=_currency(events),
        average_latency_ms=average_latency,
        unavailable_event_count=sum(
            1
            for event in events
            if _event_confidence(event)
            in {
                UsageReactConfidenceStatus.MISSING,
                UsageReactConfidenceStatus.UNAVAILABLE,
            }
        ),
        confidence_status=_confidence(events),
        attempt_summary=_physical_attempt_label(first)
        if group_by
        in {UsageReactGroupBy.GATEWAY_OPERATION, UsageReactGroupBy.PHYSICAL_ATTEMPT}
        else None,
        tool_summary=_tool_label(first)
        if group_by is UsageReactGroupBy.GOVERNED_TOOL
        else None,
        drilldown_href=(
            "/admin/app/usage/events.json?"
            + urlencode({"group_by": group_by.value, "rollup_key": key})
        ),
    )


def _drilldown(
    events: list[LlmUsageEvent],
    *,
    total_rows: int,
    tenant_labels: dict[UUID, str],
) -> UsageReactEventDrilldown:
    return UsageReactEventDrilldown(
        rows=tuple(_event_row(event, tenant_labels) for event in events),
        limit=DRILLDOWN_LIMIT,
        total_rows=total_rows,
        truncated=total_rows > DRILLDOWN_LIMIT,
    )


def _event_row(
    event: LlmUsageEvent,
    tenant_labels: dict[UUID, str],
) -> UsageReactEventRow:
    return UsageReactEventRow(
        event_id=event.llm_usage_event_id,
        recorded_at=event.recorded_at,
        tenant_label=_tenant_label(event.tenant_id, tenant_labels),
        provider_label=_safe_label(event.provider_key, fallback="Provider unavailable"),
        model_label=_safe_label(event.model_id, fallback="Model unavailable"),
        workflow_label=_workflow_label(event),
        agent_label=_safe_optional(event.agent_key),
        prompt_label=_prompt_label(event),
        graph_node_label=_graph_node_label(event),
        gateway_operation_label=_gateway_operation_label(event),
        physical_attempt_label=_physical_attempt_label(event),
        tool_label=_tool_label(event),
        total_tokens=event.total_tokens or 0,
        input_tokens=event.input_tokens or 0,
        output_tokens=event.output_tokens or 0,
        estimated_cost_display=_cost_display(event),
        latency_ms=event.latency_ms,
        usage_status=_event_confidence(event),
        cost_status=_cost_confidence([event]),
        safe_attribution_summary=_safe_attribution_summary(event),
        audit_reference=f"usage-event:{event.llm_usage_event_id}",
        trace_reference=_safe_optional(event.trace_id),
    )


def _rollup_key(
    event: LlmUsageEvent,
    group_by: UsageReactGroupBy,
    tenant_labels: dict[UUID, str],
) -> str:
    if group_by is UsageReactGroupBy.DAY:
        return event.recorded_at.strftime("%Y-%m-%d")
    if group_by is UsageReactGroupBy.TENANT:
        return _tenant_label(event.tenant_id, tenant_labels)
    if group_by is UsageReactGroupBy.PROVIDER:
        return _safe_label(event.provider_key, fallback="Provider unavailable")
    if group_by is UsageReactGroupBy.MODEL:
        return _safe_label(event.model_id, fallback="Model unavailable")
    if group_by is UsageReactGroupBy.WORKFLOW:
        return _workflow_label(event)
    if group_by is UsageReactGroupBy.AGENT:
        return _safe_optional(event.agent_key) or "Agent unavailable"
    if group_by is UsageReactGroupBy.SUB_AGENT:
        return _safe_optional(event.sub_agent_key) or "Sub-agent unavailable"
    if group_by is UsageReactGroupBy.PROMPT:
        return _prompt_label(event)
    if group_by is UsageReactGroupBy.EXECUTION_MODE:
        return _safe_label(event.execution_mode, fallback="Mode unavailable")
    if group_by is UsageReactGroupBy.PRINCIPAL:
        return _safe_optional(event.principal_id) or "System"
    if group_by is UsageReactGroupBy.GRAPH_NODE:
        return _graph_node_label(event) or "Graph node unavailable"
    if group_by is UsageReactGroupBy.GATEWAY_OPERATION:
        return _gateway_operation_label(event) or "Gateway operation unavailable"
    if group_by is UsageReactGroupBy.PHYSICAL_ATTEMPT:
        return _physical_attempt_label(event) or "Provider attempt unavailable"
    if group_by is UsageReactGroupBy.GOVERNED_TOOL:
        return _tool_label(event) or "Governed tool unavailable"
    return "All usage"


def _workflow_label(event: LlmUsageEvent) -> str:
    from_attr = _safe_attr(event, "workflow_label", "workflow", "workflow_name")
    if from_attr:
        return from_attr
    if event.workflow_lineage_id:
        return f"Workflow {str(event.workflow_lineage_id)[:8]}"
    if event.workflow_run_id:
        return f"Run {str(event.workflow_run_id)[:8]}"
    return "Workflow unavailable"


def _prompt_label(event: LlmUsageEvent) -> str:
    from_attr = _safe_attr(event, "prompt_label", "prompt_version_label")
    if from_attr:
        return from_attr
    if event.prompt_version_id:
        return f"Prompt {str(event.prompt_version_id)[:8]}"
    return "Prompt unavailable"


def _graph_node_label(event: LlmUsageEvent) -> str | None:
    return _safe_attr(event, "graph_node_label", "graph_node", "node")


def _gateway_operation_label(event: LlmUsageEvent) -> str | None:
    return _safe_optional(event.operation_identity) or _safe_attr(
        event,
        "gateway_operation_label",
        "gateway_operation",
        "operation",
    )


def _physical_attempt_label(event: LlmUsageEvent) -> str | None:
    if event.source_gateway_attempt_id:
        return f"Gateway attempt {str(event.source_gateway_attempt_id)[:8]}"
    return _safe_attr(event, "physical_attempt_label", "physical_attempt")


def _tool_label(event: LlmUsageEvent) -> str | None:
    return _safe_attr(event, "governed_tool_label", "governed_tool", "tool_label")


def _safe_attr(event: LlmUsageEvent, *keys: str) -> str | None:
    current: Any = event.safe_attribution or {}
    if not isinstance(current, dict):
        return None
    for key in keys:
        value = current.get(key)
        if isinstance(value, str):
            return _safe_optional(value)
    runtime = current.get("runtime")
    if isinstance(runtime, dict):
        for key in keys:
            value = runtime.get(key)
            if isinstance(value, str):
                return _safe_optional(value)
    return None


def _safe_attribution_summary(event: LlmUsageEvent) -> str:
    value = _safe_attr(event, "summary", "safe_summary")
    if value:
        return value
    parts = [
        _workflow_label(event),
        _safe_optional(event.agent_key),
        _gateway_operation_label(event),
        _tool_label(event),
    ]
    return " / ".join(part for part in parts if part) or "Safe attribution unavailable."


def _event_confidence(event: LlmUsageEvent) -> UsageReactConfidenceStatus:
    if event.usage_status is UsageEventStatus.CONFIRMED:
        return UsageReactConfidenceStatus.CONFIRMED
    if event.usage_status is UsageEventStatus.ESTIMATED:
        return UsageReactConfidenceStatus.ESTIMATED
    if event.usage_status is UsageEventStatus.PARTIAL:
        return UsageReactConfidenceStatus.RECONCILIATION_PENDING
    if event.usage_status is UsageEventStatus.MALFORMED:
        return UsageReactConfidenceStatus.MISSING
    return UsageReactConfidenceStatus.UNAVAILABLE


def _cost_confidence(events: list[LlmUsageEvent]) -> UsageReactConfidenceStatus:
    if not events:
        return UsageReactConfidenceStatus.UNAVAILABLE
    statuses = {_cost_status(event) for event in events}
    if statuses == {UsageReactConfidenceStatus.CONFIRMED}:
        return UsageReactConfidenceStatus.CONFIRMED
    if UsageReactConfidenceStatus.MISSING in statuses:
        return UsageReactConfidenceStatus.MISSING
    if UsageReactConfidenceStatus.UNAVAILABLE in statuses:
        return UsageReactConfidenceStatus.UNAVAILABLE
    if UsageReactConfidenceStatus.RECONCILIATION_PENDING in statuses:
        return UsageReactConfidenceStatus.RECONCILIATION_PENDING
    if UsageReactConfidenceStatus.ESTIMATED in statuses:
        return UsageReactConfidenceStatus.ESTIMATED
    return UsageReactConfidenceStatus.PARTIAL


def _cost_status(event: LlmUsageEvent) -> UsageReactConfidenceStatus:
    if event.pricing_version_id is None and event.estimated_cost_micros is None:
        return UsageReactConfidenceStatus.MISSING
    if event.cost_status is UsageValueStatus.CONFIRMED:
        return UsageReactConfidenceStatus.CONFIRMED
    if event.cost_status is UsageValueStatus.ESTIMATED:
        return UsageReactConfidenceStatus.ESTIMATED
    if event.cost_status is UsageValueStatus.NOT_APPLICABLE:
        return UsageReactConfidenceStatus.UNAVAILABLE
    return UsageReactConfidenceStatus.UNAVAILABLE


def _confidence(events: list[LlmUsageEvent]) -> UsageReactConfidenceStatus:
    if not events:
        return UsageReactConfidenceStatus.UNAVAILABLE
    statuses = {_event_confidence(event) for event in events}
    if statuses == {UsageReactConfidenceStatus.CONFIRMED}:
        return UsageReactConfidenceStatus.CONFIRMED
    if UsageReactConfidenceStatus.UNAVAILABLE in statuses:
        return UsageReactConfidenceStatus.UNAVAILABLE
    if UsageReactConfidenceStatus.MISSING in statuses:
        return UsageReactConfidenceStatus.MISSING
    if UsageReactConfidenceStatus.RECONCILIATION_PENDING in statuses:
        return UsageReactConfidenceStatus.RECONCILIATION_PENDING
    if UsageReactConfidenceStatus.ESTIMATED in statuses:
        return UsageReactConfidenceStatus.ESTIMATED
    return UsageReactConfidenceStatus.PARTIAL


def _cost_display(event: LlmUsageEvent) -> str:
    if _cost_status(event) is UsageReactConfidenceStatus.MISSING:
        return "Missing pricing"
    return _money(event.estimated_cost_micros or 0)


def _states(
    access_scope: UsageAccessScope,
    events: list[LlmUsageEvent],
    exports: list[UsageExportRequest],
) -> tuple[UsageReactProblem, ...]:
    states: list[UsageReactProblem] = []
    if not events:
        states.append(
            UsageReactProblem(
                reason=UsageReactProblemReason.EMPTY,
                title="No usage events",
                detail="No live usage events match the selected filters.",
                next_action="Adjust the range or wait for usage capture.",
            )
        )
    if any(
        _event_confidence(event) is UsageReactConfidenceStatus.RECONCILIATION_PENDING
        for event in events
    ):
        states.append(
            UsageReactProblem(
                reason=UsageReactProblemReason.PARTIAL,
                title="Reconciliation pending",
                detail=(
                    "Some usage values are partial or pending provider reconciliation."
                ),
                next_action="Review confidence labels before exporting.",
            )
        )
    if any(
        _cost_status(event) is UsageReactConfidenceStatus.MISSING for event in events
    ):
        states.append(
            UsageReactProblem(
                reason=UsageReactProblemReason.STALE_PRICING,
                title="Missing pricing",
                detail="Some usage events do not have persisted pricing metadata.",
                next_action="Review pricing setup before using cost estimates.",
            )
        )
    if any(export.status is UsageExportStatus.PENDING for export in exports):
        states.append(
            UsageReactProblem(
                reason=UsageReactProblemReason.EXPORT_PENDING,
                title="Export queued",
                detail="At least one export request is still queued.",
                next_action="Refresh the export detail later.",
            )
        )
    if access_scope.scope_type is UsageScopeType.TENANT:
        states.append(
            UsageReactProblem(
                reason=UsageReactProblemReason.DENIED,
                title="Tenant scope enforced",
                detail="This view is limited to the active tenant.",
                next_action="Ask a platform administrator for cross-tenant analysis.",
                audit_reference=f"usage-scope:{access_scope.tenant_id}",
            )
        )
    return tuple(states)


def _common_states(events: list[LlmUsageEvent]) -> tuple[ReactAdminShellState, ...]:
    return (
        ReactAdminShellState(
            state=ReactAdminShellStateKind.PARTIAL_DATA
            if events
            else ReactAdminShellStateKind.EMPTY,
            title="Usage analytics ready" if events else "No usage events",
            summary=(
                "Summary, trend, rollups, drilldown, and export evidence are "
                "live and bounded."
                if events
                else "No live usage events match the active filters."
            ),
            action=ReactAdminPageAction(
                action_id="usage-refresh",
                label="Refresh usage",
                href="/admin/app/usage/bootstrap.json",
                variant=ReactAdminPageActionVariant.SECONDARY,
            ),
        ),
    )


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
        comparison="Selected range",
        detail=detail,
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


def _export_summary(export: UsageExportRequest) -> UsageReactExportSummary:
    status = _export_status(export.status)
    return UsageReactExportSummary(
        usage_export_request_id=export.usage_export_request_id,
        status=status,
        scope_label=(
            "Platform"
            if export.scope_type is UsageScopeType.PLATFORM and export.tenant_id is None
            else f"Tenant {str(export.tenant_id)[:8]}"
            if export.tenant_id is not None
            else "Active scope"
        ),
        requested_by_label=_safe_label(
            export.requested_by_principal_id,
            fallback="Requester unavailable",
        ),
        filter_snapshot={key: str(value) for key, value in export.filters.items()},
        row_count=export.row_count,
        artifact_reference=(
            f"usage-export:{export.usage_export_request_id}"
            if export.artifact_uri
            else None
        ),
        artifact_size_label=_size_label(export.artifact_size_bytes),
        checksum_prefix=(
            f"sha256:{export.artifact_sha256[:12]}" if export.artifact_sha256 else None
        ),
        created_at=export.created_at,
        completed_at=export.completed_at,
        expires_at=export.expires_at,
        audit_reference=f"usage-export:{export.usage_export_request_id}:{status.value}",
        denial_reason=_safe_optional(export.denial_reason),
        failure_reason=_safe_optional(export.failure_reason),
        next_step=_export_next_step(status),
    )


def _synthetic_export_summary(
    *,
    access_scope: UsageAccessScope,
    filters: UsageFilters,
    status: UsageReactExportStatus,
    reason: str,
) -> UsageReactExportSummary:
    now = datetime.now(UTC)
    synthetic_id = UUID("00000000-0000-0000-0000-000000000000")
    return UsageReactExportSummary(
        usage_export_request_id=synthetic_id,
        status=status,
        scope_label="Platform"
        if access_scope.scope_type is UsageScopeType.PLATFORM
        else f"Tenant {str(access_scope.tenant_id)[:8]}",
        requested_by_label=_safe_label(
            access_scope.principal_id,
            fallback="Requester unavailable",
        ),
        filter_snapshot=filters.safe_snapshot(),
        row_count=0,
        created_at=now,
        audit_reference=f"usage-export:{status.value}",
        denial_reason=reason if status is UsageReactExportStatus.DENIED else None,
        failure_reason=reason if status is not UsageReactExportStatus.DENIED else None,
        next_step=_export_next_step(status),
    )


async def _latest_export(
    repository: UsageRepository,
    access_scope: UsageAccessScope,
    filters: UsageFilters,
) -> UsageExportRequest | None:
    exports = await repository.list_export_requests(
        access_scope=access_scope,
        filters=filters,
        limit=1,
    )
    return exports[0] if exports else None


def _export_status(status: UsageExportStatus) -> UsageReactExportStatus:
    if status is UsageExportStatus.PENDING:
        return UsageReactExportStatus.QUEUED
    if status is UsageExportStatus.COMPLETED:
        return UsageReactExportStatus.COMPLETED
    if status is UsageExportStatus.FAILED:
        return UsageReactExportStatus.FAILED
    if status is UsageExportStatus.DENIED:
        return UsageReactExportStatus.DENIED
    return UsageReactExportStatus.UNAVAILABLE


def _export_next_step(status: UsageReactExportStatus) -> str:
    if status is UsageReactExportStatus.COMPLETED:
        return "Use the persisted artifact reference from governed storage."
    if status is UsageReactExportStatus.DENIED:
        return "Review the safe denial and adjust tenant scope."
    if status in {UsageReactExportStatus.QUEUED, UsageReactExportStatus.PENDING}:
        return "Refresh later for completion evidence."
    if status is UsageReactExportStatus.VALIDATION:
        return "Correct the export filters and retry."
    if status is UsageReactExportStatus.CONFLICT:
        return "Refresh the export request and retry if still needed."
    return "Review dependency health before retrying the export."


def _group_label(group: UsageReactGroupBy) -> str:
    return group.value.replace("_", " ").title()


def _status_label(value: str) -> str:
    return value.replace("_", " ").title()


def _tenant_label(tenant_id: UUID, tenant_labels: dict[UUID, str]) -> str:
    return _safe_label(
        tenant_labels.get(tenant_id) or f"Tenant {str(tenant_id)[:8]}",
        fallback="Tenant unavailable",
    )


def _rollup_summary(group_by: UsageReactGroupBy, event: LlmUsageEvent) -> str:
    if group_by is UsageReactGroupBy.TENANT:
        return "Grouped by authorized tenant."
    if group_by is UsageReactGroupBy.WORKFLOW:
        return "Grouped by safe workflow or run reference."
    if group_by is UsageReactGroupBy.PROMPT:
        return "Grouped by safe prompt version reference."
    if group_by is UsageReactGroupBy.GATEWAY_OPERATION:
        return "Grouped by provider gateway operation evidence."
    if group_by is UsageReactGroupBy.PHYSICAL_ATTEMPT:
        return "Grouped by provider attempt evidence."
    if group_by is UsageReactGroupBy.GOVERNED_TOOL:
        return "Grouped by governed tool attribution."
    if group_by is UsageReactGroupBy.PRINCIPAL and event.principal_id is None:
        return "Grouped by system usage."
    return f"Grouped by {_group_label(group_by).lower()}."


def _safe_optional(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        return safe_usage_text(str(value), max_length=160)
    except ValueError:
        return None


def _safe_label(value: str, *, fallback: str) -> str:
    try:
        return safe_usage_text(value, max_length=160)
    except ValueError:
        return fallback


def _money(micros: int | None) -> str:
    if not micros:
        return "$0.0000"
    return f"${micros / 1_000_000:.4f}"


def _currency(events: list[LlmUsageEvent]) -> str:
    for event in events:
        if event.currency:
            return event.currency
    return "USD"


def _size_label(size_bytes: int | None) -> str | None:
    if size_bytes is None:
        return None
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"
