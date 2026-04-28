from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest

from multi_agent_platform.api.ui import admin_console
from multi_agent_platform.api.ui.admin_console import (
    AdminConsoleAccessError,
    AdminScope,
    BreadcrumbItem,
    CommonStateType,
    NavigationItem,
    _item_scope_allowed,
    _policy_allows,
    build_admin_shell_context,
    build_common_state,
    build_saved_filter_summary,
    navigation_registry,
    normalize_filter_criteria,
    resolve_admin_scope,
    safe_redirect_target,
    sanitize_breadcrumbs,
    sanitize_flash_message,
    sanitize_text,
    with_scope_query,
)
from multi_agent_platform.auth.policy import ProtectedSurface, SurfaceClassification
from tests.fixtures.admin_console import tenant_principal


def test_admin_scope_serializes_platform_and_tenant_scope() -> None:
    tenant_id = uuid4()

    platform_scope = AdminScope.platform()
    tenant_scope = AdminScope.tenant(tenant_id, label="Acme")

    assert platform_scope.scope_type == "platform"
    assert platform_scope.tenant_id is None
    assert platform_scope.query_params() == {}
    assert tenant_scope.scope_type == "tenant"
    assert tenant_scope.tenant_id == tenant_id
    assert tenant_scope.query_params() == {"tenant_id": str(tenant_id)}


def test_admin_scope_rejects_inconsistent_scope_data() -> None:
    tenant_id = uuid4()

    with pytest.raises(ValueError):
        AdminScope.tenant(None)
    with pytest.raises(ValueError):
        AdminScope(scope_type="platform", tenant_id=tenant_id)
    with pytest.raises(ValueError):
        AdminScope(scope_type="tenant")

    assert AdminScope(scope_type="platform").label == "Platform"


def test_navigation_registry_has_required_metadata() -> None:
    items = navigation_registry()

    assert {item.group for item in items} >= {
        "Workflows",
        "Model And Skill Config",
        "Run Inspection",
        "Reliability",
    }
    assert all(item.route_surface_key.startswith("GET:/admin") for item in items)
    assert all(item.active_matchers for item in items)


def test_shell_context_filters_navigation_and_marks_active_url() -> None:
    tenant = tenant_principal()
    context = build_admin_shell_context(
        principal=tenant,
        active_scope=AdminScope.tenant(tenant.tenant_id),
        current_path="/admin/config/ui/history",
        title="History",
        breadcrumbs=[BreadcrumbItem(label="History", href="/admin/config/ui/history")],
    )

    labels = [item.label for group in context.navigation_groups for item in group.items]
    assert "Configuration" in labels
    assert "Configuration History" in labels
    assert "Console Home" in labels
    assert any(
        item.label == "Configuration History" and item.active
        for group in context.navigation_groups
        for item in group.items
    )


def test_platform_admin_can_inspect_an_external_tenant_scope() -> None:
    principal = tenant_principal()
    platform = principal.model_copy(
        update={
            "tenant_id": None,
            "role_codes": ("platform_admin",),
            "principal_id": "platform-admin",
        }
    )
    selected_tenant = uuid4()

    context = build_admin_shell_context(
        principal=platform,
        active_scope=AdminScope.tenant(selected_tenant, label="Selected"),
        current_path="/admin/runs",
        title="Runs",
    )

    assert any(
        option.scope.tenant_id == selected_tenant for option in context.available_scopes
    )
    assert context.active_scope.tenant_id == selected_tenant


def test_forged_tenant_scope_is_rejected_for_tenant_admin() -> None:
    principal = tenant_principal()

    with pytest.raises(AdminConsoleAccessError):
        build_admin_shell_context(
            principal=principal,
            active_scope=AdminScope.tenant(uuid4()),
            current_path="/admin",
            title="Admin",
        )


def test_resolve_admin_scope_rejects_invalid_or_missing_scope() -> None:
    tenant = tenant_principal()
    tenant_without_id = tenant.model_copy(update={"tenant_id": None})
    viewer = tenant.model_copy(update={"role_codes": ("tenant_user",)})

    with pytest.raises(AdminConsoleAccessError):
        resolve_admin_scope(viewer, None)
    with pytest.raises(AdminConsoleAccessError):
        resolve_admin_scope(tenant_without_id, None)
    with pytest.raises(AdminConsoleAccessError):
        resolve_admin_scope(tenant, "not-a-uuid")


