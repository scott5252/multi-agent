from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

import pytest

from multi_agent_platform.api.routers import admin_agent_profiles
from multi_agent_platform.api.schemas.agent_profiles import (
    ActivationRequest,
    ProfileCreate,
    ProfileDraftSave,
)


class _FakeRepository:
    profile_id = uuid4()
    draft_id = uuid4()
    revision_id = uuid4()
    validation_id = uuid4()
    version_id = uuid4()
    tenant_id = uuid4()

    def __init__(self, session: object) -> None:
        self.session = session

    async def create_profile_with_draft(self, **kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(
            profile=SimpleNamespace(agent_runtime_profile_id=self.profile_id),
            draft=SimpleNamespace(
                agent_profile_draft_id=self.draft_id,
                current_revision_number=0,
            ),
        )

    async def get_active_draft(
        self,
        agent_runtime_profile_id: object,
    ) -> SimpleNamespace:
        return SimpleNamespace(
            agent_runtime_profile_id=agent_runtime_profile_id,
            agent_profile_draft_id=self.draft_id,
            current_revision_number=1,
            last_validation_result_id=self.validation_id,
        )

    async def get_latest_revision(self, draft: object) -> SimpleNamespace:
        return SimpleNamespace(
            agent_profile_draft_revision_id=self.revision_id,
            prompt_references_json=[],
            model_routing_hints_json={},
            memory_scope_policy_json={},
            skill_requirements_json=[],
            tool_policy_expectations_json=[],
            output_contract_expectations_json={},
            test_suite_requirements_json=[],
        )

    async def get_validation_result(
        self,
        validation_result_id: object,
    ) -> SimpleNamespace:
        return SimpleNamespace(
            agent_profile_validation_result_id=validation_result_id,
            status="passed",
            blocking_issue_count=0,
            findings_json=[],
        )

    async def get_profile(self, agent_runtime_profile_id: object) -> SimpleNamespace:
        return SimpleNamespace(
            agent_runtime_profile_id=agent_runtime_profile_id,
            scope_type="tenant",
            tenant_id=self.tenant_id,
        )


class _FakeService:
    def __init__(self, repository: _FakeRepository) -> None:
        self.repository = repository

    async def save_draft_revision(self, **kwargs: object) -> SimpleNamespace:
        draft = kwargs["draft"]
        draft.current_revision_number = 2
        return SimpleNamespace()

    async def validate_revision(self, **kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(
            agent_profile_validation_result_id=_FakeRepository.validation_id,
            status="passed",
            blocking_issue_count=0,
            advisory_issue_count=0,
            findings_json=[],
        )

    async def activate(self, **kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(
            agent_profile_version_id=_FakeRepository.version_id,
            agent_runtime_profile_id=_FakeRepository.profile_id,
            agent_key="planner",
            agent_kind="agent",
            display_version="v1",
            status="active",
        )


@pytest.mark.asyncio
async def test_agent_profile_json_routes_use_repository_and_service(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        admin_agent_profiles,
        "AgentProfileRepository",
        _FakeRepository,
    )
    monkeypatch.setattr(admin_agent_profiles, "AgentProfileService", _FakeService)
    tenant_id = uuid4()
    _FakeRepository.tenant_id = tenant_id
    principal = SimpleNamespace(
        principal_id="tenant-admin",
        tenant_id=tenant_id,
        role_codes=("tenant_admin",),
    )
    session = SimpleNamespace()
    profile_id = _FakeRepository.profile_id

    created = await admin_agent_profiles.create_agent_profile(
        payload=ProfileCreate(
            scope_type="tenant",
            tenant_id=tenant_id,
            agent_key="planner",
            agent_kind="agent",
            display_name="Planner",
            purpose="Plan",
        ),
        principal=principal,
        session=session,
    )
    saved = await admin_agent_profiles.save_agent_profile_draft(
        agent_runtime_profile_id=profile_id,
        payload=ProfileDraftSave(
            expected_revision_number=1,
            purpose="Plan",
            prompt_references=[],
            model_routing_hints={},
            memory_scope_policy={},
            skill_requirements=[],
            tool_policy_expectations=[],
            output_contract_expectations={},
            test_suite_requirements=[],
        ),
        principal=principal,
        session=session,
    )
    validation = await admin_agent_profiles.validate_agent_profile_draft(
        agent_runtime_profile_id=profile_id,
        principal=principal,
        session=session,
    )
    activated = await admin_agent_profiles.activate_agent_profile(
        agent_runtime_profile_id=profile_id,
        payload=ActivationRequest(reason="QA"),
        principal=principal,
        session=session,
    )

    assert created.current_revision_number == 0
    assert saved.current_revision_number == 2
    assert validation.status == "passed"
    assert activated.agent_profile_version_id == _FakeRepository.version_id
