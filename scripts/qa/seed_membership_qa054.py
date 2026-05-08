from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID

from sqlalchemy import create_engine, select
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
    GrantSource,
    PrincipalIdentity,
    PrincipalIdentityStatus,
    RoleCode,
    RoleGrant,
    RoleGrantStatus,
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

ACME_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
GLOBEX_TENANT_ID = UUID("22222222-2222-2222-2222-222222222222")
SEED_INVITATION_EMAIL = "invited.user@example.test"
PLAYWRIGHT_INVITATION_EMAIL = "invite.replay@example.test"


def main() -> int:
    engine = create_engine(_database_url())
    now = datetime(2026, 5, 7, 18, tzinfo=UTC)
    with Session(engine) as session:
        _upsert_tenant(session, ACME_TENANT_ID, "acme", "Acme")
        _upsert_tenant(session, GLOBEX_TENANT_ID, "globex", "Globex")
        platform = _upsert_principal(
            session,
            external_subject="local|platform-admin",
            display_name="Platform Admin",
            email="platform.admin@example.test",
        )
        tenant_admin = _upsert_principal(
            session,
            external_subject="local|tenant-admin-acme",
            display_name="Maya Chen",
            email="maya.chen@example.test",
        )
        auditor = _upsert_principal(
            session,
            external_subject="local|auditor-acme",
            display_name="Jordan Lee",
            email="jordan.lee@example.test",
        )
        _upsert_membership(session, tenant_admin, "qa054-live-membership-revision")
        _upsert_membership(session, auditor, "qa054-live-auditor-revision")
        _upsert_role_grant(
            session,
            principal=tenant_admin,
            scope_type=RoleScopeType.TENANT,
            tenant_id=ACME_TENANT_ID,
            role_code=RoleCode.TENANT_ADMIN,
            granted_by=platform,
        )
        _upsert_role_grant(
            session,
            principal=auditor,
            scope_type=RoleScopeType.TENANT,
            tenant_id=ACME_TENANT_ID,
            role_code=RoleCode.TENANT_USER,
            granted_by=platform,
        )
        _upsert_role_grant(
            session,
            principal=platform,
            scope_type=RoleScopeType.PLATFORM,
            tenant_id=None,
            role_code=RoleCode.PLATFORM_ADMIN,
            granted_by=platform,
        )
        _upsert_invitation(
            session,
            email=SEED_INVITATION_EMAIL,
            idempotency_key="qa054-live-invite",
            invited_by="tenant-admin-acme",
            now=now,
        )
        _upsert_access_decision(session, tenant_admin)
        _upsert_audit_record(session, tenant_admin)
        _upsert_support_override(session, platform, now)
        session.commit()
    print("Seeded QA054 membership live records")
    print(f"tenant_id={ACME_TENANT_ID}")
    print(f"seed_invitation_hash={email_fingerprint(SEED_INVITATION_EMAIL)[:16]}")
    print(
        f"playwright_invitation_hash={email_fingerprint(PLAYWRIGHT_INVITATION_EMAIL)[:16]}"
    )
    return 0


def _upsert_tenant(
    session: Session, tenant_id: UUID, slug: str, display_name: str
) -> None:
    record = session.get(Tenant, tenant_id)
    if record is None:
        record = Tenant(tenant_id=tenant_id)
        session.add(record)
    record.slug = slug
    record.display_name = display_name
    record.status = TenantStatus.ACTIVE


def _upsert_principal(
    session: Session,
    *,
    external_subject: str,
    display_name: str,
    email: str,
) -> PrincipalIdentity:
    record = session.scalar(
        select(PrincipalIdentity).where(
            PrincipalIdentity.external_subject == external_subject
        )
    )
    if record is None:
        record = PrincipalIdentity(
            auth_provider=AuthProviderType.LOCAL_PRINCIPAL,
            external_subject=external_subject,
        )
        session.add(record)
    record.display_name = display_name
    record.email = email
    record.status = PrincipalIdentityStatus.ACTIVE
    session.flush()
    return record


def _upsert_membership(
    session: Session, principal: PrincipalIdentity, revision_token: str
) -> TenantMembership:
    record = session.scalar(
        select(TenantMembership).where(
            TenantMembership.tenant_id == ACME_TENANT_ID,
            TenantMembership.principal_identity_id == principal.principal_identity_id,
        )
    )
    if record is None:
        record = TenantMembership(
            tenant_id=ACME_TENANT_ID,
            principal_identity_id=principal.principal_identity_id,
            created_by_principal_id="platform-admin",
            updated_by_principal_id="platform-admin",
        )
        session.add(record)
    record.status = "active"
    record.revision_token = revision_token
    record.membership_source = MembershipSource.ADMIN_ASSIGNMENT.value
    record.removed_at = None
    record.suspended_at = None
    session.flush()
    return record


