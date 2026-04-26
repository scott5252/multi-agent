from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.config.service import (
    ModelSkillConfigService,
    ModelSkillServiceError,
    PinRunConfigurationRequest,
)
from multi_agent_platform.db.repositories.model_skill_config import (
    ModelSkillConfigRepository,
)


def _principal(tenant_id, *roles: str) -> PrincipalContext:
    return PrincipalContext(
        principal_identity_id=uuid4(),
        principal_id="principal",
        tenant_id=tenant_id,
        role_codes=roles,
        trace_id="trace",
    )


async def test_model_skill_authorization_matrix_fails_closed_cross_tenant(
    session,
) -> None:
    service = ModelSkillConfigService(
        repository=ModelSkillConfigRepository(session),
    )
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    operator = _principal(other_tenant_id, "operator")

    surfaces = [
        service.list_history(
            principal=operator,
            tenant_id=tenant_id,
        ),
        service.pin_run_configuration(
            principal=operator,
            request=PinRunConfigurationRequest(
                tenant_id=tenant_id,
                workflow_run_id=uuid4(),
                run_bundle_id=uuid4(),
                bundle_digest="digest",
                workflow_lineage_id=None,
                workflow_version_bundle_id=uuid4(),
            ),
        ),
    ]
    for call in surfaces:
        with pytest.raises(ModelSkillServiceError) as exc_info:
            await call
        assert exc_info.value.category.value == "authorization_failed"
