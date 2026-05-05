from __future__ import annotations

from time import perf_counter
from uuid import UUID

from multi_agent_platform.admin.usage.react_usage import (
    ACME_TENANT_ID,
    build_usage_dashboard,
    build_usage_events,
)
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminScope,
    ReactAdminScopeType,
)
from multi_agent_platform.api.schemas.admin_usage_react import (
    UsageReactDashboardQuery,
    UsageReactEventQuery,
    UsageReactGroupBy,
)
from multi_agent_platform.auth.principal import AuthProvider, PrincipalContext


def test_usage_dashboard_projection_is_bounded_and_fast() -> None:
    principal = PrincipalContext(
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        principal_id="platform-admin",
        role_codes=("platform_admin",),
    )
    scope = ReactAdminScope(
        scope_type=ReactAdminScopeType.PLATFORM,
        tenant_id=None,
        label="Platform",
    )

    started = perf_counter()
    dashboard = build_usage_dashboard(
        scope=scope,
        principal=principal,
        allowed_scope_options=(),
        query=UsageReactDashboardQuery(group_by=UsageReactGroupBy.PROVIDER),
    )
    elapsed_ms = (perf_counter() - started) * 1000

    assert elapsed_ms < 300
    assert len(dashboard.summary_cards) <= 8
    assert len(dashboard.trend) <= 31
    assert len(dashboard.rollup.rows) <= 25
    assert len(dashboard.drilldown.rows) <= 100


def test_tenant_event_drilldown_projection_is_bounded() -> None:
    principal = PrincipalContext(
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        principal_id="tenant-admin-acme",
        role_codes=("tenant_admin",),
        tenant_id=UUID(ACME_TENANT_ID),
    )
    scope = ReactAdminScope(
        scope_type=ReactAdminScopeType.TENANT,
        tenant_id=UUID(ACME_TENANT_ID),
        label="Acme",
    )

    drilldown = build_usage_events(
        scope=scope,
        principal=principal,
        query=UsageReactEventQuery(group_by=UsageReactGroupBy.GOVERNED_TOOL),
    )

    assert len(drilldown.rows) <= 100
    assert drilldown.total_rows >= len(drilldown.rows)
