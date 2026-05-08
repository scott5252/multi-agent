from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Select, false, select
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.db.base import utcnow
from multi_agent_platform.db.models.tenant import Tenant
from multi_agent_platform.db.models.usage import (
    LlmPricingVersion,
    LlmUsageEvent,
    UsageExportRequest,
    UsageReconciliationRecord,
)
from multi_agent_platform.usage.models import (
    UsageAccessScope,
    UsageEventStatus,
    UsageExportStatus,
    UsageFilters,
    UsageScopeType,
)


class UsageAccessDeniedError(PermissionError):
    pass


class UsageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_or_create_pricing_version(
        self,
        *,
        provider_key: str,
        model_id: str,
        actor_principal_id: str = "system",
    ) -> LlmPricingVersion:
        existing = await self._session.scalar(
            select(LlmPricingVersion)
            .where(
                LlmPricingVersion.provider_key == provider_key,
                LlmPricingVersion.model_id == model_id,
                LlmPricingVersion.currency == "USD",
                LlmPricingVersion.effective_to.is_(None),
            )
            .order_by(LlmPricingVersion.effective_from.desc())
            .limit(1)
        )
        if existing is not None:
            return existing
        pricing = LlmPricingVersion(
            provider_key=provider_key,
            model_id=model_id,
            currency="USD",
            input_token_micros=1,
            output_token_micros=3,
            cached_token_micros=0,
            reasoning_token_micros=3,
            billable_unit_micros=None,
            calculation_method="default_internal_per_token",
            source_note="default internal QA pricing",
            created_by_principal_id=actor_principal_id,
        )
        self._session.add(pricing)
        await self._session.flush()
        return pricing

    async def record_usage_event(self, event: LlmUsageEvent) -> LlmUsageEvent:
        if event.idempotency_key:
            existing = await self._session.scalar(
                select(LlmUsageEvent).where(
                    LlmUsageEvent.tenant_id == event.tenant_id,
                    LlmUsageEvent.idempotency_key == event.idempotency_key,
                    LlmUsageEvent.provider_key == event.provider_key,
                    LlmUsageEvent.model_id == event.model_id,
                )
            )
            if existing is not None:
                return existing
        self._session.add(event)
        await self._session.flush()
        return event

    async def get_event(self, event_id: UUID) -> LlmUsageEvent | None:
        return await self._session.get(LlmUsageEvent, event_id)

    async def list_events(
        self,
        *,
        access_scope: UsageAccessScope,
        filters: UsageFilters,
        limit: int = 200,
    ) -> list[LlmUsageEvent]:
        stmt = _event_stmt_for_scope(access_scope, filters)
        stmt = _apply_event_filters(stmt, filters)
        stmt = stmt.order_by(LlmUsageEvent.recorded_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars())

    async def list_events_for_export(
        self,
        *,
        access_scope: UsageAccessScope,
        filters: UsageFilters,
        limit: int = 5000,
    ) -> list[LlmUsageEvent]:
        stmt = _event_stmt_for_scope(access_scope, filters)
        stmt = _apply_event_filters(stmt, filters)
        stmt = stmt.order_by(LlmUsageEvent.recorded_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars())

    async def create_export_request(
        self,
        *,
        access_scope: UsageAccessScope,
        filters: UsageFilters,
        status: UsageExportStatus = UsageExportStatus.PENDING,
        row_count: int = 0,
        denial_reason: str | None = None,
    ) -> UsageExportRequest:
        export = UsageExportRequest(
            tenant_id=access_scope.tenant_id
            if access_scope.scope_type is UsageScopeType.TENANT
            else filters.tenant_id,
            requested_by_principal_id=access_scope.principal_id,
            scope_type=access_scope.scope_type,
            filters=filters.safe_snapshot(),
            status=status,
            row_count=row_count,
            denial_reason=denial_reason,
        )
        self._session.add(export)
        await self._session.flush()
        return export

    async def complete_export_request(
        self,
        export: UsageExportRequest,
        *,
        row_count: int,
        artifact_uri: str,
        artifact_sha256: str,
        artifact_size_bytes: int,
    ) -> UsageExportRequest:
        export.status = UsageExportStatus.COMPLETED
        export.row_count = row_count
        export.artifact_uri = artifact_uri
        export.artifact_sha256 = artifact_sha256
        export.artifact_size_bytes = artifact_size_bytes
        export.completed_at = utcnow()
        await self._session.flush()
        return export

    async def fail_export_request(
        self,
        export: UsageExportRequest,
        *,
        reason: str,
    ) -> UsageExportRequest:
        export.status = UsageExportStatus.FAILED
        export.failure_reason = reason[:255]
        export.completed_at = utcnow()
        await self._session.flush()
        return export

    async def get_export_request(
        self,
        export_id: UUID,
        *,
        access_scope: UsageAccessScope,
    ) -> UsageExportRequest | None:
        export = await self._session.get(UsageExportRequest, export_id)
        if export is None:
            return None
        if access_scope.scope_type is UsageScopeType.PLATFORM:
            return export
        if export.tenant_id == access_scope.tenant_id:
            return export
        raise UsageAccessDeniedError("usage export is outside tenant scope")

    async def list_export_requests(
        self,
        *,
        access_scope: UsageAccessScope,
        filters: UsageFilters,
        limit: int = 10,
    ) -> list[UsageExportRequest]:
        stmt = select(UsageExportRequest)
        if access_scope.scope_type is UsageScopeType.PLATFORM:
            if filters.tenant_id is not None:
                stmt = stmt.where(UsageExportRequest.tenant_id == filters.tenant_id)
        else:
            stmt = stmt.where(UsageExportRequest.tenant_id == access_scope.tenant_id)
        stmt = stmt.order_by(UsageExportRequest.created_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars())

    async def list_tenant_labels(
        self,
        *,
        access_scope: UsageAccessScope,
        tenant_ids: set[UUID],
    ) -> dict[UUID, str]:
        if not tenant_ids:
            return {}
        visible_tenant_ids = set(tenant_ids)
        if (
            access_scope.scope_type is UsageScopeType.TENANT
            and access_scope.tenant_id is not None
        ):
            visible_tenant_ids = {access_scope.tenant_id} & visible_tenant_ids
        if not visible_tenant_ids:
            return {}
        result = await self._session.execute(
            select(Tenant.tenant_id, Tenant.display_name).where(
                Tenant.tenant_id.in_(visible_tenant_ids)
            )
        )
        return {tenant_id: display_name for tenant_id, display_name in result.all()}

    async def record_reconciliation(
        self,
        *,
        event: LlmUsageEvent,
        source: str,
        confirmed_values: dict[str, object],
        reconciled_by_principal_id: str | None = None,
    ) -> UsageReconciliationRecord:
        previous_values = {
            "input_tokens": event.input_tokens,
            "output_tokens": event.output_tokens,
            "cached_tokens": event.cached_tokens,
            "reasoning_tokens": event.reasoning_tokens,
            "total_tokens": event.total_tokens,
            "estimated_cost_micros": event.estimated_cost_micros,
            "usage_status": event.usage_status.value,
        }
        record = UsageReconciliationRecord(
            llm_usage_event_id=event.llm_usage_event_id,
            source=source,
            previous_values=previous_values,
            confirmed_values=confirmed_values,
            reconciled_by_principal_id=reconciled_by_principal_id,
        )
        for key, value in confirmed_values.items():
            if hasattr(event, key):
                setattr(event, key, value)
        event.usage_status = UsageEventStatus.CONFIRMED
        event.updated_at = utcnow()
        self._session.add(record)
        await self._session.flush()
        return record


