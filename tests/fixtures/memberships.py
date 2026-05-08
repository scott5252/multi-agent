from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from multi_agent_platform.admin.memberships.models import (
    MembershipAuditAction,
    MembershipAuditDecision,
    MembershipSource,
)
from multi_agent_platform.admin.memberships.redaction import (
    email_fingerprint,
    mask_email,
)
from multi_agent_platform.db.models.access_control import (
    AccessDecision,
    AccessDecisionRecord,
    AccessReasonCode,
    AuthProviderType,
    PrincipalIdentity,
    RoleCode,
    RoleGrant,
    RoleScopeType,
    SupportOverrideRequest,
    SupportOverrideStatus,
)
from multi_agent_platform.db.models.tenant import Tenant, TenantStatus
from multi_agent_platform.db.models.user_management import (
    MembershipAuditRecord,
    TenantMembership,
    UserInvitation,
)
from multi_agent_platform.db.repositories.memberships import MembershipRepository

ACME_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
GLOBEX_TENANT_ID = UUID("22222222-2222-2222-2222-222222222222")


@dataclass(frozen=True, slots=True)
class MembershipSeed:
    acme_tenant_id: UUID
    globex_tenant_id: UUID
    platform_principal_id: UUID
    tenant_principal_id: UUID
    other_principal_id: UUID
    tenant_membership_id: UUID
    role_grant_id: UUID


async def seed_membership_live_data(session: AsyncSession) -> MembershipSeed:
    await session.merge(
        Tenant(
            tenant_id=ACME_TENANT_ID,
            slug="acme",
            display_name="Acme",
            status=TenantStatus.ACTIVE,
        )
    )
    await session.merge(
        Tenant(
            tenant_id=GLOBEX_TENANT_ID,
            slug="globex",
            display_name="Globex",
            status=TenantStatus.ACTIVE,
        )
    )
    await session.flush()
    repository = MembershipRepository(session)
    platform = await repository.upsert_principal(
        auth_provider=AuthProviderType.LOCAL_PRINCIPAL,
        external_subject="local|platform-admin",
        display_name="Platform Admin",
        email="platform.admin@example.test",
    )
    tenant_admin = await repository.upsert_principal(
        auth_provider=AuthProviderType.LOCAL_PRINCIPAL,
        external_subject="local|tenant-admin-acme",
        display_name="Maya Chen",
        email="maya.chen@example.test",
    )
    other = await repository.upsert_principal(
        auth_provider=AuthProviderType.LOCAL_PRINCIPAL,
        external_subject="local|auditor-acme",
        display_name="Jordan Lee",
        email="jordan.lee@example.test",
    )
    membership = await repository.get_or_create_membership(
        tenant_id=ACME_TENANT_ID,
        principal_identity_id=tenant_admin.principal_identity_id,
        actor_principal_id="platform-admin",
        source=MembershipSource.ADMIN_ASSIGNMENT,
    )
    await repository.get_or_create_membership(
        tenant_id=ACME_TENANT_ID,
        principal_identity_id=other.principal_identity_id,
        actor_principal_id="platform-admin",
        source=MembershipSource.ADMIN_ASSIGNMENT,
    )
    grant, _ = await repository.create_role_grant(
        principal_identity_id=tenant_admin.principal_identity_id,
        scope_type=RoleScopeType.TENANT,
        tenant_id=ACME_TENANT_ID,
        role_code=RoleCode.TENANT_ADMIN,
        granted_by_principal_id=platform.principal_identity_id,
    )
    session.add(
        RoleGrant(
            principal_identity_id=platform.principal_identity_id,
            scope_type=RoleScopeType.PLATFORM,
            tenant_id=None,
            role_code=RoleCode.PLATFORM_ADMIN,
            granted_by_principal_id=platform.principal_identity_id,
        )
    )
    await repository.create_or_replay_invitation(
        tenant_id=ACME_TENANT_ID,
        email="invited.user@example.test",
        requested_roles=["tenant_user"],
        idempotency_key="qa054-live-invite",
        invited_by_principal_id="tenant-admin-acme",
        expires_at=datetime.now(UTC) + timedelta(days=7),
        trace_id="trace-qa054-invite",
    )
    session.add(
        AccessDecisionRecord(
            principal_identity_id=tenant_admin.principal_identity_id,
            scope_type=RoleScopeType.TENANT,
            tenant_id=ACME_TENANT_ID,
            surface_key="GET:/admin/app/memberships/bootstrap.json",
            requested_action="Open membership workspace",
            decision=AccessDecision.ALLOW,
            reason_code=AccessReasonCode.INSUFFICIENT_ROLE,
            auth_mode="local_principal",
            token_subject=None,
            token_jti=None,
            trace_id="trace-qa054-allow",
            request_id="request-qa054-allow",
            required_roles=["tenant_admin"],
            required_permissions=["membership-admin:read"],
            secret_free=True,
        )
    )
    await repository.add_audit_record(
        tenant_id=ACME_TENANT_ID,
        actor_principal_id="tenant-admin-acme",
        target_principal_identity_id=tenant_admin.principal_identity_id,
        action=MembershipAuditAction.ROLE_GRANT_CREATED,
        decision=MembershipAuditDecision.ALLOW,
        summary="Role grant created from qa054 live seed.",
        trace_id="trace-qa054-audit",
        redacted_metadata={"role_code": "tenant_admin"},
    )
    session.add(
        SupportOverrideRequest(
            requester_principal_id=platform.principal_identity_id,
            target_tenant_id=ACME_TENANT_ID,
            justification="Safe qa054 support review",
            status=SupportOverrideStatus.APPROVED,
            approver_principal_id=platform.principal_identity_id,
            request_trace_id="trace-qa054-support",
            idempotency_key="qa054-support-override",
            decided_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(hours=2),
        )
    )
    await session.flush()
    return MembershipSeed(
        acme_tenant_id=ACME_TENANT_ID,
        globex_tenant_id=GLOBEX_TENANT_ID,
        platform_principal_id=platform.principal_identity_id,
        tenant_principal_id=tenant_admin.principal_identity_id,
        other_principal_id=other.principal_identity_id,
        tenant_membership_id=membership.tenant_membership_id,
        role_grant_id=grant.role_grant_id,
    )


