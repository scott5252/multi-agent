from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.api.schemas.model_skill_config import (
    ModelRoutingCreateRequest,
    PromptReferenceCreateRequest,
)
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.config.model_skill import ScopeSelector
from multi_agent_platform.config.service import ModelSkillConfigService
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


async def test_admin_model_skill_configures_default_override_and_history(
    session,
) -> None:
    tenant_id = uuid4()
    workflow_id = uuid4()
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
            reason="default",
        ),
    )
    override = await service.create_model_routing(
        principal=principal,
        payload=ModelRoutingCreateRequest(
            scope=ScopeSelector(
                tenant_id=tenant_id,
                workflow_lineage_id=workflow_id,
                agent_key="researcher",
                step_key="summarize",
            ),
            provider_key="openai",
            model_id="gpt-5.4-mini",
            activate=True,
            reason="step override",
        ),
    )
    await service.create_prompt_reference(
        principal=principal,
        payload=PromptReferenceCreateRequest(
            scope=ScopeSelector(tenant_id=tenant_id, workflow_lineage_id=workflow_id),
            prompt_id=uuid4(),
            prompt_version_id=uuid4(),
            prompt_digest="digest",
            activate=True,
            reason="prompt",
        ),
    )

    preview = await service.preview_model(
        principal=principal,
        scope=ScopeSelector(
            tenant_id=tenant_id,
            workflow_lineage_id=workflow_id,
            agent_key="researcher",
            step_key="summarize",
        ),
    )
    history = await service.list_history(principal=principal, tenant_id=tenant_id)

    assert preview.model_routing_version_id == override.version_id
    assert history.items
