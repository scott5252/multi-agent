from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest

from multi_agent_platform.api.routers import admin_agent_profiles, admin_prompts


def _container() -> SimpleNamespace:
    return SimpleNamespace()


def _principal() -> SimpleNamespace:
    return SimpleNamespace(
        principal_id="tenant-admin-acme",
        tenant_id=uuid4(),
        role_codes=("tenant_admin",),
    )


class _FakePromptRepository:
    lineage_id = uuid4()
    draft_id = uuid4()
    revision_id = uuid4()
    version_id = uuid4()

    def __init__(self, session: object) -> None:
        self.session = session
        self.lineage = SimpleNamespace(
            prompt_lineage_id=self.lineage_id,
            scope_type="tenant",
            tenant_id=uuid4(),
            slug="triage",
            display_name="Triage",
            purpose="Summarize",
            status="active",
            latest_published_prompt_version_id=self.version_id,
        )
        self.draft = SimpleNamespace(
            prompt_draft_id=self.draft_id,
            prompt_lineage_id=self.lineage_id,
            current_revision_number=1,
            last_validation_result_id=uuid4(),
        )
        self.revision = SimpleNamespace(
            prompt_title="Triage",
            purpose="Summarize",
            usage_notes="",
            template_content="Hello {{name}}",
            variable_declarations_json=[
                {"name": "name", "purpose": "Recipient", "required": True}
            ],
            fixture_value_sets_json=[
                {
                    "fixture_set_id": "default",
                    "label": "Default",
                    "values_by_variable": {"name": "Ada"},
                }
            ],
        )
        self.validation = SimpleNamespace(
            prompt_validation_result_id=uuid4(),
            status="passed",
            blocking_issue_count=0,
            advisory_issue_count=0,
            findings_json=[],
        )
        self.version = SimpleNamespace(
            prompt_version_id=self.version_id,
            prompt_lineage_id=self.lineage_id,
            display_version="v1",
            status="active",
            template_content_sha256="a" * 64,
            safe_summary_json={},
            scope_type="tenant",
            tenant_id=self.lineage.tenant_id,
        )

    async def list_visible_lineages(self, **kwargs: object) -> list[SimpleNamespace]:
        return [self.lineage]

    async def get_lineage(self, prompt_lineage_id: object) -> SimpleNamespace:
        return self.lineage

    async def get_active_draft(self, prompt_lineage_id: object) -> SimpleNamespace:
        return self.draft

    async def get_latest_revision(self, draft: object) -> SimpleNamespace:
        return self.revision

    async def get_validation_result(self, validation_id: object) -> SimpleNamespace:
        return self.validation

    async def get_prompt_version(self, prompt_version_id: object) -> SimpleNamespace:
        return self.version

    async def list_grants_for_version(self, prompt_version_id: object) -> list[object]:
        return []

    async def list_prompt_history(self, **kwargs: object) -> list[dict[str, object]]:
        return [
            {
                "action": "save_draft",
                "actor_principal_id": "tenant-admin-acme",
                "created_at": datetime.now(UTC),
                "outcome": "recorded",
                "reason": "",
                "redacted_diff_summary": {},
            }
        ]


class _FakeAgentProfileRepository:
    profile_id = uuid4()
    draft_id = uuid4()
    version_id = uuid4()

    def __init__(self, session: object) -> None:
        self.session = session
        self.profile = SimpleNamespace(
            agent_runtime_profile_id=self.profile_id,
            scope_type="tenant",
            tenant_id=uuid4(),
            agent_key="planner",
            agent_kind="agent",
            display_name="Planner",
            purpose="Plan",
            status="active",
            active_profile_version_id=self.version_id,
        )
        self.draft = SimpleNamespace(
            agent_profile_draft_id=self.draft_id,
            agent_runtime_profile_id=self.profile_id,
            current_revision_number=1,
            last_validation_result_id=uuid4(),
        )
        self.revision = SimpleNamespace(
            purpose="Plan",
            prompt_references_json=[],
            model_routing_hints_json={},
            memory_scope_policy_json={},
            skill_requirements_json=[],
            tool_policy_expectations_json=[],
            output_contract_expectations_json={},
            test_suite_requirements_json=[],
        )
        self.validation = SimpleNamespace(
            agent_profile_validation_result_id=uuid4(),
            status="passed",
            blocking_issue_count=0,
            advisory_issue_count=0,
            findings_json=[],
        )
        self.version = SimpleNamespace(
            agent_profile_version_id=self.version_id,
            agent_runtime_profile_id=self.profile_id,
            scope_type="tenant",
            tenant_id=self.profile.tenant_id,
            agent_key="planner",
            agent_kind="agent",
            display_version="v1",
            status="active",
            safe_summary_json={},
        )

    async def list_visible_profiles(self, **kwargs: object) -> list[SimpleNamespace]:
        return [self.profile]

    async def get_profile(self, profile_id: object) -> SimpleNamespace:
        return self.profile

    async def get_active_draft(self, profile_id: object) -> SimpleNamespace:
        return self.draft

    async def get_latest_revision(self, draft: object) -> SimpleNamespace:
        return self.revision

    async def get_validation_result(self, validation_id: object) -> SimpleNamespace:
        return self.validation

    async def get_profile_version(self, version_id: object) -> SimpleNamespace:
        return self.version

    async def list_grants_for_version(self, version_id: object) -> list[object]:
        return []

    async def list_profile_history(self, **kwargs: object) -> list[dict[str, object]]:
        return [
            {
                "action": "activate",
                "actor_principal_id": "tenant-admin-acme",
                "created_at": datetime.now(UTC),
                "outcome": "active",
                "reason": "QA",
                "redacted_diff_summary": {},
            }
        ]


