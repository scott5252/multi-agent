from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest

from multi_agent_platform.runtime.orchestration.graph_execution import (
    BranchResult,
    GraphJoinPolicy,
    GraphValidationError,
    JoinDecisionType,
    _extract_workflow_document,
    build_graph_execution_plan,
    evaluate_join_policy,
)


def simple_graph_document() -> dict[str, object]:
    return {
        "workflow_key": "simple-graph",
        "workflow_kind": "main_workflow",
        "entry_node_key": "entry",
        "roles": [
            {
                "role_key": "entry-role",
                "role_kind": "agent",
                "profile_reference_key": "profile-entry",
                "graph_node_keys": ["entry"],
            },
            {
                "role_key": "writer-role",
                "role_kind": "agent",
                "profile_reference_key": "profile-writer",
                "graph_node_keys": ["writer"],
            },
        ],
        "contracts": [
            {
                "contract_key": "handoff",
                "semantic_version": "1.0.0",
                "json_schema": {"type": "object"},
            }
        ],
        "nodes": [
            {
                "node_key": "entry",
                "node_type": "role",
                "display_name": "Entry",
                "role_key": "entry-role",
            },
            {
                "node_key": "writer",
                "node_type": "role",
                "display_name": "Writer",
                "role_key": "writer-role",
            },
            {
                "node_key": "terminal",
                "node_type": "terminal",
                "display_name": "Done",
            },
        ],
        "edges": [
            {
                "edge_key": "entry-writer",
                "source_node_key": "entry",
                "target_node_key": "writer",
                "contract_key": "handoff",
            },
            {
                "edge_key": "writer-terminal",
                "source_node_key": "writer",
                "target_node_key": "terminal",
                "contract_key": "handoff",
            },
        ],
    }


def daily_briefing_graph_document() -> dict[str, object]:
    roles = [
        ("orchestrator", "agent", "orchestrator-intake"),
        ("calendar-scout", "subagent", "calendar-scout-node"),
        ("email-triage", "subagent", "email-triage-node"),
        ("news-context", "subagent", "news-context-node"),
        ("logistics-agent", "subagent", "logistics-node"),
        ("focus-recommender", "subagent", "focus-node"),
        ("briefing-synthesizer", "agent", "synthesis-node"),
    ]
    return {
        "workflow_key": "daily-intelligence-briefing",
        "workflow_kind": "main_workflow",
        "entry_node_key": "orchestrator-intake",
        "roles": [
            {
                "role_key": role_key,
                "role_kind": role_kind,
                "profile_reference_key": f"profile-{role_key}",
                "skill_installation_keys": [f"{role_key}-skill"]
                if role_kind == "subagent"
                else [],
                "graph_node_keys": [node_key],
            }
            for role_key, role_kind, node_key in roles
        ],
        "contracts": [
            {
                "contract_key": "briefing-request",
                "semantic_version": "1.0.0",
                "json_schema": {"type": "object"},
            }
        ],
        "nodes": [
            {
                "node_key": "orchestrator-intake",
                "node_type": "role",
                "display_name": "Orchestrator",
                "role_key": "orchestrator",
            },
            {
                "node_key": "calendar-scout-node",
                "node_type": "role",
                "display_name": "Calendar Scout",
                "role_key": "calendar-scout",
            },
            {
                "node_key": "email-triage-node",
                "node_type": "role",
                "display_name": "Email Triage",
                "role_key": "email-triage",
            },
            {
                "node_key": "news-context-node",
                "node_type": "role",
                "display_name": "News Context",
                "role_key": "news-context",
            },
            {
                "node_key": "logistics-node",
                "node_type": "role",
                "display_name": "Logistics",
                "role_key": "logistics-agent",
            },
            {
                "node_key": "scout-join",
                "node_type": "join",
                "display_name": "Scout Join",
                "join_policy_key": "all-scouts-return",
            },
            {
                "node_key": "focus-node",
                "node_type": "role",
                "display_name": "Focus",
                "role_key": "focus-recommender",
            },
            {
                "node_key": "synthesis-node",
                "node_type": "role",
                "display_name": "Synthesis",
                "role_key": "briefing-synthesizer",
            },
            {
                "node_key": "terminal",
                "node_type": "terminal",
                "display_name": "Complete",
            },
        ],
        "edges": [
            *[
                {
                    "edge_key": f"orchestrator-to-{target}",
                    "source_node_key": "orchestrator-intake",
                    "target_node_key": target,
                    "contract_key": "briefing-request",
                }
                for target in (
                    "calendar-scout-node",
                    "email-triage-node",
                    "news-context-node",
                    "logistics-node",
                )
            ],
            *[
                {
                    "edge_key": f"{source}-to-join",
                    "source_node_key": source,
                    "target_node_key": "scout-join",
                    "contract_key": "briefing-request",
                }
                for source in (
                    "calendar-scout-node",
                    "email-triage-node",
                    "news-context-node",
                    "logistics-node",
                )
            ],
            {
                "edge_key": "join-to-focus",
                "source_node_key": "scout-join",
                "target_node_key": "focus-node",
                "contract_key": "briefing-request",
            },
            {
                "edge_key": "focus-to-synthesis",
                "source_node_key": "focus-node",
                "target_node_key": "synthesis-node",
                "contract_key": "briefing-request",
            },
            {
                "edge_key": "synthesis-to-terminal",
                "source_node_key": "synthesis-node",
                "target_node_key": "terminal",
                "contract_key": "briefing-request",
            },
        ],
        "join_policies": [
            {
                "join_policy_key": "all-scouts-return",
                "strategy": "all_success",
                "inbound_edge_keys": [
                    "calendar-scout-node-to-join",
                    "email-triage-node-to-join",
                    "news-context-node-to-join",
                    "logistics-node-to-join",
                ],
                "failure_behavior": "manual_resolution",
            }
        ],
    }


