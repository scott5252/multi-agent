from __future__ import annotations

import pytest

from multi_agent_platform.skill_execution.adapters import (
    DAILY_BRIEFING_TOOL_NAMES,
    default_adapter_registry,
)
from multi_agent_platform.skill_execution.schemas import (
    ExecutionMode,
    SkillToolExecutionRequest,
)


@pytest.mark.asyncio
async def test_daily_briefing_adapters_return_contract_outputs() -> None:
    registry = default_adapter_registry()

    for tool_name in DAILY_BRIEFING_TOOL_NAMES:
        adapter = registry[tool_name]
        result = await adapter.execute(
            SkillToolExecutionRequest(
                tenant_id="11111111-1111-1111-1111-111111111111",
                actor_id="qa",
                skill_package=adapter.skill_package,
                skill_version="1.0.0",
                tool_name=tool_name,
                execution_mode=ExecutionMode.MOCK,
                input={"date": "2026-05-04", "location": "Providence"},
            )
        )

        assert result.tool_name == tool_name
        assert result.contract_version == "v1"
        assert result.output


def test_adapter_registry_declares_read_only_domains_and_credentials() -> None:
    registry = default_adapter_registry()

    assert set(registry) == set(DAILY_BRIEFING_TOOL_NAMES)
    for adapter in registry.values():
        assert adapter.read_only is True
        assert adapter.allowed_domains
        assert adapter.action_category == "read"
        assert adapter.required_credential_kind
