from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.reliability.leases import FencingToken, validate_fencing_token
from multi_agent_platform.reliability.models import RecoveryOutcome


def test_in_flight_compatibility_rejects_stale_fencing_tokens() -> None:
    active = FencingToken(worker_lease_id=uuid4(), claim_attempt=2)
    stale = FencingToken(worker_lease_id=active.worker_lease_id, claim_attempt=1)
    assert (
        validate_fencing_token(stale, active=active)
        is RecoveryOutcome.STALE_TOKEN_SUPPRESSED
    )
