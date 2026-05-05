from __future__ import annotations

from uuid import UUID

from multi_agent_platform.admin.memberships.react_memberships import (
    ACME_TENANT_ID,
    GLOBEX_TENANT_ID,
    build_invitation_result,
    build_membership_dashboard,
    build_principal_link_result,
    build_role_grant_result,
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


def _principal(*, platform: bool) -> PrincipalContext:
    return PrincipalContext(
        principal_id="platform-admin" if platform else "tenant-admin-acme",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        tenant_id=None if platform else UUID(ACME_TENANT_ID),
        org_id="org-acme",
        role_codes=("platform_admin",) if platform else ("tenant_admin",),
        permission_codes=("tenant:admin",),
        trace_id="trace-qa034",
    )


def _scope(*, platform: bool) -> ReactAdminScope:
    if platform:
        return ReactAdminScope(scope_type="platform", tenant_id=None, label="Platform")
    return ReactAdminScope(scope_type="tenant", tenant_id=ACME_TENANT_ID, label="Acme")


def test_platform_dashboard_contains_authorized_cross_tenant_rows() -> None:
    dashboard = build_membership_dashboard(
        scope=_scope(platform=True),
        principal=_principal(platform=True),
        allowed_scope_options=(),
    )

    serialized = dashboard.model_dump_json()
    assert "Globex" in serialized
    assert "qa034-secret-value" not in serialized
    assert any(entry.raw_identifier_detail for entry in dashboard.directory)


def test_tenant_dashboard_omits_other_tenant_and_platform_roles() -> None:
    dashboard = build_membership_dashboard(
        scope=_scope(platform=False),
        principal=_principal(platform=False),
        allowed_scope_options=(),
    )

    serialized = dashboard.model_dump_json()
    assert "Globex" not in serialized
    assert "platform_admin" not in serialized
    assert all(entry.raw_identifier_detail is None for entry in dashboard.directory)
    assert dashboard.status_actions[0].authorized_actions
    assert (
        dashboard.status_actions[0].authorized_actions[0].label == "Remove membership"
    )


def test_invitation_idempotency_replay_is_explicit() -> None:
    result = build_invitation_result(
        scope=_scope(platform=False),
        principal=_principal(platform=False),
        request=MembershipInvitationSaveRequest(
            email="invite.replay@example.test",
            requested_roles=("tenant_user",),
            idempotency_key="invite-ui-qa034-replay",
            tenant_id=ACME_TENANT_ID,
        ),
    )

    assert result.status is AdminMutationStatus.REPLAYED
    assert result.invitation is not None
    assert result.invitation.replayed is True


def test_tenant_admin_platform_role_is_denied() -> None:
    result = build_role_grant_result(
        scope=_scope(platform=False),
        principal=_principal(platform=False),
        request=RoleGrantSaveRequest(
            confirmed=True,
            idempotency_key="role-grant-ui-qa034",
            principal_identity_id="principal-qa034-maya",
            role_code="platform_admin",
            scope_type="platform",
            tenant_id=None,
        ),
    )

    assert result.status is AdminMutationStatus.VALIDATION_ERROR
    assert result.field_errors[0].code == "scope_denied"


def test_tenant_admin_principal_link_is_denied() -> None:
    result = build_principal_link_result(
        scope=_scope(platform=False),
        principal=_principal(platform=False),
        request=PrincipalLinkRequest(
            display_name="Linked Reviewer",
            email="linked@example.test",
            external_subject="auth0-safe-subject-7788",
            idempotency_key="principal-link-ui-qa034",
        ),
    )

    assert result.status is AdminMutationStatus.VALIDATION_ERROR
    assert result.audit_reference_id == "audit-membership-qa034-principal-link-denied"


def test_cross_tenant_invite_is_denied_without_confirming_resource() -> None:
    result = build_invitation_result(
        scope=_scope(platform=False),
        principal=_principal(platform=False),
        request=MembershipInvitationSaveRequest(
            email="invite@example.test",
            requested_roles=("tenant_user",),
            idempotency_key="invite-ui-qa034-create",
            tenant_id=GLOBEX_TENANT_ID,
        ),
    )

    assert result.status is AdminMutationStatus.VALIDATION_ERROR
    assert result.audit_reference_id == "audit-membership-qa034-cross-tenant-denied"