def test_no_020_migration_is_required() -> None:
    assert not list(Path("alembic/versions").glob("*020*graph*execution*.py"))


def test_build_graph_execution_plan_validates_simple_graph() -> None:
    plan = build_graph_execution_plan(simple_graph_document())

    assert plan.entry_node_key == "entry"
    assert plan.terminal_node_keys == ("terminal",)
    assert plan.outbound_edges_by_source["entry"][0].target_node_key == "writer"


@pytest.mark.asyncio
async def test_extract_workflow_document_falls_back_to_source_revision() -> None:
    revision_id = uuid4()

    class Repository:
        async def get_workflow_draft_revision(self, *, workflow_draft_revision_id):
            assert workflow_draft_revision_id == revision_id
            return SimpleNamespace(authoring_document_json=simple_graph_document())

    document = await _extract_workflow_document(
        Repository(),
        {},
        SimpleNamespace(summary_json={}, published_from_revision_id=revision_id),
    )

    assert document["workflow_key"] == "simple-graph"


def test_build_graph_execution_plan_rejects_cycles() -> None:
    document = simple_graph_document()
    document["edges"] = [
        *document["edges"],  # type: ignore[list-item]
        {
            "edge_key": "terminal-entry",
            "source_node_key": "terminal",
            "target_node_key": "entry",
        },
    ]

    with pytest.raises(GraphValidationError, match="acyclic"):
        build_graph_execution_plan(document)


def test_daily_briefing_plan_contains_four_parallel_scouts() -> None:
    plan = build_graph_execution_plan(daily_briefing_graph_document())

    scout_targets = {
        edge.target_node_key
        for edge in plan.outbound_edges_by_source["orchestrator-intake"]
    }
    assert scout_targets == {
        "calendar-scout-node",
        "email-triage-node",
        "news-context-node",
        "logistics-node",
    }


def test_join_policy_all_success_and_manual_resolution() -> None:
    policy = GraphJoinPolicy(
        join_policy_key="join",
        strategy="all_success",
        failure_behavior="manual_resolution",
    )

    proceed = evaluate_join_policy(
        policy,
        [
            BranchResult(node_key="a", status="succeeded"),
            BranchResult(node_key="b", status="succeeded"),
        ],
    )
    pause = evaluate_join_policy(
        policy,
        [
            BranchResult(node_key="a", status="succeeded"),
            BranchResult(node_key="b", status="failed"),
        ],
    )

    assert proceed.decision is JoinDecisionType.PROCEED
    assert pause.decision is JoinDecisionType.PAUSE_MANUAL_RESOLUTION


def test_join_policy_quorum_and_first_success() -> None:
    quorum = evaluate_join_policy(
        GraphJoinPolicy(join_policy_key="q", strategy="quorum", quorum_count=2),
        [
            BranchResult(node_key="a", status="succeeded"),
            BranchResult(node_key="b", status="succeeded"),
            BranchResult(node_key="c", status="failed"),
        ],
    )
    first = evaluate_join_policy(
        GraphJoinPolicy(join_policy_key="f", strategy="first_success"),
        [
            BranchResult(node_key="a", status="failed"),
            BranchResult(node_key="b", status="succeeded"),
        ],
    )

    assert quorum.decision is JoinDecisionType.PROCEED
    assert first.decision is JoinDecisionType.PROCEED
    assert first.winning_branch_key == "b"
