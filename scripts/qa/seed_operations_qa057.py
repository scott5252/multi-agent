from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from multi_agent_platform.db.models.audit_debugging import (
    AuditRuntimeTraceRecord,
    AuditTimelineEventRecord,
)
from multi_agent_platform.db.models.model_providers import GatewayInvocationAttempt
from multi_agent_platform.db.models.reliability import CapacitySnapshotRecord
from multi_agent_platform.db.models.tenant import Tenant, TenantStatus
from multi_agent_platform.model_providers.models import (
    ErrorCategory,
    ProviderType,
    TestOutcome,
)

ACME_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
GLOBEX_TENANT_ID = UUID("22222222-2222-2222-2222-222222222222")
QA057_RUN_ID = UUID("57000000-0000-0000-0000-000000000057")
QA057_GATEWAY_ATTEMPT_ID = UUID("57000000-0000-0000-0000-000000000105")
QA057_TIMELINE_START_ID = UUID("57000000-0000-0000-0000-000000000201")
QA057_TIMELINE_TOOL_ID = UUID("57000000-0000-0000-0000-000000000202")
QA057_TIMELINE_DELIVERY_ID = UUID("57000000-0000-0000-0000-000000000203")
QA057_TOOL_TRACE_ID = UUID("57000000-0000-0000-0000-000000000301")
QA057_DELIVERY_TRACE_ID = UUID("57000000-0000-0000-0000-000000000302")


def main() -> int:
    engine = create_engine(_database_url())
    now = datetime.now(UTC)
    with Session(engine) as session:
        _upsert_tenant(session, ACME_TENANT_ID, "acme", "Acme")
        _upsert_tenant(session, GLOBEX_TENANT_ID, "globex", "Globex")
        _upsert_capacity(session, now=now)
        _upsert_timeline(session, now=now)
        _upsert_traces(session, now=now)
        _upsert_gateway_attempt(session, now=now)
        session.commit()
    print("Seeded QA057 operations live records")
    print(f"tenant_id={ACME_TENANT_ID}")
    print(f"globex_tenant_id={GLOBEX_TENANT_ID}")
    print(f"workflow_run_id={QA057_RUN_ID}")
    print("timeline_events=3")
    print("gateway_attempts=1")
    return 0


def _upsert_tenant(
    session: Session,
    tenant_id: UUID,
    slug: str,
    display_name: str,
) -> None:
    record = session.get(Tenant, tenant_id)
    if record is None:
        record = Tenant(tenant_id=tenant_id)
        session.add(record)
    record.slug = slug
    record.display_name = display_name
    record.status = TenantStatus.ACTIVE


def _upsert_capacity(session: Session, *, now: datetime) -> None:
    record = session.get(
        CapacitySnapshotRecord,
        UUID("57000000-0000-0000-0000-000000000401"),
    )
    if record is None:
        record = CapacitySnapshotRecord(
            capacity_snapshot_id=UUID("57000000-0000-0000-0000-000000000401")
        )
        session.add(record)
    record.tenant_id = None
    record.snapshot_scope = "global"
    record.runnable_depth = 7
    record.delayed_depth = 2
    record.active_leases = 3
    record.recovery_backlog = 1
    record.retry_backlog = 2
    record.compensation_backlog = 1
    record.dead_letter_count = 0
    record.db_pool_wait_p95_ms = 18
    record.db_pool_in_use = 2
    record.db_pool_available = 8
    record.artifact_inflight = 1
    record.artifact_wait_p95_ms = 6
    record.open_breaker_count = 1
    record.fairness_debt_total = 0
    record.created_at = now - timedelta(minutes=4)


def _upsert_timeline(session: Session, *, now: datetime) -> None:
    _upsert_timeline_event(
        session,
        timeline_event_id=QA057_TIMELINE_START_ID,
        sequence=1,
        event_category="runtime",
        run_status_after="running",
        trace_id="trace-qa057-live-run",
        source_event_id="qa057-live-run-started",
        criticality="diagnostic",
        safe_summary="Live run started with persisted audit evidence.",
        safe_details={"dependency": "runtime", "category": "run_started"},
        occurred_at=now - timedelta(minutes=12),
    )
    _upsert_timeline_event(
        session,
        timeline_event_id=QA057_TIMELINE_TOOL_ID,
        sequence=2,
        event_category="tool_call",
        run_status_after="running",
        trace_id="trace-qa057-live-run",
        source_event_id="qa057-live-tool",
        criticality="diagnostic",
        safe_summary="Live tool call completed with a safe summary.",
        safe_details={"dependency": "weather-tool", "category": "tool_success"},
        occurred_at=now - timedelta(minutes=8),
    )
    _upsert_timeline_event(
        session,
        timeline_event_id=QA057_TIMELINE_DELIVERY_ID,
        sequence=3,
        event_category="telegram_delivery",
        run_status_after="recoverable_failed",
        trace_id="trace-qa057-live-delivery",
        source_event_id="qa057-live-delivery",
        criticality="warning",
        safe_summary="Telegram delivery is queued for a live retry.",
        safe_details={"dependency": "telegram", "category": "delivery_retry"},
        occurred_at=now - timedelta(minutes=5),
    )


