from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from multi_agent_platform.admin.memberships.models import (
    InvitationStatus,
    MembershipAuditAction,
    MembershipAuditDecision,
    TenantMembershipStatus,
)
from multi_agent_platform.db.models.access_control import (
    AccessDecision,
    AccessReasonCode,
    AuthProviderType,
    PrincipalIdentityStatus,
    RoleCode,
    RoleGrantStatus,
    RoleScopeType,
)


class MembershipPrincipalResponse(BaseModel):
    principal_identity_id: UUID
    auth_provider: AuthProviderType
    external_subject: str
    subject_display: str
    display_name: str | None
    masked_email: str | None
    status: PrincipalIdentityStatus
    created_at: datetime
    updated_at: datetime


class MembershipInvitationCreateRequest(BaseModel):
    tenant_id: UUID | None = None
    email: str = Field(min_length=3, max_length=320)
    requested_roles: tuple[RoleCode, ...] = (RoleCode.TENANT_USER,)
    idempotency_key: str | None = Field(default=None, max_length=128)

    @field_validator("requested_roles")
    @classmethod
    def validate_roles(cls, values: tuple[RoleCode, ...]) -> tuple[RoleCode, ...]:
        if not values:
            return (RoleCode.TENANT_USER,)
        return values

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip()
        if "@" not in normalized or normalized.startswith("@"):
            raise ValueError("valid email address required")
        return normalized


class MembershipInvitationResponse(BaseModel):
    user_invitation_id: UUID
    tenant_id: UUID | None
    masked_email: str
    email_hash: str
    requested_roles: tuple[RoleCode, ...]
    status: InvitationStatus
    idempotency_key: str | None
    invited_by_principal_id: str
    principal_identity_id: UUID | None
    expires_at: datetime | None
    created_at: datetime
    updated_at: datetime
    replayed: bool = False


class MembershipPrincipalLinkRequest(BaseModel):
    principal_identity_id: UUID | None = None
    auth0_subject: str = Field(min_length=3, max_length=255)
    email: str | None = Field(default=None, max_length=320)
    display_name: str | None = Field(default=None, max_length=255)


class MembershipRoleGrantCreateRequest(BaseModel):
    principal_identity_id: UUID
    scope_type: RoleScopeType
    tenant_id: UUID | None = None
    role_code: RoleCode


class MembershipRoleGrantResponse(BaseModel):
    role_grant_id: UUID
    principal_identity_id: UUID
    scope_type: RoleScopeType
    tenant_id: UUID | None
    role_code: RoleCode
    status: RoleGrantStatus
    effective_at: datetime
    expires_at: datetime | None
    revoked_at: datetime | None
    updated_at: datetime


class TenantMembershipResponse(BaseModel):
    tenant_membership_id: UUID
    tenant_id: UUID
    principal_identity_id: UUID
    status: TenantMembershipStatus
    revision_token: str
    membership_source: str
    created_by_principal_id: str
    updated_by_principal_id: str
    created_at: datetime
    updated_at: datetime
    suspended_at: datetime | None
    removed_at: datetime | None


class MembershipAuditResponse(BaseModel):
    membership_audit_record_id: UUID
    tenant_id: UUID | None
    actor_principal_id: str
    target_principal_identity_id: UUID | None
    action: MembershipAuditAction
    decision: MembershipAuditDecision
    summary: str
    trace_id: str
    redacted_metadata: dict[str, object]
    created_at: datetime


class MembershipAccessHistoryResponse(BaseModel):
    access_decision_record_id: UUID
    principal_identity_id: UUID | None
    tenant_id: UUID | None
    surface_key: str
    requested_action: str
    decision: AccessDecision
    reason_code: AccessReasonCode
    trace_id: str
    occurred_at: datetime


class MembershipSnapshotResponse(BaseModel):
    principals: tuple[MembershipPrincipalResponse, ...]
    invitations: tuple[MembershipInvitationResponse, ...]
    memberships: tuple[TenantMembershipResponse, ...]
    role_grants: tuple[MembershipRoleGrantResponse, ...]
    access_history: tuple[MembershipAccessHistoryResponse, ...]
    audit_records: tuple[MembershipAuditResponse, ...]


class MembershipStatusUpdateRequest(BaseModel):
    status: TenantMembershipStatus


class MembershipPageActionResponse(BaseModel):
    ok: bool = True
    message: str
