from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from multi_agent_platform.db.models.access_control import RoleCode, RoleScopeType

TENANT_ADMIN_ASSIGNABLE_ROLES = (RoleCode.TENANT_USER, RoleCode.TENANT_ADMIN)


class MembershipScopeType(StrEnum):
    PLATFORM = "platform"
    TENANT = "tenant"


class InvitationStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REVOKED = "revoked"
    EXPIRED = "expired"


class TenantMembershipStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REMOVED = "removed"


class MembershipSource(StrEnum):
    INVITATION = "invitation"
    ADMIN_ASSIGNMENT = "admin_assignment"
    AUTH0_LINK = "auth0_link"
    LOCAL_CATALOG = "local_catalog"


class MembershipAuditAction(StrEnum):
    INVITATION_CREATED = "invitation_created"
    INVITATION_REPLAYED = "invitation_replayed"
    PRINCIPAL_LINKED = "principal_linked"
    PRINCIPAL_SUSPENDED = "principal_suspended"
    PRINCIPAL_REACTIVATED = "principal_reactivated"
    MEMBERSHIP_CREATED = "membership_created"
    MEMBERSHIP_SUSPENDED = "membership_suspended"
    MEMBERSHIP_RESTORED = "membership_restored"
    MEMBERSHIP_REMOVED = "membership_removed"
    ROLE_GRANT_CREATED = "role_grant_created"
    ROLE_GRANT_REVOKED = "role_grant_revoked"
    ACCESS_DENIED = "access_denied"


class MembershipAuditDecision(StrEnum):
    ALLOW = "allow"
    DENY = "deny"


class MembershipError(ValueError):
    """Base membership administration error."""


class MembershipPermissionError(PermissionError):
    """Raised when an admin crosses a membership authorization boundary."""


class MembershipConflictError(ValueError):
    """Raised when identity/provider references conflict."""


@dataclass(frozen=True, slots=True)
class MembershipAccessScope:
    scope_type: MembershipScopeType
    principal_id: str
    tenant_id: UUID | None = None
    platform_admin: bool = False
    trace_id: str = "membership-admin"

    def require_tenant(self) -> UUID:
        if self.tenant_id is None:
            raise MembershipPermissionError("tenant membership scope required")
        return self.tenant_id


def role_scope_type(scope_type: MembershipScopeType) -> RoleScopeType:
    if scope_type is MembershipScopeType.PLATFORM:
        return RoleScopeType.PLATFORM
    return RoleScopeType.TENANT
