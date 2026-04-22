from __future__ import annotations

from pathlib import Path


def test_local_bootstrap_scaffolding_exists() -> None:
    assert Path(".env.example").exists()
    assert Path("compose.yaml").exists()
    assert Path("docs/quickstart.md").exists()
