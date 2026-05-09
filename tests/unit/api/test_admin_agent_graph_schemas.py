from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from multi_agent_platform.api.schemas.admin_agent_graph import (
    AgentCommunicationGraph,
    AgentGraphAccessibility,
    AgentGraphNode,
    AgentGraphNodeCategory,
    AgentGraphProvenance,
    AgentGraphSource,
    AgentGraphState,
    safe_agent_graph_text,
)


def _minimal_graph(**updates: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "graph_id": "draft:graph",
        "source": "draft",
        "state": "ready",
        "partial": False,
        "provenance": {
            "source_type": "draft",
            "workflow_draft_id": "draft-id",
            "workflow_version_bundle_id": None,
            "workflow_lineage_id": "lineage-id",
            "workflow_key": "workflow",
            "revision": "1",
            "source_revision_id": "revision-id",
            "source_digest": "sha256",
            "scope_type": "tenant",
            "tenant_id": "tenant-id",
            "generated_at": datetime.now(UTC).isoformat(),
        },
        "nodes": [],
        "edges": [],
        "badges": [],
        "accessibility": {
            "summary": "Agent graph is ready with 0 nodes and 0 edges.",
            "node_summaries": [],
            "edge_summaries": [],
        },
    }
    payload.update(updates)
    return payload


def test_agent_graph_schema_accepts_safe_empty_graph() -> None:
    graph = AgentCommunicationGraph.model_validate(
        _minimal_graph(
            state="empty",
            accessibility={
                "summary": "Agent graph is empty with 0 nodes and 0 edges.",
                "node_summaries": [],
                "edge_summaries": [],
            },
        )
    )

    assert graph.state == AgentGraphState.EMPTY
    assert graph.provenance.source_type == AgentGraphSource.DRAFT
    assert graph.nodes == ()


@pytest.mark.parametrize(
    "unsafe_text",
    [
        "raw prompt should not render",
        "raw completion should not render",
        "provider payload should not render",
        "private channel message should not render",
        "memory contents should not render",
        "credential should not render",
        "authorization: bearer token",
        "raw tool payload should not render",
    ],
)
def test_agent_graph_schema_rejects_unsafe_renderable_text(
    unsafe_text: str,
) -> None:
    with pytest.raises(ValidationError):
        AgentGraphNode(
            node_id="node:unsafe",
            node_key="unsafe",
            category=AgentGraphNodeCategory.COORDINATOR_AGENT,
            label=unsafe_text,
            summary="Safe summary",
            status="ready",
            role_key=None,
            accessibility_label="Safe accessibility label.",
        )


def test_agent_graph_provenance_and_accessibility_are_strict() -> None:
    provenance = AgentGraphProvenance(
        source_type=AgentGraphSource.PUBLISHED_VERSION,
        workflow_draft_id="draft-id",
        workflow_version_bundle_id="version-id",
        workflow_lineage_id="lineage-id",
        workflow_key="workflow",
        revision="v1",
        source_revision_id="revision-id",
        source_digest="digest",
        scope_type="tenant",
        tenant_id="tenant-id",
        generated_at=datetime.now(UTC),
    )
    accessibility = AgentGraphAccessibility(
        summary="Agent graph is ready with one node.",
        node_summaries=("Coordinator agent node Review is ready.",),
        edge_summaries=(),
    )

    assert provenance.workflow_version_bundle_id == "version-id"
    assert accessibility.node_summaries[0].startswith("Coordinator")

    with pytest.raises(ValidationError):
        AgentCommunicationGraph.model_validate(
            _minimal_graph(extra_field="not allowed")
        )


def test_agent_graph_safe_text_allows_profile_ids_but_rejects_file_urls() -> None:
    assert safe_agent_graph_text("prompt-profile:coordinator-profile") == (
        "prompt-profile:coordinator-profile"
    )
    with pytest.raises(ValueError):
        safe_agent_graph_text("file:///Users/example/private.txt")
