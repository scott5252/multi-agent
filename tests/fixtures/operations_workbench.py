from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from multi_agent_platform.db.models.audit_debugging import (
    AuditRuntimeTraceRecord,
    AuditTimelineEventRecord,
)
from multi_agent_platform.db.models.model_providers import GatewayInvocationAttempt
from multi_agent_platform.db.models.reliability import CapacitySnapshotRecord
from multi_agent_platform.model_providers.models import (
    ErrorCategory,
    ProviderType,
    TestOutcome,
)


def seed_operations_workbench_live_data_sync(
    session: Session,
    *,
    tenant_id: UUID,
) -> dict[str, UUID]:
    ids = _ids()
    _add_records(session, ids=ids, tenant_id=tenant_id)
    session.flush()
    return ids


async def seed_operations_workbench_live_data(
    session: AsyncSession,
    *,
    tenant_id: UUID,
) -> dict[str, UUID]:
    ids = _ids()
    _add_records(session, ids=ids, tenant_id=tenant_id)
    await session.flush()
    return ids


def _ids() -> dict[str, UUID]:
    return {
        "run_id": uuid4(),
        "gateway_attempt_id": uuid4(),
        "timeline_start_id": uuid4(),
        "timeline_tool_id": uuid4(),
        "timeline_delivery_id": uuid4(),
        "tool_trace_id": uuid4(),
        "delivery_trace_id": uuid4(),
    }


def _add_records(
    session: Session | AsyncSession,
    *,
    ids: dict[str, UUID],
    tenant_id: UUID,
) -> None:
    now = datetime.now(UTC)
    session.add(
        CapacitySnapshotRecord(
            tenant_id=None,
            runnable_depth=7,
            delayed_depth=2,
            active_leases=3,
            retry_backlog=2,
            compensation_backlog=1,
            dead_letter_count=0,
            db_pool_wait_p95_ms=18,
            db_pool_in_use=2,
            db_pool_available=8,
            artifact_inflight=1,
            artifact_wait_p95_ms=6,
            open_breaker_count=1,
            created_at=now - timedelta(minutes=4),
        )
    )
    start = AuditTimelineEventRecord(
        timeline_event_id=ids["timeline_start_id"],
        tenant_id=tenant_id,
        workflow_run_id=ids["run_id"],
        sequence=1,
        event_category="runtime",
        run_status_after="running",
        origin_type="system",
        actor_principal_id="platform-admin",
        trace_id="trace-qa057-live-run",
        source_event_id=f"qa057-start-{ids['run_id']}",
        criticality="diagnostic",
        safe_summary="Live run started with persisted audit evidence.",
        safe_details={"dependency": "runtime", "category": "run_started"},
        occurred_at=now - timedelta(minutes=12),
    )
    tool_timeline = AuditTimelineEventRecord(
        timeline_event_id=ids["timeline_tool_id"],
        tenant_id=tenant_id,
        workflow_run_id=ids["run_id"],
        sequence=2,
        event_category="tool_call",
        run_status_after="running",
        origin_type="system",
        actor_principal_id="platform-admin",
        trace_id="trace-qa057-live-run",
        source_event_id=f"qa057-tool-{ids['run_id']}",
        criticality="diagnostic",
        safe_summary="Live tool call completed with a safe summary.",
        safe_details={"dependency": "weather-tool", "category": "tool_success"},
        occurred_at=now - timedelta(minutes=8),
    )
    delivery_timeline = AuditTimelineEventRecord(
        timeline_event_id=ids["timeline_delivery_id"],
        tenant_id=tenant_id,
        workflow_run_id=ids["run_id"],
        sequence=3,
        event_category="telegram_delivery",
        run_status_after="recoverable_failed",
        origin_type="system",
        actor_principal_id="platform-admin",
        trace_id="trace-qa057-live-delivery",
        source_event_id=f"qa057-delivery-{ids['run_id']}",
        criticality="warning",
        safe_summary="Telegram delivery is queued for a live retry.",
        safe_details={"dependency": "telegram", "category": "delivery_retry"},
        occurred_at=now - timedelta(minutes=5),
    )
    session.add_all([start, tool_timeline, delivery_timeline])
    session.add_all(
        [
            AuditRuntimeTraceRecord(
                trace_record_id=ids["tool_trace_id"],
                tenant_id=tenant_id,
                workflow_run_id=ids["run_id"],
                timeline_event_id=ids["timeline_tool_id"],
                trace_type="tool_call",
                trace_id="trace-qa057-live-run",
                status="recorded",
                outcome="succeeded",
                duration_ms=64,
                policy_outcome="allowed_read_only",
                subject_ref="weather-tool",
                metadata_json={
                    "tool": "Weather live summary",
                    "connector": "Weather connector",
                    "policy_outcome": "allowed_read_only",
                    "side_effect": "read_only",
                    "result_category": "safe_summary",
                },
                occurred_at=now - timedelta(minutes=7),
            ),
            AuditRuntimeTraceRecord(
                trace_record_id=ids["delivery_trace_id"],
                tenant_id=tenant_id,
                workflow_run_id=ids["run_id"],
                timeline_event_id=ids["timeline_delivery_id"],
                trace_type="telegram_delivery",
                trace_id="trace-qa057-live-delivery",
                status="recorded",
                outcome="retry_scheduled",
                duration_ms=38,
                policy_outcome="runtime_required",
                subject_ref="telegram",
                metadata_json={"alias": "Live briefing alias"},
                occurred_at=now - timedelta(minutes=4),
            ),
        ]
    )
    session.add(
        GatewayInvocationAttempt(
            gateway_invocation_attempt_id=ids["gateway_attempt_id"],
            tenant_id=tenant_id,
            workflow_run_id=ids["run_id"],
            trace_id="trace-qa057-live-run",
            provider_type=ProviderType.OPENAI,
            model_id="gpt-qa057-live",
            started_at=now - timedelta(minutes=6),
            completed_at=now - timedelta(minutes=6, seconds=-1),
            latency_ms=840,
            outcome=TestOutcome.FAILURE,
            normalized_error_category=ErrorCategory.TIMEOUT,
            retry_attempt_number=1,
            retry_decision_summary={"category": "retryable_timeout"},
            breaker_scope="model-gateway",
            breaker_decision_summary={"state": "closed"},
            usage_metadata={"usage_reference_id": "usage-live-qa057"},
            usage_available=True,
            safe_audit_summary={
                "summary": "Gateway attempt recorded retryable timeout category.",
                "provider": "OpenAI provider",
                "model": "gpt-qa057-live",
                "credential": "resolved_reference",
                "retry_category": "retryable_timeout",
                "breaker_category": "closed",
                "usage_reference_id": "usage-live-qa057",
            },
            created_at=now - timedelta(minutes=6),
        )
    )
