from __future__ import annotations

from multi_agent_platform.db.models.tenant import TenantLimitPolicy
from multi_agent_platform.db.repositories.tenant_limits import TenantLimitRepository


class AdminService:
    def __init__(self, repository: TenantLimitRepository) -> None:
        self.repository = repository

    async def update_limits(self, policy: TenantLimitPolicy) -> TenantLimitPolicy:
        return await self.repository.upsert(policy)
