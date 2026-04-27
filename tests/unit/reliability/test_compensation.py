from __future__ import annotations

from uuid import UUID

import pytest

from multi_agent_platform.reliability.compensation import (
    CompensationRequest,
    request_compensation,
)
from tests.fixtures.reliability import RUN_ID, STEP_ID, TENANT_ID


def test_compensation_request_is_at_most_once() -> None:
    existing: set[tuple[UUID, UUID, str]] = set()
    intent_id = UUID("00000000-0000-0000-0000-000000000301")
    request = CompensationRequest(
        tenant_id=TENANT_ID,
        workflow_run_id=RUN_ID,
        run_step_id=STEP_ID,
        side_effect_intent_id=intent_id,
        hook_ref="undo-charge",
    )
    assert request_compensation(existing=existing, request=request).status == "queued"
    with pytest.raises(ValueError):
        request_compensation(existing=existing, request=request)
