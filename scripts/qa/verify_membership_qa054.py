from __future__ import annotations

import os
from pathlib import Path
from uuid import UUID

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from multi_agent_platform.admin.memberships.models import MembershipAuditAction
from multi_agent_platform.admin.memberships.redaction import email_fingerprint
from multi_agent_platform.db.models.access_control import (
    AccessDecisionRecord,
    RoleGrant,
    SupportOverrideRequest,
)
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
    with Session(engine) as session:
        memberships = _count(
            session,
            select(func.count())
            .select_from(TenantMembership)
            .where(TenantMembership.tenant_id == ACME_TENANT_ID),
        )
        grants = _count(
            session,
            select(func.count())
            .select_from(RoleGrant)
            .where(RoleGrant.tenant_id == ACME_TENANT_ID),
        )
        access_decisions = _count(
            session,
            select(func.count())
            .select_from(AccessDecisionRecord)
            .where(AccessDecisionRecord.tenant_id == ACME_TENANT_ID),
        )
        support_overrides = _count(
            session,
            select(func.count())
            .select_from(SupportOverrideRequest)
            .where(SupportOverrideRequest.target_tenant_id == ACME_TENANT_ID),
        )
        seed_invitations = _count_invitations(session, SEED_INVITATION_EMAIL)
        playwright_invitations = _count_invitations(
            session, PLAYWRIGHT_INVITATION_EMAIL
        )
        playwright_audits = _count(
            session,
            select(func.count())
            .select_from(MembershipAuditRecord)
            .where(
                MembershipAuditRecord.tenant_id == ACME_TENANT_ID,
                MembershipAuditRecord.action.in_(
                    [
                        MembershipAuditAction.INVITATION_CREATED.value,
                        MembershipAuditAction.INVITATION_REPLAYED.value,
                    ]
                ),
                MembershipAuditRecord.actor_principal_id == "tenant-admin-acme",
            ),
        )
        globex_memberships = _count(
            session,
            select(func.count())
            .select_from(TenantMembership)
            .where(TenantMembership.tenant_id == GLOBEX_TENANT_ID),
        )
        if memberships < 2:
            raise RuntimeError("Expected at least two Acme membership rows")
        if grants < 2:
            raise RuntimeError("Expected at least two Acme role grants")
        if access_decisions < 1:
            raise RuntimeError("Expected at least one Acme access decision")
        if support_overrides < 1:
            raise RuntimeError("Expected at least one Acme support override")
        if seed_invitations < 1:
            raise RuntimeError("Expected the seeded Acme invitation")
        if playwright_invitations < 1:
            raise RuntimeError(
                "Expected Playwright to create the invite.replay@example.test "
                "invitation"
            )
        if playwright_audits < 1:
            raise RuntimeError("Expected invitation audit evidence after Playwright")
        if globex_memberships:
            raise RuntimeError("Globex should not have QA054 seeded memberships")
    print("Verified QA054 membership live-data persistence")
    print(f"tenant_id={ACME_TENANT_ID}")
    print(f"memberships={memberships}")
    print(f"role_grants={grants}")
    print(f"access_decisions={access_decisions}")
    print(f"support_overrides={support_overrides}")
    print(f"seed_invitations={seed_invitations}")
    print(f"playwright_invitations={playwright_invitations}")
    print(f"invitation_audits={playwright_audits}")
    return 0


def _count(session: Session, stmt) -> int:
    return int(session.scalar(stmt) or 0)


def _count_invitations(session: Session, email: str) -> int:
    return _count(
        session,
        select(func.count())
        .select_from(UserInvitation)
        .where(
            UserInvitation.tenant_id == ACME_TENANT_ID,
            UserInvitation.invited_email_hash == email_fingerprint(email),
        ),
    )


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
