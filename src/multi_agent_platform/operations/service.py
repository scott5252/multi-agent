from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Select, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.audit.models import AuthorizationOutcome, InspectionAction
from multi_agent_platform.bootstrap.container import Container
from multi_agent_platform.config.settings import AppEnvironment
from multi_agent_platform.db.models.audit_debugging import (
    AuditRuntimeTraceRecord,
    AuditTimelineEventRecord,
)
from multi_agent_platform.db.models.model_providers import GatewayInvocationAttempt
from multi_agent_platform.db.repositories.audit_debugging import (
    AuditDebuggingRepository,
)
from multi_agent_platform.db.repositories.model_providers import ModelProviderRepository
from multi_agent_platform.db.repositories.reliability import ReliabilityRepository
from multi_agent_platform.db.repositories.usage import UsageRepository
from multi_agent_platform.operations.export import store_operations_csv_export
from multi_agent_platform.operations.models import (
    OperationalLogEvent,
    OperationsAccessScope,
    OperationsAuthorizationError,
    OperationsCapacitySummary,
    OperationsDashboardSnapshot,
    OperationsDependencyView,
    OperationsExportResult,
    OperationsLink,
    OperationsLogFilters,
    OperationsProviderSummary,
    OperationsStatusCard,
    OperationsUsageSummary,
)
from multi_agent_platform.operations.redaction import (
    redaction_notice,
    sanitize_operations_metadata,
    sanitize_operations_text,
)
from multi_agent_platform.runtime.health.models import DependencyStatus
from multi_agent_platform.runtime.health.service import HealthService
from multi_agent_platform.storage.base import StorageProvider
from multi_agent_platform.usage.models import (
    UsageAccessScope,
    UsageFilters,
    UsageScopeType,
)
from multi_agent_platform.usage.service import UsageAnalyticsService


