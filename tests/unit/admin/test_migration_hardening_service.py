from __future__ import annotations

from uuid import UUID

from multi_agent_platform.admin.migration_hardening import (
    build_migration_dashboard,
    build_migration_rollback_plan,
    build_migration_route_groups,
)
from multi_agent_platform.admin.migration_hardening.react_migration_hardening import (
    ACME_TENANT_ID,
)
from multi_agent_platform.api.schemas.admin_migration_hardening_react import (
    MigrationEvidenceStatus,
    MigrationRouteDecision,
    MigrationScopeRequirement,
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


def test_platform_dashboard_includes_all_route_groups_and_evidence() -> None:
    dashboard = build_migration_dashboard(
        scope=_platform_scope(),
        principal=_principal("platform-admin", roles=("platform_admin",)),
    )

    entries = [entry for group in dashboard.route_groups for entry in group.entries]
    assert dashboard.summary.total_destinations == len(entries)
    assert {group.group_id for group in dashboard.route_groups} == {
        "foundation-shell-qa037",
        "operations-workflows-qa037",
        "governance-skills-tests-qa037",
        "people-usage-channels-qa037",
    }
    assert not any(
        entry.decision == MigrationRouteDecision.RETAINED_FALLBACK for entry in entries
    )
    assert all(entry.parity_evidence for entry in entries if entry.retirement_allowed)
    assert "qa037-secret-value" not in dashboard.model_dump_json()
    assert dashboard.title == "React-only browser UI"
    assert dashboard.jinja_inventory.summary.template_count == 0
    assert "qa038-secret-value" not in dashboard.model_dump_json()


def test_tenant_admin_dashboard_filters_platform_only_destinations() -> None:
    dashboard = build_migration_dashboard(
        scope=_tenant_scope(),
        principal=_principal(
            "tenant-admin-acme",
            roles=("tenant_user", "tenant_admin"),
            tenant_id=ACME_TENANT_ID,
        ),
    )

    entries = [entry for group in dashboard.route_groups for entry in group.entries]
    assert entries
    assert all(
        entry.scope_requirement
        in {
            MigrationScopeRequirement.TENANT_ADMIN,
            MigrationScopeRequirement.TENANT_USER,
            MigrationScopeRequirement.MIXED,
        }
        for entry in entries
    )
    assert not any(entry.entry_id == "operations-qa037" for entry in entries)
    assert dashboard.tenant_isolation_sweep.checked_artifacts == 6


def test_tenant_user_dashboard_only_exposes_user_safe_rows() -> None:
    dashboard = build_migration_dashboard(
        scope=_tenant_scope(),
        principal=_principal(
            "tenant-user-acme",
            roles=("tenant_user",),
            tenant_id=ACME_TENANT_ID,
        ),
    )

    entries = [entry for group in dashboard.route_groups for entry in group.entries]
    assert entries
    assert all(
        entry.scope_requirement
        in {MigrationScopeRequirement.TENANT_USER, MigrationScopeRequirement.MIXED}
        for entry in entries
    )
    assert any(state.reason == "user_scope_limited" for state in dashboard.states)


def test_rollback_budget_accessibility_and_sweeps_are_ready() -> None:
    principal = _principal("platform-admin", roles=("platform_admin",))
    dashboard = build_migration_dashboard(scope=_platform_scope(), principal=principal)
    rollback = build_migration_rollback_plan(
        scope=_platform_scope(),
        principal=principal,
    )

    assert rollback.plan_id == dashboard.rollback_plan.plan_id
    assert rollback.steps
    assert dashboard.performance_budget.status == MigrationEvidenceStatus.PASS
    assert dashboard.performance_budget.route_bootstrap_ms_limit == 500
    assert (
        dashboard.accessibility_audit.text_overlap_status
        == MigrationEvidenceStatus.PASS
    )
    assert dashboard.redaction_sweep.unsafe_match_count == 0
    assert dashboard.tenant_isolation_sweep.status == MigrationEvidenceStatus.PASS


def test_route_group_projection_is_bounded() -> None:
    groups = build_migration_route_groups(
        scope=_platform_scope(),
        principal=_principal("platform-admin", roles=("platform_admin",)),
    )

    assert len(groups) <= 20
    assert all(len(group.entries) <= 40 for group in groups)


def _platform_scope() -> ReactAdminScope:
    return ReactAdminScope(
        scope_type=ReactAdminScopeType.PLATFORM,
        tenant_id=None,
        label="Platform",
    )


def _tenant_scope(tenant_id: UUID = ACME_TENANT_ID) -> ReactAdminScope:
    return ReactAdminScope(
        scope_type=ReactAdminScopeType.TENANT,
        tenant_id=tenant_id,
        label="Acme",
    )


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
