from __future__ import annotations

import yaml

from multi_agent_platform.admin.migration_hardening import (
    build_live_data_inventory_dashboard,
)
from multi_agent_platform.api.schemas.admin_migration_hardening_react import (
    LiveDataCiStatus,
    LiveDataInventoryDashboard,
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


def test_live_data_inventory_contract_shape_matches_dashboard() -> None:
    dashboard = build_live_data_inventory_dashboard(
        scope=ReactAdminScope(
            scope_type=ReactAdminScopeType.PLATFORM,
            tenant_id=None,
            label="Platform",
        ),
        principal=_platform_principal(),
    )

    payload = dashboard.model_dump(mode="json")
    assert LiveDataInventoryDashboard.model_validate(payload) == dashboard
    assert payload["page_id"] == "qa058-live-only-gate"
    assert payload["summary"]["ci_status"] == LiveDataCiStatus.PASS
    assert payload["findings"]
    assert payload["allowlist"]
    assert payload["route_targets"]
    assert "raw prompt" not in dashboard.model_dump_json().lower()
    assert "/Users/" not in dashboard.model_dump_json()


def test_openapi_contract_names_live_data_inventory_endpoint() -> None:
    contract = yaml.safe_load(
        open(
            "specs/058-live-only-ui-decommission-gate/contracts/live-only-ui-gate.openapi.yaml",
            encoding="utf-8",
        )
    )

    assert "/admin/app/migration/live-data-inventory.json" in contract["paths"]
    schema = contract["components"]["schemas"]["LiveDataInventoryDashboard"]
    assert {
        "page_id",
        "generated_at",
        "summary",
        "findings",
        "allowlist",
        "route_targets",
        "evidence",
        "states",
    } <= set(schema["required"])


def _platform_principal() -> PrincipalContext:
    return PrincipalContext(
        principal_id="platform-admin",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        tenant_id=None,
        org_id=None,
        role_codes=("platform_admin",),
        permission_codes=("platform:admin",),
        trace_id="trace-contract-qa048",
    )