class OperationsConsoleService:
    def __init__(self, *, session: AsyncSession, container: Container) -> None:
        self.session = session
        self.container = container

    async def dashboard(
        self,
        *,
        access_scope: OperationsAccessScope,
        filters: OperationsLogFilters,
    ) -> OperationsDashboardSnapshot:
        dependencies = await self._dependency_views()
        capacity = await self._capacity_summary()
        providers = await self._provider_summaries()
        usage = await self._usage_summary(access_scope=access_scope, filters=filters)
        logs = await self.query_logs(access_scope=access_scope, filters=filters)
        cards = self._status_cards(
            dependencies=dependencies,
            capacity=capacity,
            providers=providers,
            usage=usage,
            logs=logs,
        )
        health_status = "ready"
        if any(
            item.status == DependencyStatus.UNAVAILABLE.value and item.required
            for item in dependencies
        ):
            health_status = "not_ready"
        elif any(
            item.status == DependencyStatus.DEGRADED.value for item in dependencies
        ):
            health_status = "degraded"
        return OperationsDashboardSnapshot(
            health_status=health_status,
            status_cards=cards,
            dependencies=dependencies,
            capacity=capacity,
            providers=providers,
            usage=usage,
            logs=logs,
            filters=filters,
            redaction_notice=redaction_notice(),
        )

    async def query_logs(
        self,
        *,
        access_scope: OperationsAccessScope,
        filters: OperationsLogFilters,
    ) -> tuple[OperationalLogEvent, ...]:
        _ = access_scope
        events: list[OperationalLogEvent] = []
        events.extend(await self._timeline_log_events(filters))
        events.extend(await self._runtime_trace_log_events(filters))
        events.extend(await self._gateway_log_events(filters))
        matching = [event for event in events if _matches_filters(event, filters)]
        matching.sort(key=lambda event: event.occurred_at, reverse=True)
        return tuple(matching[: filters.limit])

    async def export_logs(
        self,
        *,
        access_scope: OperationsAccessScope,
        filters: OperationsLogFilters,
        storage_provider: StorageProvider,
    ) -> OperationsExportResult:
        export_id = uuid4()
        audit_repository = AuditDebuggingRepository(self.session)
        if not access_scope.can_export:
            audit = await audit_repository.create_inspection_access_event(
                tenant_id=filters.tenant_id,
                actor_principal_id=access_scope.principal_id,
                actor_role=access_scope.role.value,
                action=InspectionAction.EXPORT_CREATE.value,
                authorization_outcome=AuthorizationOutcome.DENIED.value,
                denial_category="operations_export_permission",
                filters=dict[str, object](filters.safe_snapshot()),
                export_id=export_id,
                trace_id=access_scope.trace_id,
                safe_metadata={"surface": "operations_console"},
            )
            raise OperationsAuthorizationError(
                f"operations export denied: {audit.denial_category}"
            )
        events = list(await self.query_logs(access_scope=access_scope, filters=filters))
        artifact_uri, checksum, size_bytes = await store_operations_csv_export(
            storage_provider=storage_provider,
            export_id=export_id,
            principal_id=access_scope.principal_id,
            events=events,
        )
        audit = await audit_repository.create_inspection_access_event(
            tenant_id=filters.tenant_id,
            actor_principal_id=access_scope.principal_id,
            actor_role=access_scope.role.value,
            action=InspectionAction.EXPORT_CREATE.value,
            authorization_outcome=AuthorizationOutcome.ALLOWED.value,
            filters=dict[str, object](filters.safe_snapshot()),
            export_id=export_id,
            trace_id=access_scope.trace_id,
            safe_metadata={
                "surface": "operations_console",
                "row_count": len(events),
                "artifact_size_bytes": size_bytes,
            },
        )
        return OperationsExportResult(
            export_id=export_id,
            artifact_uri=artifact_uri,
            artifact_sha256=checksum,
            artifact_size_bytes=size_bytes,
            row_count=len(events),
            filters=filters.safe_snapshot(),
            requested_by=access_scope.principal_id,
            audit_event_id=audit.inspection_access_audit_event_id,
        )

    async def _dependency_views(self) -> tuple[OperationsDependencyView, ...]:
        try:
            report = await HealthService(self.container).dependency_status()
        except Exception as exc:
            return (
                OperationsDependencyView(
                    name="health",
                    required=True,
                    status=DependencyStatus.UNAVAILABLE.value,
                    detail=sanitize_operations_text(exc.__class__.__name__),
                ),
            )
        return tuple(
            OperationsDependencyView(
                name=check.name,
                required=check.required,
                status=check.status.value,
                detail=sanitize_operations_text(check.detail, fallback="")
                if check.detail
                else None,
                checked_at=check.checked_at,
            )
            for check in report.dependencies
        )

    async def _capacity_summary(self) -> OperationsCapacitySummary:
        try:
            snapshot = await ReliabilityRepository(
                self.session
            ).latest_capacity_snapshot(tenant_id=None)
        except SQLAlchemyError:
            snapshot = None
        if snapshot is None:
            return OperationsCapacitySummary()
        return OperationsCapacitySummary(
            runnable_depth=snapshot.runnable_depth,
            delayed_depth=snapshot.delayed_depth,
            active_leases=snapshot.active_leases,
            retry_backlog=snapshot.retry_backlog,
            compensation_backlog=snapshot.compensation_backlog,
            dead_letter_count=snapshot.dead_letter_count,
            db_pool_wait_p95_ms=snapshot.db_pool_wait_p95_ms,
            db_pool_in_use=snapshot.db_pool_in_use,
            db_pool_available=snapshot.db_pool_available,
            artifact_inflight=snapshot.artifact_inflight,
            artifact_wait_p95_ms=snapshot.artifact_wait_p95_ms,
            open_breaker_count=snapshot.open_breaker_count,
            fairness_debt_total=float(snapshot.fairness_debt_total),
            recorded_at=snapshot.created_at,
        )

    async def _provider_summaries(self) -> tuple[OperationsProviderSummary, ...]:
        try:
            summaries = await ModelProviderRepository(self.session).list_connections(
                tenant_id=None,
                platform_scope=True,
            )
        except SQLAlchemyError:
            return ()
        return tuple(
            OperationsProviderSummary(
                provider_connection_id=item.provider_connection_id,
                display_name=sanitize_operations_text(item.display_name),
                provider_type=item.provider_type.value,
                active=item.active,
                health_state=item.health_state.value,
                model_count=item.model_count,
                last_test_outcome=item.last_test_outcome.value
                if item.last_test_outcome
                else None,
                href=f"/admin/model-providers/{item.provider_connection_id}",
            )
            for item in summaries
        )

    async def _usage_summary(
        self,
        *,
        access_scope: OperationsAccessScope,
        filters: OperationsLogFilters,
    ) -> OperationsUsageSummary:
        usage_scope = UsageAccessScope(
            scope_type=UsageScopeType.PLATFORM,
            principal_id=access_scope.principal_id,
            platform_admin=True,
        )
        usage_filters = UsageFilters(
            tenant_id=filters.tenant_id,
            start=filters.start,
            end=filters.end,
        )
        try:
            summary = await UsageAnalyticsService(
                UsageRepository(self.session)
            ).summarize_usage(
                access_scope=usage_scope,
                filters=usage_filters,
                limit=500,
            )
        except (SQLAlchemyError, ValueError):
            return OperationsUsageSummary(usage_status="unavailable")
        latencies = await self._gateway_latencies(filters)
        model_latency = _p95(latencies)
        return OperationsUsageSummary(
            total_events=summary.totals.total_events,
            total_tokens=summary.totals.total_tokens,
            estimated_cost_micros=summary.totals.estimated_cost_micros,
            model_latency_ms=model_latency,
            token_throughput=summary.totals.total_tokens,
            usage_status="available",
        )

    async def _gateway_latencies(self, filters: OperationsLogFilters) -> list[int]:
        stmt = select(GatewayInvocationAttempt.latency_ms)
        stmt = _apply_common_gateway_filters(stmt, filters)
        stmt = stmt.order_by(GatewayInvocationAttempt.completed_at.desc()).limit(
            filters.candidate_limit()
        )
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError:
            return []
        return [int(value) for value in result.scalars() if value is not None]

    def _status_cards(
        self,
        *,
        dependencies: tuple[OperationsDependencyView, ...],
        capacity: OperationsCapacitySummary,
        providers: tuple[OperationsProviderSummary, ...],
        usage: OperationsUsageSummary,
        logs: tuple[OperationalLogEvent, ...],
    ) -> tuple[OperationsStatusCard, ...]:
        dependency_failures = sum(
            1
            for item in dependencies
            if item.required and item.status == DependencyStatus.UNAVAILABLE.value
        )
        provider_counts = Counter(item.health_state for item in providers)
        error_count = sum(
            1
            for event in logs
            if event.status in {"failure", "failed", "unavailable", "not_ready"}
            or event.severity in {"security_governance", "runtime_required"}
        )
        error_rate = 0 if not logs else round((error_count / len(logs)) * 100, 2)
        request_latency = _p95(
            [event.latency_ms for event in logs if event.latency_ms is not None]
        )
        telegram_ready = _telegram_ready(self.container)
        return (
            OperationsStatusCard(
                label="System Health",
                value="ready" if dependency_failures == 0 else "not ready",
                status="ready" if dependency_failures == 0 else "unavailable",
                summary=f"{len(dependencies)} dependency checks evaluated.",
                href="/dependencies",
            ),
            OperationsStatusCard(
                label="Worker Capacity",
                value=str(capacity.active_leases),
                status="available",
                summary=(
                    f"{capacity.runnable_depth} runnable, "
                    f"{capacity.delayed_depth} delayed."
                ),
                href="/admin/reliability/ui/",
            ),
            OperationsStatusCard(
                label="DB Pool Pressure",
                value=f"{capacity.db_pool_wait_p95_ms} ms",
                status="degraded"
                if capacity.db_pool_wait_p95_ms
                > self.container.settings.reliability_db_pool_wait_p95_ms_threshold
                else "ready",
                summary=(
                    f"{capacity.db_pool_in_use} in use, "
                    f"{capacity.db_pool_available} available."
                ),
            ),
            OperationsStatusCard(
                label="Object Storage",
                value=self.container.storage_provider.provider_name,
                status="ready",
                summary=(
                    f"{capacity.artifact_inflight} artifact operations in flight."
                ),
            ),
            OperationsStatusCard(
                label="Model Providers",
                value=str(len(providers)),
                status="ready"
                if not providers or provider_counts.get("unavailable", 0) == 0
                else "degraded",
                summary=(
                    f"{provider_counts.get('healthy', 0)} healthy, "
                    f"{provider_counts.get('unavailable', 0)} unavailable."
                ),
                href="/admin/model-providers",
            ),
            OperationsStatusCard(
                label="Telegram And Channels",
                value="ready" if telegram_ready else "not ready",
                status="ready" if telegram_ready else "degraded",
                summary="Channel readiness uses safe configuration references.",
                href="/admin/telegram",
            ),
            OperationsStatusCard(
                label="Reliability State",
                value=str(capacity.open_breaker_count),
                status="ready" if capacity.open_breaker_count == 0 else "degraded",
                summary=(
                    f"{capacity.retry_backlog} retries, "
                    f"{capacity.dead_letter_count} dead letters."
                ),
                href="/admin/reliability/ui/breakers",
            ),
            OperationsStatusCard(
                label="Request Latency",
                value=f"{request_latency} ms",
                status="available",
                summary="p95 over the bounded redacted operational rows.",
            ),
            OperationsStatusCard(
                label="Run Throughput",
                value=str(len(logs)),
                status="available",
                summary="Recent lifecycle and gateway events in the filter window.",
                href="/admin/runs",
            ),
            OperationsStatusCard(
                label="Token Throughput",
                value=str(usage.token_throughput),
                status=usage.usage_status,
                summary=f"{usage.total_events} usage events in the filter window.",
                href="/admin/usage",
            ),
            OperationsStatusCard(
                label="Error Rate",
                value=f"{error_rate}%",
                status="ready" if error_count == 0 else "degraded",
                summary=f"{error_count} error-like events in displayed rows.",
            ),
        )

    async def _timeline_log_events(
        self, filters: OperationsLogFilters
    ) -> list[OperationalLogEvent]:
        stmt = select(AuditTimelineEventRecord)
        stmt = _apply_common_timeline_filters(stmt, filters)
        stmt = stmt.order_by(AuditTimelineEventRecord.occurred_at.desc()).limit(
            filters.candidate_limit()
        )
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError:
            return []
        return [_timeline_to_event(record) for record in result.scalars()]

    async def _runtime_trace_log_events(
        self, filters: OperationsLogFilters
    ) -> list[OperationalLogEvent]:
        stmt = select(AuditRuntimeTraceRecord)
        stmt = _apply_common_trace_filters(stmt, filters)
        stmt = stmt.order_by(AuditRuntimeTraceRecord.occurred_at.desc()).limit(
            filters.candidate_limit()
        )
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError:
            return []
        return [_trace_to_event(record) for record in result.scalars()]

    async def _gateway_log_events(
        self, filters: OperationsLogFilters
    ) -> list[OperationalLogEvent]:
        stmt = select(GatewayInvocationAttempt)
        stmt = _apply_common_gateway_filters(stmt, filters)
        stmt = stmt.order_by(GatewayInvocationAttempt.completed_at.desc()).limit(
            filters.candidate_limit()
        )
        try:
            result = await self.session.execute(stmt)
        except SQLAlchemyError:
            return []
        return [_gateway_to_event(record) for record in result.scalars()]


