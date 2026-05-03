from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from multi_agent_platform.admin.memberships.models import (
    TENANT_ADMIN_ASSIGNABLE_ROLES,
    MembershipAccessScope,
    MembershipAuditAction,
    MembershipAuditDecision,
    MembershipConflictError,
    MembershipPermissionError,
    MembershipScopeType,
    MembershipSource,
    TenantMembershipStatus,
)
from multi_agent_platform.admin.memberships.redaction import (
    email_fingerprint,
    mask_email,
    mask_identifier,
)
from multi_agent_platform.db.models.access_control import (
    AccessDecisionRecord,
    AuthProviderType,
    PrincipalIdentity,
    PrincipalIdentityStatus,
    RoleCode,
    RoleGrant,
    RoleScopeType,
)
from multi_agent_platform.db.models.user_management import (
    MembershipAuditRecord,
    TenantMembership,
    UserInvitation,
)
from multi_agent_platform.db.repositories.memberships import MembershipRepository


@dataclass(frozen=True, slots=True)
class MembershipSnapshot:
    principals: tuple[PrincipalIdentity, ...]
    invitations: tuple[UserInvitation, ...]
    memberships: tuple[TenantMembership, ...]
    role_grants: tuple[RoleGrant, ...]
    access_history: tuple[AccessDecisionRecord, ...]
    audit_records: tuple[MembershipAuditRecord, ...]


@dataclass(frozen=True, slots=True)
class InvitationResult:
    invitation: UserInvitation
    replayed: bool


