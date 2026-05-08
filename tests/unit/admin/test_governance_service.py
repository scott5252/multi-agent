from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest

from multi_agent_platform.admin.governance import (
    build_credential_reference_result,
    build_governance_dashboard,
    build_profile_resolution,
    build_profile_save_result,
    build_prompt_preview,
    build_prompt_save_result,
    build_provider_list,
    build_provider_probe_result,
    build_routing_preview_mutation,
)
from multi_agent_platform.api.schemas.admin_governance import (
    ProfileSaveRequest,
    PromptPreviewRequest,
    PromptSaveRequest,
    ProviderCredentialReferenceRequest,
    RoutingPreviewRequest,
)
from multi_agent_platform.api.schemas.admin_react import ReactAdminScope
from multi_agent_platform.auth.principal import (
    AuthMode,
    AuthProvider,
    PrincipalContext,
)
from multi_agent_platform.model_providers.models import HealthState, ProviderType

TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
PROVIDER_ID = UUID("22222222-2222-4222-8222-222222222222")
PROMPT_ID = UUID("33333333-3333-4333-8333-333333333333")
PROFILE_ID = UUID("44444444-4444-4444-8444-444444444444")


def _platform_principal() -> PrincipalContext:
    return PrincipalContext(
        principal_id="platform-admin",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        role_codes=("platform_admin",),
        permission_codes=("tenant:read", "admin:model-providers:write"),
        trace_id="trace-governance-platform-test",
    )


def _tenant_principal() -> PrincipalContext:
    return PrincipalContext(
        principal_id="tenant-admin",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        tenant_id=TENANT_ID,
        role_codes=("tenant_user", "tenant_admin"),
        permission_codes=("tenant:read", "tenant:admin"),
        trace_id="trace-governance-tenant-test",
    )


def _platform_scope() -> ReactAdminScope:
    return ReactAdminScope(scope_type="platform", tenant_id=None, label="Platform")


def _tenant_scope() -> ReactAdminScope:
    return ReactAdminScope(
        scope_type="tenant",
        tenant_id=str(TENANT_ID),
        label="Acme",
    )


class FakeProviderRepository:
    def __init__(self, *, seeded: bool = True) -> None:
        now = datetime(2026, 5, 7, 12, tzinfo=UTC)
        self.connection = SimpleNamespace(
            provider_connection_id=PROVIDER_ID,
            display_name="Governance provider",
            provider_type=ProviderType.OPENAI,
            status="active",
            active=True,
            health_state=HealthState.HEALTHY,
            model_count=1,
            updated_at=now,
            credential_secret_reference_ids=["secret-ref-governance-provider"],
            allowlist_decision_hash="allowlist-hash",
        )
        self.test = SimpleNamespace(
            completed_at=now,
            latency_ms=120,
            safe_diagnostic_summary="Provider health check has safe metadata.",
        )
        self.seeded = seeded
        self.saved_tests: list[SimpleNamespace] = []

    async def list_connections(
        self, *, tenant_id: UUID | None, platform_scope: bool
    ) -> list[SimpleNamespace]:
        _ = tenant_id
        _ = platform_scope
        return [self.connection] if self.seeded else []

    async def get_connection(self, provider_connection_id: UUID) -> SimpleNamespace:
        if not self.seeded or provider_connection_id != PROVIDER_ID:
            raise LookupError(provider_connection_id)
        return self.connection

    async def latest_test(self, provider_connection_id: UUID) -> SimpleNamespace | None:
        if self.seeded and provider_connection_id == PROVIDER_ID:
            return self.test
        return None

    async def visible_tenant_ids(
        self, provider_connection_id: UUID
    ) -> tuple[UUID, ...]:
        _ = provider_connection_id
        return (TENANT_ID,)

    async def list_models(self, provider_connection_id: UUID) -> list[SimpleNamespace]:
        _ = provider_connection_id
        return [
            SimpleNamespace(
                model_id="governance-safe-model",
                provider_model_definition_id=uuid4(),
            )
        ]

    async def append_test_result(self, **kwargs: object) -> SimpleNamespace:
        result = kwargs["result"]
        record = SimpleNamespace(
            connection_test_result_id=uuid4(),
            safe_diagnostic_summary=result.safe_diagnostic_summary,
            latency_ms=result.latency_ms,
        )
        self.saved_tests.append(record)
        return record

    async def update_health(self, **kwargs: object) -> None:
        self.connection.health_state = kwargs["health_state"]


