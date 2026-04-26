from __future__ import annotations

from pathlib import Path


def test_admin_run_inspection_ui_contains_safe_controls() -> None:
    detail = Path(
        "src/multi_agent_platform/web_admin/templates/runs/detail.html"
    ).read_text()
    script = Path(
        "src/multi_agent_platform/web_admin/static/run_inspection.js"
    ).read_text()
    assert "data-audit-timeline" in detail
    assert "data-export-run" in detail
    assert "/admin/runs/" in script
    assert "raw" not in detail.lower()