def test_common_states_and_flash_messages_are_sanitized() -> None:
    state = build_common_state(
        CommonStateType.UNEXPECTED_ERROR,
        title="Traceback from secret token",
        summary="password=abc stack trace prompt memory",
        trace_id="trace-123",
    )
    message = sanitize_flash_message(
        "Saved secret token with password=abc",
        scope=AdminScope.platform(),
        principal_id="platform-admin",
    )
    crumbs = sanitize_breadcrumbs(
        [
            BreadcrumbItem(
                label="secret prompt memory payload",
                href="/admin/runs/not-allowed",
            )
        ]
    )

    assert "secret" not in state.title.lower()
    assert "password" not in state.summary.lower()
    assert "trace-123" == state.trace_id
    assert "password" not in message.summary.lower()
    assert crumbs[0].label == "Protected detail"


def test_redirects_breadcrumbs_and_scope_queries_are_sanitized() -> None:
    tenant_id = uuid4()
    crumbs = sanitize_breadcrumbs(
        [
            BreadcrumbItem(label="Admin", href="/admin"),
            BreadcrumbItem(label="external", href="https://example.test/admin"),
        ]
    )

    assert safe_redirect_target(None) == "/admin"
    assert safe_redirect_target("https://example.test/admin") == "/admin"
    assert safe_redirect_target("/not-admin") == "/admin"
    assert safe_redirect_target("//example.test/admin") == "/admin"
    assert safe_redirect_target("////admin") == "/admin"
    assert (
        safe_redirect_target("/admin/runs?status=failed") == "/admin/runs?status=failed"
    )
    assert (
        with_scope_query(
            "/admin/runs?tenant_id=bad&status=failed",
            AdminScope.platform(),
        )
        == "/admin/runs?status=failed"
    )
    assert (
        with_scope_query("/admin/runs?status=failed", AdminScope.tenant(tenant_id))
        == f"/admin/runs?status=failed&tenant_id={tenant_id}"
    )
    assert crumbs[-1].active is True
    assert crumbs[-1].href is None
    assert sanitize_breadcrumbs(()) == ()
    assert sanitize_text("") == "Protected detail"
    assert sanitize_text("x" * 200, max_length=8) == "xxxxxxx..."


def test_filter_normalization_rejects_unknown_and_unsafe_criteria() -> None:
    scope = AdminScope.platform()

    normalized = normalize_filter_criteria(
        "workflows",
        {"status": "draft", "slug": "customer-intake", "workflow_kind": ""},
        active_scope=scope,
    )

    assert normalized.criteria == {"status": "draft", "slug": "customer-intake"}
    assert normalized.safe_summary["status"] == "draft"
    with pytest.raises(ValueError):
        normalize_filter_criteria("workflows", {"raw_secret": "x"}, active_scope=scope)


def test_filter_normalization_handles_json_lists_and_invalid_values() -> None:
    tenant_id = uuid4()
    normalized = normalize_filter_criteria(
        "run_inspection",
        (
            '{"tenant_id": "'
            + str(tenant_id)
            + '", "status": ["failed", "blocked"], "agent": true, "tool": 2}'
        ),
        active_scope=AdminScope.tenant(tenant_id),
    )

    assert normalized.criteria["status"] == ["failed", "blocked"]
    assert normalized.criteria["agent"] is True
    assert normalized.criteria["tool"] == 2
    with pytest.raises(ValueError):
        normalize_filter_criteria("unknown", {}, active_scope=AdminScope.platform())
    with pytest.raises(ValueError):
        normalize_filter_criteria("workflows", "[]", active_scope=AdminScope.platform())
    with pytest.raises(ValueError):
        normalize_filter_criteria(
            "workflows",
            {"status": "secret token"},
            active_scope=AdminScope.platform(),
        )
    with pytest.raises(ValueError):
        normalize_filter_criteria(
            "workflows",
            {"status": {"raw": "object"}},
            active_scope=AdminScope.platform(),
        )
    with pytest.raises(ValueError):
        normalize_filter_criteria(
            "workflows",
            {"status": ["draft", "secret token"]},
            active_scope=AdminScope.platform(),
        )


