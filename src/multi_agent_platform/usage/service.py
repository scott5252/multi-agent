from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from uuid import UUID

from multi_agent_platform.db.models.usage import (
    LlmPricingVersion,
    LlmUsageEvent,
    UsageExportRequest,
    UsageReconciliationRecord,
)
from multi_agent_platform.db.repositories.usage import (
    UsageAccessDeniedError,
    UsageRepository,
)
from multi_agent_platform.model_providers.models import (
    GatewayInvocationContext,
    GatewayResult,
    ProviderType,
    UsageAvailability,
    UsageValueStatus,
)
from multi_agent_platform.storage.base import StorageProvider
from multi_agent_platform.usage.export import store_usage_csv_export
from multi_agent_platform.usage.models import (
    UsageAccessScope,
    UsageEventStatus,
    UsageEventView,
    UsageExportStatus,
    UsageFilters,
    UsageRollup,
    UsageScopeType,
    UsageSummary,
    UsageTotals,
    sanitize_safe_attribution,
)
from multi_agent_platform.usage.pricing import PricingRate, estimate_usage_cost


class UsageCaptureSkippedError(ValueError):
    pass


class UsageAnalyticsService:
    def __init__(self, repository: UsageRepository) -> None:
        self.repository = repository

    async def record_gateway_result(
        self,
        *,
        context: GatewayInvocationContext,
        provider_key: str | ProviderType,
        model_id: str,
        result: GatewayResult,
        provider_connection_id: UUID | None = None,
        source_gateway_attempt_id: UUID | None = None,
    ) -> LlmUsageEvent:
        if context.tenant_id is None:
            raise UsageCaptureSkippedError("usage capture requires tenant scope")
        provider = (
            provider_key.value
            if isinstance(provider_key, ProviderType)
            else provider_key
        )
        pricing = await self.repository.get_or_create_pricing_version(
            provider_key=provider,
            model_id=model_id,
            actor_principal_id=context.initiating_principal_id or "system",
        )
        estimate = estimate_usage_cost(
            result.usage,
            rate=_pricing_rate(pricing),
        )
        event = LlmUsageEvent(
            tenant_id=context.tenant_id,
            principal_id=context.initiating_principal_id,
            workflow_run_id=context.workflow_run_id,
            workflow_run_step_id=context.workflow_run_step_id,
            workflow_lineage_id=context.workflow_lineage_id,
            workflow_version_id=context.workflow_version_id,
            agent_key=context.agent_key,
            sub_agent_key=context.sub_agent_key,
            provider_key=provider,
            provider_connection_id=provider_connection_id,
            model_id=model_id,
            prompt_version_id=context.prompt_version_ids[0]
            if context.prompt_version_ids
            else None,
            agent_profile_version_id=context.agent_profile_version_id,
            execution_mode=context.execution_mode,
            operation_identity=context.operation_identity,
            idempotency_key=context.idempotency_key,
            trace_id=context.trace_id,
            input_tokens=result.usage.input_tokens,
            output_tokens=result.usage.output_tokens,
            cached_tokens=result.usage.cached_tokens,
            reasoning_tokens=result.usage.reasoning_tokens,
            total_tokens=result.usage.total_tokens,
            provider_billable_units=result.usage.provider_billable_units,
            input_status=result.usage.input_token_status,
            output_status=result.usage.output_token_status,
            cached_status=result.usage.cached_token_status,
            reasoning_status=result.usage.reasoning_token_status,
            total_status=result.usage.total_token_status,
            billable_status=result.usage.billable_unit_status,
            cost_status=estimate.cost_status,
            latency_ms=result.latency_ms,
            currency=estimate.currency,
            estimated_cost_micros=estimate.estimated_cost_micros,
            pricing_version_id=pricing.llm_pricing_version_id,
            usage_status=_usage_status(result),
            source_gateway_attempt_id=source_gateway_attempt_id,
            safe_attribution=sanitize_safe_attribution(
                {
                    **context.safe_summary(),
                    "result": result.safe_audit_summary,
                    "usage_available": result.usage.availability.value,
                }
            ),
        )
        return await self.repository.record_usage_event(event)

    async def summarize_usage(
        self,
        *,
        access_scope: UsageAccessScope,
        filters: UsageFilters,
        limit: int = 200,
    ) -> UsageSummary:
        events = await self.repository.list_events(
            access_scope=access_scope,
            filters=filters,
            limit=limit,
        )
        views = [_event_view(event) for event in events]
        totals = UsageTotals(
            total_events=len(views),
            total_tokens=sum(event.total_tokens or 0 for event in views),
            input_tokens=sum(event.input_tokens or 0 for event in views),
            output_tokens=sum(event.output_tokens or 0 for event in views),
            cached_tokens=sum(event.cached_tokens or 0 for event in views),
            reasoning_tokens=sum(event.reasoning_tokens or 0 for event in views),
            provider_billable_units=sum(
                event.provider_billable_units or 0 for event in views
            ),
            estimated_cost_micros=sum(
                event.estimated_cost_micros or 0 for event in views
            ),
            estimated_event_count=sum(
                1 for event in views if event.usage_status is UsageEventStatus.ESTIMATED
            ),
            confirmed_event_count=sum(
                1 for event in views if event.usage_status is UsageEventStatus.CONFIRMED
            ),
            unavailable_event_count=sum(
                1
                for event in views
                if event.usage_status
                in {UsageEventStatus.UNAVAILABLE, UsageEventStatus.MALFORMED}
            ),
        )
        return UsageSummary(
            totals=totals,
            rollups=tuple(_build_rollups(views, filters.group_by)),
            events=tuple(views),
        )

    async def create_csv_export(
        self,
        *,
        access_scope: UsageAccessScope,
        filters: UsageFilters,
        storage_provider: StorageProvider,
    ) -> UsageExportRequest:
        if (
            access_scope.scope_type is UsageScopeType.TENANT
            and filters.tenant_id is not None
            and filters.tenant_id != access_scope.tenant_id
        ):
            export = await self.repository.create_export_request(
                access_scope=access_scope,
                filters=filters,
                status=UsageExportStatus.DENIED,
                denial_reason="cross_tenant_scope",
            )
            raise UsageAccessDeniedError(
                f"usage export denied: {export.denial_reason or 'denied'}"
            )
        export = await self.repository.create_export_request(
            access_scope=access_scope,
            filters=filters,
            status=UsageExportStatus.PENDING,
        )
        try:
            events = await self.repository.list_events_for_export(
                access_scope=access_scope,
                filters=filters,
            )
            views = [_event_view(event) for event in events]
            tenant_label = (
                "platform"
                if access_scope.scope_type is UsageScopeType.PLATFORM
                else str(access_scope.tenant_id)
            )
            artifact_uri, checksum, size_bytes = await store_usage_csv_export(
                storage_provider=storage_provider,
                export_id=export.usage_export_request_id,
                tenant_label=tenant_label,
                events=views,
            )
            return await self.repository.complete_export_request(
                export,
                row_count=len(views),
                artifact_uri=artifact_uri,
                artifact_sha256=checksum,
                artifact_size_bytes=size_bytes,
            )
        except Exception as exc:
            await self.repository.fail_export_request(
                export,
                reason="usage export failed",
            )
            raise RuntimeError("usage export failed") from exc

    async def reconcile_usage_event(
        self,
        *,
        event_id: UUID,
        confirmed_values: dict[str, object],
        source: str,
        reconciled_by_principal_id: str | None = None,
    ) -> UsageReconciliationRecord:
        event = await self.repository.get_event(event_id)
        if event is None:
            raise LookupError("usage event not found")
        allowed = {
            "input_tokens",
            "output_tokens",
            "cached_tokens",
            "reasoning_tokens",
            "total_tokens",
            "provider_billable_units",
            "estimated_cost_micros",
        }
        safe_values = {
            key: value for key, value in confirmed_values.items() if key in allowed
        }
        return await self.repository.record_reconciliation(
            event=event,
            source=source,
            confirmed_values=safe_values,
            reconciled_by_principal_id=reconciled_by_principal_id,
        )