def seed_membership_live_data_sync(
    session: Session,
    *,
    tenant_id: UUID,
    other_tenant_id: UUID,
) -> dict[str, UUID]:
    session.merge(
        Tenant(
            tenant_id=tenant_id,
            slug="acme",
            display_name="Acme",
            status=TenantStatus.ACTIVE,
        )
    )
    session.merge(
        Tenant(
            tenant_id=other_tenant_id,
            slug="globex",
            display_name="Globex",
            status=TenantStatus.ACTIVE,
        )
    )
    platform = PrincipalIdentity(
        auth_provider=AuthProviderType.LOCAL_PRINCIPAL,
        external_subject="local|platform-admin",
        display_name="Platform Admin",
        email="platform.admin@example.test",
    )
    tenant_admin = PrincipalIdentity(
        auth_provider=AuthProviderType.LOCAL_PRINCIPAL,
        external_subject="local|tenant-admin-acme",
        display_name="Maya Chen",
        email="maya.chen@example.test",
    )
    other = PrincipalIdentity(
        auth_provider=AuthProviderType.LOCAL_PRINCIPAL,
        external_subject="local|auditor-acme",
        display_name="Jordan Lee",
        email="jordan.lee@example.test",
    )
    session.add_all([platform, tenant_admin, other])
    session.flush()
    membership = TenantMembership(
        tenant_id=tenant_id,
        principal_identity_id=tenant_admin.principal_identity_id,
        status="active",
        revision_token="qa054-live-membership-revision",
        membership_source=MembershipSource.ADMIN_ASSIGNMENT.value,
        created_by_principal_id="platform-admin",
        updated_by_principal_id="platform-admin",
    )
    session.add(
        TenantMembership(
            tenant_id=tenant_id,
            principal_identity_id=other.principal_identity_id,
            status="active",
            revision_token="qa054-live-other-revision",
            membership_source=MembershipSource.ADMIN_ASSIGNMENT.value,
            created_by_principal_id="platform-admin",
            updated_by_principal_id="platform-admin",
        )
    )
    session.add(membership)
    grant = RoleGrant(
        principal_identity_id=tenant_admin.principal_identity_id,
        scope_type=RoleScopeType.TENANT,
        tenant_id=tenant_id,
        role_code=RoleCode.TENANT_ADMIN,
        granted_by_principal_id=platform.principal_identity_id,
    )
    session.add(grant)
    session.add(
        RoleGrant(
            principal_identity_id=platform.principal_identity_id,
            scope_type=RoleScopeType.PLATFORM,
            tenant_id=None,
            role_code=RoleCode.PLATFORM_ADMIN,
            granted_by_principal_id=platform.principal_identity_id,
        )
    )
    invitation_email = "invited.user@example.test"
    session.add(
        UserInvitation(
            tenant_id=tenant_id,
            invited_email=invitation_email,
            invited_email_hash=email_fingerprint(invitation_email),
            masked_email=mask_email(invitation_email),
            requested_roles=["tenant_user"],
            status="pending",
            idempotency_key="qa054-live-invite",
            invited_by_principal_id="tenant-admin-acme",
            expires_at=datetime.now(UTC) + timedelta(days=7),
            trace_id="trace-qa054-invite",
        )
    )
    session.add(
        AccessDecisionRecord(
            principal_identity_id=tenant_admin.principal_identity_id,
            scope_type=RoleScopeType.TENANT,
            tenant_id=tenant_id,
            surface_key="GET:/admin/app/memberships/bootstrap.json",
            requested_action="Open membership workspace",
            decision=AccessDecision.ALLOW,
            reason_code=AccessReasonCode.INSUFFICIENT_ROLE,
            auth_mode="local_principal",
            token_subject=None,
            token_jti=None,
            trace_id="trace-qa054-allow",
            request_id="request-qa054-allow",
            required_roles=["tenant_admin"],
            required_permissions=["membership-admin:read"],
            secret_free=True,
        )
    )
    session.add(
        MembershipAuditRecord(
            tenant_id=tenant_id,
            actor_principal_id="tenant-admin-acme",
            target_principal_identity_id=tenant_admin.principal_identity_id,
            action=MembershipAuditAction.ROLE_GRANT_CREATED.value,
            decision=MembershipAuditDecision.ALLOW.value,
            summary="Role grant created from qa054 live seed.",
            trace_id="trace-qa054-audit",
            redacted_metadata={"role_code": "tenant_admin"},
        )
    )
    session.add(
        SupportOverrideRequest(
            requester_principal_id=platform.principal_identity_id,
            target_tenant_id=tenant_id,
            justification="Safe qa054 support review",
            status=SupportOverrideStatus.APPROVED,
            approver_principal_id=platform.principal_identity_id,
            request_trace_id="trace-qa054-support",
            idempotency_key="qa054-support-override",
            decided_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(hours=2),
        )
    )
    session.commit()
    return {
        "platform_principal_id": platform.principal_identity_id,
        "tenant_principal_id": tenant_admin.principal_identity_id,
        "other_principal_id": other.principal_identity_id,
        "tenant_membership_id": membership.tenant_membership_id,
        "role_grant_id": grant.role_grant_id,
    }
