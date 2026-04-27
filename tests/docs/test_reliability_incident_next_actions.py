from __future__ import annotations

from pathlib import Path


def test_incident_guidance_lists_representative_next_actions() -> None:
    text = Path("docs/reliability-scale-hardening.md").read_text()
    assert text.count("- ") >= 10
