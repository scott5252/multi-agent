from __future__ import annotations

from uuid import UUID

from multi_agent_platform.reliability.admission import decide_admission
from multi_agent_platform.reliability.models import (
    AdmissionDecisionKind,
    CapacitySnapshot,
    ReliabilityPolicy,
)

TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")


def test_admission_accepts_when_capacity_available(
    reliability_policy: ReliabilityPolicy, capacity_snapshot: CapacitySnapshot
) -> None:
    decision = decide_admission(
        tenant_id=TENANT_ID,
        policy=reliability_policy,
        snapshot=capacity_snapshot,
        submitted_count=0,
        active_count=0,
    )
    assert decision.decision is AdmissionDecisionKind.ACCEPTED


def test_admission_exposes_overload_statuses(
    reliability_policy: ReliabilityPolicy,
) -> None:
    rejected = decide_admission(
        tenant_id=TENANT_ID,
        policy=reliability_policy,
        snapshot=CapacitySnapshot(),
        submitted_count=1_000,
        active_count=0,
    )
    delayed = decide_admission(
        tenant_id=TENANT_ID,
        policy=reliability_policy,
        snapshot=CapacitySnapshot(db_pool_available=0),
        submitted_count=0,
        active_count=0,
    )
    throttled = decide_admission(
        tenant_id=TENANT_ID,
        policy=reliability_policy,
        snapshot=CapacitySnapshot(db_pool_available=10, open_breaker_count=1),
        submitted_count=0,
        active_count=0,
    )
    assert rejected.decision is AdmissionDecisionKind.REJECTED
    assert delayed.decision is AdmissionDecisionKind.DELAYED
    assert throttled.decision is AdmissionDecisionKind.THROTTLED