class FakePromptRepository:
    def __init__(self, *, seeded: bool = True) -> None:
        self.seeded = seeded
        self.lineage = SimpleNamespace(
            prompt_lineage_id=PROMPT_ID,
            display_name="Governance prompt",
            status="active",
            purpose="Governance summary",
        )
        self.draft = SimpleNamespace(
            current_revision_number=2,
            last_validation_result_id=uuid4(),
        )
        self.revision = SimpleNamespace(
            prompt_draft_revision_id=uuid4(),
            prompt_title="Governance prompt",
            usage_notes="Safe usage notes",
            template_content="Summarized template",
            variable_declarations_json=[{"name": "topic"}],
            fixture_value_sets_json=[{"fixture_set_id": "safe-summary"}],
            safe_summary_json={"summary": "Prompt draft contains safe metadata."},
        )
        self.version = SimpleNamespace(
            prompt_version_id=uuid4(),
            display_version="v1",
            status="active",
            safe_summary_json={"summary": "Published prompt version is available."},
            publication_reason="Published with safe evidence.",
        )
        self.validation = SimpleNamespace(status="passed")

    async def list_visible_lineages(
        self, *, principal_tenant_id: UUID | None, include_platform_admin: bool
    ) -> list[SimpleNamespace]:
        _ = principal_tenant_id
        _ = include_platform_admin
        return [self.lineage] if self.seeded else []

    async def get_active_draft(self, prompt_lineage_id: UUID) -> SimpleNamespace | None:
        return self.draft if self.seeded and prompt_lineage_id == PROMPT_ID else None

    async def get_latest_revision(
        self, draft: SimpleNamespace
    ) -> SimpleNamespace | None:
        _ = draft
        return self.revision if self.seeded else None

    async def get_validation_result(
        self, validation_result_id: UUID
    ) -> SimpleNamespace | None:
        _ = validation_result_id
        return self.validation if self.seeded else None

    async def list_versions_for_lineage(
        self, prompt_lineage_id: UUID
    ) -> list[SimpleNamespace]:
        return [self.version] if self.seeded and prompt_lineage_id == PROMPT_ID else []

    async def list_grants_for_version(
        self, prompt_version_id: UUID
    ) -> list[SimpleNamespace]:
        _ = prompt_version_id
        return [SimpleNamespace(grantee_tenant_id=TENANT_ID)]

    async def get_lineage(self, prompt_lineage_id: UUID) -> SimpleNamespace | None:
        return self.lineage if self.seeded and prompt_lineage_id == PROMPT_ID else None

    async def save_draft_revision(self, **kwargs: object) -> SimpleNamespace:
        safe_summary = kwargs["safe_summary"]
        self.revision.safe_summary_json = dict(safe_summary)  # type: ignore[arg-type]
        self.draft.current_revision_number += 1
        return SimpleNamespace(
            revision_number=self.draft.current_revision_number,
            prompt_draft_revision_id=uuid4(),
        )


