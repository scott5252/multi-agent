from __future__ import annotations

from uuid import UUID

from multi_agent_platform.reliability.leases import (
    FencingToken,
    LeasePolicy,
    tuned_expiry_seconds,
    validate_fencing_token,
)
from multi_agent_platform.reliability.models import RecoveryOutcome, now_utc


def test_lease_policy_deadlines_and_fencing() -> None:
    claimed = now_utc()
    policy = LeasePolicy(expiry_seconds=120)
    assert policy.renewal_deadline(claimed) < policy.expires_at(claimed)
    token = FencingToken(UUID("00000000-0000-0000-0000-000000000001"), 1)
    assert validate_fencing_token(token, active=token) is RecoveryOutcome.RESUMED
    stale = FencingToken(UUID("00000000-0000-0000-0000-000000000002"), 1)
    assert (
        validate_fencing_token(stale, active=token)
        is RecoveryOutcome.STALE_TOKEN_SUPPRESSED
    )


def test_tuned_expiry_uses_heartbeat_floor() -> None:
    assert tuned_expiry_seconds(p99_heartbeat_seconds=10) == 30
    assert tuned_expiry_seconds(p99_heartbeat_seconds=90) == 180
