from __future__ import annotations

from typing import cast
from uuid import uuid4

import pytest

from multi_agent_platform.api.schemas.admin_agent_graph import (
    AgentGraphReferenceType,
    AgentGraphSource,
    AgentGraphState,
)
from multi_agent_platform.db.models.runtime_orchestration import (
    RuntimeInteractionEvidenceRecord,
    RuntimeInteractionKind,
    RuntimeInteractionStatus,
    RuntimeRunStatus,
    RuntimeStepStatus,
)
from multi_agent_platform.db.models.workflow_registry import (
    WorkflowDraftRevision,
    WorkflowVersionBundle,
    WorkflowVersionStatus,
)
from multi_agent_platform.db.repositories.runtime_orchestration import (
    RuntimeOrchestrationRepository,
)
from multi_agent_platform.operations.runtime_agent_graph import (
    _interaction_status,
    _payload_node_key,
    _reference_status,
    _safe_ref_summary,
    _severity_for_status,
    _step_status,
    build_runtime_agent_graph,
)
from tests.fixtures.runtime_agent_graph import (
    runtime_graph_document_dict,
    runtime_graph_records,
)


@pytest.mark.asyncio
async def test_runtime_agent_graph_projects_completed_run_evidence() -> None:
    workflow_run_id, tenant_id, repository = runtime_graph_records(
        run_status=RuntimeRunStatus.SUCCEEDED,
        step_statuses={
            "specialist": RuntimeStepStatus.SUCCEEDED,
            "approval": RuntimeStepStatus.SUCCEEDED,
            "done": RuntimeStepStatus.SUCCEEDED,
        },
        include_interactions=True,
    )

    graph = await build_runtime_agent_graph(
        repository=cast(RuntimeOrchestrationRepository, repository),
        workflow_run_id=workflow_run_id,
        tenant_id=tenant_id,
    )

    assert graph is not None
    assert graph.source == AgentGraphSource.RUNTIME_RUN
    assert graph.state == AgentGraphState.READY
    assert graph.provenance.workflow_run_id == str(workflow_run_id)
    assert graph.provenance.run_status == "completed"
    assert graph.provenance.evidence_counts["run_steps"] == 4
    assert graph.provenance.evidence_counts["interaction_evidence"] == 1
    nodes = {node.node_key: node for node in graph.nodes}
    assert nodes["coordinator"].status == "succeeded"
    assert any(
        reference.reference_type == AgentGraphReferenceType.RUN_STEP
        for reference in nodes["coordinator"].references
    )
    assert any(edge.status == "succeeded" for edge in graph.edges)
    replay_edge = next(
        edge for edge in graph.edges if edge.edge_key == "edge-coordinator-specialist"
    )
    assert any(
        reference.reference_type == AgentGraphReferenceType.INTERACTION_EVIDENCE
        for reference in replay_edge.references
    )
    assert "raw prompt" not in graph.model_dump_json().lower()


@pytest.mark.asyncio
async def test_runtime_agent_graph_projects_failed_and_retrying_branches() -> None:
    workflow_run_id, tenant_id, repository = runtime_graph_records(
        run_status=RuntimeRunStatus.RECOVERABLE_FAILED,
        step_statuses={
            "specialist": RuntimeStepStatus.RETRY_SCHEDULED,
            "approval": RuntimeStepStatus.PENDING,
        },
    )

    graph = await build_runtime_agent_graph(
        repository=cast(RuntimeOrchestrationRepository, repository),
        workflow_run_id=workflow_run_id,
        tenant_id=tenant_id,
    )

    assert graph is not None
    nodes = {node.node_key: node for node in graph.nodes}
    assert nodes["specialist"].status == "retry_scheduled"
    assert "safe issue" in nodes["specialist"].summary
    edge = next(
        edge for edge in graph.edges if edge.edge_key == "edge-specialist-approval"
    )
    assert edge.status == "retry_scheduled"


@pytest.mark.asyncio
async def test_runtime_agent_graph_projects_paused_waiting_evidence() -> None:
    workflow_run_id, tenant_id, repository = runtime_graph_records(
        run_status=RuntimeRunStatus.PAUSED,
        step_statuses={
            "specialist": RuntimeStepStatus.SUCCEEDED,
            "approval": RuntimeStepStatus.PAUSED,
        },
    )

    graph = await build_runtime_agent_graph(
        repository=cast(RuntimeOrchestrationRepository, repository),
        workflow_run_id=workflow_run_id,
        tenant_id=tenant_id,
    )

    assert graph is not None
    nodes = {node.node_key: node for node in graph.nodes}
    assert nodes["approval"].status == "paused"
    assert any(badge.source == "runtime" for badge in nodes["approval"].badges)
    assert graph.provenance.run_status == "paused"


@pytest.mark.asyncio
async def test_runtime_agent_graph_marks_partial_and_unmapped_evidence() -> None:
    workflow_run_id, tenant_id, repository = runtime_graph_records(
        include_timeline=False,
        include_unmapped_step=True,
        include_interactions=True,
        include_unmapped_interaction=True,
    )

    graph = await build_runtime_agent_graph(
        repository=cast(RuntimeOrchestrationRepository, repository),
        workflow_run_id=workflow_run_id,
        tenant_id=tenant_id,
    )

    assert graph is not None
    assert graph.partial is True
    assert graph.state == AgentGraphState.PARTIAL
    assert graph.provenance.evidence_counts["timeline_events"] == 0
    assert graph.provenance.evidence_counts["unmapped_interaction_evidence"] == 1
    badge_codes = {badge.code for badge in graph.badges}
    assert "runtime.partial.timeline" in badge_codes
    assert "runtime.partial.unmapped_steps" in badge_codes
    assert "runtime.partial.unmapped_interactions" in badge_codes


