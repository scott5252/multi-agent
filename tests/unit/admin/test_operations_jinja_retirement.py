from __future__ import annotations

from pathlib import Path

RETIRED_TEMPLATES = (
    "src/multi_agent_platform/web_admin/templates/operations/index.html",
    "src/multi_agent_platform/web_admin/templates/reliability/index.html",
    "src/multi_agent_platform/web_admin/templates/reliability/breakers.html",
    "src/multi_agent_platform/web_admin/templates/reliability/dead_letters.html",
    "src/multi_agent_platform/web_admin/templates/runs/index.html",
    "src/multi_agent_platform/web_admin/templates/runs/detail.html",
    "src/multi_agent_platform/web_admin/templates/runs/replay.html",
    "src/multi_agent_platform/web_admin/templates/usage/index.html",
    "src/multi_agent_platform/web_admin/templates/usage/export_detail.html",
    "src/multi_agent_platform/web_admin/static/run_inspection.js",
)

CONVERTED_ROUTERS = (
    "src/multi_agent_platform/api/routers/admin_operations.py",
    "src/multi_agent_platform/api/ui/reliability_controls.py",
    "src/multi_agent_platform/api/routers/admin_run_inspection.py",
    "src/multi_agent_platform/api/routers/web_run_ui.py",
    "src/multi_agent_platform/api/routers/admin_usage.py",
)


def test_operations_reliability_runs_usage_templates_are_retired() -> None:
    for template in RETIRED_TEMPLATES:
        assert not Path(template).exists(), template


def test_converted_routers_do_not_render_retired_templates() -> None:
    forbidden = (
        "TemplateResponse",
        "Jinja2Templates",
        "operations/index.html",
        "reliability/index.html",
        "reliability/breakers.html",
        "reliability/dead_letters.html",
        "runs/index.html",
        "runs/detail.html",
        "runs/replay.html",
        "usage/index.html",
        "usage/export_detail.html",
        "run_inspection.js",
    )
    for router in CONVERTED_ROUTERS:
        text = Path(router).read_text(encoding="utf-8")
        for marker in forbidden:
            assert marker not in text, f"{router} still references {marker}"