def _upsert_timeline_event(
    session: Session,
    *,
    timeline_event_id: UUID,
    sequence: int,
    event_category: str,
    run_status_after: str,
    trace_id: str,
    source_event_id: str,
    criticality: str,
    safe_summary: str,
    safe_details: dict[str, object],
    occurred_at: datetime,
) -> None:
    record = session.get(AuditTimelineEventRecord, timeline_event_id)
    if record is None:
        record = AuditTimelineEventRecord(timeline_event_id=timeline_event_id)
        session.add(record)
    record.tenant_id = ACME_TENANT_ID
    record.workflow_run_id = QA057_RUN_ID
    record.sequence = sequence
    record.event_category = event_category
    record.run_status_after = run_status_after
    record.origin_type = "system"
    record.origin_ref = None
    record.actor_principal_id = "platform-admin"
    record.trace_id = trace_id
    record.correlation_id = None
    record.source_event_id = source_event_id
    record.occurred_at = occurred_at
    record.criticality = criticality
    record.safe_summary = safe_summary
    record.safe_details = safe_details
    record.classification_version = "qa057-live-ops-v1"


def _upsert_traces(session: Session, *, now: datetime) -> None:
    _upsert_trace(
        session,
        trace_record_id=QA057_TOOL_TRACE_ID,
        timeline_event_id=QA057_TIMELINE_TOOL_ID,
        trace_type="tool_call",
        trace_id="trace-qa057-live-run",
        outcome="succeeded",
        duration_ms=64,
        policy_outcome="allowed_read_only",
        subject_ref="weather-tool",
        metadata={
            "tool": "Weather live summary",
            "connector": "Weather connector",
            "policy_outcome": "allowed_read_only",
            "side_effect": "read_only",
            "result_category": "safe_summary",
        },
        occurred_at=now - timedelta(minutes=7),
    )
    _upsert_trace(
        session,
        trace_record_id=QA057_DELIVERY_TRACE_ID,
        timeline_event_id=QA057_TIMELINE_DELIVERY_ID,
        trace_type="telegram_delivery",
        trace_id="trace-qa057-live-delivery",
        outcome="retry_scheduled",
        duration_ms=38,
        policy_outcome="runtime_required",
        subject_ref="telegram",
        metadata={"alias": "Live briefing alias"},
        occurred_at=now - timedelta(minutes=4),
    )


def _upsert_trace(
    session: Session,
    *,
    trace_record_id: UUID,
    timeline_event_id: UUID,
    trace_type: str,
    trace_id: str,
    outcome: str,
    duration_ms: int,
    policy_outcome: str,
    subject_ref: str,
    metadata: dict[str, object],
    occurred_at: datetime,
) -> None:
    record = session.get(AuditRuntimeTraceRecord, trace_record_id)
    if record is None:
        record = AuditRuntimeTraceRecord(trace_record_id=trace_record_id)
        session.add(record)
    record.tenant_id = ACME_TENANT_ID
    record.workflow_run_id = QA057_RUN_ID
    record.timeline_event_id = timeline_event_id
    record.trace_type = trace_type
    record.trace_id = trace_id
    record.status = "recorded"
    record.outcome = outcome
    record.duration_ms = duration_ms
    record.policy_outcome = policy_outcome
    record.subject_ref = subject_ref
    record.safe_input_summary = {}
    record.safe_output_summary = {}
    record.safe_error_summary = {}
    record.metadata_json = metadata
    record.occurred_at = occurred_at


def _upsert_gateway_attempt(session: Session, *, now: datetime) -> None:
    record = session.get(GatewayInvocationAttempt, QA057_GATEWAY_ATTEMPT_ID)
    if record is None:
        record = GatewayInvocationAttempt(
            gateway_invocation_attempt_id=QA057_GATEWAY_ATTEMPT_ID,
            provider_type=ProviderType.OPENAI,
            model_id="gpt-qa057-live",
            started_at=now - timedelta(minutes=6),
            completed_at=now - timedelta(minutes=5, seconds=59),
            latency_ms=840,
            outcome=TestOutcome.FAILURE,
        )
        session.add(record)
    record.tenant_id = ACME_TENANT_ID
    record.workflow_run_id = QA057_RUN_ID
    record.trace_id = "trace-qa057-live-run"
    record.provider_type = ProviderType.OPENAI
    record.model_id = "gpt-qa057-live"
    record.started_at = now - timedelta(minutes=6)
    record.completed_at = now - timedelta(minutes=5, seconds=59)
    record.latency_ms = 840
    record.outcome = TestOutcome.FAILURE
    record.normalized_error_category = ErrorCategory.TIMEOUT
    record.retry_attempt_number = 1
    record.retry_decision_summary = {"category": "retryable_timeout"}
    record.breaker_scope = "model-gateway"
    record.breaker_decision_summary = {"state": "closed"}
    record.usage_metadata = {"usage_reference_id": "usage-live-qa057"}
    record.usage_available = True
    record.safe_audit_summary = {
        "summary": "Gateway attempt recorded retryable timeout category.",
        "provider": "OpenAI provider",
        "model": "gpt-qa057-live",
        "credential": "resolved_reference",
        "retry_category": "retryable_timeout",
        "breaker_category": "closed",
        "usage_reference_id": "usage-live-qa057",
    }
    record.created_at = now - timedelta(minutes=6)


def _database_url() -> str:
    value = os.environ.get("DATABASE_URL") or _env_file_value("DATABASE_URL")
    if not value:
        raise RuntimeError("DATABASE_URL is required")
    return value


def _env_file_value(key: str) -> str | None:
    env_file = Path(".env")
    if not env_file.exists():
        return None
    for line in env_file.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name == key:
            return value
    return None


if __name__ == "__main__":
    raise SystemExit(main())
