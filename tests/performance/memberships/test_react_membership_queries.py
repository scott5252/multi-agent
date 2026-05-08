from __future__ import annotations

from tests.fixtures.memberships import ACME_TENANT_ID, seed_membership_live_data

from multi_agent_platform.admin.memberships.react_memberships import (
    build_membership_access_history,
    build_membership_audit,
    build_membership_dashboard,
)
from multi_agent_platform.admin.memberships.service import (
    MembershipAdministrationService,
)
from multi_agent_platform.api.schemas.admin_react import ReactAdminScope
from multi_agent_platform.auth.principal import (
    AuthMode,
    AuthProvider,
    PrincipalContext,
)
from multi_agent_platform.db.repositories.memberships import MembershipRepository


async def test_react_membership_builders_return_bounded_collections(session) -> None:
    await seed_membership_live_data(session)
    repository = MembershipRepository(session)
    service = MembershipAdministrationService(repository)
    principal = PrincipalContext(
        principal_id="tenant-admin-acme",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        tenant_id=ACME_TENANT_ID,
        org_id="org-acme",
        role_codes=("tenant_admin",),
        permission_codes=("tenant:admin",),
        trace_id="trace-qa054",
    )
    scope = ReactAdminScope(scope_type="tenant", tenant_id=ACME_TENANT_ID, label="Acme")

    dashboard = await build_membership_dashboard(
        repository=repository,
        service=service,
        scope=scope,
        principal=principal,
        allowed_scope_options=(),
    )
    history = await build_membership_access_history(
        service=service,
        scope=scope,
        principal=principal,
    )
    audit = await build_membership_audit(
        service=service,
        scope=scope,
        principal=principal,
    )

    assert len(dashboard.directory) <= 50
    assert len(history.records) <= 50
    assert len(audit.records) <= 50
