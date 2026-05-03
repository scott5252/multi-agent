from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from multi_agent_platform.db.base import Base, TimestampMixin, utcnow


def _revision_token() -> str:
    return uuid4().hex


class UserInvitation(Base, TimestampMixin):
    __tablename__ = "user_invitations"
    __table_args__ = (
        Index("ix_user_invitations_tenant_status", "tenant_id", "status"),
        Index("ix_user_invitations_email_hash", "tenant_id", "invited_email_hash"),
        Index("ix_user_invitations_idempotency", "idempotency_key"),
    )

    user_invitation_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(ForeignKey("tenants.tenant_id"))
    invited_email: Mapped[str] = mapped_column(String(320))
    invited_email_hash: Mapped[str] = mapped_column(String(128))
    masked_email: Mapped[str] = mapped_column(String(320))
    requested_roles: Mapped[list[str]] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    idempotency_key: Mapped[str | None] = mapped_column(String(128))
    invited_by_principal_id: Mapped[str] = mapped_column(String(255))
    principal_identity_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("principal_identities.principal_identity_id")
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    trace_id: Mapped[str] = mapped_column(String(128))


class TenantMembership(Base, TimestampMixin):
    __tablename__ = "tenant_memberships"
    __table_args__ = (
        UniqueConstraint("tenant_id", "principal_identity_id"),
        Index("ix_tenant_memberships_tenant_status", "tenant_id", "status"),
        Index(
            "ix_tenant_memberships_principal",
            "principal_identity_id",
            "tenant_id",
        ),
        Index("ix_tenant_memberships_revision", "tenant_id", "revision_token"),
    )

    tenant_membership_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=False
    )
    principal_identity_id: Mapped[UUID] = mapped_column(
        ForeignKey("principal_identities.principal_identity_id", ondelete="CASCADE"),
        nullable=False,
    )
    invitation_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("user_invitations.user_invitation_id")
    )
    status: Mapped[str] = mapped_column(String(32), default="active")
    revision_token: Mapped[str] = mapped_column(String(64), default=_revision_token)
    membership_source: Mapped[str] = mapped_column(
        String(64),
        default="admin_assignment",
    )
    created_by_principal_id: Mapped[str] = mapped_column(String(255))
    updated_by_principal_id: Mapped[str] = mapped_column(String(255))
    suspended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    removed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class MembershipAuditRecord(Base):
    __tablename__ = "membership_audit_records"
    __table_args__ = (
        Index("ix_membership_audit_tenant_created", "tenant_id", "created_at"),
        Index("ix_membership_audit_actor", "actor_principal_id", "created_at"),
        Index("ix_membership_audit_target", "target_principal_identity_id"),
        Index("ix_membership_audit_action", "action", "decision"),
    )

    membership_audit_record_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID | None] = mapped_column(ForeignKey("tenants.tenant_id"))
    actor_principal_id: Mapped[str] = mapped_column(String(255))
    target_principal_identity_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("principal_identities.principal_identity_id")
    )
    action: Mapped[str] = mapped_column(String(64))
    decision: Mapped[str] = mapped_column(String(32))
    summary: Mapped[str] = mapped_column(String(500))
    trace_id: Mapped[str] = mapped_column(String(128))
    redacted_metadata: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )
