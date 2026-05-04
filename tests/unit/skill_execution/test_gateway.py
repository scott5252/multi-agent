from __future__ import annotations

import pytest

from multi_agent_platform.skill_execution.adapters import DAILY_BRIEFING_TOOL_NAMES
from multi_agent_platform.skill_execution.gateway import SkillExecutionGateway
from multi_agent_platform.skill_execution.policies import SkillExecutionPolicyBundle
from multi_agent_platform.skill_execution.schemas import (
    ExecutionMode,
    ExecutionStatus,
    SkillToolExecutionRequest,
)

TENANT_ID = "11111111-1111-1111-1111-111111111111"


@pytest.mark.asyncio
async def test_gateway_executes_all_daily_briefing_tools_with_safe_summaries() -> None:
    gateway = SkillExecutionGateway(
        policy_bundle=SkillExecutionPolicyBundle.local_qa_default(tenant_id=TENANT_ID)
    )

    for tool_name in DAILY_BRIEFING_TOOL_NAMES:
        adapter = gateway.adapters[tool_name]
        result = await gateway.execute(
            SkillToolExecutionRequest(
                tenant_id=TENANT_ID,
                actor_id="qa",
                workflow_run_id="33333333-3333-3333-3333-333333333333",
                role_node_id="calendar-scout",
                skill_package=adapter.skill_package,
                skill_version="1.0.0",
                tool_name=tool_name,
                execution_mode=ExecutionMode.MOCK,
                input={"date": "2026-05-04", "location": "Providence"},
                contract_version="v1",
            )
        )

        assert result.status is ExecutionStatus.SUCCEEDED
        assert result.output["contract_version"] == "v1"
        assert result.policy_decisions
        assert "secret" not in result.request_summary.lower()
        assert "token" not in result.response_summary.lower()


@pytest.mark.asyncio
async def test_gateway_records_diagnostic_results() -> None:
    gateway = SkillExecutionGateway(
        policy_bundle=SkillExecutionPolicyBundle.local_qa_default(tenant_id=TENANT_ID)
    )

    diagnostics = await gateway.run_mock_diagnostics(tenant_id=TENANT_ID, actor_id="qa")
    records = gateway.diagnostic_records()

    assert len(diagnostics) == len(DAILY_BRIEFING_TOOL_NAMES)
    assert all(result.status is ExecutionStatus.SUCCEEDED for result in diagnostics)
    assert {record.tool_name for record in records} == set(DAILY_BRIEFING_TOOL_NAMES)
    assert all(record.latest_summary for record in records)
