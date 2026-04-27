from __future__ import annotations

from uuid import UUID

from multi_agent_platform.reliability.models import QuotaCounter, QuotaResourceKind
from multi_agent_platform.reliability.quotas import release_quota, reserve_quota


def test_quota_reservation_and_release_are_bounded() -> None:
    counter = QuotaCounter(
        tenant_id=UUID("00000000-0000-0000-0000-000000000001"),
        resource_kind=QuotaResourceKind.ACTIVE_WORK,
        limit_value=2,
    )
    assert reserve_quota(counter).allowed
    assert reserve_quota(counter).allowed
    denied = reserve_quota(counter)
    assert not denied.allowed
    assert denied.reason_code == "quota_exhausted"
    assert release_quota(counter) == 1
