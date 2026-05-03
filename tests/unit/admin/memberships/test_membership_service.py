from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.admin.memberships.models import (
    MembershipAccessScope,
    MembershipConflictError,
    MembershipPermissionError,
    MembershipScopeType,
    TenantMembershipStatus,
)
from multi_agent_platform.admin.memberships.service import (
    MembershipAdministrationService,
)
from multi_agent_platform.db.models.access_control import (
    AuthProviderType,
    RoleCode,
    RoleScopeType,
)
from multi_agent_platform.db.repositories.memberships import MembershipRepository


def platform_scope() -> MembershipAccessScope:
    return MembershipAccessScope(
        scope_type=MembershipScopeType.PLATFORM,
        principal_id="platform-admin",
        platform_admin=True,
        trace_id="trace-platform",
    )


def tenant_scope(tenant_id) -> MembershipAccessScope:
    return MembershipAccessScope(
        scope_type=MembershipScopeType.TENANT,
        principal_id="tenant-admin-acme",
        tenant_id=tenant_id,
        platform_admin=False,
        trace_id="trace-tenant",
    )


async def test_service_creates_idempotent_invitation_and_audit(session) -> None:
    service = MembershipAdministrationService(MembershipRepository(session))
    tenant_id = uuid4()

    first = await service.create_invitation(
        access_scope=platform_scope(),
        tenant_id=tenant_id,
        email="Reviewer@Example.com",
        requested_roles=(RoleCode.TENANT_USER,),
        idempotency_key="invite-1",
    )
    second = await service.create_invitation(
        access_scope=platform_scope(),
        tenant_id=tenant_id,
        email="reviewer@example.com",
        requested_roles=(RoleCode.TENANT_USER,),
        idempotency_key="invite-1",
    )
    snapshot = await service.snapshot(platform_scope())

    assert first.replayed is False
    assert second.replayed is True
    assert second.invitation.user_invitation_id == first.invitation.user_invitation_id
    assert len(snapshot.audit_records) == 2
    assert "reviewer@example.com" not in str(
        snapshot.audit_records[0].redacted_metadata
    )


async def test_tenant_admin_cannot_assign_platform_role(session) -> None:
    service = MembershipAdministrationService(MembershipRepository(session))
    tenant_id = uuid4()
    principal = await service.repository.upsert_principal(
        auth_provider=AuthProviderType.AUTH0,
        external_subject="auth0|member",
    )

    with pytest.raises(MembershipPermissionError):
        await service.create_role_grant(
            access_scope=tenant_scope(tenant_id),
            principal_identity_id=principal.principal_identity_id,
            scope_type=RoleScopeType.PLATFORM,
            role_code=RoleCode.PLATFORM_ADMIN,
        )


async def test_tenant_admin_can_assign_and_revoke_tenant_role(session) -> None:
    service = MembershipAdministrationService(MembershipRepository(session))
    tenant_id = uuid4()
    principal = await service.repository.upsert_principal(
        auth_provider=AuthProviderType.AUTH0,
        external_subject="auth0|tenant-role-member",
    )

    grant = await service.create_role_grant(
        access_scope=tenant_scope(tenant_id),
        principal_identity_id=principal.principal_identity_id,
        scope_type=RoleScopeType.TENANT,
        tenant_id=tenant_id,
        role_code=RoleCode.TENANT_ADMIN,
    )
    replay = await service.create_role_grant(
        access_scope=tenant_scope(tenant_id),
        principal_identity_id=principal.principal_identity_id,
        scope_type=RoleScopeType.TENANT,
        tenant_id=tenant_id,
        role_code=RoleCode.TENANT_ADMIN,
    )
    revoked = await service.revoke_role_grant(
        access_scope=tenant_scope(tenant_id),
        role_grant_id=grant.role_grant_id,
    )

    assert replay.role_grant_id == grant.role_grant_id
    assert revoked is not None
    assert revoked.status.value == "revoked"


async def test_service_denies_invalid_role_assignment_edges(session) -> None:
    service = MembershipAdministrationService(MembershipRepository(session))
    tenant_id = uuid4()
    principal = await service.repository.upsert_principal(
        auth_provider=AuthProviderType.AUTH0,
        external_subject="auth0|guardrail-member",
    )

    with pytest.raises(MembershipPermissionError, match="tenant role grant requires"):
        await service.create_role_grant(
            access_scope=platform_scope(),
            principal_identity_id=principal.principal_identity_id,
            scope_type=RoleScopeType.TENANT,
            role_code=RoleCode.TENANT_USER,
        )

    with pytest.raises(MembershipPermissionError, match="platform grants require"):
        await service.create_role_grant(
            access_scope=platform_scope(),
            principal_identity_id=principal.principal_identity_id,
            scope_type=RoleScopeType.PLATFORM,
            role_code=RoleCode.TENANT_USER,
        )

    with pytest.raises(MembershipPermissionError, match="tenant scope"):
        await service.create_role_grant(
            access_scope=tenant_scope(tenant_id),
            principal_identity_id=principal.principal_identity_id,
            scope_type=RoleScopeType.TENANT,
            tenant_id=uuid4(),
            role_code=RoleCode.TENANT_USER,
        )

    with pytest.raises(LookupError):
        await service.create_role_grant(
            access_scope=platform_scope(),
            principal_identity_id=uuid4(),
            scope_type=RoleScopeType.TENANT,
            tenant_id=tenant_id,
            role_code=RoleCode.TENANT_USER,
        )


