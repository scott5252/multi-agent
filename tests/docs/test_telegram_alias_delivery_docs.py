from __future__ import annotations

from pathlib import Path

SPEC_ROOT = Path("specs/022-telegram-natural-language-trigger-delivery-persistence")


def test_telegram_alias_delivery_docs_are_present() -> None:
    required = [
        SPEC_ROOT / "spec.md",
        SPEC_ROOT / "plan.md",
        SPEC_ROOT / "research.md",
        SPEC_ROOT / "data-model.md",
        SPEC_ROOT / "quickstart.md",
        SPEC_ROOT / "contracts" / "telegram-alias-delivery.md",
        SPEC_ROOT / "testing-instructions.md",
        SPEC_ROOT / "pr-review-notes.md",
        SPEC_ROOT / "qa022.md",
        SPEC_ROOT / "qa022_ui.md",
        SPEC_ROOT / "qa022_user_guide.md",
    ]

    for path in required:
        assert path.exists(), path
        assert path.read_text(encoding="utf-8").strip()


def test_telegram_alias_delivery_docs_cover_operator_workflow() -> None:
    combined = "\n".join(
        [
            Path("README.md").read_text(encoding="utf-8"),
            Path("docs/quickstart.md").read_text(encoding="utf-8"),
            (SPEC_ROOT / "qa022_user_guide.md").read_text(encoding="utf-8"),
            (SPEC_ROOT / "testing-instructions.md").read_text(encoding="utf-8"),
        ]
    ).lower()

    for topic in (
        "/admin/telegram",
        "telegram command aliases",
        "morning briefing",
        "linked",
        "delivery attempt",
        "duplicate",
        "redaction",
    ):
        assert topic in combined


def test_telegram_alias_user_guide_is_non_developer_ready() -> None:
    guide = (SPEC_ROOT / "qa022_user_guide.md").read_text(encoding="utf-8")

    assert guide.startswith("# QA022 User Guide")
    assert "## Expected Results" in guide
    assert "## Step-by-Step Manual QA" in guide
    assert "## Troubleshooting" in guide
    assert "Telegram Command Aliases" in guide
    assert len(guide.splitlines()) >= 160
