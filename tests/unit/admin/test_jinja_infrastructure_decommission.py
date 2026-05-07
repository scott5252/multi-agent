from __future__ import annotations

from pathlib import Path
from uuid import UUID

from multi_agent_platform.admin.migration_hardening import (
    build_decommission_inventory_dashboard,
    build_migration_dashboard,
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
RUNTIME_ROOT = Path("src/multi_agent_platform")
TEMPLATE_ROOT = Path("src/multi_agent_platform/web_admin/templates")
REACT_ASSET_ROOT = Path("src/multi_agent_platform/web_admin/static/react")
LEGACY_STATIC_FILES = (
    Path("src/multi_agent_platform/web_admin/static/admin_shell.js"),
    Path("src/multi_agent_platform/web_admin/static/model_providers.js"),
    Path("src/multi_agent_platform/web_admin/static/model_skill_config.js"),
    Path("src/multi_agent_platform/web_admin/static/prompt_runtime.js"),
    Path("src/multi_agent_platform/web_admin/static/reliability_controls.js"),
    Path("src/multi_agent_platform/web_admin/static/run_details.js"),
    Path("src/multi_agent_platform/web_admin/static/run_inspection.js"),
    Path("src/multi_agent_platform/web_admin/static/workflow_studio.css"),
    Path("src/multi_agent_platform/web_admin/static/workflow_studio.js"),
)
FORBIDDEN_RUNTIME_MARKERS = (
    "from starlette.templating import",
    "Jinja2Templates",
    "TemplateResponse",
    "workflow_ui_templates",
    "import jinja2",
    "from jinja2",
)


def test_runtime_source_has_no_jinja_template_infrastructure() -> None:
    offenders: list[str] = []
    for path in sorted(RUNTIME_ROOT.rglob("*.py")):
        if _is_react_asset(path):
            continue
        text = path.read_text(encoding="utf-8")
        for marker in FORBIDDEN_RUNTIME_MARKERS:
            if marker in text:
                offenders.append(f"{path}:{marker}")

    assert offenders == []


def test_server_templates_and_legacy_static_assets_are_removed() -> None:
    template_files = list(TEMPLATE_ROOT.rglob("*")) if TEMPLATE_ROOT.exists() else []

    assert [path for path in template_files if path.is_file()] == []
    assert all(not path.exists() for path in LEGACY_STATIC_FILES)
    assert (REACT_ASSET_ROOT / "manifest.json").exists()


def test_project_metadata_has_no_direct_jinja2_dependency() -> None:
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8").lower()
    lock = Path("uv.lock").read_text(encoding="utf-8").lower()

    assert '"jinja2' not in pyproject
    assert '{ name = "jinja2" }' not in lock
    assert '{ name = "jinja2", specifier' not in lock


def test_decommission_dashboard_reports_react_only_state() -> None:
    dashboard = build_migration_dashboard(
        scope=_tenant_scope(),
        principal=_principal(
            "tenant-admin-acme",
            roles=("tenant_user", "tenant_admin"),
            tenant_id=ACME_TENANT_ID,
        ),
    )
    inventory = build_decommission_inventory_dashboard()

    assert dashboard.title == "React-only browser UI"
    assert dashboard.summary.retained_fallback_count == 0
    assert dashboard.summary.blocked_count == 0
    assert inventory.summary.total_items == 0
    assert inventory.summary.template_count == 0
    assert "qa047-secret-value" not in dashboard.model_dump_json()


def _is_react_asset(path: Path) -> bool:
    try:
        path.relative_to(REACT_ASSET_ROOT)
    except ValueError:
        return False
    return True


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
