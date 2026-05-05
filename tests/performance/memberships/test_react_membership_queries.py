from __future__ import annotations

from uuid import UUID

from multi_agent_platform.admin.memberships.react_memberships import (
    ACME_TENANT_ID,
    build_membership_access_history,
    build_membership_audit,
    build_membership_dashboard,
)
from multi_agent_platform.api.schemas.admin_react import ReactAdminScope
from multi_agent_platform.auth.principal import (
    AuthMode,
    AuthProvider,
    PrincipalContext,
)


def test_react_membership_builders_return_bounded_collections() -> None:
    principal = PrincipalContext(
        principal_id="tenant-admin-acme",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        tenant_id=UUID(ACME_TENANT_ID),
        org_id="org-acme",
        role_codes=("tenant_admin",),
        permission_codes=("tenant:admin",),
        trace_id="trace-qa034",
    )
    scope = ReactAdminScope(scope_type="tenant", tenant_id=ACME_TENANT_ID, label="Acme")

    dashboard = build_membership_dashboard(
        scope=scope,
        principal=principal,
        allowed_scope_options=(),
    )
    history = build_membership_access_history(scope=scope, principal=principal)
    audit = build_membership_audit(scope=scope, principal=principal)

    assert len(dashboard.directory) <= 10
    assert len(history.records) <= 10
    assert len(audit.records) <= 10