class FakeProfileRepository:
    def __init__(self, *, seeded: bool = True) -> None:
        self.seeded = seeded
        self.profile = SimpleNamespace(
            agent_runtime_profile_id=PROFILE_ID,
            display_name="Governance runtime profile",
            status="active",
            active_profile_version_id=uuid4(),
            scope_type="tenant",
            tenant_id=TENANT_ID,
            agent_kind="workflow",
            agent_key="governance",
        )
        self.draft = SimpleNamespace(current_revision_number=2)
        self.revision = SimpleNamespace(
            agent_profile_draft_revision_id=uuid4(),
            purpose="Governance profile",
            prompt_references_json=[{"prompt_version_id": str(PROMPT_ID)}],
            model_routing_hints_json={
                "model_id": "governance-safe-model",
                "provider_key": str(PROVIDER_ID),
            },
            memory_scope_policy_json={},
            skill_requirements_json=[{"skill_slug": "read-only-governance-tool"}],
            tool_policy_expectations_json={},
            output_contract_expectations_json={},
            test_suite_requirements_json=[],
            safe_summary_json={"summary": "Profile summary is safe."},
        )
        self.version = SimpleNamespace(
            display_version="v2",
            prompt_references_json=self.revision.prompt_references_json,
            model_routing_hints_json=self.revision.model_routing_hints_json,
            skill_requirements_json=self.revision.skill_requirements_json,
        )

    async def list_visible_profiles(
        self, *, principal_tenant_id: UUID | None, include_platform_admin: bool
    ) -> list[SimpleNamespace]:
        _ = principal_tenant_id
        _ = include_platform_admin
        return [self.profile] if self.seeded else []

    async def get_active_draft(
        self, agent_runtime_profile_id: UUID
    ) -> SimpleNamespace | None:
        if self.seeded and agent_runtime_profile_id == PROFILE_ID:
            return self.draft
        return None

    async def get_latest_revision(
        self, draft: SimpleNamespace
    ) -> SimpleNamespace | None:
        _ = draft
        return self.revision if self.seeded else None

    async def get_profile_version(
        self, active_profile_version_id: UUID
    ) -> SimpleNamespace | None:
        _ = active_profile_version_id
        return self.version if self.seeded else None

    async def list_grants_for_version(
        self, active_profile_version_id: UUID
    ) -> list[SimpleNamespace]:
        _ = active_profile_version_id
        return [SimpleNamespace(grantee_tenant_id=TENANT_ID)]

    async def get_profile(self, profile_id: UUID) -> SimpleNamespace | None:
        return self.profile if self.seeded and profile_id == PROFILE_ID else None

    async def resolve_active_pointer(self, **kwargs: object) -> SimpleNamespace:
        _ = kwargs
        return SimpleNamespace(
            active_profile_version_id=self.profile.active_profile_version_id
        )

    async def save_draft_revision(self, **kwargs: object) -> SimpleNamespace:
        self.revision.model_routing_hints_json = dict(kwargs["model_routing_hints"])  # type: ignore[arg-type]
        self.draft.current_revision_number += 1
        return SimpleNamespace(
            revision_number=self.draft.current_revision_number,
            agent_profile_draft_revision_id=uuid4(),
        )


class FakeConfigRepository:
    def __init__(self, *, seeded: bool = True) -> None:
        self.seeded = seeded
        self.resolved_id = uuid4()

    async def list_active_model_routes(self, tenant_id: UUID) -> list[object]:
        _ = tenant_id
        return [object()] if self.seeded else []

    async def list_active_prompt_references(self, tenant_id: UUID) -> list[object]:
        _ = tenant_id
        return [object()] if self.seeded else []

    async def list_active_skill_bindings(self, tenant_id: UUID) -> list[object]:
        _ = tenant_id
        return [object()] if self.seeded else []

    async def list_active_tool_policies(self, tenant_id: UUID) -> list[object]:
        _ = tenant_id
        return [object()] if self.seeded else []

    async def list_history(
        self, *, tenant_id: UUID, limit: int
    ) -> list[SimpleNamespace]:
        _ = tenant_id
        _ = limit
        if not self.seeded:
            return []
        return [
            SimpleNamespace(
                configuration_audit_record_id=uuid4(),
                config_kind=SimpleNamespace(value="provider"),
                actor_role="Platform Admin",
                created_at=datetime(2026, 5, 7, 12, tzinfo=UTC),
                action="credential_reference_reviewed",
                redacted_diff_summary={
                    "summary": "Credential reference metadata was reviewed."
                },
                reason="Safe governance change.",
            )
        ]

    async def get_resolved_configuration_for_run(
        self, *, tenant_id: UUID, workflow_run_id: UUID
    ) -> SimpleNamespace | None:
        _ = tenant_id
        _ = workflow_run_id
        if not self.seeded:
            return None
        return SimpleNamespace(
            resolved_execution_configuration_id=self.resolved_id,
            workflow_version_bundle_id=uuid4(),
            accepted_at=datetime(2026, 5, 7, 12, tzinfo=UTC),
            model_routing_version_ids=[uuid4()],
            prompt_reference_version_ids=[uuid4()],
            secret_reference_version_ids=[uuid4()],
            resolution_digest="abcdef1234567890",
        )

    async def list_run_decisions(
        self, *, tenant_id: UUID, workflow_run_id: UUID
    ) -> list[object]:
        _ = tenant_id
        _ = workflow_run_id
        return [object()] if self.seeded else []