def _timeline_to_event(record: AuditTimelineEventRecord) -> OperationalLogEvent:
    links = []
    if record.workflow_run_id:
        links.append(
            OperationsLink(
                label="Run",
                href=_run_href(record.workflow_run_id, record.tenant_id),
            )
        )
    return OperationalLogEvent(
        event_id=f"audit:{record.timeline_event_id}",
        source="audit_timeline",
        occurred_at=_ensure_aware(record.occurred_at),
        tenant_id=record.tenant_id,
        trace_id=record.trace_id,
        run_id=record.workflow_run_id,
        component=record.event_category,
        severity=record.criticality,
        status=record.run_status_after,
        dependency=_dependency_from_details(record.safe_details),
        summary=sanitize_operations_text(record.safe_summary),
        details=sanitize_operations_metadata(record.safe_details),
        links=tuple(links),
    )


def _trace_to_event(record: AuditRuntimeTraceRecord) -> OperationalLogEvent:
    links = []
    if record.workflow_run_id:
        links.append(
            OperationsLink(
                label="Run",
                href=_run_href(record.workflow_run_id, record.tenant_id),
            )
        )
    return OperationalLogEvent(
        event_id=f"trace:{record.trace_record_id}",
        source="runtime_trace",
        occurred_at=_ensure_aware(record.occurred_at),
        tenant_id=record.tenant_id,
        trace_id=record.trace_id,
        run_id=record.workflow_run_id,
        component=record.trace_type,
        severity=record.policy_outcome,
        status=record.outcome,
        dependency=record.subject_ref,
        summary=sanitize_operations_text(
            record.subject_ref, fallback=record.trace_type
        ),
        details=sanitize_operations_metadata(record.metadata_json),
        links=tuple(links),
        latency_ms=record.duration_ms,
    )


