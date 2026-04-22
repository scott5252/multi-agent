from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.admin.service import AdminService
from multi_agent_platform.db.models.tenant import TenantLimitPolicy
from multi_agent_platform.db.repositories.tenant_limits import TenantLimitRepository


async def test_admin_service_updates_policy(session) -> None:
    repository = TenantLimitRepository(session)
    service = AdminService(repository)
    policy = TenantLimitPolicy(tenant_id=uuid4())
    saved = await service.update_limits(policy)
    assert saved.policy_id is not None
