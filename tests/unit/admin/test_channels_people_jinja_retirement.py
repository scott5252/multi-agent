from __future__ import annotations

from pathlib import Path

RETIRED_PATHS = (
    "src/multi_agent_platform/web_admin/templates/memberships/index.html",
    "src/multi_agent_platform/web_admin/templates/telegram/index.html",
    "src/multi_agent_platform/web_admin/templates/briefing_preferences/index.html",
)

CONVERTED_ROUTERS = (
    "src/multi_agent_platform/api/routers/admin_memberships.py",
    "src/multi_agent_platform/api/routers/admin_telegram.py",
    "src/multi_agent_platform/api/routers/admin_briefing_preferences.py",
)


def test_channels_people_jinja_templates_are_retired() -> None:
    for path in RETIRED_PATHS:
        assert not Path(path).exists(), path


def test_channels_people_routers_do_not_render_retired_templates() -> None:
    forbidden = (
        "TemplateResponse",
        "Jinja2Templates",
        "workflow_ui_templates",
        "memberships/index.html",
        "telegram/index.html",
        "briefing_preferences/index.html",
    )
    for path in CONVERTED_ROUTERS:
        text = Path(path).read_text()
        for marker in forbidden:
            assert marker not in text, f"{marker} still referenced in {path}"
