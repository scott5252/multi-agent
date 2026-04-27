from __future__ import annotations

from uuid import UUID

import pytest

from multi_agent_platform.reliability.models import (
    CapacitySnapshot,
    ReliabilityPolicy,
    ReliabilityPolicySettings,
    ReliabilityScopeType,
    WorkerContext,
)

TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")
RUN_ID = UUID("00000000-0000-0000-0000-000000000101")
STEP_ID = UUID("00000000-0000-0000-0000-000000000201")
LEASE_ID = UUID("00000000-0000-0000-0000-000000000301")
BUNDLE_ID = UUID("00000000-0000-0000-0000-000000000401")
POLICY_ID = UUID("00000000-0000-0000-0000-000000000501")


@pytest.fixture
def reliability_policy() -> ReliabilityPolicy:
    return ReliabilityPolicy(
        tenant_id=TENANT_ID,
        scope_type=ReliabilityScopeType.TENANT,
        scope_key=None,
        settings=ReliabilityPolicySettings(),
        policy_id=POLICY_ID,
    )


@pytest.fixture
def capacity_snapshot() -> CapacitySnapshot:
    return CapacitySnapshot(db_pool_available=10)


@pytest.fixture
def worker_context() -> WorkerContext:
    return WorkerContext(
        tenant_id=TENANT_ID,
        workflow_run_id=RUN_ID,
        run_step_id=STEP_ID,
        worker_id="worker-a",
        worker_lease_id=LEASE_ID,
        claim_attempt=1,
        run_bundle_id=BUNDLE_ID,
        bundle_digest="a" * 64,
        trace_id="trace-1",
        policy_id=POLICY_ID,
        policy_version=1,
    )


FAILURE_INJECTION_POINTS = (
    "after_claim",
    "after_checkpoint",
    "after_side_effect_intent",
    "after_side_effect_applied_before_state_advance",
    "after_retry_scheduled",
    "during_compensation",
    "during_artifact_export",
)
