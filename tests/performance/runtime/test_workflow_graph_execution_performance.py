from __future__ import annotations

from time import perf_counter

from multi_agent_platform.runtime.orchestration.graph_execution import (
    build_graph_execution_plan,
)


def test_graph_plan_builds_fifty_nodes_within_budget() -> None:
    nodes = [
        {
            "node_key": f"node-{index}",
            "node_type": "role",
            "display_name": f"Node {index}",
            "role_key": f"role-{index}",
        }
        for index in range(50)
    ]
    nodes.append(
        {
            "node_key": "terminal",
            "node_type": "terminal",
            "display_name": "Terminal",
        }
    )
    document = {
        "workflow_key": "performance-graph",
        "workflow_kind": "main_workflow",
        "entry_node_key": "node-0",
        "roles": [
            {
                "role_key": f"role-{index}",
                "role_kind": "agent",
                "graph_node_keys": [f"node-{index}"],
            }
            for index in range(50)
        ],
        "nodes": nodes,
        "edges": [
            {
                "edge_key": f"edge-{index}",
                "source_node_key": f"node-{index}",
                "target_node_key": f"node-{index + 1}" if index < 49 else "terminal",
            }
            for index in range(50)
        ],
    }

    started = perf_counter()
    plan = build_graph_execution_plan(document)
    elapsed = perf_counter() - started

    assert len(plan.nodes_by_key) == 51
    assert elapsed < 0.25
