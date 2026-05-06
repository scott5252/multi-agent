from __future__ import annotations

from pathlib import Path
from uuid import UUID

from multi_agent_platform.admin.migration_hardening.jinja_inventory import (
    build_jinja_inventory_dashboard,
)
from multi_agent_platform.api.schemas.admin_migration_hardening_react import (
    JinjaInventoryClassification,
    JinjaInventoryItemType,
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

ACME_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")


def test_scanner_discovers_templates_static_routes_and_docs(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "src/multi_agent_platform/web_admin/templates/admin_react/app.html",
        '{% extends "admin_shell/base.html" %}<form method="post" action="/admin">',
    )
    _write(
        tmp_path,
        "src/multi_agent_platform/web_admin/templates/runs/index.html",
        '<a href="/runs/123">Run</a><script>progress</script>',
    )
    _write(
        tmp_path,
        "src/multi_agent_platform/web_admin/static/admin_shell.js",
        "console.log('legacy shell');",
    )
    _write(
        tmp_path,
        "src/multi_agent_platform/api/routers/web_run_ui.py",
        "\n".join(
            [
                "from fastapi import APIRouter",
                "router = APIRouter()",
                '@router.get("/runs")',
                "async def runs_index(request, container):",
                "    return container.workflow_ui_templates.TemplateResponse(",
                '        request, "runs/index.html", {}',
                "    )",
            ]
        ),
    )
    _write(
        tmp_path,
        "docs/runbook.md",
        "Open /admin/app/migration and /runs during migration QA.",
    )

    dashboard = build_jinja_inventory_dashboard(
        scope=_platform_scope(),
        principal=_principal("platform-admin", roles=("platform_admin",)),
        repo_root=tmp_path,
    )
    items = [item for group in dashboard.groups for item in group.items]

    assert dashboard.summary.template_count >= 2
    assert dashboard.summary.static_asset_count == 1
    assert dashboard.summary.route_count >= 1
    assert dashboard.summary.direct_link_count >= 2
    assert any(item.item_type == JinjaInventoryItemType.REACT_HOST for item in items)
    assert any(
        item.item_type == JinjaInventoryItemType.TEMPLATE_INCLUDE for item in items
    )
    assert any(item.legacy_route == "/runs" for item in items)
    assert any(
        item.classification
        == JinjaInventoryClassification.NON_JINJA_COMPATIBILITY_NEEDED
        for item in items
    )
    assert "/Users/" not in dashboard.model_dump_json()


def test_tenant_scope_filters_platform_only_inventory(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "src/multi_agent_platform/web_admin/templates/operations/index.html",
        "<h1>Operations</h1>",
    )
    _write(
        tmp_path,
        "src/multi_agent_platform/web_admin/templates/memberships/index.html",
        "<h1>Memberships</h1>",
    )

    dashboard = build_jinja_inventory_dashboard(
        scope=_tenant_scope(),
        principal=_principal(
            "tenant-admin-acme",
            roles=("tenant_user", "tenant_admin"),
            tenant_id=ACME_TENANT_ID,
        ),
        repo_root=tmp_path,
    )
    specs = {
        item.planned_removal_spec for group in dashboard.groups for item in group.items
    }

    assert "044" not in specs
    assert "045" in specs


def _write(root: Path, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _platform_scope() -> ReactAdminScope:
    return ReactAdminScope(
        scope_type=ReactAdminScopeType.PLATFORM,
        tenant_id=None,
        label="Platform",
    )


def _tenant_scope() -> ReactAdminScope:
    return ReactAdminScope(
        scope_type=ReactAdminScopeType.TENANT,
        tenant_id=ACME_TENANT_ID,
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
