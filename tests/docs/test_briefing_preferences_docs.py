from __future__ import annotations

from pathlib import Path

FEATURE_DIR = Path("specs/023-user-briefing-preferences-and-context")


def test_briefing_preferences_spec_docs_exist() -> None:
    for path in (
        "spec.md",
        "plan.md",
        "research.md",
        "data-model.md",
        "quickstart.md",
        "contracts/briefing-preferences.md",
        "tasks.md",
    ):
        assert (FEATURE_DIR / path).is_file()


def test_briefing_preferences_docs_capture_safe_boundaries() -> None:
    combined = "\n".join(
        (FEATURE_DIR / path).read_text(encoding="utf-8")
        for path in ("spec.md", "plan.md", "contracts/briefing-preferences.md")
    )

    assert "safe summaries" in combined
    assert "raw credentials" in combined
    assert "tenant" in combined
