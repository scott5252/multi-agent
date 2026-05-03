from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException

from multi_agent_platform.admin.memberships.models import (
    MembershipPermissionError,
    TenantMembershipStatus,
)
from multi_agent_platform.admin.memberships.service import MembershipSnapshot
from multi_agent_platform.api.routers import admin_memberships
from multi_agent_platform.api.schemas.memberships import (
    MembershipInvitationCreateRequest,
    MembershipPrincipalLinkRequest,
    MembershipRoleGrantCreateRequest,
)
from multi_agent_platform.auth.principal import AuthProvider, PrincipalContext
from multi_agent_platform.db.models.access_control import (
    AccessDecision,
    AccessReasonCode,
    AuthProviderType,
    PrincipalIdentityStatus,
    RoleCode,
    RoleGrantStatus,
    RoleScopeType,
)
from multi_agent_platform.tenancy.context import ScopeType


class FakeMembershipService:
    def __init__(self) -> None:
        self.raise_permission_for: set[str] = set()
        self.return_none_for: set[str] = set()
        self.raise_conflict = False
        self.raise_lookup = False
        self.denials: list[dict[str, object]] = []
        self.tenant_id = uuid4()
        self.principal_identity_id = uuid4()
        self.role_grant_id = uuid4()
        self.tenant_membership_id = uuid4()
        self.now = datetime.now(UTC)

    def principal_record(self):
        return SimpleNamespace(
            principal_identity_id=self.principal_identity_id,
            auth_provider=AuthProviderType.AUTH0,
            external_subject="auth0|router-edge",
            display_name="Router Edge",
            email="router.edge@example.com",
            status=PrincipalIdentityStatus.ACTIVE,
            created_at=self.now,
            updated_at=self.now,
        )

    def invitation_record(self):
        return SimpleNamespace(
            user_invitation_id=uuid4(),
            tenant_id=self.tenant_id,
            invited_email_hash="1234567890abcdef1234",
            masked_email="ro***e@e***.com",
            requested_roles=["tenant_user"],
            status="pending",
            idempotency_key="router-edge",
            invited_by_principal_id="platform-admin",
            principal_identity_id=None,
            expires_at=self.now,
            created_at=self.now,
            updated_at=self.now,
        )

    def role_grant_record(self):
        return SimpleNamespace(
            role_grant_id=self.role_grant_id,
            principal_identity_id=self.principal_identity_id,
            scope_type=RoleScopeType.TENANT,
            tenant_id=self.tenant_id,
            role_code=RoleCode.TENANT_USER,
            status=RoleGrantStatus.ACTIVE,
            effective_at=self.now,
            expires_at=None,
            revoked_at=None,
            updated_at=self.now,
        )

    def membership_record(self):
        return SimpleNamespace(
            tenant_membership_id=self.tenant_membership_id,
            tenant_id=self.tenant_id,
            principal_identity_id=self.principal_identity_id,
            status="active",
            revision_token="revision-token",
            membership_source="admin_assignment",
            created_by_principal_id="platform-admin",
            updated_by_principal_id="platform-admin",
            created_at=self.now,
            updated_at=self.now,
            suspended_at=None,
            removed_at=None,
        )

    def access_history_record(self):
        return SimpleNamespace(
            access_decision_record_id=uuid4(),
            principal_identity_id=self.principal_identity_id,
            tenant_id=self.tenant_id,
            surface_key="GET:/admin/memberships",
            requested_action="render_membership_administration_ui",
            decision=AccessDecision.ALLOW,
            reason_code=AccessReasonCode.UNAUTHENTICATED,
            trace_id="trace-router-edge",
            occurred_at=self.now,
        )

    def audit_record(self):
        return SimpleNamespace(
            membership_audit_record_id=uuid4(),
            tenant_id=self.tenant_id,
            actor_principal_id="platform-admin",
            target_principal_identity_id=self.principal_identity_id,
            action="invitation_created",
            decision="allow",
            summary="Membership invitation created.",
            trace_id="trace-router-edge",
            redacted_metadata={"masked_email": "ro***e@e***.com"},
            created_at=self.now,
        )

    async def snapshot(self, access_scope, *, query=None):  # noqa: ANN001
        return MembershipSnapshot(
            principals=(self.principal_record(),),
            invitations=(self.invitation_record(),),
            memberships=(self.membership_record(),),
            role_grants=(self.role_grant_record(),),
            access_history=(self.access_history_record(),),
            audit_records=(self.audit_record(),),
        )

    async def create_invitation(self, **kwargs):  # noqa: ANN003
        if "create_invitation" in self.raise_permission_for:
            raise MembershipPermissionError("invite denied")
        return SimpleNamespace(invitation=self.invitation_record(), replayed=True)

    async def link_auth0_principal(self, **kwargs):  # noqa: ANN003
        if "link_auth0_principal" in self.raise_permission_for:
            raise MembershipPermissionError("link denied")
        if self.raise_conflict:
            from multi_agent_platform.admin.memberships.models import (
                MembershipConflictError,
            )

            raise MembershipConflictError("subject conflict")
        return self.principal_record()

    async def create_role_grant(self, **kwargs):  # noqa: ANN003
        if "create_role_grant" in self.raise_permission_for:
            raise MembershipPermissionError("grant denied")
        if self.raise_lookup:
            raise LookupError("principal missing")
        return self.role_grant_record()

    async def revoke_role_grant(self, **kwargs):  # noqa: ANN003
        if "revoke_role_grant" in self.raise_permission_for:
            raise MembershipPermissionError("revoke denied")
        if "revoke_role_grant" in self.return_none_for:
            return None
        return self.role_grant_record()

    async def suspend_principal(self, **kwargs):  # noqa: ANN003
        if "suspend_principal" in self.raise_permission_for:
            raise MembershipPermissionError("suspend denied")
        if "suspend_principal" in self.return_none_for:
            return None
        return self.principal_record()

    async def reactivate_principal(self, **kwargs):  # noqa: ANN003
        if "reactivate_principal" in self.raise_permission_for:
            raise MembershipPermissionError("reactivate denied")
        if "reactivate_principal" in self.return_none_for:
            return None
        return self.principal_record()

    async def update_membership_status(self, **kwargs):  # noqa: ANN003
        if "update_membership_status" in self.return_none_for:
            return None
        return self.membership_record()

    async def record_denial(self, **kwargs):  # noqa: ANN003
        self.denials.append(kwargs)
        return self.audit_record()


