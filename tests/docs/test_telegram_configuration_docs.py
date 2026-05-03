from __future__ import annotations

from pathlib import Path


def test_telegram_configuration_docs_are_reviewer_ready() -> None:
    root = Path("specs/017-telegram-configuration-console")
    required = [
        root / ".env.qa017",
        root / "qa017.md",
        root / "qa017_ui.md",
        root / "qa017_user_guide.md",
        root / "pr-review-notes.md",
        root / "testing-instructions.md",
    ]

    for path in required:
        assert path.exists(), path
        assert path.read_text(encoding="utf-8").strip()


def test_telegram_configuration_docs_cover_security_and_validation() -> None:
    combined = "\n".join(
        [
            Path("README.md").read_text(encoding="utf-8"),
            Path("docs/quickstart.md").read_text(encoding="utf-8"),
            Path("specs/017-telegram-configuration-console/qa017.md").read_text(
                encoding="utf-8"
            ),
            Path("specs/017-telegram-configuration-console/qa017_ui.md").read_text(
                encoding="utf-8"
            ),
            Path(
                "specs/017-telegram-configuration-console/qa017_user_guide.md"
            ).read_text(encoding="utf-8"),
            Path(
                "specs/017-telegram-configuration-console/testing-instructions.md"
            ).read_text(encoding="utf-8"),
            Path(
                "specs/017-telegram-configuration-console/pr-review-notes.md"
            ).read_text(encoding="utf-8"),
        ]
    )
    lowered = combined.lower()

    for topic in (
        "/admin/telegram",
        "/admin/telegram/api",
        "telegram configuration",
        "link token",
        "tenant isolation",
        "redaction",
        "webhook validation",
        "multi_agent_platform_qa017",
        "uv run pytest --cov=src/multi_agent_platform "
        "--cov-report=term-missing --cov-fail-under=90",
    ):
        assert topic.lower() in lowered

    assert (
        len(
            Path("specs/017-telegram-configuration-console/qa017_user_guide.md")
            .read_text(encoding="utf-8")
            .splitlines()
        )
        >= 160
    )
