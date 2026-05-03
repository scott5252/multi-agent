from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from multi_agent_platform.admin.memberships.models import (
    MembershipAuditAction,
    MembershipAuditDecision,
    MembershipSource,
    TenantMembershipStatus,
)
from multi_agent_platform.db.models.access_control import (
    AccessDecision,
    AccessDecisionRecord,
    AccessReasonCode,
    AuthProviderType,
    RoleCode,
    RoleGrant,
    RoleScopeType,
)
from multi_agent_platform.db.repositories.memberships import MembershipRepository


async def test_membership_repository_replays_active_invitation(session) -> None:
    repository = MembershipRepository(session)
    tenant_id = uuid4()
    first, first_replayed = await repository.create_or_replay_invitation(
        tenant_id=tenant_id,
        email="Reviewer@Example.com",
        requested_roles=["tenant_user"],
        idempotency_key="invite-1",
        invited_by_principal_id="platform-admin",
        expires_at=datetime.now(UTC) + timedelta(days=7),
        trace_id="trace-1",
    )
    second, second_replayed = await repository.create_or_replay_invitation(
        tenant_id=tenant_id,
        email=" reviewer@example.COM ",
        requested_roles=["tenant_user"],
        idempotency_key="invite-1",
        invited_by_principal_id="platform-admin",
        expires_at=datetime.now(UTC) + timedelta(days=7),
        trace_id="trace-2",
    )

    assert first_replayed is False
    assert second_replayed is True
    assert second.user_invitation_id == first.user_invitation_id


async def test_membership_repository_creates_and_revokes_grant(session) -> None:
    repository = MembershipRepository(session)
    principal = await repository.upsert_principal(
        auth_provider=AuthProviderType.AUTH0,
        external_subject="auth0|member",
        display_name="Member",
        email="member@example.com",
    )
    grant, replayed = await repository.create_role_grant(
        principal_identity_id=principal.principal_identity_id,
        scope_type=RoleScopeType.TENANT,
        tenant_id=uuid4(),
        role_code=RoleCode.TENANT_ADMIN,
        granted_by_principal_id=None,
    )

    revoked = await repository.revoke_role_grant(role_grant_id=grant.role_grant_id)

    assert replayed is False
    assert revoked is not None
    assert revoked.status.value == "revoked"


async def test_membership_repository_lists_principals_by_tenant_grant(session) -> None:
    repository = MembershipRepository(session)
    tenant_id = uuid4()
    principal = await repository.upsert_principal(
        auth_provider=AuthProviderType.AUTH0,
        external_subject="auth0|tenant-member",
    )
    await repository.create_role_grant(
        principal_identity_id=principal.principal_identity_id,
        scope_type=RoleScopeType.TENANT,
        tenant_id=tenant_id,
        role_code=RoleCode.TENANT_USER,
        granted_by_principal_id=None,
    )

    principals = await repository.list_principals(tenant_id=tenant_id)

    assert [item.principal_identity_id for item in principals] == [
        principal.principal_identity_id
    ]


async def test_membership_repository_updates_existing_principal_and_filters(
    session,
) -> None:
    repository = MembershipRepository(session)
    tenant_id = uuid4()
    principal = await repository.upsert_principal(
        auth_provider=AuthProviderType.AUTH0,
        external_subject="auth0|query-member",
        display_name="Query Member",
        email="query@example.com",
    )
    updated = await repository.upsert_principal(
        auth_provider=AuthProviderType.AUTH0,
        principal_identity_id=principal.principal_identity_id,
        external_subject="auth0|query-member",
        display_name=None,
        email="Query.Updated@Example.com",
    )
    await repository.get_or_create_membership(
        tenant_id=tenant_id,
        principal_identity_id=principal.principal_identity_id,
        actor_principal_id="platform-admin",
        source=MembershipSource.ADMIN_ASSIGNMENT,
    )

    queried = await repository.list_principals(tenant_id=tenant_id, query="updated")

    assert updated.principal_identity_id == principal.principal_identity_id
    assert updated.display_name == "Query Member"
    assert updated.email == "query.updated@example.com"
    assert [item.principal_identity_id for item in queried] == [
        principal.principal_identity_id
    ]


async def test_membership_repository_invitation_filter_branches(session) -> None:
    repository = MembershipRepository(session)
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    first, _ = await repository.create_or_replay_invitation(
        tenant_id=tenant_id,
        email="filter@example.com",
        requested_roles=["tenant_user"],
        idempotency_key=None,
        invited_by_principal_id="platform-admin",
        expires_at=None,
        trace_id="trace-filter-1",
    )
    second, replayed = await repository.create_or_replay_invitation(
        tenant_id=tenant_id,
        email="filter@example.com",
        requested_roles=["tenant_admin"],
        idempotency_key=None,
        invited_by_principal_id="platform-admin",
        expires_at=None,
        trace_id="trace-filter-2",
    )
    await repository.create_or_replay_invitation(
        tenant_id=other_tenant_id,
        email="other@example.com",
        requested_roles=["tenant_user"],
        idempotency_key="other",
        invited_by_principal_id="platform-admin",
        expires_at=None,
        trace_id="trace-filter-3",
    )

    platform_filtered = await repository.list_invitations(
        tenant_id=tenant_id,
        platform_scope=True,
    )
    tenant_filtered = await repository.list_invitations(
        tenant_id=tenant_id,
        platform_scope=False,
    )

    assert replayed is False
    assert first.user_invitation_id != second.user_invitation_id
    assert {item.tenant_id for item in platform_filtered} == {tenant_id}
    assert {item.tenant_id for item in tenant_filtered} == {tenant_id}


