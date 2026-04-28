from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.agents.service import (
    AgentProfileActivationError,
    AgentProfileService,
)
from multi_agent_platform.db.repositories.agent_profiles import (
    StaleAgentProfileRevisionError,
)


async def test_profile_service_creates_draft_rejects_stale_save_and_activates(
    session,
) -> None:
    service = AgentProfileService.from_session(session)
    created = await service.create_profile(
        scope_type="tenant",
        tenant_id=uuid4(),
        agent_key="planner",
        agent_kind="agent",
        display_name="Planner",
        purpose="Plan work",
        principal_id="tenant-admin",
    )
    revision = await service.save_draft_revision(
        draft=created.draft,
        expected_revision_number=0,
        purpose="Plan work",
        prompt_references=[{"purpose": "system", "prompt_version_id": str(uuid4())}],
        model_routing_hints={"provider": "openai"},
        memory_scope_policy={"scope": "tenant"},
        skill_requirements=[{"skill": "planning"}],
        tool_policy_expectations=[{"category": "read"}],
        output_contract_expectations={"type": "object"},
        test_suite_requirements=[{"suite": "planner-smoke"}],
        principal_id="tenant-admin",
    )

    with pytest.raises(StaleAgentProfileRevisionError):
        await service.save_draft_revision(
            draft=created.draft,
            expected_revision_number=0,
            purpose="Plan work",
            prompt_references=[],
            model_routing_hints={},
            memory_scope_policy={},
            skill_requirements=[],
            tool_policy_expectations=[],
            output_contract_expectations={},
            test_suite_requirements=[],
            principal_id="tenant-admin",
        )

    validation = await service.validate_revision(
        draft_revision=revision,
        principal_id="tenant-admin",
    )
    version = await service.activate(
        profile=created.profile,
        draft=created.draft,
        draft_revision=revision,
        validation_result=validation,
        principal_id="tenant-admin",
        reason="Initial activation",
    )

    assert validation.status == "passed"
    assert version.version_sequence == 1
    assert created.profile.active_profile_version_id == version.agent_profile_version_id


async def test_profile_service_blocks_activation_without_passing_validation(
    session,
) -> None:
    service = AgentProfileService.from_session(session)
    created = await service.create_profile(
        scope_type="tenant",
        tenant_id=uuid4(),
        agent_key="planner",
        agent_kind="agent",
        display_name="Planner",
        purpose="Plan work",
        principal_id="tenant-admin",
    )
    revision = await service.save_draft_revision(
        draft=created.draft,
        expected_revision_number=0,
        purpose="Plan work",
        prompt_references=[],
        model_routing_hints={},
        memory_scope_policy={},
        skill_requirements=[],
        tool_policy_expectations=[],
        output_contract_expectations={},
        test_suite_requirements=[],
        principal_id="tenant-admin",
    )
    validation = await service.validate_revision(
        draft_revision=revision,
        principal_id="tenant-admin",
    )

    with pytest.raises(AgentProfileActivationError):
        await service.activate(
            profile=created.profile,
            draft=created.draft,
            draft_revision=revision,
            validation_result=validation,
            principal_id="tenant-admin",
            reason="Initial activation",
        )
