from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.db.models.tenant import TenantLimitPolicy


class TenantLimitRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert(self, policy: TenantLimitPolicy) -> TenantLimitPolicy:
        self.session.add(policy)
        await self.session.flush()
        return policy

    async def get_active(self, tenant_id: object) -> TenantLimitPolicy | None:
        stmt = (
            select(TenantLimitPolicy)
            .where(
                TenantLimitPolicy.tenant_id == tenant_id,
                TenantLimitPolicy.enabled.is_(True),
            )
            .order_by(TenantLimitPolicy.effective_from.desc())
            .limit(1)
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()
