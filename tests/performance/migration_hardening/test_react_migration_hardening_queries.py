from __future__ import annotations

import time
from uuid import UUID

from multi_agent_platform.admin.migration_hardening import (
    build_migration_dashboard,
    build_migration_route_groups,
)
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminScope,
    ReactAdminScopeType,
)
from multi_agent_platform.auth.principal import (
    AuthMode,
    AuthProvider,
    PrincipalContext,
)

ACME_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")


def test_migration_dashboard_projection_is_bounded_and_fast() -> None:
    started = time.perf_counter()

    dashboard = build_migration_dashboard(
        scope=ReactAdminScope(
            scope_type=ReactAdminScopeType.PLATFORM,
            tenant_id=None,
            label="Platform",
        ),
        principal=_principal("platform-admin", roles=("platform_admin",)),
    )

    elapsed_ms = (time.perf_counter() - started) * 1000
    assert elapsed_ms < 50
    assert len(dashboard.route_groups) <= 20
    assert sum(len(group.entries) for group in dashboard.route_groups) <= 40


def test_tenant_route_group_projection_does_not_expand_hidden_rows() -> None:
    groups = build_migration_route_groups(
        scope=ReactAdminScope(
            scope_type=ReactAdminScopeType.TENANT,
            tenant_id=ACME_TENANT_ID,
            label="Acme",
        ),
        principal=_principal(
            "tenant-user-acme",
            roles=("tenant_user",),
            tenant_id=ACME_TENANT_ID,
        ),
    )

    assert len(groups) <= 20
    assert sum(len(group.entries) for group in groups) <= 8


def _principal(
    principal_id: str,
    *,
    roles: tuple[str, ...],
    tenant_id: UUID | None = None,
) -> PrincipalContext:
    return PrincipalContext(
        principal_id=principal_id,
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        tenant_id=tenant_id,
        org_id="org-acme" if tenant_id else None,
        role_codes=roles,
        permission_codes=("tenant:read", "tenant:admin"),
        trace_id=f"trace-{principal_id}",
    )
