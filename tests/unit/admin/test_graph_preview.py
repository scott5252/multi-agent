from __future__ import annotations

from multi_agent_platform.admin.workflow_registry.graph_preview import (
    build_graph_preview,
    validate_graph_policy,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    ApprovalGateDefinition,
    JoinPolicyDefinition,
    WorkflowEdgeDefinition,
    WorkflowNodeDefinition,
    WorkflowNodeType,
)


def test_graph_preview_uses_stable_element_ids(sample_workflow_document) -> None:
    preview = build_graph_preview(sample_workflow_document)

    assert preview.nodes[0].id == "node:triage-node"
    assert preview.summary.entry_node_id == "node:triage-node"
    assert preview.field_to_graph["nodes[0]"] == "node:triage-node"


def test_graph_policy_blocks_disconnected_nodes_and_unbounded_cycles(
    sample_workflow_document,
) -> None:
    document = sample_workflow_document.model_copy(deep=True)
    document.nodes.append(
        WorkflowNodeDefinition(
            node_key="review",
            node_type="role",
            display_name="Review",
            role_key="triage-role",
        )
    )
    document.edges.append(
        WorkflowEdgeDefinition(
            edge_key="review-loop",
            source_node_key="review",
            target_node_key="review",
        )
    )

    findings = validate_graph_policy(document)

    assert any(finding["code"] == "graph.node.disconnected" for finding in findings)
    assert any(finding["code"] == "graph.self_cycle.unbounded" for finding in findings)


def test_graph_preview_maps_badges_edges_and_allowed_loops(
    sample_workflow_document,
) -> None:
    document = sample_workflow_document.model_copy(deep=True)
    document.nodes[0].node_type = WorkflowNodeType.TERMINAL
    document.edges.append(
        WorkflowEdgeDefinition(
            edge_key="bounded",
            source_node_key="triage-node",
            target_node_key="triage-node",
            loop_type="retry",
            max_attempts=2,
            contract_key="triage-result",
        )
    )

    preview = build_graph_preview(
        document,
        findings=[
            {
                "graph_element_id": "edge:bounded",
                "code": "graph.test",
                "severity": "blocking",
                "message": "Graph issue",
                "blocking": True,
            }
        ],
    )
    findings = validate_graph_policy(document)

    assert preview.edges[0].id == "edge:bounded"
    assert preview.edges[0].badges[0].code == "graph.test"
    assert preview.summary.terminal_node_ids == ["node:triage-node"]
    assert findings == []


def test_graph_policy_flags_invalid_loops_join_policy_and_cycles(
    sample_workflow_document,
) -> None:
    document = sample_workflow_document.model_copy(deep=True)
    document.nodes.extend(
        [
            WorkflowNodeDefinition(
                node_key="review",
                node_type=WorkflowNodeType.ROLE,
                display_name="Review",
                role_key="triage-role",
            ),
            WorkflowNodeDefinition(
                node_key="merge",
                node_type=WorkflowNodeType.JOIN,
                display_name="Merge",
            ),
            WorkflowNodeDefinition(
                node_key="terminal",
                node_type=WorkflowNodeType.TERMINAL,
                display_name="Done",
            ),
        ]
    )
    document.edges.extend(
        [
            WorkflowEdgeDefinition(
                edge_key="to-review",
                source_node_key="triage-node",
                target_node_key="review",
                loop_type="manual",
            ),
            WorkflowEdgeDefinition(
                edge_key="review-cycle",
                source_node_key="review",
                target_node_key="triage-node",
            ),
        ]
    )

    findings = validate_graph_policy(document)

    assert {finding["code"] for finding in findings} >= {
        "graph.loop_type.invalid",
        "graph.cycle.unbounded",
        "graph.join.missing_policy",
        "graph.node.missing_outgoing",
    }


def test_graph_preview_summarizes_join_and_approval_loops(
    sample_workflow_document,
) -> None:
    document = sample_workflow_document.model_copy(
        deep=True,
        update={
            "join_policies": [
                JoinPolicyDefinition(join_policy_key="all", strategy="all")
            ],
            "approval_gates": [
                ApprovalGateDefinition(
                    approval_gate_key="manager",
                    display_name="Manager",
                    approver_scope="tenant",
                    resume_behavior="resume_origin",
                )
            ],
        },
    )

    preview = build_graph_preview(document)

    assert preview.summary.join_summaries == ["all:all"]
    assert preview.summary.approval_loop_summaries == ["manager:resume_origin"]
