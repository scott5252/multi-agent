from __future__ import annotations

from multi_agent_platform.admin.channel_telegram_briefing import (
    ACME_TENANT_ID,
    build_channel_telegram_briefing_dashboard,
    build_delivery_diagnostics,
)
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminScope,
    ReactAdminScopeType,
)
from multi_agent_platform.auth.principal import PrincipalContext


def test_channel_dashboard_projects_bounded_rows_without_database_queries() -> None:
    principal = PrincipalContext(
        principal_id="tenant-admin-acme",
        role_codes=("tenant_user", "tenant_admin"),
        tenant_id=ACME_TENANT_ID,
    )
    scope = ReactAdminScope(
        scope_type=ReactAdminScopeType.TENANT,
        tenant_id=ACME_TENANT_ID,
        label="Acme",
    )

    dashboard = build_channel_telegram_briefing_dashboard(
        scope=scope,
        principal=principal,
    )
    diagnostics = build_delivery_diagnostics(scope=scope, principal=principal)

    assert len(dashboard.aliases) <= 25
    assert len(dashboard.delivery_attempts) <= 25
    assert diagnostics.limit == 25