def platform_principal() -> PrincipalContext:
    return PrincipalContext(
        principal_id="platform-admin",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        tenant_id=None,
        role_codes=("platform_admin",),
        permission_codes=("membership-admin:read",),
        scope_type=ScopeType.PLATFORM,
        trace_id="trace-platform",
    )


def tenant_principal(tenant_id: UUID | None) -> PrincipalContext:
    return PrincipalContext(
        principal_id="tenant-admin",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        tenant_id=tenant_id,
        role_codes=("tenant_admin",),
        permission_codes=("membership-admin:read",),
        scope_type=ScopeType.TENANT,
        trace_id="trace-tenant",
    )


@pytest.fixture
def fake_service(monkeypatch: pytest.MonkeyPatch) -> FakeMembershipService:
    service = FakeMembershipService()
    monkeypatch.setattr(admin_memberships, "_service", lambda session: service)
    return service


async def test_snapshot_api_maps_full_snapshot(
    fake_service: FakeMembershipService,
) -> None:
    response = await admin_memberships.memberships_snapshot_api(
        platform_principal(),
        object(),
        tenant_id=fake_service.tenant_id,
        q="router",
    )

    assert response.principals[0].subject_display == "auth***edge"
    assert response.invitations[0].replayed is False
    assert response.access_history[0].surface_key == "GET:/admin/memberships"
    assert response.audit_records[0].action.value == "invitation_created"


