from __future__ import annotations

from uuid import UUID

from multi_agent_platform.reliability.dead_letters import create_dead_letter
from multi_agent_platform.reliability.models import (
    FailureCategory,
    RecommendedAction,
)
from tests.fixtures.reliability import TENANT_ID


def test_dead_letter_contains_safe_state_and_recommended_action() -> None:
    record = create_dead_letter(
        tenant_id=TENANT_ID,
        source_kind="run_step",
        source_id=UUID("00000000-0000-0000-0000-000000000201"),
        failure_category=FailureCategory.UNKNOWN_SIDE_EFFECT,
        latest_state={"status": "failed"},
    )
    assert record.recommended_action is RecommendedAction.OPERATOR_INTERVENTION
    assert record.latest_state == {"status": "failed"}
