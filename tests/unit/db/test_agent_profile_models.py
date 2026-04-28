from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.db.base import Base
from multi_agent_platform.db.models import import_models
from multi_agent_platform.db.models.agent_profiles import (
    ActiveAgentProfilePointer,
    AgentProfileVersion,
    AgentRuntimeProfile,
)


def test_agent_profile_tables_are_registered() -> None:
    import_models()

    assert "agent_runtime_profiles" in Base.metadata.tables
    assert "agent_profile_versions" in Base.metadata.tables
    assert "active_agent_profile_pointers" in Base.metadata.tables


def test_agent_profile_models_track_active_pointer_and_contract_sections() -> None:
    tenant_id = uuid4()
    profile = AgentRuntimeProfile(
        scope_type="tenant",
        tenant_id=tenant_id,
        agent_key="planner",
        agent_kind="agent",
        display_name="Planner",
        purpose="Plan work",
        created_by_principal_id="tenant-admin",
    )
    version = AgentProfileVersion(
        agent_runtime_profile_id=uuid4(),
        scope_type="tenant",
        tenant_id=tenant_id,
        agent_key=profile.agent_key,
        agent_kind=profile.agent_kind,
        version_sequence=1,
        display_version="v1",
        activated_from_draft_id=uuid4(),
        activated_from_revision_id=uuid4(),
        validation_result_id=uuid4(),
        purpose=profile.purpose,
        prompt_references_json=[],
        model_routing_hints_json={},
        memory_scope_policy_json={},
        skill_requirements_json=[],
        tool_policy_expectations_json=[],
        output_contract_expectations_json={},
        test_suite_requirements_json=[],
        safe_summary_json={},
        activated_by_principal_id="tenant-admin",
        activation_reason="Initial activation",
    )
    pointer = ActiveAgentProfilePointer(
        scope_type="tenant",
        tenant_id=tenant_id,
        agent_kind="agent",
        agent_key="planner",
        active_profile_version_id=uuid4(),
        activated_by_principal_id="tenant-admin",
        activation_reason="Initial activation",
    )

    assert profile.agent_key == "planner"
    assert version.prompt_references_json == []
    assert pointer.active_profile_version_id is not None
