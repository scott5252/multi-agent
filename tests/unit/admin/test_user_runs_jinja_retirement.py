from __future__ import annotations

from pathlib import Path

RETIRED_RUN_PATHS = (
    "src/multi_agent_platform/web_admin/templates/runs/index.html",
    "src/multi_agent_platform/web_admin/templates/runs/detail.html",
    "src/multi_agent_platform/web_admin/templates/runs/replay.html",
    "src/multi_agent_platform/web_admin/static/run_inspection.js",
)

USER_RUN_ROUTERS = (
    "src/multi_agent_platform/api/routers/web_run_ui.py",
    "src/multi_agent_platform/api/routers/channel_runs.py",
)


def test_user_run_jinja_templates_are_retired() -> None:
    for path in RETIRED_RUN_PATHS:
        assert not Path(path).exists(), path


def test_user_run_routes_do_not_render_retired_templates() -> None:
    forbidden = (
        "TemplateResponse",
        "Jinja2Templates",
        "workflow_ui_templates",
        "runs/index.html",
        "runs/detail.html",
        "runs/replay.html",
        "run_inspection.js",
    )
    for path in USER_RUN_ROUTERS:
        text = Path(path).read_text(encoding="utf-8")
        for marker in forbidden:
            assert marker not in text, f"{marker} still referenced in {path}"