async def test_router_api_error_branches(fake_service: FakeMembershipService) -> None:
    fake_service.raise_permission_for.add("create_invitation")
    with pytest.raises(HTTPException) as invitation_exc:
        await admin_memberships.create_invitation_api(
            MembershipInvitationCreateRequest(
                tenant_id=fake_service.tenant_id,
                email="denied@example.com",
                requested_roles=(RoleCode.PLATFORM_ADMIN,),
            ),
            tenant_principal(fake_service.tenant_id),
            object(),
        )
    assert invitation_exc.value.status_code == 403
    assert fake_service.denials

    fake_service.raise_permission_for = {"link_auth0_principal"}
    with pytest.raises(HTTPException) as link_permission_exc:
        await admin_memberships.link_principal_api(
            MembershipPrincipalLinkRequest(auth0_subject="auth0|tenant"),
            tenant_principal(fake_service.tenant_id),
            object(),
        )
    assert link_permission_exc.value.status_code == 403

    fake_service.raise_permission_for.clear()
    fake_service.raise_conflict = True
    with pytest.raises(HTTPException) as link_conflict_exc:
        await admin_memberships.link_principal_api(
            MembershipPrincipalLinkRequest(auth0_subject="auth0|conflict"),
            platform_principal(),
            object(),
        )
    assert link_conflict_exc.value.status_code == 409

    fake_service.raise_conflict = False
    fake_service.raise_permission_for = {"create_role_grant"}
    with pytest.raises(HTTPException) as grant_permission_exc:
        await admin_memberships.create_role_grant_api(
            MembershipRoleGrantCreateRequest(
                principal_identity_id=fake_service.principal_identity_id,
                scope_type=RoleScopeType.TENANT,
                tenant_id=fake_service.tenant_id,
                role_code=RoleCode.PLATFORM_ADMIN,
            ),
            tenant_principal(fake_service.tenant_id),
            object(),
        )
    assert grant_permission_exc.value.status_code == 403

    fake_service.raise_permission_for.clear()
    fake_service.raise_lookup = True
    with pytest.raises(HTTPException) as grant_lookup_exc:
        await admin_memberships.create_role_grant_api(
            MembershipRoleGrantCreateRequest(
                principal_identity_id=fake_service.principal_identity_id,
                scope_type=RoleScopeType.TENANT,
                tenant_id=fake_service.tenant_id,
                role_code=RoleCode.TENANT_USER,
            ),
            platform_principal(),
            object(),
        )
    assert grant_lookup_exc.value.status_code == 404


async def test_router_api_status_and_scope_edges(
    fake_service: FakeMembershipService,
) -> None:
    fake_service.raise_permission_for = {"revoke_role_grant"}
    with pytest.raises(HTTPException) as revoke_permission_exc:
        await admin_memberships.revoke_role_grant_api(
            fake_service.role_grant_id,
            platform_principal(),
            object(),
        )
    assert revoke_permission_exc.value.status_code == 403

    fake_service.raise_permission_for.clear()
    fake_service.return_none_for = {"revoke_role_grant"}
    with pytest.raises(HTTPException) as revoke_missing_exc:
        await admin_memberships.revoke_role_grant_api(
            fake_service.role_grant_id,
            platform_principal(),
            object(),
        )
    assert revoke_missing_exc.value.status_code == 404

    fake_service.return_none_for = {"suspend_principal"}
    with pytest.raises(HTTPException) as suspend_missing_exc:
        await admin_memberships.suspend_principal_api(
            fake_service.principal_identity_id,
            platform_principal(),
            object(),
        )
    assert suspend_missing_exc.value.status_code == 404

    fake_service.raise_permission_for = {"suspend_principal"}
    fake_service.return_none_for.clear()
    with pytest.raises(HTTPException) as suspend_permission_exc:
        await admin_memberships.suspend_principal_api(
            fake_service.principal_identity_id,
            tenant_principal(fake_service.tenant_id),
            object(),
        )
    assert suspend_permission_exc.value.status_code == 403

    fake_service.raise_permission_for.clear()
    fake_service.return_none_for = {"reactivate_principal"}
    with pytest.raises(HTTPException) as reactivate_missing_exc:
        await admin_memberships.reactivate_principal_api(
            fake_service.principal_identity_id,
            platform_principal(),
            object(),
        )
    assert reactivate_missing_exc.value.status_code == 404

    fake_service.return_none_for = {"update_membership_status"}
    with pytest.raises(HTTPException) as membership_missing_exc:
        await admin_memberships.update_membership_status_api(
            fake_service.tenant_membership_id,
            TenantMembershipStatus.SUSPENDED,
            platform_principal(),
            object(),
            tenant_id=fake_service.tenant_id,
        )
    assert membership_missing_exc.value.status_code == 404

    with pytest.raises(HTTPException) as missing_tenant_scope_exc:
        await admin_memberships.memberships_snapshot_api(
            tenant_principal(None),
            object(),
        )
    assert missing_tenant_scope_exc.value.status_code == 403


