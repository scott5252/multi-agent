from __future__ import annotations

import yaml

from multi_agent_platform.admin.migration_hardening import (
    build_transitional_label_gate,
)
from multi_agent_platform.api.schemas.admin_migration_hardening_react import (
    LiveDataCiStatus,
    TransitionalLabelGate,
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


def test_transitional_label_gate_contract_shape_matches_dashboard() -> None:
    gate = build_transitional_label_gate(
        scope=ReactAdminScope(
            scope_type=ReactAdminScopeType.PLATFORM,
            tenant_id=None,
            label="Platform",
        ),
        principal=_platform_principal(),
    )

    payload = gate.model_dump(mode="json")
    assert TransitionalLabelGate.model_validate(payload) == gate
    assert payload["page_id"] == "qa059-transitional-label-gate"
    assert payload["summary"]["ci_status"] == LiveDataCiStatus.PASS
    assert payload["summary"]["blocked_count"] == 0
    assert payload["findings"]
    assert "React Admin" not in gate.model_dump_json()
    assert "/Users/" not in gate.model_dump_json()


def test_openapi_contract_names_transitional_label_gate_endpoint() -> None:
    contract = yaml.safe_load(
        open(
            "specs/059-admin-ui-transitional-react-label-removal/contracts/transitional-label-gate.openapi.yaml",
            encoding="utf-8",
        )
    )

    assert "/admin/app/migration/transitional-labels.json" in contract["paths"]
    schema = contract["components"]["schemas"]["TransitionalLabelGate"]
    assert {
        "page_id",
        "generated_at",
        "summary",
        "findings",
        "evidence",
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
        trace_id="trace-contract-qa059",
    )
