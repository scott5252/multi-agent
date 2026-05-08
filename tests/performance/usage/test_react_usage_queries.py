from __future__ import annotations

from time import perf_counter

from tests.fixtures.usage_react import seed_usage_react_live_data

from multi_agent_platform.admin.usage.react_usage import (
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
from multi_agent_platform.db.repositories.usage import UsageRepository
from multi_agent_platform.usage.service import UsageAnalyticsService


async def test_usage_dashboard_projection_is_bounded_and_fast(
    session,
    seeded_tenant,
) -> None:
    await seed_usage_react_live_data(session, tenant_id=seeded_tenant.tenant_id)
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
    repository = UsageRepository(session)

    started = perf_counter()
    dashboard = await build_usage_dashboard(
        scope=scope,
        principal=principal,
        allowed_scope_options=(),
        repository=repository,
        service=UsageAnalyticsService(repository),
        query=UsageReactDashboardQuery(group_by=UsageReactGroupBy.PROVIDER),
    )
    elapsed_ms = (perf_counter() - started) * 1000

    assert elapsed_ms < 300
    assert len(dashboard.summary_cards) <= 8
    assert len(dashboard.trend) <= 31
    assert len(dashboard.rollup.rows) <= 25
    assert len(dashboard.drilldown.rows) <= 100


async def test_tenant_event_drilldown_projection_is_bounded(
    session,
    seeded_tenant,
) -> None:
    await seed_usage_react_live_data(session, tenant_id=seeded_tenant.tenant_id)
    principal = PrincipalContext(
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        principal_id="tenant-admin-acme",
        role_codes=("tenant_admin",),
        tenant_id=seeded_tenant.tenant_id,
    )
    scope = ReactAdminScope(
        scope_type=ReactAdminScopeType.TENANT,
        tenant_id=seeded_tenant.tenant_id,
        label="Acme",
    )

    drilldown = await build_usage_events(
        scope=scope,
        principal=principal,
        repository=UsageRepository(session),
        query=UsageReactEventQuery(group_by=UsageReactGroupBy.GOVERNED_TOOL),
    )

    assert len(drilldown.rows) <= 100
    assert drilldown.total_rows >= len(drilldown.rows)