async def test_router_page_post_error_branches(
    fake_service: FakeMembershipService,
) -> None:
    fake_service.raise_permission_for = {"create_invitation"}
    with pytest.raises(HTTPException) as invite_page_exc:
        await admin_memberships.create_invitation_page(
            platform_principal(),
            object(),
            tenant_id=fake_service.tenant_id,
            email="page@example.com",
            requested_roles=["tenant_user"],
        )
    assert invite_page_exc.value.status_code == 403

    fake_service.raise_permission_for = {"create_role_grant"}
    with pytest.raises(HTTPException) as grant_page_exc:
        await admin_memberships.create_role_grant_page(
            platform_principal(),
            object(),
            principal_identity_id=fake_service.principal_identity_id,
            scope_type=RoleScopeType.TENANT,
            role_code=RoleCode.TENANT_USER,
            tenant_id=fake_service.tenant_id,
        )
    assert grant_page_exc.value.status_code == 403

    fake_service.raise_permission_for = {"revoke_role_grant"}
    with pytest.raises(HTTPException) as revoke_page_permission_exc:
        await admin_memberships.revoke_role_grant_page(
            fake_service.role_grant_id,
            platform_principal(),
            object(),
            tenant_id=fake_service.tenant_id,
        )
    assert revoke_page_permission_exc.value.status_code == 403

    fake_service.raise_permission_for.clear()
    fake_service.return_none_for = {"revoke_role_grant"}
    with pytest.raises(HTTPException) as revoke_page_missing_exc:
        await admin_memberships.revoke_role_grant_page(
            fake_service.role_grant_id,
            platform_principal(),
            object(),
            tenant_id=fake_service.tenant_id,
        )
    assert revoke_page_missing_exc.value.status_code == 404

    fake_service.raise_permission_for = {"suspend_principal"}
    fake_service.return_none_for.clear()
    with pytest.raises(HTTPException) as principal_page_permission_exc:
        await admin_memberships.principal_status_page(
            fake_service.principal_identity_id,
            "suspend",
            tenant_principal(fake_service.tenant_id),
            object(),
            tenant_id=fake_service.tenant_id,
        )
    assert principal_page_permission_exc.value.status_code == 403

    fake_service.raise_permission_for.clear()
    fake_service.return_none_for = {"suspend_principal"}
    with pytest.raises(HTTPException) as principal_page_missing_exc:
        await admin_memberships.principal_status_page(
            fake_service.principal_identity_id,
            "suspend",
            platform_principal(),
            object(),
        )
    assert principal_page_missing_exc.value.status_code == 404

    fake_service.return_none_for = {"update_membership_status"}
    with pytest.raises(HTTPException) as membership_page_missing_exc:
        await admin_memberships.membership_status_page(
            fake_service.tenant_membership_id,
            TenantMembershipStatus.SUSPENDED,
            platform_principal(),
            object(),
            tenant_id=fake_service.tenant_id,
        )
    assert membership_page_missing_exc.value.status_code == 404
