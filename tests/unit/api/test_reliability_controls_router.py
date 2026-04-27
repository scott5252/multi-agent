from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from multi_agent_platform.api.routers import reliability_controls as router
from multi_agent_platform.api.schemas.reliability import (
    BreakerResetRequest,
    PolicyChangeRequest,
)
from multi_agent_platform.reliability.models import BreakerState

TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")


@pytest.mark.asyncio
async def test_reliability_router_empty_list_handlers() -> None:
    session = object()
    assert (await router.get_dashboard(session=session)).status == "available"  # type: ignore[arg-type]
    assert (await router.list_policies(session=session)).items == []  # type: ignore[arg-type]
    assert (await router.list_admission_decisions(session=session)).items == []  # type: ignore[arg-type]
    assert (await router.list_breakers(session=session)).items == []  # type: ignore[arg-type]
    assert (await router.list_retries(session=session)).items == []  # type: ignore[arg-type]
    assert (await router.list_compensations(session=session)).items == []  # type: ignore[arg-type]
    assert (await router.list_dead_letters(session=session)).items == []  # type: ignore[arg-type]
    assert (await router.list_load_test_reports(session=session)).items == []  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_reliability_router_action_handlers() -> None:
    session = object()
    change = await router.create_policy(
        PolicyChangeRequest(
            tenant_id=TENANT_ID,
            scope_type="tenant",
            settings={},
            reason="test",
            unsafe_override=True,
        ),
        session=session,  # type: ignore[arg-type]
    )
    assert change.validation_outcome == "override_accepted"
    breaker = await router.reset_breaker(
        uuid4(),
        BreakerResetRequest(reason="healthy", target_state=BreakerState.HALF_OPEN),
        session=session,  # type: ignore[arg-type]
    )
    assert breaker.state is BreakerState.HALF_OPEN
    action = await router.act_on_dead_letter(
        uuid4(),
        "resolve",
        session=session,  # type: ignore[arg-type]
    )
    assert action["status"] == "accepted"
