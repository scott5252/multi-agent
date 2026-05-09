from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.db.models.artifact import ArtifactRecord


class ArtifactRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, artifact_id: object) -> ArtifactRecord | None:
        return await self.session.get(ArtifactRecord, artifact_id)

    async def create(self, artifact: ArtifactRecord) -> ArtifactRecord:
        self.session.add(artifact)
        await self.session.flush()
        return artifact

    async def list_for_tenant(self, tenant_id: object) -> list[ArtifactRecord]:
        stmt = select(ArtifactRecord).where(ArtifactRecord.tenant_id == tenant_id)
        return list((await self.session.execute(stmt)).scalars().all())