def _gateway_to_event(record: GatewayInvocationAttempt) -> OperationalLogEvent:
    links = [
        OperationsLink(label="Model Providers", href="/admin/model-providers"),
        OperationsLink(label="Usage", href=_usage_href(record.tenant_id)),
    ]
    if record.workflow_run_id:
        links.append(
            OperationsLink(
                label="Run",
                href=_run_href(record.workflow_run_id, record.tenant_id),
            )
        )
    provider_type = record.provider_type.value
    outcome = record.outcome.value
    reason = record.normalized_error_category.value
    return OperationalLogEvent(
        event_id=f"gateway:{record.gateway_invocation_attempt_id}",
        source="gateway_attempt",
        occurred_at=_ensure_aware(record.completed_at),
        tenant_id=record.tenant_id,
        trace_id=record.trace_id,
        run_id=record.workflow_run_id,
        component="model_provider",
        severity=reason,
        status=outcome,
        dependency=f"{provider_type}:{record.model_id}",
        summary=sanitize_operations_text(
            record.safe_audit_summary.get("summary")
            if record.safe_audit_summary
            else f"{provider_type} {record.model_id} {outcome}",
        ),
        details=sanitize_operations_metadata(record.safe_audit_summary),
        links=tuple(links),
        latency_ms=record.latency_ms,
    )


