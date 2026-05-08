from __future__ import annotations

from pathlib import Path

SPEC_ROOT = Path("specs/058-live-only-ui-decommission-gate")


def test_live_only_ui_decommission_gate_docs_are_reviewer_ready() -> None:
    required = [
        SPEC_ROOT / ".env.qa058",
        SPEC_ROOT / "qa058.md",
        SPEC_ROOT / "qa058_ui.md",
        SPEC_ROOT / "qa058_user_guide.md",
        SPEC_ROOT / "pr_notes.md",
    ]

    for path in required:
        assert path.exists(), path
        assert path.read_text(encoding="utf-8").strip()


def test_live_only_ui_decommission_gate_docs_cover_validation_and_policy() -> None:
    combined = "\n".join(
        [
            (SPEC_ROOT / "qa058.md").read_text(encoding="utf-8"),
            (SPEC_ROOT / "qa058_ui.md").read_text(encoding="utf-8"),
            (SPEC_ROOT / "qa058_user_guide.md").read_text(encoding="utf-8"),
            (SPEC_ROOT / "pr_notes.md").read_text(encoding="utf-8"),
        ]
    )
    lowered = " ".join(combined.lower().split())

    for topic in (
        "/admin/app/migration/live-data-inventory.json",
        "qa058-live-only-source-scan",
        "qa058-live-data-ui-api-smoke.png",
        "multi_agent_platform_qa058",
        "seed_live_only_gate_qa058.py",
        "verify_live_only_gate_qa058.py",
        "tenant isolation",
        "redaction",
        "no shared update is required",
    ):
        assert topic.lower() in lowered

    guide_lines = (
        (SPEC_ROOT / "qa058_user_guide.md").read_text(encoding="utf-8").splitlines()
    )
    assert len(guide_lines) >= 160
