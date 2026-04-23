from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.db.models.delegated_credential import (
    DelegatedCredentialLink,
    DelegatedCredentialStatus,
)


def _is_unexpired(expires_at: datetime | None, now: datetime) -> bool:
    if expires_at is None:
        return True
    if expires_at.tzinfo is None:
        return expires_at > now.replace(tzinfo=None)
    return expires_at > now


class DelegatedCredentialRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self, delegated_credential: DelegatedCredentialLink
    ) -> DelegatedCredentialLink:
        self.session.add(delegated_credential)
        await self.session.flush()
        return delegated_credential

    async def get(
        self,
        delegated_credential_link_id: UUID,
    ) -> DelegatedCredentialLink | None:
        return await self.session.get(
            DelegatedCredentialLink,
            delegated_credential_link_id,
        )

    async def resolve_for_tool(
        self,
        *,
        delegated_credential_link_id: UUID,
        tenant_id: UUID,
        tool_id: str,
    ) -> DelegatedCredentialLink | None:
        link = await self.get(delegated_credential_link_id)
        if link is None:
            return None
        if link.tenant_id != tenant_id:
            return None
        if link.status is not DelegatedCredentialStatus.ACTIVE:
            return None
        if not _is_unexpired(link.expires_at, datetime.now(UTC)):
            return None
        if tool_id not in link.approved_tool_ids:
            return None
        link.last_used_at = datetime.now(UTC)
        await self.session.flush()
        return link

    async def list_for_principal(
        self, owner_principal_id: UUID
    ) -> list[DelegatedCredentialLink]:
        stmt = select(DelegatedCredentialLink).where(
            DelegatedCredentialLink.owner_principal_id == owner_principal_id
        )
        return list((await self.session.execute(stmt)).scalars().all())
