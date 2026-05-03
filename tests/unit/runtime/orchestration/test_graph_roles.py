from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.runtime.orchestration.graph_roles import (
    DeterministicRoleNodeExecutor,
    RoleExecutionContext,
)


def _context(node_key: str = "calendar-scout-node") -> RoleExecutionContext:
    return RoleExecutionContext(
        workflow_run_id=uuid4(),
        tenant_id=uuid4(),
        trace_id="trace-graph-role",
        node_key=node_key,
        role_key="calendar-scout",
        role_kind="subagent",
        attempt=1,
        input_summary={"upstream_node_keys": ["orchestrator-intake"]},
        pinned_context={"profile_reference_key": "profile-calendar"},
    )


async def test_deterministic_role_executor_returns_safe_success() -> None:
    result = await DeterministicRoleNodeExecutor().execute(_context())

    assert result.succeeded
    assert result.status == "succeeded"
    assert result.structured_output["role_key"] == "calendar-scout"
    assert result.structured_output["upstream_node_keys"] == ["orchestrator-intake"]


async def test_deterministic_role_executor_can_fail_named_nodes() -> None:
    result = await DeterministicRoleNodeExecutor(
        fail_node_keys={"calendar-scout-node"}
    ).execute(_context())

    assert not result.succeeded
    assert result.error_code == "deterministic_role_failure"