def _pricing_rate(pricing: LlmPricingVersion) -> PricingRate:
    return PricingRate(
        currency=pricing.currency,
        input_token_micros=pricing.input_token_micros,
        output_token_micros=pricing.output_token_micros,
        cached_token_micros=pricing.cached_token_micros,
        reasoning_token_micros=pricing.reasoning_token_micros,
        billable_unit_micros=pricing.billable_unit_micros,
    )


def _usage_status(result: GatewayResult) -> UsageEventStatus:
    if result.usage.availability is UsageAvailability.MALFORMED:
        return UsageEventStatus.MALFORMED
    if result.usage.availability is UsageAvailability.UNAVAILABLE:
        return UsageEventStatus.UNAVAILABLE
    statuses = {
        result.usage.input_token_status,
        result.usage.output_token_status,
        result.usage.total_token_status,
    }
    if statuses <= {UsageValueStatus.CONFIRMED, UsageValueStatus.NOT_APPLICABLE}:
        return UsageEventStatus.CONFIRMED
    if UsageValueStatus.ESTIMATED in statuses:
        return UsageEventStatus.ESTIMATED
    return UsageEventStatus.PARTIAL


def _event_view(event: LlmUsageEvent) -> UsageEventView:
    return UsageEventView(
        llm_usage_event_id=event.llm_usage_event_id,
        tenant_id=event.tenant_id,
        principal_id=event.principal_id,
        provider_key=event.provider_key,
        model_id=event.model_id,
        workflow_run_id=event.workflow_run_id,
        workflow_run_step_id=event.workflow_run_step_id,
        workflow_lineage_id=event.workflow_lineage_id,
        workflow_version_id=event.workflow_version_id,
        agent_key=event.agent_key,
        sub_agent_key=event.sub_agent_key,
        prompt_version_id=event.prompt_version_id,
        execution_mode=event.execution_mode,
        input_tokens=event.input_tokens,
        output_tokens=event.output_tokens,
        cached_tokens=event.cached_tokens,
        reasoning_tokens=event.reasoning_tokens,
        total_tokens=event.total_tokens,
        provider_billable_units=event.provider_billable_units,
        latency_ms=event.latency_ms,
        estimated_cost_micros=event.estimated_cost_micros,
        currency=event.currency,
        usage_status=event.usage_status,
        recorded_at=event.recorded_at,
    )


