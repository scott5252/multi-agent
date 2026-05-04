from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any
from uuid import UUID

from multi_agent_platform.skill_execution.gateway import SkillExecutionGateway
from multi_agent_platform.skill_execution.schemas import (
    ExecutionMode,
    SkillToolExecutionRequest,
    SkillToolExecutionResult,
)


async def execute_role_skill_tools(
    *,
    gateway: SkillExecutionGateway,
    tenant_id: str | UUID,
    actor_id: str,
    role_node_id: str,
    skill_package: str,
    skill_version: str,
    tool_requests: Sequence[Mapping[str, Any]],
    workflow_run_id: str | UUID | None = None,
) -> dict[str, SkillToolExecutionResult]:
    tenant_uuid = UUID(str(tenant_id))
    workflow_run_uuid = UUID(str(workflow_run_id)) if workflow_run_id else None
    results: dict[str, SkillToolExecutionResult] = {}
    for item in tool_requests:
        tool_name = str(item["tool_name"])
        adapter = gateway.adapters.get(tool_name)
        request = SkillToolExecutionRequest(
            tenant_id=tenant_uuid,
            actor_id=actor_id,
            workflow_run_id=workflow_run_uuid,
            role_node_id=role_node_id,
            skill_package=str(
                item.get("skill_package")
                or (adapter.skill_package if adapter else skill_package)
            ),
            skill_version=str(item.get("skill_version") or skill_version),
            tool_name=tool_name,
            execution_mode=ExecutionMode(str(item.get("execution_mode") or "mock")),
            input=dict(item.get("input") or {}),
            contract_version=str(item.get("contract_version") or "v1"),
            side_effect_requested=bool(item.get("side_effect_requested", False)),
        )
        results[tool_name] = await gateway.execute(request)
    return results