async def test_membership_repository_membership_lifecycle_branches(session) -> None:
    repository = MembershipRepository(session)
    tenant_id = uuid4()
    principal = await repository.upsert_principal(
        auth_provider=AuthProviderType.AUTH0,
        external_subject="auth0|membership-lifecycle",
    )
    created = await repository.get_or_create_membership(
        tenant_id=tenant_id,
        principal_identity_id=principal.principal_identity_id,
        actor_principal_id="platform-admin",
        source=MembershipSource.INVITATION,
    )
    first_revision = created.revision_token
    suspended = await repository.update_membership_status(
        tenant_membership_id=created.tenant_membership_id,
        tenant_id=tenant_id,
        status=TenantMembershipStatus.SUSPENDED,
        actor_principal_id="tenant-admin",
    )
    removed = await repository.update_membership_status(
        tenant_membership_id=created.tenant_membership_id,
        tenant_id=tenant_id,
        status=TenantMembershipStatus.REMOVED,
        actor_principal_id="tenant-admin",
    )
    restored = await repository.get_or_create_membership(
        tenant_id=tenant_id,
        principal_identity_id=principal.principal_identity_id,
        actor_principal_id="tenant-admin",
        source=MembershipSource.ADMIN_ASSIGNMENT,
    )
    missing = await repository.update_membership_status(
        tenant_membership_id=created.tenant_membership_id,
        tenant_id=uuid4(),
        status=TenantMembershipStatus.SUSPENDED,
        actor_principal_id="tenant-admin",
    )

    assert suspended is not None
    assert suspended.suspended_at is None
    assert removed is not None
    assert removed.removed_at is None
    assert restored.status == "active"
    assert restored.removed_at is None
    assert restored.revision_token != first_revision
    assert missing is None


async def test_membership_repository_role_grant_and_history_filters(session) -> None:
    repository = MembershipRepository(session)
    tenant_id = uuid4()
    principal = await repository.upsert_principal(
        auth_provider=AuthProviderType.AUTH0,
        external_subject="auth0|history-member",
    )
    grant, _ = await repository.create_role_grant(
        principal_identity_id=principal.principal_identity_id,
        scope_type=RoleScopeType.TENANT,
        tenant_id=tenant_id,
        role_code=RoleCode.TENANT_USER,
        granted_by_principal_id=None,
    )
    replayed_grant, replayed = await repository.create_role_grant(
        principal_identity_id=principal.principal_identity_id,
        scope_type=RoleScopeType.TENANT,
        tenant_id=tenant_id,
        role_code=RoleCode.TENANT_USER,
        granted_by_principal_id=None,
    )
    platform_grant = RoleGrant(
        principal_identity_id=principal.principal_identity_id,
        scope_type=RoleScopeType.PLATFORM,
        tenant_id=None,
        role_code=RoleCode.PLATFORM_ADMIN,
    )
    session.add(platform_grant)
    session.add(
        AccessDecisionRecord(
            principal_identity_id=principal.principal_identity_id,
            scope_type=RoleScopeType.TENANT,
            tenant_id=tenant_id,
            surface_key="GET:/admin/memberships",
            requested_action="render_membership_administration_ui",
            decision=AccessDecision.ALLOW,
            reason_code=AccessReasonCode.UNAUTHENTICATED,
            auth_mode="local_principal",
            trace_id="trace-history",
            required_roles=[],
            required_permissions=["membership-admin:read"],
        )
    )
    await repository.add_audit_record(
        tenant_id=tenant_id,
        actor_principal_id="tenant-admin",
        action=MembershipAuditAction.ROLE_GRANT_CREATED,
        decision=MembershipAuditDecision.ALLOW,
        summary="",
        trace_id="trace-audit",
        target_principal_identity_id=principal.principal_identity_id,
        redacted_metadata={"credential": "secret", "role_code": "tenant_user"},
    )
    await session.flush()

    tenant_grants = await repository.list_role_grants(
        tenant_id=tenant_id,
        platform_scope=False,
    )
    platform_tenant_grants = await repository.list_role_grants(
        tenant_id=tenant_id,
        platform_scope=True,
    )
    access_history = await repository.list_access_history(
        tenant_id=tenant_id,
        platform_scope=True,
        principal_identity_id=principal.principal_identity_id,
    )
    tenant_history = await repository.list_access_history(
        tenant_id=tenant_id,
        platform_scope=False,
    )
    audit_records = await repository.list_audit_records(
        tenant_id=tenant_id,
        platform_scope=True,
    )
    tenant_audit_records = await repository.list_audit_records(
        tenant_id=tenant_id,
        platform_scope=False,
    )

    assert replayed is True
    assert replayed_grant.role_grant_id == grant.role_grant_id
    assert [item.role_grant_id for item in tenant_grants] == [grant.role_grant_id]
    assert [item.role_grant_id for item in platform_tenant_grants] == [
        grant.role_grant_id
    ]
    assert len(access_history) == 1
    assert len(tenant_history) == 1
    assert audit_records[0].summary == "Membership administration event recorded."
    assert audit_records[0].redacted_metadata["credential"] == "[redacted]"
    assert len(tenant_audit_records) == 1
