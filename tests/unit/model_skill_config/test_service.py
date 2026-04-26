from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.api.schemas.model_skill_config import (
    CredentialRequirementCreateRequest,
    ModelRoutingCreateRequest,
    OutboundDomainPolicyCreateRequest,
    PromptReferenceCreateRequest,
    SecretReferenceCreateRequest,
    SkillBindingCreateRequest,
    ToolPolicyCreateRequest,
    ToolPreviewRequest,
)
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.config.model_skill import ConfigKind, ScopeSelector
from multi_agent_platform.config.service import (
    ModelSkillConfigService,
    ModelSkillServiceError,
)
from multi_agent_platform.db.repositories.model_skill_config import (
    ModelSkillConfigRepository,
)


def _principal(tenant_id):
    return PrincipalContext(
        principal_identity_id=uuid4(),
        principal_id="tenant-admin",
        tenant_id=tenant_id,
        role_codes=("tenant_admin",),
        trace_id="trace",
    )


async def test_service_creates_activates_previews_and_lists_history(session) -> None:
    tenant_id = uuid4()
    workflow_id = uuid4()
    principal = _principal(tenant_id)
    service = ModelSkillConfigService(
        repository=ModelSkillConfigRepository(session),
    )
    tenant_scope = ScopeSelector(tenant_id=tenant_id)
    workflow_scope = ScopeSelector(
        tenant_id=tenant_id,
        workflow_lineage_id=workflow_id,
    )

    route = await service.create_model_routing(
        principal=principal,
        payload=ModelRoutingCreateRequest(
            scope=tenant_scope,
            provider_key="openai",
            model_id="gpt-5.4",
            activate=True,
            reason="default",
        ),
    )
    prompt = await service.create_prompt_reference(
        principal=principal,
        payload=PromptReferenceCreateRequest(
            scope=workflow_scope,
            prompt_id=uuid4(),
            prompt_version_id=uuid4(),
            prompt_digest="digest",
            activate=True,
            reason="prompt",
        ),
    )

    preview = await service.preview_model(principal=principal, scope=workflow_scope)
    history = await service.list_history(principal=principal, tenant_id=tenant_id)

    assert route.active
    assert prompt.active
    assert preview.model_id == "gpt-5.4"
    assert len(history.items) >= 4


async def test_service_creates_policy_versions_and_denies_tool_preview(session) -> None:
    tenant_id = uuid4()
    principal = _principal(tenant_id)
    scope = ScopeSelector(tenant_id=tenant_id, agent_key="agent")
    service = ModelSkillConfigService(
        repository=ModelSkillConfigRepository(session),
    )

    skill = await service.create_skill_binding(
        principal=principal,
        payload=SkillBindingCreateRequest(
            scope=scope,
            skill_slug="web",
            skill_version="1.0.0",
            allowed_contexts=["runtime_step"],
            activate=True,
            reason="skill",
        ),
    )
    tool = await service.create_tool_policy(
        principal=principal,
        payload=ToolPolicyCreateRequest(
            scope=scope,
            skill_slug="web",
            tool_id="http.fetch",
            allowed_action_categories=["read"],
            activate=True,
            reason="tool",
        ),
    )
    outbound = await service.create_outbound_policy(
        principal=principal,
        payload=OutboundDomainPolicyCreateRequest(
            scope=scope,
            tool_id="http.fetch",
            action_category="read",
            allowed_domain_patterns=["docs.example.com"],
            allowed_schemes=["https"],
            allowed_ports=[443],
            activate=True,
            reason="domain",
        ),
    )
    secret = await service.create_secret_reference(
        principal=principal,
        payload=SecretReferenceCreateRequest(
            scope=scope,
            secret_reference_id="ref",
            provider_key="vault",
            external_reference="path/to/ref",
            activate=True,
            reason="secret",
        ),
    )
    credential = await service.create_credential_requirement(
        principal=principal,
        payload=CredentialRequirementCreateRequest(
            scope=scope,
            tool_id="http.fetch",
            action_category="read",
            credential_kind="secret_reference",
            secret_reference_version_id=secret.version_id,
            activate=True,
            reason="credential",
        ),
    )
    preview = await service.preview_tool(
        principal=principal,
        payload=ToolPreviewRequest(
            tenant_id=tenant_id,
            agent_key="agent",
            skill_slug="web",
            tool_id="http.fetch",
            action_category="read",
        ),
    )

    assert {
        skill.config_kind,
        tool.config_kind,
        outbound.config_kind,
        credential.config_kind,
    }
    assert preview.outcome.value == "deny"


async def test_service_authorization_fails_closed_for_cross_tenant(session) -> None:
    service = ModelSkillConfigService(
        repository=ModelSkillConfigRepository(session),
    )
    with pytest.raises(ModelSkillServiceError) as exc_info:
        await service.list_history(
            principal=_principal(uuid4()),
            tenant_id=uuid4(),
        )

    assert exc_info.value.category.value == "authorization_failed"


async def test_service_stale_activation_returns_stable_category(session) -> None:
    tenant_id = uuid4()
    principal = _principal(tenant_id)
    service = ModelSkillConfigService(
        repository=ModelSkillConfigRepository(session),
    )
    scope = ScopeSelector(tenant_id=tenant_id)
    route = await service.create_model_routing(
        principal=principal,
        payload=ModelRoutingCreateRequest(
            scope=scope,
            provider_key="openai",
            model_id="gpt-5.4",
            activate=False,
            reason="draft",
        ),
    )

    with pytest.raises(ModelSkillServiceError) as exc_info:
        await service.activate_version(
            principal=principal,
            kind=ConfigKind.MODEL_ROUTING,
            scope=scope,
            version_id=route.version_id,
            reason="stale",
            expected_active_version_id=uuid4(),
        )

    assert exc_info.value.category.value == "stale_configuration"
