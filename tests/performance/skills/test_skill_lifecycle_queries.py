from __future__ import annotations

from tests.fixtures.skill_registry import seed_live_skill_lifecycle_repository

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
from multi_agent_platform.db.repositories.skill_registry import SkillRegistryRepository


def _scope(tenant_id: str) -> ReactAdminScope:
    return ReactAdminScope(
        scope_type=ReactAdminScopeType.TENANT,
        tenant_id=tenant_id,
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


async def test_skill_lifecycle_bootstrap_outputs_are_bounded(
    session,
    seeded_tenant,
) -> None:
    repository = SkillRegistryRepository(session)
    await seed_live_skill_lifecycle_repository(
        repository,
        tenant_id=seeded_tenant.tenant_id,
    )

    dashboard = await build_skill_lifecycle_dashboard(
        scope=_scope(str(seeded_tenant.tenant_id)),
        principal=_principal(),
        repository=repository,
    )

    assert len(dashboard.installations) <= 10
    assert len(dashboard.connector_diagnostics) <= 10
    assert len(dashboard.skill_execution_diagnostics) <= 10
    assert len(dashboard.audit_timeline) <= 20


async def test_skill_lifecycle_diagnostics_and_audit_lists_are_bounded(
    session,
    seeded_tenant,
) -> None:
    repository = SkillRegistryRepository(session)
    await seed_live_skill_lifecycle_repository(
        repository,
        tenant_id=seeded_tenant.tenant_id,
    )

    diagnostics = await build_skill_execution_diagnostics(
        scope=_scope(str(seeded_tenant.tenant_id)),
        repository=repository,
    )
    audit = await build_skill_lifecycle_audit(
        scope=_scope(str(seeded_tenant.tenant_id)),
        repository=repository,
    )

    assert len(diagnostics.diagnostics) <= 10
    assert len(audit.audit_timeline) <= 20
    assert all(record.audit_reference_id for record in audit.audit_timeline)
