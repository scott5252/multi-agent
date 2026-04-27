from __future__ import annotations

from pathlib import Path


def test_readme_mentions_reliability_operator_guidance() -> None:
    text = Path("README.md").read_text()
    assert "Reliability" in text
