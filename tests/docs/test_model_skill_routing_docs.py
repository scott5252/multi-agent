from __future__ import annotations

from pathlib import Path


def test_model_skill_routing_docs_cover_review_topics() -> None:
    docs = "\n".join(
        [
            Path("README.md").read_text(),
            Path("docs/model-skill-routing.md").read_text(),
            Path("specs/007-model-skill-routing/testing-instructions.md").read_text(),
            Path("specs/007-model-skill-routing/pr-review-notes.md").read_text(),
        ]
    ).lower()

    for topic in (
        "precedence",
        "skill",
        "tool",
        "secret",
        "outbound",
        "credential",
        "provenance",
        "uv run pytest --cov=src/multi_agent_platform "
        "--cov-report=term-missing --cov-fail-under=90",
        "elapsed time",
        "aggregate pass/fail",
    ):
        assert topic in docs
