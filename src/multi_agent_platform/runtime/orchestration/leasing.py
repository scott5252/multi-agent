from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum
from uuid import UUID, uuid4

from multi_agent_platform.runtime.orchestration.models import (
    TERMINAL_RUN_STATUSES,
    RunStatus,
    now_utc,
)


class LeaseStatus(StrEnum):
    ACTIVE = "active"
    RELEASED = "released"
    EXPIRED = "expired"
    COMPLETED = "completed"
    LOST = "lost"


@dataclass(slots=True, frozen=True)
class LeasePolicy:
    expiry_seconds: int = 120
    duplicate_claim_backoff_seconds: float = 1.0

    def expires_at(self, claimed_at: datetime | None = None) -> datetime:
        return (claimed_at or now_utc()) + timedelta(seconds=self.expiry_seconds)


@dataclass(slots=True)
class WorkerLease:
    tenant_id: UUID | None
    workflow_run_id: UUID
    worker_id: str
    run_step_id: UUID | None = None
    worker_lease_id: UUID = field(default_factory=uuid4)
    lease_status: LeaseStatus = LeaseStatus.ACTIVE
    claimed_at: datetime = field(default_factory=now_utc)
    expires_at: datetime = field(default_factory=lambda: LeasePolicy().expires_at())
    last_renewed_at: datetime | None = None
    released_at: datetime | None = None
    claim_attempt: int = 1

    @property
    def is_active(self) -> bool:
        return self.lease_status is LeaseStatus.ACTIVE and self.expires_at > now_utc()

    def renew(self, *, worker_id: str, policy: LeasePolicy) -> None:
        if worker_id != self.worker_id:
            raise ValueError("lease renewal requires the owning worker")
        if self.lease_status is not LeaseStatus.ACTIVE:
            raise ValueError("only active leases can be renewed")
        self.last_renewed_at = now_utc()
        self.expires_at = policy.expires_at(self.last_renewed_at)

    def release(self, status: LeaseStatus = LeaseStatus.RELEASED) -> None:
        self.lease_status = status
        self.released_at = now_utc()


def can_claim_run(status: RunStatus, existing_lease: WorkerLease | None) -> bool:
    if status in TERMINAL_RUN_STATUSES:
        return False
    return existing_lease is None or not existing_lease.is_active
