from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.config.model_skill import PolicyOutcome
from multi_agent_platform.config.service import (
    ModelSkillConfigService,
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


async def test_disallowed_tool_attempt_is_persisted_before_side_effects(
    session,
) -> None:
    tenant_id = uuid4()
    run_id = uuid4()
    service = ModelSkillConfigService(
        repository=ModelSkillConfigRepository(session),
    )
    principal = _principal(tenant_id)

    decision = await service.evaluate_tool_use(
        principal=principal,
        request=ToolUseRequest(
            tenant_id=tenant_id,
            workflow_run_id=run_id,
            run_step_id=uuid4(),
            resolved_execution_configuration_id=uuid4(),
            agent_key="researcher",
            step_key=None,
            skill_slug="web",
            tool_id="http.fetch",
            action_category="read",
            destination_url="https://blocked.example.net",
            idempotency_key="blocked-tool",
        ),
    )
    provenance = await service.run_provenance(
        principal=principal,
        tenant_id=tenant_id,
        workflow_run_id=run_id,
    )

    assert decision.outcome is PolicyOutcome.DENY
    assert provenance.decisions[0]["outcome"] == "deny"
    assert "secret" not in str(provenance.decisions[0]).lower()
