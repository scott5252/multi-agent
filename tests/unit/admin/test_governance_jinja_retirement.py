from __future__ import annotations

from pathlib import Path

GOVERNANCE_TEMPLATE_PATHS = (
    "src/multi_agent_platform/web_admin/templates/model_providers/index.html",
    "src/multi_agent_platform/web_admin/templates/model_providers/detail.html",
    "src/multi_agent_platform/web_admin/templates/model_providers/edit.html",
    "src/multi_agent_platform/web_admin/templates/model_providers/catalog.html",
    "src/multi_agent_platform/web_admin/templates/model_providers/test_results.html",
    "src/multi_agent_platform/web_admin/templates/prompts/index.html",
    "src/multi_agent_platform/web_admin/templates/prompts/detail.html",
    "src/multi_agent_platform/web_admin/templates/prompts/edit.html",
    "src/multi_agent_platform/web_admin/templates/prompts/history.html",
    "src/multi_agent_platform/web_admin/templates/prompts/preview.html",
    "src/multi_agent_platform/web_admin/templates/agent_profiles/index.html",
    "src/multi_agent_platform/web_admin/templates/agent_profiles/detail.html",
    "src/multi_agent_platform/web_admin/templates/agent_profiles/edit.html",
    "src/multi_agent_platform/web_admin/templates/agent_profiles/history.html",
    "src/multi_agent_platform/web_admin/templates/agent_profiles/resolve.html",
    "src/multi_agent_platform/web_admin/templates/model_skill_config/index.html",
    "src/multi_agent_platform/web_admin/templates/model_skill_config/history.html",
    (
        "src/multi_agent_platform/web_admin/templates/model_skill_config/"
        "run_provenance.html"
    ),
)

GOVERNANCE_BROWSER_ROUTER_PATHS = (
    "src/multi_agent_platform/api/routers/admin_model_providers.py",
    "src/multi_agent_platform/api/routers/admin_prompts.py",
    "src/multi_agent_platform/api/routers/admin_agent_profiles.py",
    "src/multi_agent_platform/api/routers/admin_model_skill_config.py",
)


def test_governance_owned_templates_are_deleted() -> None:
    for path in GOVERNANCE_TEMPLATE_PATHS:
        assert not Path(path).exists(), path


def test_governance_browser_routers_do_not_render_templates() -> None:
    for path in GOVERNANCE_BROWSER_ROUTER_PATHS:
        text = Path(path).read_text(encoding="utf-8")
        assert "TemplateResponse" not in text
        assert "workflow_ui_templates" not in text
