from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.config.model_skill import ConfigKind, ScopeSelector
from multi_agent_platform.config.service import (
    ModelSkillConfigService,
    ModelSkillServiceError,
)
from multi_agent_platform.config.validation import require_reason
from multi_agent_platform.db.repositories.model_skill_config import (
    ModelSkillConfigRepository,
)


async def test_stale_expected_active_version_fails_with_stable_category(
    session,
) -> None:
    service = ModelSkillConfigService(
        repository=ModelSkillConfigRepository(session),
    )
    tenant_id = uuid4()

    with pytest.raises(ModelSkillServiceError) as exc_info:
        await service.activate_version(
            principal=PrincipalContext(
                principal_identity_id=uuid4(),
                principal_id="tenant-admin",
                tenant_id=tenant_id,
                role_codes=("tenant_admin",),
            ),
            kind=ConfigKind.MODEL_ROUTING,
            scope=ScopeSelector(tenant_id=tenant_id),
            version_id=uuid4(),
            reason="stale",
            expected_active_version_id=uuid4(),
        )

    assert exc_info.value.category.value == "stale_configuration"


def test_missing_activation_reason_is_rejected() -> None:
    with pytest.raises(ValueError):
        require_reason(" ")
