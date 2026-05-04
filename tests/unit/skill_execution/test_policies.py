from __future__ import annotations

import pytest

from multi_agent_platform.skill_execution.adapters import default_adapter_registry
from multi_agent_platform.skill_execution.gateway import SkillExecutionGateway
from multi_agent_platform.skill_execution.policies import SkillExecutionPolicyBundle
from multi_agent_platform.skill_execution.schemas import (
    CredentialResolutionSummary,
    ExecutionMode,
    ExecutionStatus,
    SkillToolExecutionRequest,
)

TENANT_ID = "11111111-1111-1111-1111-111111111111"


def _request(
    tool_name: str = "google_calendar.events.read",
) -> SkillToolExecutionRequest:
    adapter = default_adapter_registry()[tool_name]
    return SkillToolExecutionRequest(
        tenant_id=TENANT_ID,
        actor_id="qa",
        skill_package=adapter.skill_package,
        skill_version="1.0.0",
        tool_name=tool_name,
        execution_mode=ExecutionMode.MOCK,
        input={"date": "2026-05-04"},
    )


def _policy() -> SkillExecutionPolicyBundle:
    return SkillExecutionPolicyBundle.local_qa_default(tenant_id=TENANT_ID)


@pytest.mark.asyncio
async def test_missing_credential_denies_before_adapter_invocation() -> None:
    gateway = SkillExecutionGateway(policy_bundle=_policy().without_credentials())

    result = await gateway.execute(_request())

    assert result.status is ExecutionStatus.DENIED
    assert result.error_code == "credential_unsatisfied"
    assert gateway.adapter_invocation_count("google_calendar.events.read") == 0


@pytest.mark.asyncio
async def test_blocked_outbound_domain_denies_before_adapter_invocation() -> None:
    policy = _policy().model_copy(update={"allowed_outbound_domains": frozenset()})
    gateway = SkillExecutionGateway(policy_bundle=policy)

    result = await gateway.execute(_request("news.search"))

    assert result.status is ExecutionStatus.DENIED
    assert result.error_code == "domain_denied"
    assert gateway.adapter_invocation_count("news.search") == 0


@pytest.mark.asyncio
async def test_side_effect_request_is_blocked_by_default() -> None:
    gateway = SkillExecutionGateway(policy_bundle=_policy())
    request = _request().model_copy(update={"side_effect_requested": True})

    result = await gateway.execute(request)

    assert result.status is ExecutionStatus.DENIED
    assert result.error_code == "side_effect_denied"
    assert gateway.adapter_invocation_count("google_calendar.events.read") == 0


@pytest.mark.asyncio
async def test_cross_tenant_credential_is_denied() -> None:
    credential = CredentialResolutionSummary(
        required=True,
        credential_kind="google_calendar_oauth",
        tenant_id="22222222-2222-2222-2222-222222222222",
        reference="delegated:calendar:globex",
        available=True,
        safe_label="Globex calendar",
    )
    policy = _policy().model_copy(
        update={"credential_summaries": {"google_calendar_oauth": credential}}
    )
    gateway = SkillExecutionGateway(policy_bundle=policy)

    result = await gateway.execute(_request())

    assert result.status is ExecutionStatus.DENIED
    assert result.error_code == "credential_tenant_mismatch"


@pytest.mark.asyncio
async def test_uninstalled_tool_is_denied() -> None:
    policy = _policy().model_copy(update={"installed_skill_versions": {}})
    gateway = SkillExecutionGateway(policy_bundle=policy)

    result = await gateway.execute(_request())

    assert result.status is ExecutionStatus.DENIED
    assert result.error_code == "skill_not_installed"


@pytest.mark.asyncio
async def test_local_live_probe_is_denied() -> None:
    gateway = SkillExecutionGateway(policy_bundle=_policy())
    request = _request().model_copy(update={"execution_mode": ExecutionMode.LIVE_PROBE})

    result = await gateway.execute(request)

    assert result.status is ExecutionStatus.DENIED
    assert result.error_code == "live_probe_denied"
