from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.db.models.access_control import (
    AccessDecisionRecord,
    PrincipalIdentity,
    RoleGrant,
    RoleGrantStatus,
    RoleScopeType,
    SupportOverrideRequest,
    SupportOverrideStatus,
)


def _is_unexpired(expires_at: datetime | None, now: datetime) -> bool:
    if expires_at is None:
        return True
    if expires_at.tzinfo is None:
        return expires_at > now.replace(tzinfo=None)
    return expires_at > now


class AccessControlRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_principal_by_subject(
        self, external_subject: str
    ) -> PrincipalIdentity | None:
        stmt = select(PrincipalIdentity).where(
            PrincipalIdentity.external_subject == external_subject
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def upsert_principal(self, principal: PrincipalIdentity) -> PrincipalIdentity:
        self.session.add(principal)
        await self.session.flush()
        return principal

    async def active_role_grants_for_principal(
        self, principal_identity_id: UUID
    ) -> list[RoleGrant]:
        now = datetime.now(UTC)
        stmt: Select[tuple[RoleGrant]] = (
            select(RoleGrant)
            .where(
                RoleGrant.principal_identity_id == principal_identity_id,
                RoleGrant.status == RoleGrantStatus.ACTIVE,
            )
            .order_by(RoleGrant.updated_at.desc())
        )
        grants = list((await self.session.execute(stmt)).scalars().all())
        return [grant for grant in grants if _is_unexpired(grant.expires_at, now)]

    async def list_role_grants_for_tenant(self, tenant_id: UUID) -> list[RoleGrant]:
        stmt = select(RoleGrant).where(
            RoleGrant.scope_type == RoleScopeType.TENANT,
            RoleGrant.tenant_id == tenant_id,
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def upsert_role_grant(self, grant: RoleGrant) -> RoleGrant:
        self.session.add(grant)
        await self.session.flush()
        return grant

    async def revoke_role_grant(self, role_grant_id: UUID) -> RoleGrant | None:
        grant = await self.session.get(RoleGrant, role_grant_id)
        if grant is None:
            return None
        grant.status = RoleGrantStatus.REVOKED
        grant.revoked_at = datetime.now(UTC)
        await self.session.flush()
        return grant

    async def create_support_override(
        self, request: SupportOverrideRequest
    ) -> SupportOverrideRequest:
        self.session.add(request)
        await self.session.flush()
        return request

    async def get_support_override(
        self, support_override_request_id: UUID
    ) -> SupportOverrideRequest | None:
        return await self.session.get(
            SupportOverrideRequest,
            support_override_request_id,
        )

    async def approve_support_override(
        self,
        support_override_request_id: UUID,
        *,
        approver_principal_id: UUID,
        expires_at: datetime | None,
    ) -> SupportOverrideRequest | None:
        request = await self.get_support_override(support_override_request_id)
        if request is None:
            return None
        request.status = SupportOverrideStatus.APPROVED
        request.approver_principal_id = approver_principal_id
        request.decided_at = datetime.now(UTC)
        request.expires_at = expires_at
        await self.session.flush()
        return request

    async def find_active_support_override(
        self, *, requester_principal_id: UUID, tenant_id: UUID
    ) -> SupportOverrideRequest | None:
        now = datetime.now(UTC)
        stmt = select(SupportOverrideRequest).where(
            SupportOverrideRequest.requester_principal_id == requester_principal_id,
            SupportOverrideRequest.target_tenant_id == tenant_id,
            SupportOverrideRequest.status == SupportOverrideStatus.APPROVED,
        )
        overrides = list((await self.session.execute(stmt)).scalars().all())
        for override in overrides:
            if _is_unexpired(override.expires_at, now):
                return override
        return None

    async def record_access_decision(
        self, record: AccessDecisionRecord
    ) -> AccessDecisionRecord:
        self.session.add(record)
        await self.session.flush()
        return record

    async def list_access_decisions_by_trace(
        self, trace_id: str
    ) -> list[AccessDecisionRecord]:
        stmt = select(AccessDecisionRecord).where(
            AccessDecisionRecord.trace_id == trace_id
        )
        return list((await self.session.execute(stmt)).scalars().all())
