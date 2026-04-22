from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.db.repositories.queue import QueueRepository
from multi_agent_platform.db.repositories.tenant_limits import TenantLimitRepository
from multi_agent_platform.runtime.queue.models import (
    QueueEnqueueRequest,
    QueueLeaseResult,
)
from multi_agent_platform.tenancy.context import ScopeContext, ScopeType
from multi_agent_platform.tenancy.guards import ensure_scope_matches


class QueueService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = QueueRepository(session)
        self.limit_repository = TenantLimitRepository(session)

    async def enqueue(
        self, scope: ScopeContext, request: QueueEnqueueRequest
    ) -> object:
        ensure_scope_matches(scope, request.tenant_id)
        if scope.scope_type is ScopeType.TENANT:
            policy = await self.limit_repository.get_active(scope.tenant_id)
            if policy is not None and request.priority < 0:
                raise ValueError("priority must be non-negative")
        return await self.repository.enqueue(request)

    async def lease_next(
        self, worker_id: str, lease_seconds: int
    ) -> QueueLeaseResult | None:
        return await self.repository.lease_next(
            worker_id=worker_id, lease_seconds=lease_seconds
        )