def test_policy_gate_covers_surface_classification_branches(monkeypatch) -> None:
    principal = tenant_principal()
    tenant_scope = AdminScope.tenant(principal.tenant_id)
    surface_prefix = "TEST:/admin-console/"
    policies = {
        f"{surface_prefix}public": ProtectedSurface(
            surface_key=f"{surface_prefix}public",
            requested_action="test",
            classification=SurfaceClassification.PUBLIC,
        ),
        f"{surface_prefix}permission": ProtectedSurface(
            surface_key=f"{surface_prefix}permission",
            requested_action="test",
            classification=SurfaceClassification.AUTHENTICATED,
            required_permissions=("missing:permission",),
        ),
        f"{surface_prefix}platform": ProtectedSurface(
            surface_key=f"{surface_prefix}platform",
            requested_action="test",
            classification=SurfaceClassification.PLATFORM_ADMIN,
        ),
        f"{surface_prefix}tenant-user": ProtectedSurface(
            surface_key=f"{surface_prefix}tenant-user",
            requested_action="test",
            classification=SurfaceClassification.TENANT_USER,
        ),
        f"{surface_prefix}tenant-admin": ProtectedSurface(
            surface_key=f"{surface_prefix}tenant-admin",
            requested_action="test",
            classification=SurfaceClassification.TENANT_ADMIN,
        ),
    }
    for key, policy in policies.items():
        monkeypatch.setitem(admin_console.SURFACE_POLICIES, key, policy)

    assert _policy_allows(
        principal=principal,
        active_scope=tenant_scope,
        surface_key=f"{surface_prefix}missing",
    ) == (False, "missing_surface_policy")
    assert _policy_allows(
        principal=principal,
        active_scope=tenant_scope,
        surface_key=f"{surface_prefix}public",
    ) == (False, "public_surface_policy")
    assert _policy_allows(
        principal=principal,
        active_scope=tenant_scope,
        surface_key=f"{surface_prefix}permission",
    ) == (False, "insufficient_permission")
    assert _policy_allows(
        principal=principal,
        active_scope=tenant_scope,
        surface_key=f"{surface_prefix}platform",
    ) == (False, "platform_admin_required")
    assert _policy_allows(
        principal=principal,
        active_scope=AdminScope.platform(),
        surface_key=f"{surface_prefix}tenant-user",
    ) == (False, "tenant_scope_required")
    assert _policy_allows(
        principal=principal.model_copy(update={"tenant_id": uuid4()}),
        active_scope=tenant_scope,
        surface_key=f"{surface_prefix}tenant-user",
    ) == (False, "cross_tenant_scope")
    assert _policy_allows(
        principal=principal,
        active_scope=tenant_scope,
        surface_key=f"{surface_prefix}tenant-user",
    ) == (True, "tenant_role")
    assert _policy_allows(
        principal=principal,
        active_scope=tenant_scope,
        surface_key=f"{surface_prefix}tenant-admin",
    ) == (True, "tenant_admin_role")
    assert _policy_allows(
        principal=principal.model_copy(update={"role_codes": ("platform_admin",)}),
        active_scope=tenant_scope,
        surface_key=f"{surface_prefix}tenant-user",
    ) == (True, "platform_admin_tenant_scope")
    monkeypatch.setitem(
        admin_console.SURFACE_POLICIES,
        f"{surface_prefix}unsupported",
        SimpleNamespace(
            classification="unsupported",
            required_permissions=(),
            required_roles=(),
        ),
    )
    assert _policy_allows(
        principal=principal,
        active_scope=tenant_scope,
        surface_key=f"{surface_prefix}unsupported",
    ) == (False, "unsupported_surface_policy")


def test_required_platform_navigation_items_are_hidden_in_tenant_scope() -> None:
    item = NavigationItem(
        item_id="platform-only",
        label="Platform",
        group="Test",
        href="/admin/platform",
        route_surface_key="GET:/admin/platform",
        required_scope="platform",
        active_matchers=("/admin/platform",),
    )

    assert _item_scope_allowed(item, AdminScope.tenant(uuid4())) == (
        False,
        "requires_platform_scope",
    )


def test_saved_filter_summary_sanitizes_records() -> None:
    filter_id = uuid4()
    restored_at = datetime(2026, 4, 27, tzinfo=UTC)
    record = SimpleNamespace(
        admin_saved_filter_id=filter_id,
        display_name="Draft secret token",
        admin_area="workflows",
        filter_key="workflow-list",
        safe_summary={"status": "draft", "raw": "password=abc"},
        last_restored_at=restored_at,
    )

    summary = build_saved_filter_summary(record, active_scope=AdminScope.platform())

    assert summary.filter_id == filter_id
    assert summary.display_name == "Protected detail"
    assert summary.safe_summary["raw"] == "Protected detail"
    assert summary.last_restored_at == restored_at.isoformat()
