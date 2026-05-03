from __future__ import annotations

from pathlib import Path


def test_workflow_graph_execution_design_docs_are_present() -> None:
    root = Path("specs/020-workflow-graph-execution-parallel-sub-agent-runtime")
    required = [
        root / "spec.md",
        root / "plan.md",
        root / "research.md",
        root / "data-model.md",
        root / "quickstart.md",
        root / "contracts" / "workflow-graph-execution.md",
        root / "tasks.md",
    ]

    for path in required:
        assert path.exists(), path
        assert path.read_text(encoding="utf-8").strip()


def test_workflow_graph_execution_docs_cover_runtime_safety() -> None:
    root = Path("specs/020-workflow-graph-execution-parallel-sub-agent-runtime")
    combined = "\n".join(
        [
            (root / "spec.md").read_text(encoding="utf-8"),
            (root / "plan.md").read_text(encoding="utf-8"),
            (root / "research.md").read_text(encoding="utf-8"),
            (root / "data-model.md").read_text(encoding="utf-8"),
            (root / "quickstart.md").read_text(encoding="utf-8"),
            (root / "contracts" / "workflow-graph-execution.md").read_text(
                encoding="utf-8"
            ),
        ]
    ).lower()

    for topic in (
        "daily intelligence briefing",
        "parallel",
        "sub-agent",
        "join",
        "tenant isolation",
        "idempotent",
        "redaction",
        "manual resolution",
        "no raw secrets",
    ):
        assert topic in combined
