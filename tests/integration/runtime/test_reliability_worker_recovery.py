from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.reliability.leases import FencingToken, validate_fencing_token
from multi_agent_platform.reliability.models import RecoveryOutcome


def test_competing_recovery_suppresses_stale_worker_return() -> None:
    recovered = FencingToken(uuid4(), 3)
    stale = FencingToken(uuid4(), 2)
    assert (
        validate_fencing_token(stale, active=recovered)
        is RecoveryOutcome.STALE_TOKEN_SUPPRESSED
    )
