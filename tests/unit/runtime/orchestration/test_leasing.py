from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

import pytest

from multi_agent_platform.runtime.orchestration.leasing import (
    LeasePolicy,
    LeaseStatus,
    WorkerLease,
    can_claim_run,
)
from multi_agent_platform.runtime.orchestration.models import RunStatus, now_utc


def test_lease_expiry_default_is_two_minutes() -> None:
    claimed_at = now_utc()
    expires_at = LeasePolicy().expires_at(claimed_at)

    assert expires_at - claimed_at == timedelta(seconds=120)


def test_terminal_run_cannot_be_claimed() -> None:
    assert not can_claim_run(RunStatus.SUCCEEDED, None)


def test_lease_renewal_requires_owner() -> None:
    lease = WorkerLease(
        tenant_id=uuid4(),
        workflow_run_id=uuid4(),
        worker_id="worker-a",
    )

    with pytest.raises(ValueError, match="owning worker"):
        lease.renew(worker_id="worker-b", policy=LeasePolicy())


def test_lease_renewal_extends_owner_expiry() -> None:
    lease = WorkerLease(
        tenant_id=uuid4(),
        workflow_run_id=uuid4(),
        worker_id="worker-a",
    )
    before = lease.expires_at

    lease.renew(worker_id="worker-a", policy=LeasePolicy(expiry_seconds=240))

    assert lease.last_renewed_at is not None
    assert lease.expires_at > before


def test_release_marks_lease_released() -> None:
    lease = WorkerLease(
        tenant_id=uuid4(),
        workflow_run_id=uuid4(),
        worker_id="worker-a",
    )

    lease.release(LeaseStatus.COMPLETED)

    assert lease.lease_status is LeaseStatus.COMPLETED
    assert lease.released_at is not None


def test_expired_lease_can_be_claimed() -> None:
    lease = WorkerLease(
        tenant_id=uuid4(),
        workflow_run_id=uuid4(),
        worker_id="worker-a",
        expires_at=now_utc() - timedelta(seconds=1),
    )

    assert can_claim_run(RunStatus.RUNNABLE, lease)
