from __future__ import annotations

from uuid import UUID

from tests.fixtures.memberships import (
    ACME_TENANT_ID,
    GLOBEX_TENANT_ID,
    seed_membership_live_data,
)

from multi_agent_platform.admin.memberships.react_memberships import (
    build_invitation_result,
    build_membership_dashboard,
    build_principal_link_result,
    build_role_grant_result,
)
from multi_agent_platform.admin.memberships.service import (
    MembershipAdministrationService,
)
from multi_agent_platform.api.schemas.admin_membership_react import (
    MembershipInvitationSaveRequest,
    PrincipalLinkRequest,
    RoleGrantSaveRequest,
)
from multi_agent_platform.api.schemas.admin_patterns import AdminMutationStatus
from multi_agent_platform.api.schemas.admin_react import ReactAdminScope
from multi_agent_platform.auth.principal import (
    AuthMode,
    AuthProvider,
    PrincipalContext,
)
from multi_agent_platform.db.repositories.memberships import MembershipRepository


def _principal(*, platform: bool) -> PrincipalContext:
    return PrincipalContext(
        principal_id="platform-admin" if platform else "tenant-admin-acme",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        tenant_id=None if platform else ACME_TENANT_ID,
        org_id="org-acme",
        role_codes=("platform_admin",) if platform else ("tenant_admin",),
        permission_codes=("tenant:admin",),
        trace_id="trace-qa054",
    )


def _scope(
    *,
    platform: bool,
    tenant_id: UUID | None = ACME_TENANT_ID,
) -> ReactAdminScope:
    if platform and tenant_id is None:
        return ReactAdminScope(scope_type="platform", tenant_id=None, label="Platform")
    return ReactAdminScope(
        scope_type="tenant",
        tenant_id=tenant_id,
        label="Acme" if tenant_id == ACME_TENANT_ID else "Globex",
    )


def _service(session):
    repository = MembershipRepository(session)
    return repository, MembershipAdministrationService(repository)


async def test_empty_tenant_dashboard_returns_truthful_empty_state(session) -> None:
    repository, service = _service(session)
    dashboard = await build_membership_dashboard(
        repository=repository,
        service=service,
        scope=_scope(platform=False),
        principal=_principal(platform=False),
        allowed_scope_options=(),
    )

    serialized = dashboard.model_dump_json()
    assert dashboard.directory == ()
    assert dashboard.invitations == ()
    assert dashboard.empty_state is not None
    assert "qa034" not in serialized.lower()


async def test_tenant_dashboard_uses_seeded_live_rows(session) -> None:
    await seed_membership_live_data(session)
    repository, service = _service(session)
    dashboard = await build_membership_dashboard(
        repository=repository,
        service=service,
        scope=_scope(platform=False),
        principal=_principal(platform=False),
        allowed_scope_options=(),
    )

    serialized = dashboard.model_dump_json()
    assert "Maya Chen" in serialized
    assert "ma***n@e***.test" in serialized
    assert "maya.chen@example.test" not in serialized
    assert "Globex" not in serialized
    assert dashboard.empty_state is None
    assert dashboard.status_actions[0].authorized_actions


async def test_platform_dashboard_contains_authorized_support_override(session) -> None:
    await seed_membership_live_data(session)
    repository, service = _service(session)
    dashboard = await build_membership_dashboard(
        repository=repository,
        service=service,
        scope=_scope(platform=True, tenant_id=None),
        principal=_principal(platform=True),
        allowed_scope_options=(),
    )

    serialized = dashboard.model_dump_json()
    assert "Globex" not in serialized
    assert "Support override evidence is persisted" in serialized
    assert dashboard.support_overrides
    assert any(entry.raw_identifier_detail for entry in dashboard.directory)


async def test_invitation_idempotency_replay_is_persisted(session) -> None:
    await seed_membership_live_data(session)
    repository, service = _service(session)
    result = await build_invitation_result(
        service=service,
        repository=repository,
        scope=_scope(platform=False),
        principal=_principal(platform=False),
        request=MembershipInvitationSaveRequest(
            email="invited.user@example.test",
            requested_roles=("tenant_user",),
            idempotency_key="qa054-live-invite",
            tenant_id=str(ACME_TENANT_ID),
        ),
    )

    assert result.status is AdminMutationStatus.REPLAYED
    assert result.invitation is not None
    assert result.invitation.replayed is True
    assert "invited.user@example.test" not in result.model_dump_json()


async def test_tenant_admin_platform_role_is_denied(session) -> None:
    seed = await seed_membership_live_data(session)
    repository, service = _service(session)
    result = await build_role_grant_result(
        service=service,
        repository=repository,
        scope=_scope(platform=False),
        principal=_principal(platform=False),
        request=RoleGrantSaveRequest(
            confirmed=True,
            idempotency_key="role-grant-ui-qa054",
            principal_identity_id=str(seed.tenant_principal_id),
            role_code="platform_admin",
            scope_type="platform",
            tenant_id=None,
        ),
    )

    assert result.status is AdminMutationStatus.VALIDATION_ERROR
    assert result.field_errors[0].code == "scope_denied"


async def test_tenant_admin_principal_link_is_denied(session) -> None:
    repository, service = _service(session)
    result = await build_principal_link_result(
        service=service,
        repository=repository,
        scope=_scope(platform=False),
        principal=_principal(platform=False),
        request=PrincipalLinkRequest(
            display_name="Linked Reviewer",
            email="linked@example.test",
            external_subject="auth0|safe-subject-7788",
            idempotency_key="principal-link-ui-qa054",
        ),
    )

    assert result.status is AdminMutationStatus.VALIDATION_ERROR
    assert result.audit_reference_id == "membership-live-denied-principal-link"


async def test_cross_tenant_invite_is_denied_without_confirming_resource(
    session,
) -> None:
    repository, service = _service(session)
    result = await build_invitation_result(
        service=service,
        repository=repository,
        scope=_scope(platform=False),
        principal=_principal(platform=False),
        request=MembershipInvitationSaveRequest(
            email="invite@example.test",
            requested_roles=("tenant_user",),
            idempotency_key="invite-ui-qa054-create",
            tenant_id=str(GLOBEX_TENANT_ID),
        ),
    )

    assert result.status is AdminMutationStatus.VALIDATION_ERROR
    assert result.audit_reference_id == "membership-live-denied-invitation"