def _upsert_role_grant(
    session: Session,
    *,
    principal: PrincipalIdentity,
    scope_type: RoleScopeType,
    tenant_id: UUID | None,
    role_code: RoleCode,
    granted_by: PrincipalIdentity,
) -> RoleGrant:
    record = session.scalar(
        select(RoleGrant).where(
            RoleGrant.principal_identity_id == principal.principal_identity_id,
            RoleGrant.scope_type == scope_type,
            RoleGrant.tenant_id == tenant_id,
            RoleGrant.role_code == role_code,
        )
    )
    if record is None:
        record = RoleGrant(
            principal_identity_id=principal.principal_identity_id,
            scope_type=scope_type,
            tenant_id=tenant_id,
            role_code=role_code,
            grant_source=GrantSource.ADMIN_ASSIGNMENT,
            granted_by_principal_id=granted_by.principal_identity_id,
        )
        session.add(record)
    record.status = RoleGrantStatus.ACTIVE
    record.revoked_at = None
    session.flush()
    return record


def _upsert_invitation(
    session: Session,
    *,
    email: str,
    idempotency_key: str,
    invited_by: str,
    now: datetime,
) -> UserInvitation:
    fingerprint = email_fingerprint(email)
    record = session.scalar(
        select(UserInvitation).where(
            UserInvitation.tenant_id == ACME_TENANT_ID,
            UserInvitation.invited_email_hash == fingerprint,
            UserInvitation.idempotency_key == idempotency_key,
        )
    )
    if record is None:
        record = UserInvitation(
            tenant_id=ACME_TENANT_ID,
            invited_email=email,
            invited_email_hash=fingerprint,
            idempotency_key=idempotency_key,
            invited_by_principal_id=invited_by,
            trace_id=f"trace-{idempotency_key}",
        )
        session.add(record)
    record.masked_email = mask_email(email)
    record.requested_roles = ["tenant_user"]
    record.status = "pending"
    record.expires_at = now + timedelta(days=7)
    session.flush()
    return record


def _upsert_access_decision(
    session: Session, tenant_admin: PrincipalIdentity
) -> AccessDecisionRecord:
    record = session.scalar(
        select(AccessDecisionRecord).where(
            AccessDecisionRecord.trace_id == "trace-qa054-allow",
            AccessDecisionRecord.request_id == "request-qa054-allow",
        )
    )
    if record is None:
        record = AccessDecisionRecord(
            principal_identity_id=tenant_admin.principal_identity_id,
            scope_type=RoleScopeType.TENANT,
            tenant_id=ACME_TENANT_ID,
            surface_key="GET:/admin/app/memberships/bootstrap.json",
            requested_action="Open membership workspace",
            decision=AccessDecision.ALLOW,
            reason_code=AccessReasonCode.INSUFFICIENT_ROLE,
            auth_mode="local_principal",
            trace_id="trace-qa054-allow",
            request_id="request-qa054-allow",
            required_roles=["tenant_admin"],
            required_permissions=["tenant:admin"],
            secret_free=True,
        )
        session.add(record)
    session.flush()
    return record


def _upsert_audit_record(
    session: Session, tenant_admin: PrincipalIdentity
) -> MembershipAuditRecord:
    record = session.scalar(
        select(MembershipAuditRecord).where(
            MembershipAuditRecord.trace_id == "trace-qa054-audit"
        )
    )
    if record is None:
        record = MembershipAuditRecord(
            tenant_id=ACME_TENANT_ID,
            actor_principal_id="tenant-admin-acme",
            target_principal_identity_id=tenant_admin.principal_identity_id,
            action=MembershipAuditAction.ROLE_GRANT_CREATED.value,
            decision=MembershipAuditDecision.ALLOW.value,
            summary="Role grant created from qa054 live seed.",
            trace_id="trace-qa054-audit",
            redacted_metadata={"role_code": "tenant_admin"},
        )
        session.add(record)
    session.flush()
    return record


def _upsert_support_override(
    session: Session, platform: PrincipalIdentity, now: datetime
) -> SupportOverrideRequest:
    record = session.scalar(
        select(SupportOverrideRequest).where(
            SupportOverrideRequest.idempotency_key == "qa054-support-override"
        )
    )
    if record is None:
        record = SupportOverrideRequest(
            requester_principal_id=platform.principal_identity_id,
            target_tenant_id=ACME_TENANT_ID,
            request_trace_id="trace-qa054-support",
            idempotency_key="qa054-support-override",
        )
        session.add(record)
    record.justification = "Safe qa054 support review"
    record.status = SupportOverrideStatus.APPROVED
    record.approver_principal_id = platform.principal_identity_id
    record.decided_at = now
    record.expires_at = now + timedelta(hours=2)
    session.flush()
    return record


def _database_url() -> str:
    value = os.environ.get("DATABASE_URL") or _env_file_value("DATABASE_URL")
    if not value:
        raise RuntimeError("DATABASE_URL is required")
    return value


def _env_file_value(key: str) -> str | None:
    env_file = Path(".env")
    if not env_file.exists():
        return None
    for line in env_file.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name == key:
            return value
    return None


if __name__ == "__main__":
    raise SystemExit(main())
