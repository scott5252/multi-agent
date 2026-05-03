from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel

from multi_agent_platform.api.schemas.memberships import (
    MembershipAccessHistoryResponse,
    MembershipAuditResponse,
    MembershipInvitationResponse,
    MembershipPrincipalResponse,
    MembershipRoleGrantResponse,
    TenantMembershipResponse,
)


class MembershipAdministrationPage(BaseModel):
    title: str = "Membership Administration"
    tenant_id: UUID | None = None
    platform_scope: bool = False
    principals: tuple[MembershipPrincipalResponse, ...]
    invitations: tuple[MembershipInvitationResponse, ...]
    memberships: tuple[TenantMembershipResponse, ...]
    role_grants: tuple[MembershipRoleGrantResponse, ...]
    access_history: tuple[MembershipAccessHistoryResponse, ...]
    audit_records: tuple[MembershipAuditResponse, ...]
    notice: str | None = None

    @property
    def scope_label(self) -> str:
        if self.tenant_id is None:
            return "Platform scope"
        return f"Tenant {self.tenant_id}"

    @property
    def active_principal_count(self) -> int:
        return sum(
            1 for principal in self.principals if principal.status.value == "active"
        )

    @property
    def active_grant_count(self) -> int:
        return sum(1 for grant in self.role_grants if grant.status.value == "active")


def redaction_notice() -> str:
    return (
        "Membership administration shows masked emails, safe subject labels, "
        "role codes, status, trace ids, and audit summaries only. Passwords, "
        "tokens, credentials, and raw secret values are never accepted or shown."
    )
