from __future__ import annotations

from pathlib import Path


def test_workflow_graph_execution_contract_covers_executor_boundary() -> None:
    contract = Path(
        "specs/020-workflow-graph-execution-parallel-sub-agent-runtime/contracts/"
        "workflow-graph-execution.md"
    ).read_text(encoding="utf-8")

    for topic in (
        "Executor Input",
        "Role Node Executor Boundary",
        "Scheduler Contract",
        "Join Policy Contract",
        "Timeline Evidence Contract",
        "all_success",
        "quorum",
        "first_success",
        "manual_resolution",
        "graph_wave_scheduled",
    ):
        assert topic in contract