@pytest.mark.asyncio
async def test_governance_dashboard_empty_and_seeded_live_states() -> None:
    empty = await build_governance_dashboard(
        scope=_tenant_scope(),
        principal=_tenant_principal(),
        provider_repository=FakeProviderRepository(seeded=False),
        prompt_repository=FakePromptRepository(seeded=False),
        profile_repository=FakeProfileRepository(seeded=False),
        config_repository=FakeConfigRepository(seeded=False),
    )
    seeded = await build_governance_dashboard(
        scope=_tenant_scope(),
        principal=_tenant_principal(),
        provider_repository=FakeProviderRepository(),
        prompt_repository=FakePromptRepository(),
        profile_repository=FakeProfileRepository(),
        config_repository=FakeConfigRepository(),
    )

    assert empty.empty_state is not None
    assert empty.routing_preview is None
    assert seeded.providers[0].display_name == "Governance provider"
    assert seeded.prompt_preview is not None
    assert seeded.profile_resolution is not None
    assert seeded.routing_preview is not None
    assert seeded.provenance is not None
    assert "qa031-secret-value" not in seeded.model_dump_json()


@pytest.mark.asyncio
async def test_provider_list_limits_tenant_actions_and_uses_live_records() -> None:
    platform = await build_provider_list(
        scope=_platform_scope(),
        principal=_platform_principal(),
        provider_repository=FakeProviderRepository(),
    )
    tenant = await build_provider_list(
        scope=_tenant_scope(),
        principal=_tenant_principal(),
        provider_repository=FakeProviderRepository(),
    )

    assert len(platform.providers) == 1
    assert platform.providers[0].authorized_actions
    assert len(tenant.providers) == 1
    assert tenant.providers[0].authorized_actions == ()
    assert tenant.provenance is not None


@pytest.mark.asyncio
async def test_provider_probe_and_prompt_preview_are_safe() -> None:
    provider_repository = FakeProviderRepository()
    prompt_repository = FakePromptRepository()
    probe = await build_provider_probe_result(
        provider_id=str(PROVIDER_ID),
        provider_repository=provider_repository,
        principal=_platform_principal(),
    )
    credential = await build_credential_reference_result(
        provider_id=str(PROVIDER_ID),
        request=ProviderCredentialReferenceRequest(
            credential_reference_id="secret-ref-governance-next",
            revision="provider-rev-current",
        ),
        provider_repository=provider_repository,
    )
    preview = await build_prompt_preview(
        prompt_lineage_id=str(PROMPT_ID),
        request=PromptPreviewRequest(fixture_id="redaction-check"),
        prompt_repository=prompt_repository,
    )

    assert probe.status == "accepted"
    assert probe.probe is not None
    assert probe.probe.credential_resolution_status == "safe metadata only"
    assert credential.status == "accepted"
    assert "resolved credential" not in credential.model_dump_json().lower()
    assert preview.status == "summarized"
    assert "raw prompt" not in preview.model_dump_json().lower()


@pytest.mark.asyncio
async def test_prompt_profile_and_routing_mutations_return_safe_evidence() -> None:
    prompt_repository = FakePromptRepository()
    profile_repository = FakeProfileRepository()
    config_repository = FakeConfigRepository()
    prompt = await build_prompt_save_result(
        prompt_lineage_id=str(PROMPT_ID),
        request=PromptSaveRequest(
            idempotency_key="prompt-save",
            revision="draft r2",
            safe_summary="Review safe prompt summary.",
        ),
        prompt_repository=prompt_repository,
        principal=_tenant_principal(),
    )
    profile = await build_profile_save_result(
        profile_id=str(PROFILE_ID),
        request=ProfileSaveRequest(
            idempotency_key="profile-save",
            model_binding="governance-safe-model-v2",
            provider_binding=str(PROVIDER_ID),
            revision="draft r2",
        ),
        profile_repository=profile_repository,
        principal=_tenant_principal(),
    )
    resolution = await build_profile_resolution(
        profile_id=str(PROFILE_ID),
        scope=_tenant_scope(),
        profile_repository=profile_repository,
    )
    routing = await build_routing_preview_mutation(
        scope=_tenant_scope(),
        request=RoutingPreviewRequest(
            workflow_context="Governance workflow",
            profile_id=str(PROFILE_ID),
            skill_id="read-only-governance-tool",
        ),
        config_repository=config_repository,
    )

    assert prompt.status == "accepted"
    assert prompt.revision == "draft r3"
    assert profile.status == "accepted"
    assert resolution.status == "ready"
    assert routing.routing_preview is not None
    assert "No live providers were invoked." in routing.diagnostics