async def test_service_link_auth0_principal_conflict_and_tenant_denial(
    session,
) -> None:
    service = MembershipAdministrationService(MembershipRepository(session))
    tenant_id = uuid4()
    existing = await service.link_auth0_principal(
        access_scope=platform_scope(),
        auth0_subject="auth0|conflict",
        email="conflict@example.com",
    )

    updated = await service.link_auth0_principal(
        access_scope=platform_scope(),
        principal_identity_id=existing.principal_identity_id,
        auth0_subject="auth0|conflict",
        display_name="Conflict Updated",
    )

    with pytest.raises(MembershipConflictError):
        await service.link_auth0_principal(
            access_scope=platform_scope(),
            auth0_subject="auth0|conflict",
            email="other@example.com",
        )

    with pytest.raises(MembershipPermissionError):
        await service.link_auth0_principal(
            access_scope=tenant_scope(tenant_id),
            auth0_subject="auth0|tenant-denied",
        )

    assert updated.display_name == "Conflict Updated"


async def test_service_principal_status_edges_and_denials(session) -> None:
    service = MembershipAdministrationService(MembershipRepository(session))
    tenant_id = uuid4()
    principal = await service.repository.upsert_principal(
        auth_provider=AuthProviderType.AUTH0,
        external_subject="auth0|status-edges",
    )

    with pytest.raises(MembershipPermissionError):
        await service.suspend_principal(
            access_scope=tenant_scope(tenant_id),
            principal_identity_id=principal.principal_identity_id,
        )

    assert (
        await service.suspend_principal(
            access_scope=platform_scope(),
            principal_identity_id=uuid4(),
        )
        is None
    )
    assert (
        await service.reactivate_principal(
            access_scope=platform_scope(),
            principal_identity_id=uuid4(),
        )
        is None
    )

    suspended = await service.suspend_principal(
        access_scope=platform_scope(),
        principal_identity_id=principal.principal_identity_id,
    )
    reactivated = await service.reactivate_principal(
        access_scope=platform_scope(),
        principal_identity_id=principal.principal_identity_id,
    )
    denial = await service.record_denial(
        access_scope=tenant_scope(tenant_id),
        reason="cross tenant",
        metadata={"raw_email": "secret@example.com"},
    )

    assert suspended is not None
    assert suspended.status.value == "active"
    assert reactivated is not None
    assert reactivated.status.value == "active"
    assert denial.decision == "deny"
    assert denial.redacted_metadata["raw_email"] == "[redacted]"


async def test_service_updates_membership_status(session) -> None:
    service = MembershipAdministrationService(MembershipRepository(session))
    tenant_id = uuid4()
    principal = await service.repository.upsert_principal(
        auth_provider=AuthProviderType.AUTH0,
        external_subject="auth0|member-status",
    )
    await service.create_role_grant(
        access_scope=platform_scope(),
        principal_identity_id=principal.principal_identity_id,
        scope_type=RoleScopeType.TENANT,
        role_code=RoleCode.TENANT_USER,
        tenant_id=tenant_id,
    )
    snapshot = await service.snapshot(platform_scope())
    membership = snapshot.memberships[0]

    suspended = await service.update_membership_status(
        access_scope=MembershipAccessScope(
            scope_type=MembershipScopeType.TENANT,
            principal_id="platform-admin",
            tenant_id=tenant_id,
            platform_admin=True,
        ),
        tenant_membership_id=membership.tenant_membership_id,
        status=TenantMembershipStatus.SUSPENDED,
    )

    assert suspended is not None
    assert suspended.status == "suspended"

    restored = await service.update_membership_status(
        access_scope=MembershipAccessScope(
            scope_type=MembershipScopeType.TENANT,
            principal_id="platform-admin",
            tenant_id=tenant_id,
            platform_admin=True,
        ),
        tenant_membership_id=membership.tenant_membership_id,
        status=TenantMembershipStatus.ACTIVE,
    )
    removed = await service.update_membership_status(
        access_scope=MembershipAccessScope(
            scope_type=MembershipScopeType.TENANT,
            principal_id="platform-admin",
            tenant_id=tenant_id,
            platform_admin=True,
        ),
        tenant_membership_id=membership.tenant_membership_id,
        status=TenantMembershipStatus.REMOVED,
    )
    missing = await service.update_membership_status(
        access_scope=MembershipAccessScope(
            scope_type=MembershipScopeType.TENANT,
            principal_id="platform-admin",
            tenant_id=uuid4(),
            platform_admin=True,
        ),
        tenant_membership_id=membership.tenant_membership_id,
        status=TenantMembershipStatus.SUSPENDED,
    )

    assert restored is not None
    assert restored.status == "removed"
    assert removed is not None
    assert removed.status == "removed"
    assert missing is None