class MembershipAdministrationService:
    def __init__(self, repository: MembershipRepository) -> None:
        self.repository = repository

    async def snapshot(
        self,
        access_scope: MembershipAccessScope,
        *,
        query: str | None = None,
    ) -> MembershipSnapshot:
        tenant_id = access_scope.tenant_id
        platform_scope = access_scope.scope_type is MembershipScopeType.PLATFORM
        return MembershipSnapshot(
            principals=tuple(
                await self.repository.list_principals(
                    tenant_id=tenant_id,
                    query=query,
                )
            ),
            invitations=tuple(
                await self.repository.list_invitations(
                    tenant_id=tenant_id,
                    platform_scope=platform_scope,
                )
            ),
            memberships=tuple(
                await self.repository.list_memberships(
                    tenant_id=tenant_id,
                    platform_scope=platform_scope,
                )
            ),
            role_grants=tuple(
                await self.repository.list_role_grants(
                    tenant_id=tenant_id,
                    platform_scope=platform_scope,
                )
            ),
            access_history=tuple(
                await self.repository.list_access_history(
                    tenant_id=tenant_id,
                    platform_scope=platform_scope,
                )
            ),
            audit_records=tuple(
                await self.repository.list_audit_records(
                    tenant_id=tenant_id,
                    platform_scope=platform_scope,
                )
            ),
        )

    async def create_invitation(
        self,
        *,
        access_scope: MembershipAccessScope,
        email: str,
        requested_roles: tuple[RoleCode, ...],
        tenant_id: UUID | None = None,
        idempotency_key: str | None = None,
    ) -> InvitationResult:
        target_tenant_id = self._target_tenant(access_scope, tenant_id)
        roles = self._eligible_requested_roles(
            access_scope=access_scope,
            target_tenant_id=target_tenant_id,
            requested_roles=requested_roles,
        )
        invitation, replayed = await self.repository.create_or_replay_invitation(
            tenant_id=target_tenant_id,
            email=email,
            requested_roles=[role.value for role in roles],
            idempotency_key=idempotency_key,
            invited_by_principal_id=access_scope.principal_id,
            expires_at=datetime.now(UTC) + timedelta(days=7),
            trace_id=access_scope.trace_id,
        )
        await self.repository.add_audit_record(
            tenant_id=target_tenant_id,
            actor_principal_id=access_scope.principal_id,
            action=MembershipAuditAction.INVITATION_REPLAYED
            if replayed
            else MembershipAuditAction.INVITATION_CREATED,
            decision=MembershipAuditDecision.ALLOW,
            summary=(
                "Membership invitation replayed."
                if replayed
                else "Membership invitation created."
            ),
            trace_id=access_scope.trace_id,
            redacted_metadata={
                "masked_email": mask_email(email),
                "email_hash": email_fingerprint(email)[:16],
                "requested_roles": [role.value for role in roles],
                "replayed": replayed,
            },
        )
        return InvitationResult(invitation=invitation, replayed=replayed)

    async def link_auth0_principal(
        self,
        *,
        access_scope: MembershipAccessScope,
        auth0_subject: str,
        email: str | None = None,
        display_name: str | None = None,
        principal_identity_id: UUID | None = None,
    ) -> PrincipalIdentity:
        self._require_platform_admin(access_scope, "link Auth0 principals")
        existing = await self.repository.get_principal_by_subject(auth0_subject)
        if existing is not None and (
            principal_identity_id is None
            or existing.principal_identity_id != principal_identity_id
        ):
            await self.record_denial(
                access_scope=access_scope,
                reason="auth0 subject already linked",
                metadata={"auth0_subject": mask_identifier(auth0_subject)},
            )
            raise MembershipConflictError("Auth0 subject is already linked")
        principal = await self.repository.upsert_principal(
            auth_provider=AuthProviderType.AUTH0,
            external_subject=auth0_subject,
            display_name=display_name,
            email=email,
            principal_identity_id=principal_identity_id,
        )
        await self.repository.add_audit_record(
            tenant_id=None,
            actor_principal_id=access_scope.principal_id,
            target_principal_identity_id=principal.principal_identity_id,
            action=MembershipAuditAction.PRINCIPAL_LINKED,
            decision=MembershipAuditDecision.ALLOW,
            summary="Auth0 principal identity linked.",
            trace_id=access_scope.trace_id,
            redacted_metadata={
                "auth0_subject": mask_identifier(auth0_subject),
                "masked_email": mask_email(email) if email else "unavailable",
            },
        )
        return principal

    async def create_role_grant(
        self,
        *,
        access_scope: MembershipAccessScope,
        principal_identity_id: UUID,
        scope_type: RoleScopeType,
        role_code: RoleCode,
        tenant_id: UUID | None = None,
    ) -> RoleGrant:
        target_tenant_id = tenant_id if scope_type is RoleScopeType.TENANT else None
        self._ensure_role_assignment_allowed(
            access_scope=access_scope,
            target_tenant_id=target_tenant_id,
            scope_type=scope_type,
            role_code=role_code,
        )
        principal = await self.repository.get_principal(principal_identity_id)
        if principal is None:
            raise LookupError("principal identity not found")
        grant, replayed = await self.repository.create_role_grant(
            principal_identity_id=principal_identity_id,
            scope_type=scope_type,
            tenant_id=target_tenant_id,
            role_code=role_code,
            granted_by_principal_id=None,
        )
        if target_tenant_id is not None:
            await self.repository.get_or_create_membership(
                tenant_id=target_tenant_id,
                principal_identity_id=principal_identity_id,
                actor_principal_id=access_scope.principal_id,
                source=MembershipSource.ADMIN_ASSIGNMENT,
            )
        await self.repository.add_audit_record(
            tenant_id=target_tenant_id,
            actor_principal_id=access_scope.principal_id,
            target_principal_identity_id=principal_identity_id,
            action=MembershipAuditAction.ROLE_GRANT_CREATED,
            decision=MembershipAuditDecision.ALLOW,
            summary="Role grant created." if not replayed else "Role grant replayed.",
            trace_id=access_scope.trace_id,
            redacted_metadata={
                "scope_type": scope_type.value,
                "role_code": role_code.value,
                "replayed": replayed,
            },
        )
        return grant

    async def revoke_role_grant(
        self,
        *,
        access_scope: MembershipAccessScope,
        role_grant_id: UUID,
    ) -> RoleGrant | None:
        grant = await self.repository.get_role_grant(role_grant_id)
        if grant is None:
            return None
        self._ensure_role_assignment_allowed(
            access_scope=access_scope,
            target_tenant_id=grant.tenant_id,
            scope_type=grant.scope_type,
            role_code=grant.role_code,
        )
        revoked = await self.repository.revoke_role_grant(role_grant_id=role_grant_id)
        if revoked is not None:
            await self.repository.add_audit_record(
                tenant_id=revoked.tenant_id,
                actor_principal_id=access_scope.principal_id,
                target_principal_identity_id=revoked.principal_identity_id,
                action=MembershipAuditAction.ROLE_GRANT_REVOKED,
                decision=MembershipAuditDecision.ALLOW,
                summary="Role grant revoked.",
                trace_id=access_scope.trace_id,
                redacted_metadata={
                    "scope_type": revoked.scope_type.value,
                    "role_code": revoked.role_code.value,
                },
            )
        return revoked

    async def update_membership_status(
        self,
        *,
        access_scope: MembershipAccessScope,
        tenant_membership_id: UUID,
        status: TenantMembershipStatus,
    ) -> TenantMembership | None:
        tenant_id = access_scope.require_tenant()
        record = await self.repository.update_membership_status(
            tenant_membership_id=tenant_membership_id,
            tenant_id=tenant_id,
            status=status,
            actor_principal_id=access_scope.principal_id,
        )
        if record is None:
            return None
        action = {
            TenantMembershipStatus.ACTIVE: MembershipAuditAction.MEMBERSHIP_RESTORED,
            TenantMembershipStatus.SUSPENDED: (
                MembershipAuditAction.MEMBERSHIP_SUSPENDED
            ),
            TenantMembershipStatus.REMOVED: MembershipAuditAction.MEMBERSHIP_REMOVED,
        }[status]
        await self.repository.add_audit_record(
            tenant_id=tenant_id,
            actor_principal_id=access_scope.principal_id,
            target_principal_identity_id=record.principal_identity_id,
            action=action,
            decision=MembershipAuditDecision.ALLOW,
            summary=f"Tenant membership marked {status.value}.",
            trace_id=access_scope.trace_id,
            redacted_metadata={"membership_status": status.value},
        )
        return record

    async def suspend_principal(
        self, *, access_scope: MembershipAccessScope, principal_identity_id: UUID
    ) -> PrincipalIdentity | None:
        self._require_platform_admin(access_scope, "suspend principals")
        record = await self.repository.update_principal_status(
            principal_identity_id,
            PrincipalIdentityStatus.SUSPENDED,
        )
        if record is not None:
            await self.repository.add_audit_record(
                tenant_id=None,
                actor_principal_id=access_scope.principal_id,
                target_principal_identity_id=principal_identity_id,
                action=MembershipAuditAction.PRINCIPAL_SUSPENDED,
                decision=MembershipAuditDecision.ALLOW,
                summary="Principal identity suspended.",
                trace_id=access_scope.trace_id,
                redacted_metadata={
                    "subject": mask_identifier(record.external_subject),
                    "status": record.status.value,
                },
            )
        return record

    async def reactivate_principal(
        self, *, access_scope: MembershipAccessScope, principal_identity_id: UUID
    ) -> PrincipalIdentity | None:
        self._require_platform_admin(access_scope, "reactivate principals")
        record = await self.repository.update_principal_status(
            principal_identity_id,
            PrincipalIdentityStatus.ACTIVE,
        )
        if record is not None:
            await self.repository.add_audit_record(
                tenant_id=None,
                actor_principal_id=access_scope.principal_id,
                target_principal_identity_id=principal_identity_id,
                action=MembershipAuditAction.PRINCIPAL_REACTIVATED,
                decision=MembershipAuditDecision.ALLOW,
                summary="Principal identity reactivated.",
                trace_id=access_scope.trace_id,
                redacted_metadata={
                    "subject": mask_identifier(record.external_subject),
                    "status": record.status.value,
                },
            )
        return record

    async def record_denial(
        self,
        *,
        access_scope: MembershipAccessScope,
        reason: str,
        metadata: dict[str, object] | None = None,
    ) -> MembershipAuditRecord:
        return await self.repository.add_audit_record(
            tenant_id=access_scope.tenant_id,
            actor_principal_id=access_scope.principal_id,
            action=MembershipAuditAction.ACCESS_DENIED,
            decision=MembershipAuditDecision.DENY,
            summary=f"Membership administration denied: {reason}.",
            trace_id=access_scope.trace_id,
            redacted_metadata=metadata or {},
        )

    def _target_tenant(
        self, access_scope: MembershipAccessScope, tenant_id: UUID | None
    ) -> UUID | None:
        if access_scope.platform_admin:
            return tenant_id
        selected_tenant = tenant_id or access_scope.tenant_id
        if selected_tenant is None or selected_tenant != access_scope.tenant_id:
            raise MembershipPermissionError("tenant scope is not authorized")
        return selected_tenant

    def _eligible_requested_roles(
        self,
        *,
        access_scope: MembershipAccessScope,
        target_tenant_id: UUID | None,
        requested_roles: tuple[RoleCode, ...],
    ) -> tuple[RoleCode, ...]:
        roles = requested_roles or (RoleCode.TENANT_USER,)
        if access_scope.platform_admin:
            return tuple(sorted(set(roles), key=lambda role: role.value))
        if target_tenant_id is None or target_tenant_id != access_scope.tenant_id:
            raise MembershipPermissionError("tenant invite scope is not authorized")
        if any(role not in TENANT_ADMIN_ASSIGNABLE_ROLES for role in roles):
            raise MembershipPermissionError(
                "tenant admins cannot assign platform roles"
            )
        return tuple(sorted(set(roles), key=lambda role: role.value))

    def _ensure_role_assignment_allowed(
        self,
        *,
        access_scope: MembershipAccessScope,
        target_tenant_id: UUID | None,
        scope_type: RoleScopeType,
        role_code: RoleCode,
    ) -> None:
        if access_scope.platform_admin:
            if scope_type is RoleScopeType.TENANT and target_tenant_id is None:
                raise MembershipPermissionError("tenant role grant requires tenant")
            if (
                scope_type is RoleScopeType.PLATFORM
                and role_code is not RoleCode.PLATFORM_ADMIN
            ):
                raise MembershipPermissionError("platform grants require platform role")
            return
        if scope_type is not RoleScopeType.TENANT:
            raise MembershipPermissionError(
                "tenant admins cannot assign platform roles"
            )
        if target_tenant_id is None or target_tenant_id != access_scope.tenant_id:
            raise MembershipPermissionError("tenant scope is not authorized")
        if role_code not in TENANT_ADMIN_ASSIGNABLE_ROLES:
            raise MembershipPermissionError(
                "tenant admins cannot assign platform roles"
            )

    @staticmethod
    def _require_platform_admin(
        access_scope: MembershipAccessScope, action: str
    ) -> None:
        if not access_scope.platform_admin:
            raise MembershipPermissionError(f"platform admin required to {action}")
