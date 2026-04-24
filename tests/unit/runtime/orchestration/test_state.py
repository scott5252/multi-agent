from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.runtime.orchestration.state import GraphRuntimeState


def test_graph_runtime_state_builds_langgraph_thread_config() -> None:
    run_id = uuid4()
    state = GraphRuntimeState(
        workflow_run_id=run_id,
        bundle_digest="digest",
        input={"prompt": "hello"},
    )

    assert state.thread_config() == {"configurable": {"thread_id": str(run_id)}}
