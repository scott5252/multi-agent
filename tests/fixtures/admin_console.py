from __future__ import annotations

from uuid import UUID, uuid4

from multi_agent_platform.auth.principal import (
    AuthMode,
    AuthProvider,
    PrincipalContext,
)
from multi_agent_platform.tenancy.context import ScopeType

ADMIN_CONSOLE_ROUTE_SURFACES = (
    "GET:/admin",
    "GET:/admin/scope",
    "GET:/admin/filters/{admin_area}",
    "POST:/admin/filters/{admin_area}",
    "GET:/admin/filters/{admin_area}/{filter_id}/restore",
    "POST:/admin/filters/{admin_area}/{filter_id}",
    "DELETE:/admin/filters/{admin_area}/{filter_id}",
    "GET:/admin/workflows/ui",
    "GET:/admin/workflows/drafts/{workflow_draft_id}/editor",
    "GET:/admin/workflows/versions/{workflow_version_bundle_id}/detail",
    "GET:/admin/config/ui",
    "GET:/admin/config/ui/history",
    "GET:/admin/config/ui/runs/{workflow_run_id}/provenance",
    "GET:/admin/runs",
    "GET:/admin/runs/{workflow_run_id}",
    "GET:/admin/runs/{workflow_run_id}/replay",
    "GET:/admin/reliability/ui/",
    "GET:/admin/reliability/ui/breakers",
    "GET:/admin/reliability/ui/dead-letters",
)

WORKFLOW_UI_PATHS = (
    "/admin/workflows/ui",
    "/admin/workflows/drafts/{workflow_draft_id}/editor",
    "/admin/workflows/versions/{workflow_version_bundle_id}/detail",
)

MODEL_SKILL_UI_PATHS = (
    "/admin/config/ui",
    "/admin/config/ui/history",
    "/admin/config/ui/runs/{workflow_run_id}/provenance",
)

RUN_INSPECTION_UI_PATHS = (
    "/admin/runs",
    "/admin/runs/{workflow_run_id}",
    "/admin/runs/{workflow_run_id}/replay",
)

RELIABILITY_UI_PATHS = (
    "/admin/reliability/ui/",
    "/admin/reliability/ui/breakers",
    "/admin/reliability/ui/dead-letters",
)


def platform_principal() -> PrincipalContext:
    return PrincipalContext(
        principal_identity_id=uuid4(),
        principal_id="platform-admin",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        role_codes=("platform_admin",),
        permission_codes=("tenant:admin", "tenant:read"),
        scope_type=ScopeType.PLATFORM,
        trace_id="trace-platform",
        request_id="request-platform",
    )


def tenant_principal(tenant_id: UUID | None = None) -> PrincipalContext:
    resolved_tenant_id = tenant_id or uuid4()
    return PrincipalContext(
        principal_identity_id=uuid4(),
        principal_id="tenant-admin-acme",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        tenant_id=resolved_tenant_id,
        role_codes=("tenant_user", "tenant_admin"),
        permission_codes=("tenant:read", "tenant:admin"),
        scope_type=ScopeType.TENANT,
        trace_id="trace-tenant",
        request_id="request-tenant",
    )


def unauthorized_principal() -> PrincipalContext:
    return PrincipalContext(
        principal_identity_id=uuid4(),
        principal_id="viewer",
        auth_provider=AuthProvider.LOCAL_PRINCIPAL,
        auth_mode=AuthMode.LOCAL_PRINCIPAL,
        role_codes=("tenant_user",),
        permission_codes=("tenant:read",),
        scope_type=ScopeType.PLATFORM,
        trace_id="trace-viewer",
        request_id="request-viewer",
    )


def assert_shell_landmarks(html: str) -> None:
    assert 'href="#admin-main-content"' in html
    assert 'aria-label="Admin"' in html
    assert 'id="admin-main-content"' in html
    assert html.count("<main") == 1


def assert_nav_item(html: str, label: str) -> None:
    assert f">{label}<" in html or f">{label}" in html


def assert_scope_label(html: str, label: str) -> None:
    assert "data-admin-scope-label" in html
    assert label in html


def assert_state_region(html: str, state_type: str) -> None:
    assert f'data-state-type="{state_type}"' in html
    assert 'role="alert"' in html or 'role="status"' in html