def _dependency_from_details(details: dict[str, object]) -> str | None:
    for key in ("dependency", "provider_key", "component", "channel", "tool"):
        value = details.get(key)
        if isinstance(value, str) and value:
            return sanitize_operations_text(value, max_length=128)
    return None


def _ensure_aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value


def _run_href(run_id: UUID, tenant_id: UUID | None) -> str:
    href = f"/admin/runs/{run_id}"
    if tenant_id is not None:
        href = f"{href}?tenant_id={tenant_id}"
    return href


def _usage_href(tenant_id: UUID | None) -> str:
    if tenant_id is None:
        return "/admin/usage"
    return f"/admin/usage?tenant_id={tenant_id}"


def _matches_filters(
    event: OperationalLogEvent,
    filters: OperationsLogFilters,
) -> bool:
    if filters.component and not _contains(event.component, filters.component):
        return False
    if filters.severity and not _contains(event.severity, filters.severity):
        return False
    if filters.status and not _contains(event.status, filters.status):
        return False
    if filters.dependency and not _contains(event.dependency or "", filters.dependency):
        return False
    return True


def _contains(value: str, expected: str) -> bool:
    return expected.lower() in value.lower()


def _apply_common_timeline_filters(
    stmt: Select[Any], filters: OperationsLogFilters
) -> Select[Any]:
    if filters.tenant_id is not None:
        stmt = stmt.where(AuditTimelineEventRecord.tenant_id == filters.tenant_id)
    if filters.run_id is not None:
        stmt = stmt.where(AuditTimelineEventRecord.workflow_run_id == filters.run_id)
    if filters.trace_id is not None:
        stmt = stmt.where(AuditTimelineEventRecord.trace_id == filters.trace_id)
    if filters.start is not None:
        stmt = stmt.where(AuditTimelineEventRecord.occurred_at >= filters.start)
    if filters.end is not None:
        stmt = stmt.where(AuditTimelineEventRecord.occurred_at < filters.end)
    return stmt


