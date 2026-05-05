from __future__ import annotations

import time

from multi_agent_platform.admin.governance import build_governance_dashboard
from multi_agent_platform.api.schemas.admin_react import ReactAdminScope
from multi_agent_platform.auth.principal import (
    AuthMode,
    AuthProvider,
    PrincipalContext,
)


def test_governance_dashboard_build_stays_bounded() -> None:
    principal = PrincipalContext(
        principal_id="tenant-admin",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        role_codes=("tenant_user", "tenant_admin"),
        permission_codes=("tenant:read", "tenant:admin"),
        trace_id="trace-governance-performance",
    )
    scope = ReactAdminScope(
        scope_type="tenant",
        tenant_id="11111111-1111-1111-1111-111111111111",
        label="Acme",
    )

    started = time.perf_counter()
    dashboard = build_governance_dashboard(scope=scope, principal=principal)
    elapsed = time.perf_counter() - started

    assert dashboard.providers
    assert dashboard.policy_history
    assert dashboard.run_provenance
    assert elapsed < 0.5
