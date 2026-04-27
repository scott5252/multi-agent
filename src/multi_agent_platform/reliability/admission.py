from __future__ import annotations

from datetime import timedelta
from uuid import UUID

from multi_agent_platform.reliability.models import (
    AdmissionDecision,
    AdmissionDecisionKind,
    CapacitySnapshot,
    ReliabilityPolicy,
    now_utc,
)


def decide_admission(
    *,
    tenant_id: UUID,
    policy: ReliabilityPolicy,
    snapshot: CapacitySnapshot,
    submitted_count: int,
    active_count: int,
    trace_id: str | None = None,
) -> AdmissionDecision:
    settings = policy.settings
    if submitted_count >= settings.max_submitted_work:
        return AdmissionDecision(
            tenant_id=tenant_id,
            decision=AdmissionDecisionKind.REJECTED,
            reason_code="submitted_quota_exhausted",
            policy_id=policy.policy_id,
            policy_version=policy.policy_version,
            capacity_snapshot_id=snapshot.capacity_snapshot_id,
            trace_id=trace_id,
        )
    if active_count >= settings.max_active_work:
        return AdmissionDecision(
            tenant_id=tenant_id,
            decision=AdmissionDecisionKind.QUEUED,
            reason_code="active_work_quota_full",
            policy_id=policy.policy_id,
            policy_version=policy.policy_version,
            capacity_snapshot_id=snapshot.capacity_snapshot_id,
            trace_id=trace_id,
        )
    if snapshot.db_pool_available <= 0 or snapshot.db_pool_wait_p95_ms > 250:
        return AdmissionDecision(
            tenant_id=tenant_id,
            decision=AdmissionDecisionKind.DELAYED,
            reason_code="db_pool_pressure",
            available_at=now_utc() + timedelta(seconds=15),
            policy_id=policy.policy_id,
            policy_version=policy.policy_version,
            capacity_snapshot_id=snapshot.capacity_snapshot_id,
            trace_id=trace_id,
        )
    if snapshot.open_breaker_count > 0:
        return AdmissionDecision(
            tenant_id=tenant_id,
            decision=AdmissionDecisionKind.THROTTLED,
            reason_code="breaker_open",
            policy_id=policy.policy_id,
            policy_version=policy.policy_version,
            capacity_snapshot_id=snapshot.capacity_snapshot_id,
            trace_id=trace_id,
        )
    return AdmissionDecision(
        tenant_id=tenant_id,
        decision=AdmissionDecisionKind.ACCEPTED,
        reason_code="capacity_available",
        policy_id=policy.policy_id,
        policy_version=policy.policy_version,
        capacity_snapshot_id=snapshot.capacity_snapshot_id,
        trace_id=trace_id,
    )
