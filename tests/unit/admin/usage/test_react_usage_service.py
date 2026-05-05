from __future__ import annotations

from uuid import UUID

from multi_agent_platform.admin.usage.react_usage import (
    ACME_TENANT_ID,
    GLOBEX_LABEL,
    build_usage_dashboard,
    build_usage_events,
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


def _platform_principal() -> PrincipalContext:
    return PrincipalContext(
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        principal_id="platform-admin",
        role_codes=("platform_admin",),
    )


def _tenant_principal() -> PrincipalContext:
    return PrincipalContext(
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        principal_id="tenant-admin-acme",
        role_codes=("tenant_admin",),
        tenant_id=UUID(ACME_TENANT_ID),
    )


def _platform_scope() -> ReactAdminScope:
    return ReactAdminScope(
        scope_type=ReactAdminScopeType.PLATFORM,
        tenant_id=None,
        label="Platform",
    )


def _tenant_scope() -> ReactAdminScope:
    return ReactAdminScope(
        scope_type=ReactAdminScopeType.TENANT,
        tenant_id=UUID(ACME_TENANT_ID),
        label="Acme",
    )


def test_platform_dashboard_includes_safe_cross_tenant_rollups() -> None:
    dashboard = build_usage_dashboard(
        scope=_platform_scope(),
        principal=_platform_principal(),
        allowed_scope_options=(),
        query=UsageReactDashboardQuery(group_by=UsageReactGroupBy.TENANT),
    )

    labels = {row.safe_label for row in dashboard.rollup.rows}
    assert {"Acme", "Globex"} <= labels
    assert len(dashboard.rollup.rows) <= 25


def test_tenant_dashboard_excludes_other_tenant_labels() -> None:
    dashboard = build_usage_dashboard(
        scope=_tenant_scope(),
        principal=_tenant_principal(),
        allowed_scope_options=(),
        query=UsageReactDashboardQuery(group_by=UsageReactGroupBy.PROVIDER),
    )

    assert GLOBEX_LABEL not in dashboard.model_dump_json()
    assert all(row.safe_label for row in dashboard.rollup.rows)


def test_all_rollup_dimensions_render_safe_rows() -> None:
    for group_by in UsageReactGroupBy:
        dashboard = build_usage_dashboard(
            scope=_platform_scope(),
            principal=_platform_principal(),
            allowed_scope_options=(),
            query=UsageReactDashboardQuery(group_by=group_by),
        )

        assert dashboard.rollup.group_by is group_by
        assert dashboard.rollup.rows
        assert "provider payload" not in dashboard.model_dump_json().lower()


def test_events_support_gateway_and_tool_attribution() -> None:
    drilldown = build_usage_events(
        scope=_platform_scope(),
        principal=_platform_principal(),
        query=UsageReactEventQuery(group_by=UsageReactGroupBy.GATEWAY_OPERATION),
    )

    assert drilldown.rows
    assert drilldown.total_rows <= 100
    assert any(row.gateway_operation_label for row in drilldown.rows)
    assert "raw prompt" not in drilldown.model_dump_json().lower()


def test_cross_tenant_export_is_denied_for_tenant_admin() -> None:
    summary = build_usage_export_result(
        scope=_tenant_scope(),
        principal=_tenant_principal(),
        request=UsageReactExportCreateRequest(
            filters={"tenant_id": "22222222-2222-2222-2222-222222222222"},
            requested_group_by=UsageReactGroupBy.PROVIDER,
        ),
    )

    assert summary.status == "denied"
    assert summary.row_count == 0
    assert "denied" in summary.audit_reference