def _build_rollups(
    events: list[UsageEventView],
    group_by: str,
) -> list[UsageRollup]:
    buckets: dict[str, list[UsageEventView]] = defaultdict(list)
    for event in events:
        buckets[_rollup_label(event, group_by)].append(event)
    return [
        UsageRollup(
            label=label,
            event_count=len(bucket),
            total_tokens=sum(event.total_tokens or 0 for event in bucket),
            estimated_cost_micros=sum(
                event.estimated_cost_micros or 0 for event in bucket
            ),
        )
        for label, bucket in sorted(buckets.items())
    ]


def _rollup_label(event: UsageEventView, group_by: str) -> str:
    if group_by == "hour":
        return _format_bucket(event.recorded_at, "%Y-%m-%d %H:00")
    if group_by == "day":
        return _format_bucket(event.recorded_at, "%Y-%m-%d")
    if group_by == "tenant":
        return str(event.tenant_id)
    if group_by == "provider":
        return event.provider_key
    if group_by == "model":
        return event.model_id
    if group_by == "workflow":
        return str(event.workflow_lineage_id or event.workflow_run_id or "none")
    if group_by == "agent":
        return event.agent_key or "none"
    if group_by == "sub_agent":
        return event.sub_agent_key or "none"
    if group_by == "prompt":
        return str(event.prompt_version_id or "none")
    if group_by == "execution_mode":
        return event.execution_mode
    if group_by == "principal":
        return event.principal_id or "system"
    return "all"


def _format_bucket(value: datetime, fmt: str) -> str:
    return value.strftime(fmt)