def _apply_common_trace_filters(
    stmt: Select[Any], filters: OperationsLogFilters
) -> Select[Any]:
    if filters.tenant_id is not None:
        stmt = stmt.where(AuditRuntimeTraceRecord.tenant_id == filters.tenant_id)
    if filters.run_id is not None:
        stmt = stmt.where(AuditRuntimeTraceRecord.workflow_run_id == filters.run_id)
    if filters.trace_id is not None:
        stmt = stmt.where(AuditRuntimeTraceRecord.trace_id == filters.trace_id)
    if filters.start is not None:
        stmt = stmt.where(AuditRuntimeTraceRecord.occurred_at >= filters.start)
    if filters.end is not None:
        stmt = stmt.where(AuditRuntimeTraceRecord.occurred_at < filters.end)
    return stmt


def _apply_common_gateway_filters(
    stmt: Select[Any], filters: OperationsLogFilters
) -> Select[Any]:
    if filters.tenant_id is not None:
        stmt = stmt.where(GatewayInvocationAttempt.tenant_id == filters.tenant_id)
    if filters.run_id is not None:
        stmt = stmt.where(GatewayInvocationAttempt.workflow_run_id == filters.run_id)
    if filters.trace_id is not None:
        stmt = stmt.where(GatewayInvocationAttempt.trace_id == filters.trace_id)
    if filters.start is not None:
        stmt = stmt.where(GatewayInvocationAttempt.completed_at >= filters.start)
    if filters.end is not None:
        stmt = stmt.where(GatewayInvocationAttempt.completed_at < filters.end)
    return stmt


def _p95(values: Sequence[int | None]) -> int:
    clean = sorted(value for value in values if value is not None)
    if not clean:
        return 0
    index = min(int(round((len(clean) - 1) * 0.95)), len(clean) - 1)
    return clean[index]


def _telegram_ready(container: Container) -> bool:
    settings = container.settings
    token_ready = bool(settings.telegram_provider_token_ref)
    webhook_ready = bool(settings.telegram_webhook_secret)
    if settings.app_env is AppEnvironment.PRODUCTION:
        token_ready = token_ready and _safe_reference(
            settings.telegram_provider_token_ref
        )
        webhook_ready = webhook_ready and _safe_reference(
            settings.telegram_webhook_secret
        )
    return token_ready and webhook_ready


def _safe_reference(value: str | None) -> bool:
    if not value:
        return False
    return value.startswith(("env:", "secret-manager/", "static:"))
