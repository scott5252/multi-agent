from __future__ import annotations

import pytest

from multi_agent_platform.reliability.dead_letters import create_dead_letter
from multi_agent_platform.reliability.models import FailureCategory
from tests.fixtures.reliability import RUN_ID, TENANT_ID


@pytest.mark.performance
def test_compensation_dead_letter_profile_records_safe_summary() -> None:
    record = create_dead_letter(
        tenant_id=TENANT_ID,
        source_kind="compensation_request",
        source_id=RUN_ID,
        failure_category=FailureCategory.TIMEOUT,
        latest_state={"status": "timed_out"},
    )
    assert record.latest_state["status"] == "timed_out"
