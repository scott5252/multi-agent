from __future__ import annotations

from pathlib import Path


def test_readme_has_admin_debugging_guidance_and_commands() -> None:
    text = Path("README.md").read_text()
    assert "Production Audit Debugging" in text
    assert "/admin/runs/{workflow_run_id}/timeline" in text
    assert "/admin/runs/debug-search" in text
    assert "uv run alembic upgrade head" in text
