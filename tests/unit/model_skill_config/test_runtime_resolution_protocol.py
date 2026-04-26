from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.api.schemas.model_skill_config import (
    CredentialRequirementCreateRequest,
    ModelRoutingCreateRequest,
    PromptReferenceCreateRequest,
    SecretReferenceCreateRequest,
    SkillBindingCreateRequest,
    ToolPolicyCreateRequest,
)
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.config.model_skill import ScopeSelector
from multi_agent_platform.config.service import (
    ModelSkillConfigService,
    ModelStepResolutionRequest,
    PinRunConfigurationRequest,
    SkillAccessRequest,
    ToolUseRequest,
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


async def test_runtime_protocol_pins_run_and_reuses_model_step_decision(
    session,
) -> None:
    tenant_id = uuid4()
    workflow_id = uuid4()
    bundle_id = uuid4()
    run_id = uuid4()
    step_id = uuid4()
    principal = _principal(tenant_id)
    service = ModelSkillConfigService(
        repository=ModelSkillConfigRepository(session),
    )
    await service.create_model_routing(
        principal=principal,
        payload=ModelRoutingCreateRequest(
            scope=ScopeSelector(tenant_id=tenant_id),
            provider_key="openai",
            model_id="gpt-5.4",
            activate=True,
            reason="default model",
        ),
    )
    prompt = await service.create_prompt_reference(
        principal=principal,
        payload=PromptReferenceCreateRequest(
            scope=ScopeSelector(
                tenant_id=tenant_id,
                workflow_lineage_id=workflow_id,
            ),
            prompt_id=uuid4(),
            prompt_version_id=uuid4(),
            prompt_digest="prompt-digest",
            activate=True,
            reason="prompt",
        ),
    )

    pinned = await service.pin_run_configuration(
        principal=principal,
        request=PinRunConfigurationRequest(
            tenant_id=tenant_id,
            workflow_run_id=run_id,
            run_bundle_id=uuid4(),
            bundle_digest="bundle-digest",
            workflow_lineage_id=workflow_id,
            workflow_version_bundle_id=bundle_id,
            initiating_principal_id=principal.principal_identity_id,
            trace_id="trace",
        ),
    )
    first = await service.resolve_model_step(
        principal=principal,
        request=ModelStepResolutionRequest(
            tenant_id=tenant_id,
            workflow_run_id=run_id,
            run_step_id=step_id,
            run_bundle_id=uuid4(),
            resolved_execution_configuration_id=(
                pinned.resolved_execution_configuration_id
            ),
            workflow_lineage_id=workflow_id,
            workflow_version_bundle_id=None,
            agent_key=None,
            step_key=None,
            trace_id="trace",
            idempotency_key="model-step-1",
        ),
    )
    second = await service.resolve_model_step(
        principal=principal,
        request=ModelStepResolutionRequest(
            tenant_id=tenant_id,
            workflow_run_id=run_id,
            run_step_id=step_id,
            run_bundle_id=uuid4(),
            resolved_execution_configuration_id=(
                pinned.resolved_execution_configuration_id
            ),
            workflow_lineage_id=workflow_id,
            workflow_version_bundle_id=None,
            agent_key=None,
            step_key=None,
            trace_id="trace",
            idempotency_key="model-step-1",
        ),
    )

    assert pinned.resolution_digest
    assert first.runtime_policy_decision_id == second.runtime_policy_decision_id
    assert first.prompt_reference_version_id == prompt.version_id


async def test_runtime_protocol_persists_skill_and_tool_decisions(session) -> None:
    tenant_id = uuid4()
    run_id = uuid4()
    step_id = uuid4()
    principal = _principal(tenant_id)
    scope = ScopeSelector(tenant_id=tenant_id, agent_key="researcher")
    service = ModelSkillConfigService(
        repository=ModelSkillConfigRepository(session),
    )
    await service.create_skill_binding(
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
    await service.create_tool_policy(
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
    secret = await service.create_secret_reference(
        principal=principal,
        payload=SecretReferenceCreateRequest(
            scope=scope,
            secret_reference_id="example/api-key",
            provider_key="static",
            external_reference="example/api-key",
            activate=True,
            reason="secret",
        ),
    )
    await service.create_credential_requirement(
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

    skill = await service.evaluate_skill_access(
        principal=principal,
        request=SkillAccessRequest(
            tenant_id=tenant_id,
            workflow_run_id=run_id,
            run_step_id=step_id,
            resolved_execution_configuration_id=uuid4(),
            agent_key="researcher",
            skill_slug="web",
            skill_version="1.0.0",
            use_context="runtime_step",
            idempotency_key="skill-1",
        ),
    )
    tool = await service.evaluate_tool_use(
        principal=principal,
        request=ToolUseRequest(
            tenant_id=tenant_id,
            workflow_run_id=run_id,
            run_step_id=step_id,
            resolved_execution_configuration_id=uuid4(),
            agent_key="researcher",
            step_key=None,
            skill_slug="web",
            tool_id="http.fetch",
            action_category="read",
            idempotency_key="tool-1",
        ),
    )

    assert skill.outcome.value == "allow"
    assert tool.outcome.value == "allow"
    assert skill.runtime_policy_decision_id != tool.runtime_policy_decision_id
