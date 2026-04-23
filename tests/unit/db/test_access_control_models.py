from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.db.models.access_control import (
    AuthProviderType,
    PrincipalIdentity,
    RoleCode,
    RoleGrant,
    RoleScopeType,
    SupportOverrideRequest,
)
from multi_agent_platform.db.repositories.access_control import AccessControlRepository


async def test_access_control_repository_round_trip_role_grant(session) -> None:
    repository = AccessControlRepository(session)
    identity = await repository.upsert_principal(
        PrincipalIdentity(
            auth_provider=AuthProviderType.LOCAL_PRINCIPAL,
            external_subject="tenant-admin-acme",
        )
    )

    grant = await repository.upsert_role_grant(
        RoleGrant(
            principal_identity_id=identity.principal_identity_id,
            scope_type=RoleScopeType.TENANT,
            tenant_id=uuid4(),
            role_code=RoleCode.TENANT_ADMIN,
        )
    )

    grants = await repository.active_role_grants_for_principal(
        identity.principal_identity_id
    )
    assert grants[0].role_grant_id == grant.role_grant_id

    revoked = await repository.revoke_role_grant(grant.role_grant_id)
    assert revoked is not None
    assert revoked.status == "revoked"


async def test_access_control_repository_support_override_lifecycle(session) -> None:
    repository = AccessControlRepository(session)
    requester = await repository.upsert_principal(
        PrincipalIdentity(
            auth_provider=AuthProviderType.LOCAL_PRINCIPAL,
            external_subject="platform-admin-a",
        )
    )
    override = await repository.create_support_override(
        SupportOverrideRequest(
            requester_principal_id=requester.principal_identity_id,
            target_tenant_id=uuid4(),
            justification="Investigate issue",
            request_trace_id="trace-1",
            idempotency_key="override-1",
        )
    )
    approved = await repository.approve_support_override(
        override.support_override_request_id,
        approver_principal_id=uuid4(),
        expires_at=None,
    )

    active = await repository.find_active_support_override(
        requester_principal_id=requester.principal_identity_id,
        tenant_id=override.target_tenant_id,
    )
    assert approved is not None
    assert active is not None
