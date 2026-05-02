from __future__ import annotations

from pathlib import Path


def test_agent_test_bench_docs_are_reviewer_ready() -> None:
    root = Path("specs/015-agent-workflow-test-bench")
    required = [
        root / ".env.qa015",
        root / "qa015.md",
        root / "qa015_ui.md",
        root / "qa015_user_guide.md",
        root / "pr-review-notes.md",
        root / "testing-instructions.md",
    ]

    for path in required:
        assert path.exists(), path
        assert path.read_text(encoding="utf-8").strip()


def test_agent_test_bench_docs_cover_safety_and_validation() -> None:
    combined = "\n".join(
        [
            Path("README.md").read_text(encoding="utf-8"),
            Path("docs/quickstart.md").read_text(encoding="utf-8"),
            Path("specs/015-agent-workflow-test-bench/qa015.md").read_text(
                encoding="utf-8"
            ),
            Path("specs/015-agent-workflow-test-bench/qa015_ui.md").read_text(
                encoding="utf-8"
            ),
            Path("specs/015-agent-workflow-test-bench/qa015_user_guide.md").read_text(
                encoding="utf-8"
            ),
            Path(
                "specs/015-agent-workflow-test-bench/testing-instructions.md"
            ).read_text(encoding="utf-8"),
            Path("specs/015-agent-workflow-test-bench/pr-review-notes.md").read_text(
                encoding="utf-8"
            ),
        ]
    )
    lowered = combined.lower()

    for topic in (
        "/admin/agent-tests/ui",
        "/admin/agent-tests",
        "mock_model",
        "real_model_side_effects_disabled",
        "approved real probe",
        "publish gate",
        "tenant isolation",
        "redaction",
        "multi_agent_platform_qa015",
        "uv run pytest --cov=src/multi_agent_platform "
        "--cov-report=term-missing --cov-fail-under=90",
    ):
        assert topic.lower() in lowered
