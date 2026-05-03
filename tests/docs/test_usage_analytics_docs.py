from __future__ import annotations

from pathlib import Path


def test_usage_analytics_docs_are_reviewer_ready() -> None:
    root = Path("specs/016-token-usage-cost-analytics")
    required = [
        root / ".env.qa016",
        root / "qa016.md",
        root / "qa016_ui.md",
        root / "qa016_user_guide.md",
        root / "pr-review-notes.md",
        root / "testing-instructions.md",
    ]

    for path in required:
        assert path.exists(), path
        assert path.read_text(encoding="utf-8").strip()


def test_usage_analytics_docs_cover_security_and_validation() -> None:
    combined = "\n".join(
        [
            Path("README.md").read_text(encoding="utf-8"),
            Path("docs/quickstart.md").read_text(encoding="utf-8"),
            Path("specs/016-token-usage-cost-analytics/qa016.md").read_text(
                encoding="utf-8"
            ),
            Path("specs/016-token-usage-cost-analytics/qa016_ui.md").read_text(
                encoding="utf-8"
            ),
            Path("specs/016-token-usage-cost-analytics/qa016_user_guide.md").read_text(
                encoding="utf-8"
            ),
            Path(
                "specs/016-token-usage-cost-analytics/testing-instructions.md"
            ).read_text(encoding="utf-8"),
            Path("specs/016-token-usage-cost-analytics/pr-review-notes.md").read_text(
                encoding="utf-8"
            ),
        ]
    )
    lowered = combined.lower()

    for topic in (
        "/admin/usage",
        "/admin/usage/api",
        "modelgateway",
        "token usage",
        "csv export",
        "tenant isolation",
        "redaction",
        "multi_agent_platform_qa016",
        "uv run pytest --cov=src/multi_agent_platform "
        "--cov-report=term-missing --cov-fail-under=90",
    ):
        assert topic.lower() in lowered

    assert (
        len(
            Path("specs/016-token-usage-cost-analytics/qa016_user_guide.md")
            .read_text(encoding="utf-8")
            .splitlines()
        )
        >= 160
    )
