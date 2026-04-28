from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.agents.resolution import AgentProfileCandidate
from multi_agent_platform.api.schemas.workflow_registry import (
    AgentRoleDefinition,
    WorkflowDraftDocument,
    WorkflowKind,
    WorkflowNodeDefinition,
    WorkflowNodeType,
)
from multi_agent_platform.prompts.workflow_hooks import (
    validate_workflow_prompt_profiles,
)


def test_workflow_validation_resolves_profile_and_prompt_pins() -> None:
    tenant_id = uuid4()
    profile_version_id = uuid4()
    document = WorkflowDraftDocument(
        workflow_key="qa-profile-workflow",
        display_name="QA Profile Workflow",
        workflow_kind=WorkflowKind.MAIN_WORKFLOW,
        entry_node_key="planner",
        roles=[
            AgentRoleDefinition(
                role_key="planner",
                display_name="Planner",
                purpose="Plan the work",
            )
        ],
        nodes=[
            WorkflowNodeDefinition(
                node_key="planner",
                node_type=WorkflowNodeType.ROLE,
                display_name="Planner",
                role_key="planner",
            )
        ],
    )

    result = validate_workflow_prompt_profiles(
        document=document,
        tenant_id=tenant_id,
        profile_candidates=(
            AgentProfileCandidate(
                agent_profile_version_id=profile_version_id,
                scope_type="tenant",
                tenant_id=tenant_id,
                agent_key="planner",
                agent_kind="agent",
                status="active",
                granted_tenant_ids=(),
            ),
        ),
        prompt_versions_by_profile={profile_version_id: ("prompt-v1",)},
    )

    assert result.blocking_issue_count == 0
    assert result.pins[0].agent_profile_version_id == profile_version_id
    assert result.pins[0].prompt_version_ids == ("prompt-v1",)


def test_workflow_validation_reports_missing_profile_as_blocking() -> None:
    tenant_id = uuid4()
    document = WorkflowDraftDocument(
        workflow_key="qa-profile-workflow",
        display_name="QA Profile Workflow",
        workflow_kind=WorkflowKind.MAIN_WORKFLOW,
        entry_node_key="planner",
        roles=[
            AgentRoleDefinition(
                role_key="planner",
                display_name="Planner",
                purpose="Plan the work",
            )
        ],
        nodes=[
            WorkflowNodeDefinition(
                node_key="planner",
                node_type=WorkflowNodeType.ROLE,
                display_name="Planner",
                role_key="planner",
            )
        ],
    )

    result = validate_workflow_prompt_profiles(
        document=document,
        tenant_id=tenant_id,
        profile_candidates=(),
    )

    assert result.blocking_issue_count == 1
    assert result.findings[0]["category"] == "prompt_runtime_profile"
    assert result.pins == ()
