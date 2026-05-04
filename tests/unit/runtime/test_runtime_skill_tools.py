from __future__ import annotations

import pytest

from multi_agent_platform.runtime.skill_tools import execute_role_skill_tools
from multi_agent_platform.skill_execution.gateway import SkillExecutionGateway
from multi_agent_platform.skill_execution.policies import SkillExecutionPolicyBundle
from multi_agent_platform.skill_execution.schemas import ExecutionStatus


@pytest.mark.asyncio
async def test_execute_role_skill_tools_returns_outputs_by_tool_name() -> None:
    tenant_id = "11111111-1111-1111-1111-111111111111"
    gateway = SkillExecutionGateway(
        policy_bundle=SkillExecutionPolicyBundle.local_qa_default(tenant_id=tenant_id)
    )

    results = await execute_role_skill_tools(
        gateway=gateway,
        tenant_id=tenant_id,
        actor_id="qa",
        role_node_id="daily-briefing-calendar",
        skill_package="daily-briefing-calendar",
        skill_version="1.0.0",
        tool_requests=[
            {
                "tool_name": "google_calendar.events.read",
                "input": {"date": "2026-05-04"},
            },
            {
                "tool_name": "weather.forecast.read",
                "input": {"location": "Providence"},
            },
        ],
    )

    assert set(results) == {
        "google_calendar.events.read",
        "weather.forecast.read",
    }
    assert all(item.status is ExecutionStatus.SUCCEEDED for item in results.values())
