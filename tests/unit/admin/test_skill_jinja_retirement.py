from __future__ import annotations

from pathlib import Path

SKILL_TEMPLATE_PATHS = (
    "src/multi_agent_platform/web_admin/templates/skill_execution/diagnostics.html",
    "src/multi_agent_platform/web_admin/templates/skill_registry/available_versions.html",
    "src/multi_agent_platform/web_admin/templates/skill_registry/index.html",
    "src/multi_agent_platform/web_admin/templates/skill_registry/installation_configure.html",
    "src/multi_agent_platform/web_admin/templates/skill_registry/installation_detail.html",
    "src/multi_agent_platform/web_admin/templates/skill_registry/installation_list.html",
    "src/multi_agent_platform/web_admin/templates/skill_registry/package_candidate_form.html",
    "src/multi_agent_platform/web_admin/templates/skill_registry/package_create.html",
    "src/multi_agent_platform/web_admin/templates/skill_registry/package_detail.html",
    "src/multi_agent_platform/web_admin/templates/skill_registry/package_list.html",
    "src/multi_agent_platform/web_admin/templates/skill_registry/package_version_detail.html",
    "src/multi_agent_platform/web_admin/templates/skill_registry/tenant_grant_form.html",
    "src/multi_agent_platform/web_admin/templates/skill_registry/components/audit_timeline.html",
    "src/multi_agent_platform/web_admin/templates/skill_registry/components/form_errors.html",
    "src/multi_agent_platform/web_admin/templates/skill_registry/components/policy_eligibility.html",
    "src/multi_agent_platform/web_admin/templates/skill_registry/components/readiness_panel.html",
    "src/multi_agent_platform/web_admin/templates/skill_registry/components/smoke_test_history.html",
    "src/multi_agent_platform/web_admin/templates/skill_registry/components/stale_conflict.html",
    "src/multi_agent_platform/web_admin/templates/skill_registry/components/validation_findings.html",
)

SKILL_BROWSER_ROUTER_PATHS = (
    "src/multi_agent_platform/api/routers/admin_skill_registry.py",
    "src/multi_agent_platform/api/routers/admin_skill_execution.py",
)


def test_skill_owned_templates_are_deleted() -> None:
    for path in SKILL_TEMPLATE_PATHS:
        assert not Path(path).exists(), path


def test_skill_browser_routers_do_not_render_templates() -> None:
    for path in SKILL_BROWSER_ROUTER_PATHS:
        text = Path(path).read_text(encoding="utf-8")
        assert "TemplateResponse" not in text
        assert "workflow_ui_templates" not in text
        assert "skill_registry/" not in text
        assert "skill_execution/diagnostics.html" not in text
