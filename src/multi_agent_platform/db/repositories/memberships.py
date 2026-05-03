from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.admin.memberships.models import (
    InvitationStatus,
    MembershipAuditAction,
    MembershipAuditDecision,
    MembershipSource,
    TenantMembershipStatus,
)
from multi_agent_platform.admin.memberships.redaction import (
    email_fingerprint,
    mask_email,
    normalize_email,
    sanitize_metadata,
    sanitize_text,
)
from multi_agent_platform.db.models.access_control import (
    AccessDecisionRecord,
    AuthProviderType,
    GrantSource,
    PrincipalIdentity,
    PrincipalIdentityStatus,
    RoleCode,
    RoleGrant,
    RoleGrantStatus,
    RoleScopeType,
)
from multi_agent_platform.db.models.user_management import (
    MembershipAuditRecord,
    TenantMembership,
    UserInvitation,
)


class MembershipRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_principal(
        self, principal_identity_id: UUID
    ) -> PrincipalIdentity | None:
        return await self.session.get(PrincipalIdentity, principal_identity_id)

    async def get_principal_by_subject(
        self, external_subject: str
    ) -> PrincipalIdentity | None:
        stmt = select(PrincipalIdentity).where(
            PrincipalIdentity.external_subject == external_subject
        )
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list_principals(
        self,
        *,
        tenant_id: UUID | None = None,
        query: str | None = None,
        limit: int = 50,
    ) -> list[PrincipalIdentity]:
        stmt = select(PrincipalIdentity)
        if tenant_id is not None:
            membership_ids = select(TenantMembership.principal_identity_id).where(
                TenantMembership.tenant_id == tenant_id
            )
            grant_ids = select(RoleGrant.principal_identity_id).where(
                RoleGrant.scope_type == RoleScopeType.TENANT,
                RoleGrant.tenant_id == tenant_id,
            )
            stmt = stmt.where(
                or_(
                    PrincipalIdentity.principal_identity_id.in_(membership_ids),
                    PrincipalIdentity.principal_identity_id.in_(grant_ids),
                )
            )
        if query:
            needle = f"%{query.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(PrincipalIdentity.external_subject).like(needle),
                    func.lower(PrincipalIdentity.display_name).like(needle),
                    func.lower(PrincipalIdentity.email).like(needle),
                )
            )
        stmt = stmt.order_by(PrincipalIdentity.updated_at.desc()).limit(limit)
        return list((await self.session.execute(stmt)).scalars().all())

    async def upsert_principal(
        self,
        *,
        auth_provider: AuthProviderType,
        external_subject: str,
        display_name: str | None = None,
        email: str | None = None,
        principal_identity_id: UUID | None = None,
    ) -> PrincipalIdentity:
        record: PrincipalIdentity | None = None
        if principal_identity_id is not None:
            record = await self.get_principal(principal_identity_id)
        if record is None:
            record = await self.get_principal_by_subject(external_subject)
        if record is None:
            record = PrincipalIdentity(
                auth_provider=auth_provider,
                external_subject=external_subject,
                display_name=sanitize_text(display_name, max_length=255),
                email=normalize_email(email) if email else None,
            )
            self.session.add(record)
        else:
            record.auth_provider = auth_provider
            record.external_subject = external_subject
            record.display_name = sanitize_text(display_name, max_length=255) or (
                record.display_name
            )
            if email:
                record.email = normalize_email(email)
            record.status = PrincipalIdentityStatus.ACTIVE
        await self.session.flush()
        return record

    async def update_principal_status(
        self, principal_identity_id: UUID, status: PrincipalIdentityStatus
    ) -> PrincipalIdentity | None:
        record = await self.get_principal(principal_identity_id)
        if record is None:
            return None
        record.status = status
        await self.session.flush()
        return record

    async def create_or_replay_invitation(
        self,
        *,
        tenant_id: UUID | None,
        email: str,
        requested_roles: list[str],
        idempotency_key: str | None,
        invited_by_principal_id: str,
        expires_at: datetime | None,
        trace_id: str,
    ) -> tuple[UserInvitation, bool]:
        normalized = normalize_email(email)
        fingerprint = email_fingerprint(normalized)
        roles = sorted(set(requested_roles))
        existing_stmt = select(UserInvitation).where(
            UserInvitation.tenant_id == tenant_id,
            UserInvitation.invited_email_hash == fingerprint,
            UserInvitation.status == InvitationStatus.PENDING.value,
        )
        if idempotency_key:
            existing_stmt = existing_stmt.where(
                UserInvitation.idempotency_key == idempotency_key
            )
        existing = list((await self.session.execute(existing_stmt)).scalars().all())
        for invitation in existing:
            if sorted(invitation.requested_roles) == roles:
                return invitation, True
        record = UserInvitation(
            tenant_id=tenant_id,
            invited_email=normalized,
            invited_email_hash=fingerprint,
            masked_email=mask_email(normalized),
            requested_roles=roles,
            status=InvitationStatus.PENDING.value,
            idempotency_key=sanitize_text(idempotency_key, max_length=128),
            invited_by_principal_id=invited_by_principal_id,
            expires_at=expires_at,
            trace_id=trace_id,
        )
        self.session.add(record)
        await self.session.flush()
        return record, False

    async def list_invitations(
        self, *, tenant_id: UUID | None, platform_scope: bool, limit: int = 50
    ) -> list[UserInvitation]:
        stmt = select(UserInvitation)
        if not platform_scope:
            stmt = stmt.where(UserInvitation.tenant_id == tenant_id)
        elif tenant_id is not None:
            stmt = stmt.where(UserInvitation.tenant_id == tenant_id)
        stmt = stmt.order_by(UserInvitation.created_at.desc()).limit(limit)
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_or_create_membership(
        self,
        *,
        tenant_id: UUID,
        principal_identity_id: UUID,
        actor_principal_id: str,
        source: MembershipSource,
        invitation_id: UUID | None = None,
    ) -> TenantMembership:
        stmt = select(TenantMembership).where(
            TenantMembership.tenant_id == tenant_id,
            TenantMembership.principal_identity_id == principal_identity_id,
        )
        record = (await self.session.execute(stmt)).scalar_one_or_none()
        if record is None:
            record = TenantMembership(
                tenant_id=tenant_id,
                principal_identity_id=principal_identity_id,
                invitation_id=invitation_id,
                status=TenantMembershipStatus.ACTIVE.value,
                revision_token=uuid4().hex,
                membership_source=source.value,
                created_by_principal_id=actor_principal_id,
                updated_by_principal_id=actor_principal_id,
            )
            self.session.add(record)
        else:
            record.status = TenantMembershipStatus.ACTIVE.value
            record.removed_at = None
            record.suspended_at = None
            record.revision_token = uuid4().hex
            record.updated_by_principal_id = actor_principal_id
        await self.session.flush()
        return record

    async def get_membership(
        self, tenant_membership_id: UUID
    ) -> TenantMembership | None:
        return await self.session.get(TenantMembership, tenant_membership_id)

    async def list_memberships(
        self, *, tenant_id: UUID | None, platform_scope: bool, limit: int = 100
    ) -> list[TenantMembership]:
        stmt = select(TenantMembership)
        if not platform_scope:
            stmt = stmt.where(TenantMembership.tenant_id == tenant_id)
        elif tenant_id is not None:
            stmt = stmt.where(TenantMembership.tenant_id == tenant_id)
        stmt = stmt.order_by(TenantMembership.updated_at.desc()).limit(limit)
        return list((await self.session.execute(stmt)).scalars().all())

    async def update_membership_status(
        self,
        *,
        tenant_membership_id: UUID,
        tenant_id: UUID,
        status: TenantMembershipStatus,
        actor_principal_id: str,
    ) -> TenantMembership | None:
        record = await self.get_membership(tenant_membership_id)
        if record is None or record.tenant_id != tenant_id:
            return None
        record.status = status.value
        record.updated_by_principal_id = actor_principal_id
        record.revision_token = uuid4().hex
        if status is TenantMembershipStatus.SUSPENDED:
            record.suspended_at = datetime.now(UTC)
        elif status is TenantMembershipStatus.REMOVED:
            record.removed_at = datetime.now(UTC)
        elif status is TenantMembershipStatus.ACTIVE:
            record.suspended_at = None
            record.removed_at = None
        await self.session.flush()
        return record

    async def create_role_grant(
        self,
        *,
        principal_identity_id: UUID,
        scope_type: RoleScopeType,
        tenant_id: UUID | None,
        role_code: RoleCode,
        granted_by_principal_id: UUID | None,
    ) -> tuple[RoleGrant, bool]:
        stmt = select(RoleGrant).where(
            RoleGrant.principal_identity_id == principal_identity_id,
            RoleGrant.scope_type == scope_type,
            RoleGrant.tenant_id == tenant_id,
            RoleGrant.role_code == role_code,
            RoleGrant.status == RoleGrantStatus.ACTIVE,
        )
        existing = (await self.session.execute(stmt)).scalar_one_or_none()
        if existing is not None:
            return existing, True
        record = RoleGrant(
            principal_identity_id=principal_identity_id,
            scope_type=scope_type,
            tenant_id=tenant_id,
            role_code=role_code,
            grant_source=GrantSource.ADMIN_ASSIGNMENT,
            status=RoleGrantStatus.ACTIVE,
            granted_by_principal_id=granted_by_principal_id,
        )
        self.session.add(record)
        await self.session.flush()
        return record, False

    async def list_role_grants(
        self, *, tenant_id: UUID | None, platform_scope: bool, limit: int = 100
    ) -> list[RoleGrant]:
        stmt = select(RoleGrant)
        if not platform_scope:
            stmt = stmt.where(
                RoleGrant.scope_type == RoleScopeType.TENANT,
                RoleGrant.tenant_id == tenant_id,
            )
        elif tenant_id is not None:
            stmt = stmt.where(
                RoleGrant.scope_type == RoleScopeType.TENANT,
                RoleGrant.tenant_id == tenant_id,
            )
        stmt = stmt.order_by(RoleGrant.updated_at.desc()).limit(limit)
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_role_grant(self, role_grant_id: UUID) -> RoleGrant | None:
        return await self.session.get(RoleGrant, role_grant_id)

    async def revoke_role_grant(self, *, role_grant_id: UUID) -> RoleGrant | None:
        record = await self.get_role_grant(role_grant_id)
        if record is None:
            return None
        record.status = RoleGrantStatus.REVOKED
        record.revoked_at = datetime.now(UTC)
        await self.session.flush()
        return record

    async def list_access_history(
        self,
        *,
        tenant_id: UUID | None,
        platform_scope: bool,
        principal_identity_id: UUID | None = None,
        limit: int = 50,
    ) -> list[AccessDecisionRecord]:
        stmt = select(AccessDecisionRecord)
        if principal_identity_id is not None:
            stmt = stmt.where(
                AccessDecisionRecord.principal_identity_id == principal_identity_id
            )
        if not platform_scope:
            stmt = stmt.where(AccessDecisionRecord.tenant_id == tenant_id)
        elif tenant_id is not None:
            stmt = stmt.where(AccessDecisionRecord.tenant_id == tenant_id)
        stmt = stmt.order_by(AccessDecisionRecord.occurred_at.desc()).limit(limit)
        return list((await self.session.execute(stmt)).scalars().all())

    async def add_audit_record(
        self,
        *,
        tenant_id: UUID | None,
        actor_principal_id: str,
        action: MembershipAuditAction,
        decision: MembershipAuditDecision,
        summary: str,
        trace_id: str,
        target_principal_identity_id: UUID | None = None,
        redacted_metadata: dict[str, object] | None = None,
    ) -> MembershipAuditRecord:
        record = MembershipAuditRecord(
            tenant_id=tenant_id,
            actor_principal_id=actor_principal_id,
            target_principal_identity_id=target_principal_identity_id,
            action=action.value,
            decision=decision.value,
            summary=sanitize_text(summary, max_length=500)
            or "Membership administration event recorded.",
            trace_id=trace_id,
            redacted_metadata=sanitize_metadata(redacted_metadata),
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def list_audit_records(
        self, *, tenant_id: UUID | None, platform_scope: bool, limit: int = 50
    ) -> list[MembershipAuditRecord]:
        stmt = select(MembershipAuditRecord)
        if not platform_scope:
            stmt = stmt.where(MembershipAuditRecord.tenant_id == tenant_id)
        elif tenant_id is not None:
            stmt = stmt.where(MembershipAuditRecord.tenant_id == tenant_id)
        stmt = stmt.order_by(MembershipAuditRecord.created_at.desc()).limit(limit)
        return list((await self.session.execute(stmt)).scalars().all())
