from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.config.service import ModelSkillConfigService
from multi_agent_platform.db.repositories.model_skill_config import (
    ModelSkillConfigRepository,
)
from multi_agent_platform.runtime.orchestration.service import (
    RuntimeOrchestrationService,
)


def _principal(tenant_id):
    return PrincipalContext(
        principal_identity_id=uuid4(),
        principal_id="tenant-admin",
        tenant_id=tenant_id,
        role_codes=("tenant_admin",),
        trace_id="trace",
    )


async def test_runtime_start_pins_configuration_when_service_is_supplied(
    session,
) -> None:
    tenant_id = uuid4()
    principal = _principal(tenant_id)
    config_service = ModelSkillConfigService(
        repository=ModelSkillConfigRepository(session),
    )
    runtime = RuntimeOrchestrationService()

    run = await runtime.start_run(
        tenant_id=tenant_id,
        scope_type="tenant",
        principal_id="tenant-admin",
        published_workflow_version_id=uuid4(),
        input_payload={"message": "hello"},
        idempotency_key="run-1",
        model_skill_config_service=config_service,
        principal_context=principal,
    )
    provenance = await config_service.run_provenance(
        principal=principal,
        tenant_id=tenant_id,
        workflow_run_id=run.workflow_run_id,
    )

    assert provenance.resolved_execution_configuration_id is not None
    assert provenance.resolution_digest is not None