def _event_stmt_for_scope(
    access_scope: UsageAccessScope,
    filters: UsageFilters,
) -> Select[tuple[LlmUsageEvent]]:
    stmt = select(LlmUsageEvent)
    if access_scope.scope_type is UsageScopeType.PLATFORM:
        if filters.tenant_id is not None:
            return stmt.where(LlmUsageEvent.tenant_id == filters.tenant_id)
        return stmt
    if filters.tenant_id is not None and filters.tenant_id != access_scope.tenant_id:
        return stmt.where(false())
    return stmt.where(LlmUsageEvent.tenant_id == access_scope.tenant_id)


def _apply_event_filters(
    stmt: Select[tuple[LlmUsageEvent]],
    filters: UsageFilters,
) -> Select[tuple[LlmUsageEvent]]:
    if filters.start is not None:
        stmt = stmt.where(LlmUsageEvent.recorded_at >= filters.start)
    if filters.end is not None:
        stmt = stmt.where(LlmUsageEvent.recorded_at < filters.end)
    if filters.provider_key is not None:
        stmt = stmt.where(LlmUsageEvent.provider_key == filters.provider_key)
    if filters.model_id is not None:
        stmt = stmt.where(LlmUsageEvent.model_id == filters.model_id)
    if filters.workflow_lineage_id is not None:
        stmt = stmt.where(
            LlmUsageEvent.workflow_lineage_id == filters.workflow_lineage_id
        )
    if filters.workflow_version_id is not None:
        stmt = stmt.where(
            LlmUsageEvent.workflow_version_id == filters.workflow_version_id
        )
    if filters.workflow_run_id is not None:
        stmt = stmt.where(LlmUsageEvent.workflow_run_id == filters.workflow_run_id)
    if filters.workflow_run_step_id is not None:
        stmt = stmt.where(
            LlmUsageEvent.workflow_run_step_id == filters.workflow_run_step_id
        )
    if filters.agent_key is not None:
        stmt = stmt.where(LlmUsageEvent.agent_key == filters.agent_key)
    if filters.sub_agent_key is not None:
        stmt = stmt.where(LlmUsageEvent.sub_agent_key == filters.sub_agent_key)
    if filters.prompt_version_id is not None:
        stmt = stmt.where(LlmUsageEvent.prompt_version_id == filters.prompt_version_id)
    if filters.execution_mode is not None:
        stmt = stmt.where(LlmUsageEvent.execution_mode == filters.execution_mode)
    if filters.usage_status is not None:
        stmt = stmt.where(LlmUsageEvent.usage_status == filters.usage_status)
    if filters.principal_id is not None:
        stmt = stmt.where(LlmUsageEvent.principal_id == filters.principal_id)
    return stmt


def now_utc() -> datetime:
    return utcnow()
