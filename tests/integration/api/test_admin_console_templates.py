from __future__ import annotations

from pathlib import Path


def test_admin_shell_templates_provide_accessible_landmarks() -> None:
    base = Path(
        "src/multi_agent_platform/web_admin/templates/admin_shell/base.html"
    ).read_text()
    navigation = Path(
        "src/multi_agent_platform/web_admin/templates/admin_shell/navigation.html"
    ).read_text()
    breadcrumbs = Path(
        "src/multi_agent_platform/web_admin/templates/admin_shell/breadcrumbs.html"
    ).read_text()

    assert "Skip to content" in base
    assert 'id="admin-main-content"' in base
    assert 'aria-label="Admin"' in navigation
    assert "aria-current" in navigation
    assert "aria-current" in breadcrumbs
