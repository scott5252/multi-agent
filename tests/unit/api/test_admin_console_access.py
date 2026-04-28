from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.api.routers.admin_console import (
    available_scope_options_for_request,
)
from multi_agent_platform.api.ui.admin_console import (
    AdminConsoleAccessError,
    AdminScope,
    build_admin_shell_context,
    resolve_admin_scope,
)
from multi_agent_platform.db.models.tenant import Tenant
from tests.fixtures.admin_console import (
    platform_principal,
    tenant_principal,
    unauthorized_principal,
)


def test_platform_admin_gets_platform_scope_and_platform_navigation() -> None:
    principal = platform_principal()
    context = build_admin_shell_context(
        principal=principal,
        active_scope=resolve_admin_scope(principal, None),
        current_path="/admin/workflows/ui",
        title="Workflows",
    )

    labels = [item.label for group in context.navigation_groups for item in group.items]
    assert context.active_scope.scope_type == "platform"
    assert "Workflow Registry" in labels
    assert "Run Search" in labels


def test_tenant_admin_gets_tenant_scope_and_tenant_navigation_links() -> None:
    principal = tenant_principal()
    context = build_admin_shell_context(
        principal=principal,
        active_scope=resolve_admin_scope(principal, str(principal.tenant_id)),
        current_path="/admin/config/ui",
        title="Config",
    )

    labels = [item.label for group in context.navigation_groups for item in group.items]
    assert context.active_scope.scope_type == "tenant"
    assert "Configuration" in labels
    assert all(
        "tenant_id=" in item.href or not item.preserve_tenant_scope
        for group in context.navigation_groups
        for item in group.items
    )


def test_unauthorized_principal_cannot_build_admin_shell() -> None:
    with pytest.raises(AdminConsoleAccessError):
        build_admin_shell_context(
            principal=unauthorized_principal(),
            active_scope=AdminScope.platform(),
            current_path="/admin",
            title="Admin",
        )


def test_tenant_admin_cannot_select_forged_tenant() -> None:
    principal = tenant_principal()
    with pytest.raises(AdminConsoleAccessError):
        resolve_admin_scope(principal, str(uuid4()))


class FakeTenantResult:
    def __init__(self, tenants: tuple[Tenant, ...]) -> None:
        self._tenants = tenants

    def scalars(self) -> tuple[Tenant, ...]:
        return self._tenants


class FakeTenantSession:
    def __init__(self, tenants: tuple[Tenant, ...]) -> None:
        self._tenants = tenants
        self.executed = False

    async def execute(self, statement: object) -> FakeTenantResult:
        self.executed = True
        return FakeTenantResult(self._tenants)


@pytest.mark.asyncio
async def test_platform_admin_scope_options_include_active_tenants() -> None:
    tenant_id = uuid4()
    session = FakeTenantSession(
        (
            Tenant(
                tenant_id=tenant_id,
                slug="acme",
                display_name="Acme",
            ),
        )
    )

    options = await available_scope_options_for_request(
        principal=platform_principal(),
        active_scope=AdminScope.platform(),
        current_path="/admin",
        session=session,  # type: ignore[arg-type]
    )

    assert session.executed
    assert [option.label for option in options] == [
        "Platform scope",
        "Tenant scope Acme",
    ]
    assert options[0].selected is True
    assert options[1].scope.tenant_id == tenant_id
    assert options[1].href == f"/admin/scope?next=/admin&tenant_id={tenant_id}"


@pytest.mark.asyncio
async def test_tenant_admin_scope_options_use_principal_home_tenant() -> None:
    principal = tenant_principal()
    session = FakeTenantSession(())

    options = await available_scope_options_for_request(
        principal=principal,
        active_scope=AdminScope.tenant(principal.tenant_id),
        current_path="/admin",
        session=session,  # type: ignore[arg-type]
    )

    assert session.executed is False
    assert len(options) == 1
    assert options[0].label.startswith("Tenant scope")
    assert options[0].selected is True