@pytest.mark.asyncio
async def test_runtime_agent_graph_returns_none_for_wrong_tenant() -> None:
    workflow_run_id, _, repository = runtime_graph_records()

    graph = await build_runtime_agent_graph(
        repository=cast(RuntimeOrchestrationRepository, repository),
        workflow_run_id=workflow_run_id,
        tenant_id=None,
    )

    assert graph is None


@pytest.mark.asyncio
async def test_runtime_agent_graph_returns_partial_without_topology() -> None:
    workflow_run_id, tenant_id, repository = runtime_graph_records()
    repository.bundle = None

    graph = await build_runtime_agent_graph(
        repository=cast(RuntimeOrchestrationRepository, repository),
        workflow_run_id=workflow_run_id,
        tenant_id=tenant_id,
    )

    assert graph is not None
    assert graph.state == AgentGraphState.PARTIAL
    assert graph.partial is True
    assert graph.nodes == ()
    assert graph.edges == ()
    assert graph.badges[0].code == "runtime.topology.partial"
    assert graph.provenance.workflow_key == "runtime-workflow"


@pytest.mark.asyncio
async def test_runtime_agent_graph_uses_published_revision_document() -> None:
    workflow_run_id, tenant_id, repository = runtime_graph_records()
    assert repository.bundle is not None
    repository.bundle.workflow_version.pop("document")
    revision_id = uuid4()
    draft_id = uuid4()
    repository.version = WorkflowVersionBundle(
        workflow_version_bundle_id=repository.bundle.published_workflow_version_id,
        workflow_lineage_id=uuid4(),
        scope_type="tenant",
        tenant_id=tenant_id,
        version_sequence=1,
        display_version="v1",
        published_from_draft_id=draft_id,
        published_from_revision_id=revision_id,
        published_by_principal_id=uuid4(),
        status=WorkflowVersionStatus.PUBLISHED,
        published_at=repository.bundle.created_at,
        summary_json={"workflow_key": "runtime-agent-review"},
    )
    repository.draft_revision = WorkflowDraftRevision(
        workflow_draft_revision_id=revision_id,
        workflow_draft_id=draft_id,
        revision_number=1,
        authoring_document_json=runtime_graph_document_dict(),
        document_sha256="b" * 64,
        created_by_principal_id=uuid4(),
    )

    graph = await build_runtime_agent_graph(
        repository=cast(RuntimeOrchestrationRepository, repository),
        workflow_run_id=workflow_run_id,
        tenant_id=tenant_id,
    )

    assert graph is not None
    assert graph.state == AgentGraphState.READY
    assert {node.node_key for node in graph.nodes} >= {"coordinator", "specialist"}
    assert graph.provenance.workflow_key == "runtime-agent-review"


@pytest.mark.asyncio
async def test_runtime_agent_graph_marks_missing_run_steps_partial() -> None:
    workflow_run_id, tenant_id, repository = runtime_graph_records()
    repository.run_steps = []
    repository.timeline_events = []

    graph = await build_runtime_agent_graph(
        repository=cast(RuntimeOrchestrationRepository, repository),
        workflow_run_id=workflow_run_id,
        tenant_id=tenant_id,
    )

    assert graph is not None
    assert graph.partial is True
    assert {badge.code for badge in graph.badges} >= {
        "runtime.partial.run_steps",
        "runtime.partial.timeline",
    }
    assert any(edge.status == "unavailable" for edge in graph.edges)


def test_runtime_agent_graph_private_status_helpers_cover_safe_edges() -> None:
    assert _step_status(None, "pending") == "queued"
    assert _step_status(None, "running") == "unavailable"
    assert (
        _safe_ref_summary(
            {"safe_summary": "raw prompt: private"},
            fallback="fallback",
        )
        == "Evidence summary was redacted for safe graph display."
    )
    assert (
        _safe_ref_summary(
            {"summary": {"safe_summary": "traceback: private"}},
            fallback="fallback",
        )
        == "Evidence summary was redacted for safe graph display."
    )
    assert _safe_ref_summary({}, fallback="fallback") == "fallback"
    assert _payload_node_key({"node_key": "coordinator"}) == "coordinator"
    assert _payload_node_key({"node_key": 123}) is None
    assert _severity_for_status("failed") == "critical"
    assert _reference_status("failed") == "blocked"
    interaction = RuntimeInteractionEvidenceRecord(
        tenant_id=None,
        workflow_run_id=uuid4(),
        source_node_key="source",
        target_node_key=None,
        interaction_kind=RuntimeInteractionKind.RESULT_RETURN,
        status=RuntimeInteractionStatus.FAILED,
        sequence=1,
        safe_summary="Safe failed interaction.",
        classification="safe-summary",
        payload_digest="f" * 64,
        artifact_refs=[],
        provenance={},
        idempotency_key="helper-status",
    )
    assert _interaction_status(interaction) == "failed"
