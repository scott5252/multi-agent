from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import JSON, Boolean, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from multi_agent_platform.db.base import Base, TimestampMixin


class PrincipalIdentityStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"


class AuthProviderType(StrEnum):
    AUTH0 = "auth0"
    LOCAL_PRINCIPAL = "local_principal"
    SYSTEM = "system"


class RoleScopeType(StrEnum):
    PLATFORM = "platform"
    TENANT = "tenant"


class RoleCode(StrEnum):
    TENANT_USER = "tenant_user"
    TENANT_ADMIN = "tenant_admin"
    PLATFORM_ADMIN = "platform_admin"


class GrantSource(StrEnum):
    BOOTSTRAP = "bootstrap"
    ADMIN_ASSIGNMENT = "admin_assignment"
    LOCAL_CATALOG = "local_catalog"
    SYNC = "sync"


class RoleGrantStatus(StrEnum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class SupportOverrideStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    REVOKED = "revoked"


class AccessDecision(StrEnum):
    ALLOW = "allow"
    DENY = "deny"
    ERROR = "error"


class AccessReasonCode(StrEnum):
    UNAUTHENTICATED = "unauthenticated"
    INVALID_TOKEN = "invalid_token"
    INSUFFICIENT_PERMISSION = "insufficient_permission"
    INSUFFICIENT_ROLE = "insufficient_role"
    CROSS_TENANT = "cross_tenant"
    SUPPORT_OVERRIDE_REQUIRED = "support_override_required"
    SUPPORT_OVERRIDE_UNAPPROVED = "support_override_unapproved"
    CONFIG_ERROR = "config_error"
    DELEGATED_CREDENTIAL_DENIED = "delegated_credential_denied"
    INTERNAL_ERROR = "internal_error"


class PrincipalIdentity(Base, TimestampMixin):
    __tablename__ = "principal_identities"

    principal_identity_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    auth_provider: Mapped[AuthProviderType] = mapped_column(
        Enum(AuthProviderType, native_enum=False)
    )
    external_subject: Mapped[str] = mapped_column(String(255), unique=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[PrincipalIdentityStatus] = mapped_column(
        Enum(PrincipalIdentityStatus, native_enum=False),
        default=PrincipalIdentityStatus.ACTIVE,
    )


class RoleGrant(Base):
    __tablename__ = "role_grants"

    role_grant_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    principal_identity_id: Mapped[UUID] = mapped_column(
        ForeignKey("principal_identities.principal_identity_id", ondelete="CASCADE")
    )
    scope_type: Mapped[RoleScopeType] = mapped_column(
        Enum(RoleScopeType, native_enum=False)
    )
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    role_code: Mapped[RoleCode] = mapped_column(Enum(RoleCode, native_enum=False))
    grant_source: Mapped[GrantSource] = mapped_column(
        Enum(GrantSource, native_enum=False),
        default=GrantSource.BOOTSTRAP,
    )
    status: Mapped[RoleGrantStatus] = mapped_column(
        Enum(RoleGrantStatus, native_enum=False),
        default=RoleGrantStatus.ACTIVE,
    )
    effective_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    granted_by_principal_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("principal_identities.principal_identity_id"), nullable=True
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )


class SupportOverrideRequest(Base):
    __tablename__ = "support_override_requests"

    support_override_request_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    requester_principal_id: Mapped[UUID] = mapped_column(
        ForeignKey("principal_identities.principal_identity_id")
    )
    target_tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.tenant_id"))
    justification: Mapped[str] = mapped_column(String(500))
    status: Mapped[SupportOverrideStatus] = mapped_column(
        Enum(SupportOverrideStatus, native_enum=False),
        default=SupportOverrideStatus.PENDING,
    )
    approver_principal_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("principal_identities.principal_identity_id"), nullable=True
    )
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    decided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    request_trace_id: Mapped[str] = mapped_column(String(64))
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True)


class AccessDecisionRecord(Base):
    __tablename__ = "access_decision_records"

    access_decision_record_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    principal_identity_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("principal_identities.principal_identity_id"), nullable=True
    )
    scope_type: Mapped[RoleScopeType] = mapped_column(
        Enum(RoleScopeType, native_enum=False)
    )
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    surface_key: Mapped[str] = mapped_column(String(255))
    requested_action: Mapped[str] = mapped_column(String(128))
    decision: Mapped[AccessDecision] = mapped_column(
        Enum(AccessDecision, native_enum=False)
    )
    reason_code: Mapped[AccessReasonCode] = mapped_column(
        Enum(AccessReasonCode, native_enum=False)
    )
    auth_mode: Mapped[str] = mapped_column(String(32))
    token_subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    token_jti: Mapped[str | None] = mapped_column(String(255), nullable=True)
    support_override_request_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("support_override_requests.support_override_request_id"),
        nullable=True,
    )
    delegated_credential_link_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("delegated_credential_links.delegated_credential_link_id"),
        nullable=True,
    )
    trace_id: Mapped[str] = mapped_column(String(64))
    request_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    classification: Mapped[str] = mapped_column(String(64), default="authenticated")
    required_roles: Mapped[list[str]] = mapped_column(JSON, default=list)
    required_permissions: Mapped[list[str]] = mapped_column(JSON, default=list)
    policy_version: Mapped[str] = mapped_column(String(32), default="2026-04-22")
    secret_free: Mapped[bool] = mapped_column(Boolean, default=True)
