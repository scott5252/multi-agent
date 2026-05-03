from __future__ import annotations

from pathlib import Path


def test_operations_console_docs_are_reviewer_ready() -> None:
    root = Path("specs/019-operations-console-logs-performance")
    required = [
        root / ".env.qa019",
        root / "qa019.md",
        root / "qa019_ui.md",
        root / "qa019_user_guide.md",
        root / "pr-review-notes.md",
        root / "testing-instructions.md",
    ]

    for path in required:
        assert path.exists(), path
        assert path.read_text(encoding="utf-8").strip()


def test_operations_console_docs_cover_security_and_validation() -> None:
    combined = "\n".join(
        [
            Path("README.md").read_text(encoding="utf-8"),
            Path("docs/quickstart.md").read_text(encoding="utf-8"),
            Path("specs/019-operations-console-logs-performance/qa019.md").read_text(
                encoding="utf-8"
            ),
            Path("specs/019-operations-console-logs-performance/qa019_ui.md").read_text(
                encoding="utf-8"
            ),
            Path(
                "specs/019-operations-console-logs-performance/qa019_user_guide.md"
            ).read_text(encoding="utf-8"),
            Path(
                "specs/019-operations-console-logs-performance/testing-instructions.md"
            ).read_text(encoding="utf-8"),
            Path(
                "specs/019-operations-console-logs-performance/pr-review-notes.md"
            ).read_text(encoding="utf-8"),
        ]
    )
    lowered = combined.lower()

    for topic in (
        "/admin/operations",
        "/admin/operations/api",
        "operations console",
        "operational logs",
        "csv export",
        "platform admin",
        "auditor",
        "tenant isolation",
        "redaction",
        "multi_agent_platform_qa019",
        "uv run pytest --cov=src/multi_agent_platform "
        "--cov-report=term-missing --cov-fail-under=90",
    ):
        assert topic.lower() in lowered

    assert (
        len(
            Path("specs/019-operations-console-logs-performance/qa019_user_guide.md")
            .read_text(encoding="utf-8")
            .splitlines()
        )
        >= 160
    )