@pytest.mark.asyncio
async def test_prompt_browser_route_handlers_redirect_to_react(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(admin_prompts, "PromptRepository", _FakePromptRepository)
    monkeypatch.setattr(
        admin_prompts,
        "_require_prompt_scope_mutation",
        lambda *args, **kwargs: None,
    )
    request = SimpleNamespace(query_params={"tenant_id": str(uuid4()), "q": "triage"})
    principal = _principal()
    session = SimpleNamespace()
    container = _container()
    lineage_id = uuid4()
    version_id = uuid4()

    responses = [
        await admin_prompts.prompt_library_index(
            request=request,
            principal=principal,
            session=session,
            container=container,
        ),
        await admin_prompts.prompt_library_new(
            request=request,
            principal=principal,
            session=session,
            container=container,
        ),
        await admin_prompts.prompt_library_edit(
            prompt_lineage_id=lineage_id,
            request=request,
            principal=principal,
            session=session,
            container=container,
        ),
        await admin_prompts.prompt_library_detail(
            prompt_version_id=version_id,
            request=request,
            principal=principal,
            session=session,
            container=container,
        ),
        await admin_prompts.prompt_library_history(
            prompt_lineage_id=lineage_id,
            request=request,
            principal=principal,
            session=session,
            container=container,
        ),
        await admin_prompts.prompt_library_preview_page(
            prompt_lineage_id=lineage_id,
            request=request,
            principal=principal,
            session=session,
            container=container,
        ),
    ]

    assert [response.status_code for response in responses] == [303] * 6
    assert [response.headers["location"].split("?")[0] for response in responses] == [
        "/admin/app/governance/prompts",
        "/admin/app/governance/prompts/new",
        f"/admin/app/governance/prompts/{lineage_id}/edit",
        f"/admin/app/governance/prompts/versions/{version_id}",
        f"/admin/app/governance/prompts/{lineage_id}/history",
        f"/admin/app/governance/prompts/{lineage_id}/preview",
    ]
    assert "tenant_id=" in responses[0].headers["location"]
    assert "q=triage" in responses[0].headers["location"]


@pytest.mark.asyncio
async def test_agent_profile_browser_route_handlers_redirect_to_react(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        admin_agent_profiles,
        "AgentProfileRepository",
        _FakeAgentProfileRepository,
    )
    monkeypatch.setattr(
        admin_agent_profiles,
        "_require_profile_scope_mutation",
        lambda *args, **kwargs: None,
    )
    request = SimpleNamespace(query_params={"agent_key": "planner"})
    principal = _principal()
    session = SimpleNamespace()
    container = _container()
    profile_id = uuid4()
    version_id = uuid4()

    responses = [
        await admin_agent_profiles.agent_profiles_index(
            request=request,
            principal=principal,
            session=session,
            container=container,
        ),
        await admin_agent_profiles.agent_profiles_new(
            request=request,
            principal=principal,
            session=session,
            container=container,
        ),
        await admin_agent_profiles.agent_profiles_edit(
            agent_runtime_profile_id=profile_id,
            request=request,
            principal=principal,
            session=session,
            container=container,
        ),
        await admin_agent_profiles.agent_profiles_detail(
            agent_profile_version_id=version_id,
            request=request,
            principal=principal,
            session=session,
            container=container,
        ),
        await admin_agent_profiles.agent_profiles_history(
            agent_runtime_profile_id=profile_id,
            request=request,
            principal=principal,
            session=session,
            container=container,
        ),
        await admin_agent_profiles.agent_profiles_resolve(
            request=request,
            principal=principal,
            session=session,
            container=container,
        ),
    ]

    assert [response.status_code for response in responses] == [303] * 6
    assert [response.headers["location"].split("?")[0] for response in responses] == [
        "/admin/app/governance/profiles",
        "/admin/app/governance/profiles/new",
        f"/admin/app/governance/profiles/{profile_id}/edit",
        f"/admin/app/governance/profiles/versions/{version_id}",
        f"/admin/app/governance/profiles/{profile_id}/history",
        "/admin/app/governance/profiles/resolve",
    ]
    assert "agent_key=planner" in responses[-1].headers["location"]
