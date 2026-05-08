from __future__ import annotations

from uuid import UUID, uuid4

from tests.fixtures.usage_react import seed_usage_react_live_data

from multi_agent_platform.admin.usage.react_usage import (
    build_usage_dashboard,
    build_usage_events,
    build_usage_export_detail,
    build_usage_export_result,
)
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminScope,
    ReactAdminScopeType,
)
from multi_agent_platform.api.schemas.admin_usage_react import (
    UsageReactDashboardQuery,
    UsageReactEventQuery,
    UsageReactExportCreateRequest,
    UsageReactGroupBy,
)
from multi_agent_platform.auth.principal import AuthProvider, PrincipalContext
from multi_agent_platform.db.repositories.usage import UsageRepository
from multi_agent_platform.usage.service import UsageAnalyticsService


def _platform_principal() -> PrincipalContext:
    return PrincipalContext(
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        principal_id="platform-admin",
        role_codes=("platform_admin",),
    )


def _tenant_principal(tenant_id: UUID) -> PrincipalContext:
    return PrincipalContext(
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        principal_id="tenant-admin-acme",
        role_codes=("tenant_admin",),
        tenant_id=tenant_id,
    )


def _platform_scope() -> ReactAdminScope:
    return ReactAdminScope(
        scope_type=ReactAdminScopeType.PLATFORM,
        tenant_id=None,
        label="Platform",
    )


def _tenant_scope(tenant_id: UUID) -> ReactAdminScope:
    return ReactAdminScope(
        scope_type=ReactAdminScopeType.TENANT,
        tenant_id=tenant_id,
        label="Acme",
    )


async def test_platform_dashboard_uses_live_usage_rows(
    session,
    seeded_tenant,
) -> None:
    await seed_usage_react_live_data(session, tenant_id=seeded_tenant.tenant_id)
    repository = UsageRepository(session)

    dashboard = await build_usage_dashboard(
        scope=_platform_scope(),
        principal=_platform_principal(),
        allowed_scope_options=(),
        repository=repository,
        service=UsageAnalyticsService(repository),
        query=UsageReactDashboardQuery(group_by=UsageReactGroupBy.TENANT),
    )

    labels = {row.safe_label for row in dashboard.rollup.rows}
    assert "Acme" in labels
    assert dashboard.summary_cards[0].value == "1,860"
    assert dashboard.exports[0].artifact_reference
    assert dashboard.exports[0].artifact_reference.startswith("usage-export:")
    assert "qa035" not in dashboard.model_dump_json().lower()


async def test_empty_dashboard_is_truthful(session, seeded_tenant) -> None:
    repository = UsageRepository(session)

    dashboard = await build_usage_dashboard(
        scope=_tenant_scope(seeded_tenant.tenant_id),
        principal=_tenant_principal(seeded_tenant.tenant_id),
        allowed_scope_options=(),
        repository=repository,
        service=UsageAnalyticsService(repository),
        query=UsageReactDashboardQuery(group_by=UsageReactGroupBy.PROVIDER),
    )

    assert dashboard.rollup.rows == ()
    assert dashboard.drilldown.rows == ()
    assert dashboard.states[0].reason == "empty"
    assert "No live usage events" in dashboard.common_states[0].summary


async def test_all_rollup_dimensions_render_safe_rows(session, seeded_tenant) -> None:
    await seed_usage_react_live_data(session, tenant_id=seeded_tenant.tenant_id)
    repository = UsageRepository(session)

    for group_by in UsageReactGroupBy:
        dashboard = await build_usage_dashboard(
            scope=_platform_scope(),
            principal=_platform_principal(),
            allowed_scope_options=(),
            repository=repository,
            service=UsageAnalyticsService(repository),
            query=UsageReactDashboardQuery(group_by=group_by),
        )

        assert dashboard.rollup.group_by is group_by
        assert dashboard.rollup.rows
        assert "raw prompt" not in dashboard.model_dump_json().lower()


async def test_events_support_gateway_and_tool_attribution(
    session,
    seeded_tenant,
) -> None:
    await seed_usage_react_live_data(session, tenant_id=seeded_tenant.tenant_id)
    repository = UsageRepository(session)

    drilldown = await build_usage_events(
        scope=_platform_scope(),
        principal=_platform_principal(),
        repository=repository,
        query=UsageReactEventQuery(group_by=UsageReactGroupBy.GATEWAY_OPERATION),
    )

    assert drilldown.rows
    assert drilldown.total_rows <= 100
    assert any(row.gateway_operation_label for row in drilldown.rows)
    assert any(row.tool_label for row in drilldown.rows)
    assert any(row.cost_status == "missing" for row in drilldown.rows)
    assert "raw prompt" not in drilldown.model_dump_json().lower()


async def test_export_creation_and_detail_are_persisted(
    session,
    seeded_tenant,
    filesystem_storage_provider,
) -> None:
    await seed_usage_react_live_data(session, tenant_id=seeded_tenant.tenant_id)
    repository = UsageRepository(session)

    summary = await build_usage_export_result(
        scope=_tenant_scope(seeded_tenant.tenant_id),
        principal=_tenant_principal(seeded_tenant.tenant_id),
        repository=repository,
        service=UsageAnalyticsService(repository),
        storage_provider=filesystem_storage_provider,
        request=UsageReactExportCreateRequest(
            filters={"tenant_id": str(seeded_tenant.tenant_id)},
            requested_group_by=UsageReactGroupBy.PROVIDER,
        ),
    )
    detail = await build_usage_export_detail(
        scope=_tenant_scope(seeded_tenant.tenant_id),
        principal=_tenant_principal(seeded_tenant.tenant_id),
        repository=repository,
        usage_export_request_id=summary.usage_export_request_id,
    )

    assert summary.status == "completed"
    assert summary.row_count == 2
    assert summary.artifact_reference == (
        f"usage-export:{summary.usage_export_request_id}"
    )
    assert "file:" not in summary.model_dump_json()
    assert detail.usage_export_request_id == summary.usage_export_request_id


async def test_cross_tenant_export_is_denied_for_tenant_admin(
    session,
    seeded_tenant,
    filesystem_storage_provider,
) -> None:
    repository = UsageRepository(session)
    summary = await build_usage_export_result(
        scope=_tenant_scope(seeded_tenant.tenant_id),
        principal=_tenant_principal(seeded_tenant.tenant_id),
        repository=repository,
        service=UsageAnalyticsService(repository),
        storage_provider=filesystem_storage_provider,
        request=UsageReactExportCreateRequest(
            filters={"tenant_id": str(uuid4())},
            requested_group_by=UsageReactGroupBy.PROVIDER,
        ),
    )

    assert summary.status == "denied"
    assert summary.row_count == 0
    assert "denied" in summary.audit_reference
