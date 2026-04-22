from __future__ import annotations

from pathlib import Path


def test_quality_workflow_files_exist() -> None:
    assert Path("scripts/check.sh").exists()
    assert Path(".github/workflows/ci.yml").exists()
