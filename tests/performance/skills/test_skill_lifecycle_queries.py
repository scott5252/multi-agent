from __future__ import annotations

from multi_agent_platform.admin.skill_lifecycle import (
    build_skill_execution_diagnostics,
    build_skill_lifecycle_audit,
    build_skill_lifecycle_dashboard,
)
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminScope,
    ReactAdminScopeType,
)
from multi_agent_platform.auth.principal import AuthMode, AuthProvider, PrincipalContext


def _scope() -> ReactAdminScope:
    return ReactAdminScope(
        scope_type=ReactAdminScopeType.TENANT,
        tenant_id="11111111-1111-1111-1111-111111111111",
        label="Acme",
    )


def _principal() -> PrincipalContext:
    return PrincipalContext(
        principal_id="tenant-admin",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        role_codes=("tenant_user", "tenant_admin"),
        permission_codes=("tenant:admin", "skill-registry:install"),
        trace_id="trace-performance-skills",
    )


def test_skill_lifecycle_bootstrap_outputs_are_bounded() -> None:
    dashboard = build_skill_lifecycle_dashboard(scope=_scope(), principal=_principal())

    assert len(dashboard.installations) <= 10
    assert len(dashboard.connector_diagnostics) == 5
    assert len(dashboard.skill_execution_diagnostics) <= 10
    assert len(dashboard.audit_timeline) <= 20


def test_skill_lifecycle_diagnostics_and_audit_lists_are_bounded() -> None:
    diagnostics = build_skill_execution_diagnostics(scope=_scope())
    audit = build_skill_lifecycle_audit(scope=_scope())

    assert len(diagnostics.diagnostics) <= 10
    assert len(audit.audit_timeline) <= 20
    assert all(record.audit_reference_id for record in audit.audit_timeline)
