from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.api.ui.admin_console import (
    AdminConsoleAccessError,
    AdminScope,
    build_admin_shell_context,
    resolve_admin_scope,
)
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
