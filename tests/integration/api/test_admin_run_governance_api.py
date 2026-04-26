from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.audit.service import (
    AuditDebuggingRateLimitError,
    AuditDebuggingService,
)
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.repositories.audit_debugging import (
    AuditDebuggingRepository,
)


async def test_export_rate_limit_fairness_is_scoped_to_actor_and_tenant(
    session,
) -> None:
    tenant_id = uuid4()
    repository = AuditDebuggingRepository(session)
    service = AuditDebuggingService(repository)
    principal = PrincipalContext(
        principal_id=f"admin-{uuid4()}",
        tenant_id=tenant_id,
        role_codes=("tenant_admin",),
    )
    for _ in range(service.EXPORT_LIMIT_PER_ACTOR):
        await service.create_export(
            principal=principal,
            tenant_id=tenant_id,
            workflow_run_id=uuid4(),
            lineage_scope="run_only",
            recipient_scope="tenant_auditor",
            included_sections=["timeline"],
            excluded_sections=[],
        )
    with pytest.raises(AuditDebuggingRateLimitError):
        await service.create_export(
            principal=principal,
            tenant_id=tenant_id,
            workflow_run_id=uuid4(),
            lineage_scope="run_only",
            recipient_scope="tenant_auditor",
            included_sections=["timeline"],
            excluded_sections=[],
        )
