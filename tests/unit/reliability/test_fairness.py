from __future__ import annotations

from uuid import UUID

from multi_agent_platform.reliability.fairness import (
    allocate_tokens,
    choose_next_tenant,
    consume_token,
)
from multi_agent_platform.reliability.models import FairnessWindow


def test_weighted_fairness_prefers_unpaid_debt() -> None:
    first = FairnessWindow(
        tenant_id=UUID("00000000-0000-0000-0000-000000000001"),
        fairness_debt=2,
    )
    second = FairnessWindow(tenant_id=UUID("00000000-0000-0000-0000-000000000002"))
    allocate_tokens([first, second], total_tokens=10)
    selection = choose_next_tenant([first, second])
    assert selection is not None
    assert selection.tenant_id == first.tenant_id
    consume_token(first)
    assert first.consumed_tokens == 1
