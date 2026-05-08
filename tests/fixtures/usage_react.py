from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from multi_agent_platform.db.models.usage import (
    LlmPricingVersion,
    LlmUsageEvent,
    UsageExportRequest,
)
from multi_agent_platform.model_providers.models import UsageValueStatus
from multi_agent_platform.usage.models import (
    UsageEventStatus,
    UsageExportStatus,
    UsageScopeType,
)


def seed_usage_react_live_data_sync(
    session: Session,
    *,
    tenant_id: UUID,
    other_tenant_id: UUID | None = None,
) -> dict[str, UUID]:
    ids = _ids()
    now = datetime.now(UTC)
    session.add(
        _pricing(
            pricing_id=ids["pricing_id"],
            provider_key="openai",
            model_id="gpt-live-usage",
        )
    )
    session.add_all(
        _events(
            ids=ids,
            tenant_id=tenant_id,
            now=now,
            include_other_tenant=False,
            other_tenant_id=other_tenant_id,
        )
    )
    session.add(_export(ids=ids, tenant_id=tenant_id, now=now))
    session.flush()
    return ids


async def seed_usage_react_live_data(
    session: AsyncSession,
    *,
    tenant_id: UUID,
    other_tenant_id: UUID | None = None,
) -> dict[str, UUID]:
    ids = _ids()
    now = datetime.now(UTC)
    session.add(
        _pricing(
            pricing_id=ids["pricing_id"],
            provider_key="openai",
            model_id="gpt-live-usage",
        )
    )
    session.add_all(
        _events(
            ids=ids,
            tenant_id=tenant_id,
            now=now,
            include_other_tenant=False,
            other_tenant_id=other_tenant_id,
        )
    )
    session.add(_export(ids=ids, tenant_id=tenant_id, now=now))
    await session.flush()
    return ids


def _ids() -> dict[str, UUID]:
    return {
        "pricing_id": uuid4(),
        "event_id": uuid4(),
        "partial_event_id": uuid4(),
        "export_id": uuid4(),
        "workflow_lineage_id": uuid4(),
        "workflow_run_id": uuid4(),
        "workflow_step_id": uuid4(),
        "prompt_version_id": uuid4(),
        "gateway_attempt_id": uuid4(),
    }


def _pricing(
    *,
    pricing_id: UUID,
    provider_key: str,
    model_id: str,
) -> LlmPricingVersion:
    return LlmPricingVersion(
        llm_pricing_version_id=pricing_id,
        provider_key=provider_key,
        model_id=model_id,
        currency="USD",
        input_token_micros=2,
        output_token_micros=6,
        cached_token_micros=0,
        reasoning_token_micros=6,
        calculation_method="qa056_live_per_token",
        source_note="qa056 persisted live pricing",
        created_by_principal_id="tenant-admin-acme",
    )


def _events(
    *,
    ids: dict[str, UUID],
    tenant_id: UUID,
    now: datetime,
    include_other_tenant: bool,
    other_tenant_id: UUID | None,
) -> list[LlmUsageEvent]:
    events = [
        LlmUsageEvent(
            llm_usage_event_id=ids["event_id"],
            tenant_id=tenant_id,
            principal_id="tenant-admin-acme",
            provider_key="openai",
            model_id="gpt-live-usage",
            workflow_lineage_id=ids["workflow_lineage_id"],
            workflow_run_id=ids["workflow_run_id"],
            workflow_run_step_id=ids["workflow_step_id"],
            agent_key="usage-reviewer",
            sub_agent_key="cost-summarizer",
            prompt_version_id=ids["prompt_version_id"],
            execution_mode="test",
            operation_identity="responses.live_usage.primary",
            trace_id="trace-qa056-live-usage",
            input_tokens=1200,
            output_tokens=360,
            total_tokens=1560,
            input_status=UsageValueStatus.CONFIRMED,
            output_status=UsageValueStatus.CONFIRMED,
            total_status=UsageValueStatus.CONFIRMED,
            cost_status=UsageValueStatus.ESTIMATED,
            latency_ms=420,
            currency="USD",
            estimated_cost_micros=4560,
            pricing_version_id=ids["pricing_id"],
            usage_status=UsageEventStatus.CONFIRMED,
            source_gateway_attempt_id=ids["gateway_attempt_id"],
            safe_attribution={
                "workflow_label": "Usage live review workflow",
                "prompt_label": "Usage summary prompt v1",
                "graph_node_label": "Summarize usage evidence",
                "governed_tool_label": "Usage export metadata lookup",
                "physical_attempt_label": "OpenAI live usage attempt",
                "summary": "Live usage attributed through safe persisted metadata.",
            },
            recorded_at=now - timedelta(days=1),
        ),
        LlmUsageEvent(
            llm_usage_event_id=ids["partial_event_id"],
            tenant_id=tenant_id,
            principal_id="tenant-admin-acme",
            provider_key="local-compatible",
            model_id="local-usage-check",
            agent_key="usage-reviewer",
            execution_mode="test",
            operation_identity="local.live_usage.fallback",
            input_tokens=300,
            output_tokens=0,
            total_tokens=300,
            input_status=UsageValueStatus.ESTIMATED,
            output_status=UsageValueStatus.UNAVAILABLE,
            total_status=UsageValueStatus.ESTIMATED,
            cost_status=UsageValueStatus.UNAVAILABLE,
            latency_ms=85,
            currency="USD",
            estimated_cost_micros=None,
            pricing_version_id=None,
            usage_status=UsageEventStatus.PARTIAL,
            safe_attribution={
                "workflow_label": "Usage live review workflow",
                "summary": "Partial local usage with missing pricing metadata.",
            },
            recorded_at=now - timedelta(hours=3),
        ),
    ]
    if include_other_tenant and other_tenant_id is not None:
        events.append(
            LlmUsageEvent(
                tenant_id=other_tenant_id,
                principal_id="tenant-admin-globex",
                provider_key="openai",
                model_id="gpt-globex",
                execution_mode="test",
                total_tokens=999,
                latency_ms=50,
                estimated_cost_micros=999,
                usage_status=UsageEventStatus.CONFIRMED,
                recorded_at=now - timedelta(hours=1),
            )
        )
    return events


def _export(
    *,
    ids: dict[str, UUID],
    tenant_id: UUID,
    now: datetime,
) -> UsageExportRequest:
    return UsageExportRequest(
        usage_export_request_id=ids["export_id"],
        tenant_id=tenant_id,
        requested_by_principal_id="tenant-admin-acme",
        scope_type=UsageScopeType.TENANT,
        filters={"tenant_id": str(tenant_id), "range": "Last 30 days"},
        status=UsageExportStatus.COMPLETED,
        row_count=2,
        artifact_uri=f"memory://qa056/{ids['export_id']}.csv",
        artifact_sha256="a" * 64,
        artifact_size_bytes=512,
        created_at=now - timedelta(minutes=10),
        completed_at=now - timedelta(minutes=9),
        expires_at=now + timedelta(days=7),
    )
