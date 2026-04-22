from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.db.models.audit import AuditEvent


class AuditRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, audit_event: AuditEvent) -> AuditEvent:
        self.session.add(audit_event)
        await self.session.flush()
        return audit_event

    async def list_by_trace(self, trace_id: str) -> list[AuditEvent]:
        stmt = select(AuditEvent).where(AuditEvent.trace_id == trace_id)
        return list((await self.session.execute(stmt)).scalars().all())
