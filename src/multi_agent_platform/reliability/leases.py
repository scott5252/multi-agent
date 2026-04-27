from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from multi_agent_platform.reliability.models import RecoveryOutcome, now_utc


@dataclass(slots=True, frozen=True)
class LeasePolicy:
    expiry_seconds: int = 120
    renewal_seconds: int = 30
    renewal_deadline_fraction: float = 0.5

    def expires_at(self, claimed_at: datetime | None = None) -> datetime:
        return (claimed_at or now_utc()) + timedelta(seconds=self.expiry_seconds)

    def renewal_deadline(self, claimed_at: datetime) -> datetime:
        return claimed_at + timedelta(
            seconds=self.expiry_seconds * self.renewal_deadline_fraction
        )

    def recovery_eligible_at(self, claimed_at: datetime) -> datetime:
        return self.expires_at(claimed_at)


@dataclass(slots=True, frozen=True)
class FencingToken:
    worker_lease_id: UUID
    claim_attempt: int


def validate_fencing_token(
    provided: FencingToken, *, active: FencingToken
) -> RecoveryOutcome:
    if provided == active:
        return RecoveryOutcome.RESUMED
    return RecoveryOutcome.STALE_TOKEN_SUPPRESSED


def tuned_expiry_seconds(
    *, p99_heartbeat_seconds: float, minimum_seconds: int = 30
) -> int:
    if p99_heartbeat_seconds < 0:
        raise ValueError("heartbeat interval cannot be negative")
    return max(int(2 * p99_heartbeat_seconds), minimum_seconds)
