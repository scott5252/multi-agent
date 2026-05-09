from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from uuid import UUID

from multi_agent_platform.admin.workflow_registry.agent_graph import (
    build_published_agent_graph,
)
from multi_agent_platform.api.schemas.admin_agent_graph import (
    AgentCommunicationGraph,
    AgentGraphAccessibility,
    AgentGraphBadge,
    AgentGraphBadgeSeverity,
    AgentGraphBadgeSource,
    AgentGraphEdge,
    AgentGraphNode,
    AgentGraphProvenance,
    AgentGraphReferenceStatus,
    AgentGraphReferenceSummary,
    AgentGraphReferenceType,
    AgentGraphSource,
    AgentGraphState,
    safe_agent_graph_text,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    WorkflowDraftDocument,
    WorkflowScopeType,
    WorkflowVersionResponse,
)
from multi_agent_platform.db.models.runtime_orchestration import (
    ApprovalGateRecord,
    HandoffEnvelopeRecord,
    RunStepRecord,
    RuntimeExecutionBundleRecord,
    RuntimeInteractionEvidenceRecord,
    RuntimeStepStatus,
    RuntimeTimelineEventRecord,
    SideEffectIntentRecord,
    WorkflowRunRecord,
)
from multi_agent_platform.db.models.workflow_registry import WorkflowVersionBundle
from multi_agent_platform.db.repositories.runtime_orchestration import (
    RuntimeOrchestrationRepository,
)

STATUS_PRECEDENCE = {
    "failed": 0,
    "manual_resolution_required": 1,
    "paused": 2,
    "waiting": 3,
    "retry_scheduled": 4,
    "running": 5,
    "completed": 6,
    "succeeded": 7,
    "skipped": 8,
    "queued": 9,
    "unavailable": 10,
    "ready": 11,
}


async def build_runtime_agent_graph(
    *,
    repository: RuntimeOrchestrationRepository,
    workflow_run_id: UUID,
    tenant_id: UUID | None,
    generated_at: datetime | None = None,
) -> AgentCommunicationGraph | None:
    run = await repository.get_run(workflow_run_id=workflow_run_id, tenant_id=tenant_id)
    if run is None:
        return None

    bundle = await repository.get_execution_bundle(run_bundle_id=run.run_bundle_id)
    version = (
        await repository.get_workflow_version_bundle(
            workflow_version_bundle_id=bundle.published_workflow_version_id
        )
        if bundle is not None
        else None
    )
    document = _document_for_runtime(bundle=bundle, version=version)
    if bundle is None or document is None:
        return _partial_without_topology(
            run=run,
            bundle=bundle,
            version=version,
            generated_at=generated_at,
        )

    base_graph = build_published_agent_graph(
        _version_response(version=version, bundle=bundle),
        document=document,
        generated_at=generated_at,
    )
    run_steps = await repository.list_run_steps(
        workflow_run_id=workflow_run_id, tenant_id=tenant_id
    )
    timeline_events = await repository.list_timeline(
        workflow_run_id=workflow_run_id, tenant_id=tenant_id, limit=250
    )
    handoffs = await repository.list_handoff_envelopes(
        workflow_run_id=workflow_run_id, tenant_id=tenant_id
    )
    side_effects = await repository.list_side_effect_intents(
        workflow_run_id=workflow_run_id, tenant_id=tenant_id
    )
    approvals = await repository.list_approval_gates(
        workflow_run_id=workflow_run_id, tenant_id=tenant_id
    )
    interactions = await repository.list_interaction_evidence(
        workflow_run_id=workflow_run_id, tenant_id=tenant_id
    )
    return _overlay_runtime_evidence(
        base_graph=base_graph,
        run=run,
        bundle=bundle,
        run_steps=run_steps,
        timeline_events=timeline_events,
        handoffs=handoffs,
        side_effects=side_effects,
        approvals=approvals,
        interactions=interactions,
        generated_at=generated_at,
    )


def _document_for_runtime(
    *,
    bundle: RuntimeExecutionBundleRecord | None,
    version: WorkflowVersionBundle | None,
) -> WorkflowDraftDocument | None:
    for candidate in (
        bundle.workflow_version.get("document") if bundle is not None else None,
        version.summary_json.get("document") if version is not None else None,
    ):
        if isinstance(candidate, dict):
            return WorkflowDraftDocument.model_validate(candidate)
    return None


def _version_response(
    *,
    version: WorkflowVersionBundle | None,
    bundle: RuntimeExecutionBundleRecord,
) -> WorkflowVersionResponse:
    raw_workflow_version = bundle.workflow_version
    workflow_key = str(raw_workflow_version.get("workflow_key") or "runtime-workflow")
    workflow_lineage_id = (
        version.workflow_lineage_id
        if version is not None
        else UUID(str(raw_workflow_version.get("workflow_lineage_id")))
    )
    published_from_draft_id = (
        version.published_from_draft_id
        if version is not None
        else bundle.published_workflow_version_id
    )
    published_from_revision_id = (
        version.published_from_revision_id
        if version is not None
        else bundle.published_workflow_version_id
    )
    return WorkflowVersionResponse(
        workflow_version_bundle_id=bundle.published_workflow_version_id,
        workflow_lineage_id=workflow_lineage_id,
        slug=str(raw_workflow_version.get("workflow_key") or workflow_key),
        display_name=str(raw_workflow_version.get("display_name") or workflow_key),
        display_version=version.display_version if version is not None else "runtime",
        scope_type=WorkflowScopeType(
            _enum_value(version.scope_type) if version is not None else "tenant"
        ),
        tenant_id=bundle.tenant_id,
        status=_enum_value(version.status) if version is not None else "published",
        compiled_bundle_digest=version.compiled_bundle_digest
        if version is not None
        else bundle.bundle_digest,
        compiler_version=version.compiler_version if version is not None else None,
        published_from_draft_id=published_from_draft_id,
        published_from_revision_id=published_from_revision_id,
        previous_version_bundle_id=version.previous_version_bundle_id
        if version is not None
        else None,
        compiled_bundle_artifact_id=version.compiled_bundle_artifact_id
        if version is not None
        else None,
        summary_json=version.summary_json
        if version is not None
        else raw_workflow_version,
        sharing_grants=[],
        published_at=version.published_at if version is not None else bundle.created_at,
    )


def _overlay_runtime_evidence(
    *,
    base_graph: AgentCommunicationGraph,
    run: WorkflowRunRecord,
    bundle: RuntimeExecutionBundleRecord,
    run_steps: Sequence[RunStepRecord],
    timeline_events: Sequence[RuntimeTimelineEventRecord],
    handoffs: Sequence[HandoffEnvelopeRecord],
    side_effects: Sequence[SideEffectIntentRecord],
    approvals: Sequence[ApprovalGateRecord],
    interactions: Sequence[RuntimeInteractionEvidenceRecord],
    generated_at: datetime | None,
) -> AgentCommunicationGraph:
    latest_steps = _latest_steps_by_key(run_steps)
    events_by_step = _events_by_step(timeline_events)
    handoffs_by_receiver = _handoffs_by_receiver(handoffs)
    handoffs_by_sender = _handoffs_by_sender(handoffs)
    side_effects_by_step = _side_effects_by_step(side_effects)
    approvals_by_step = _approvals_by_step(approvals)
    interactions_by_edge = _interactions_by_edge(interactions)

    runtime_nodes: list[AgentGraphNode] = []
    for node in base_graph.nodes:
        step = latest_steps.get(node.node_key)
        runtime_nodes.append(
            _runtime_node(
                node=node,
                step=step,
                events=events_by_step.get(step.run_step_id, ())
                if step is not None
                else (),
                handoffs=handoffs_by_sender.get(step.run_step_id, ())
                if step is not None
                else (),
                side_effects=side_effects_by_step.get(step.run_step_id, ())
                if step is not None
                else (),
                approvals=approvals_by_step.get(step.run_step_id, ())
                if step is not None
                else (),
                run_status=_enum_value(run.status),
            )
        )
    nodes = tuple(runtime_nodes)
    node_status_by_id = {node.node_id: node.status for node in nodes}
    edges = tuple(
        _runtime_edge(
            edge=edge,
            source_step=latest_steps.get(_node_key_from_id(edge.source_node_id)),
            target_step=latest_steps.get(_node_key_from_id(edge.target_node_id)),
            target_handoffs=handoffs_by_receiver.get(
                _node_key_from_id(edge.target_node_id), ()
            ),
            interactions=interactions_by_edge.get(
                (
                    _node_key_from_id(edge.source_node_id),
                    _node_key_from_id(edge.target_node_id),
                ),
                (),
            ),
            source_status=node_status_by_id.get(edge.source_node_id),
            target_status=node_status_by_id.get(edge.target_node_id),
        )
        for edge in base_graph.edges
    )
    graph_edge_keys = {
        (_node_key_from_id(edge.source_node_id), _node_key_from_id(edge.target_node_id))
        for edge in base_graph.edges
    }
    partial_reasons = _partial_reasons(
        base_graph=base_graph,
        run_steps=run_steps,
        timeline_events=timeline_events,
        interactions=interactions,
        graph_edge_keys=graph_edge_keys,
        mapped_node_keys={node.node_key for node in nodes},
    )
    evidence_counts = {
        "run_steps": len(run_steps),
        "timeline_events": len(timeline_events),
        "handoffs": len(handoffs),
        "side_effects": len(side_effects),
        "approvals": len(approvals),
        "interaction_evidence": len(interactions),
        "unmapped_interaction_evidence": len(
            _unmapped_interactions(interactions, graph_edge_keys)
        ),
        "unmapped_timeline_events": len(
            [
                event
                for event in timeline_events
                if event.run_step_id is None
                and _payload_node_key(event.payload) not in latest_steps
            ]
        ),
    }
    badges = [
        *base_graph.badges,
        AgentGraphBadge(
            code=f"runtime.run.{_enum_value(run.status)}",
            severity=_severity_for_status(_runtime_status(_enum_value(run.status))),
            label=_runtime_status_label(_runtime_status(_enum_value(run.status))),
            summary=f"Runtime run is {_runtime_status(_enum_value(run.status))}.",
            source=AgentGraphBadgeSource.RUNTIME,
        ),
    ]
    for reason in partial_reasons:
        badges.append(
            AgentGraphBadge(
                code=f"runtime.partial.{reason}",
                severity=AgentGraphBadgeSeverity.WARNING,
                label="Partial runtime evidence",
                summary=_partial_reason_summary(reason),
                source=AgentGraphBadgeSource.RUNTIME,
            )
        )
    state = AgentGraphState.EMPTY if not nodes else AgentGraphState.READY
    if partial_reasons:
        state = AgentGraphState.PARTIAL
    accessibility = _accessibility(nodes=nodes, edges=edges, state=state)
    provenance = base_graph.provenance.model_copy(
        update={
            "source_type": AgentGraphSource.RUNTIME_RUN,
            "workflow_run_id": str(run.workflow_run_id),
            "run_bundle_id": str(bundle.run_bundle_id),
            "run_status": _runtime_status(_enum_value(run.status)),
            "evidence_counts": evidence_counts,
            "generated_at": generated_at or datetime.now(UTC),
        }
    )
    return AgentCommunicationGraph(
        graph_id=f"runtime_run:{run.workflow_run_id}",
        source=AgentGraphSource.RUNTIME_RUN,
        state=state,
        partial=bool(partial_reasons),
        provenance=provenance,
        nodes=nodes,
        edges=edges,
        badges=tuple(badges),
        accessibility=accessibility,
    )


def _runtime_node(
    *,
    node: AgentGraphNode,
    step: RunStepRecord | None,
    events: Sequence[RuntimeTimelineEventRecord],
    handoffs: Sequence[HandoffEnvelopeRecord],
    side_effects: Sequence[SideEffectIntentRecord],
    approvals: Sequence[ApprovalGateRecord],
    run_status: str,
) -> AgentGraphNode:
    status = _step_status(step.status if step is not None else None, run_status)
    references = [
        *node.references,
        *(_step_reference(step) if step is not None else ()),
        *(_timeline_reference(event) for event in events[:8]),
        *(_handoff_reference(handoff) for handoff in handoffs[:6]),
        *(_side_effect_reference(intent) for intent in side_effects[:6]),
        *(_approval_reference(approval) for approval in approvals[:4]),
    ]
    badges = [
        *node.badges,
        AgentGraphBadge(
            code=f"runtime.node.{status}",
            severity=_severity_for_status(status),
            label=_runtime_status_label(status),
            summary=f"Runtime node is {status}.",
            source=AgentGraphBadgeSource.RUNTIME,
        ),
    ]
    summary = _node_runtime_summary(node=node, step=step, status=status)
    return node.model_copy(
        update={
            "status": status,
            "summary": summary,
            "references": tuple(references),
            "badges": tuple(badges),
            "accessibility_label": (
                f"{node.label} runtime node is {status}. {summary}"
            ),
        }
    )


def _runtime_edge(
    *,
    edge: AgentGraphEdge,
    source_step: RunStepRecord | None,
    target_step: RunStepRecord | None,
    target_handoffs: Sequence[HandoffEnvelopeRecord],
    interactions: Sequence[RuntimeInteractionEvidenceRecord],
    source_status: str | None,
    target_status: str | None,
) -> AgentGraphEdge:
    status = _edge_runtime_status(
        source_step=source_step,
        target_step=target_step,
        target_handoffs=target_handoffs,
        interactions=interactions,
        source_status=source_status,
        target_status=target_status,
    )
    references = [
        *edge.references,
        *(_step_reference(source_step) if source_step is not None else ()),
        *(_step_reference(target_step) if target_step is not None else ()),
        *(_handoff_reference(handoff) for handoff in target_handoffs[:6]),
        *(_interaction_reference(interaction) for interaction in interactions[:8]),
    ]
    badges = [
        *edge.badges,
        AgentGraphBadge(
            code=f"runtime.edge.{status}",
            severity=_severity_for_status(status),
            label=_runtime_status_label(status),
            summary=f"Runtime communication edge is {status}.",
            source=AgentGraphBadgeSource.RUNTIME,
        ),
    ]
    summary = f"{edge.summary} Runtime evidence marks this path as {status}."
    return edge.model_copy(
        update={
            "status": status,
            "summary": summary,
            "references": tuple(references),
            "badges": tuple(badges),
            "accessibility_label": summary,
        }
    )


def _partial_without_topology(
    *,
    run: WorkflowRunRecord,
    bundle: RuntimeExecutionBundleRecord | None,
    version: WorkflowVersionBundle | None,
    generated_at: datetime | None,
) -> AgentCommunicationGraph:
    workflow_lineage_id = (
        str(version.workflow_lineage_id)
        if version is not None
        else str(
            (bundle.workflow_version if bundle is not None else {}).get(
                "workflow_lineage_id", "unavailable"
            )
        )
    )
    workflow_key = str(
        (bundle.workflow_version if bundle is not None else {}).get(
            "workflow_key", "runtime-workflow"
        )
    )
    provenance = AgentGraphProvenance(
        source_type=AgentGraphSource.RUNTIME_RUN,
        workflow_version_bundle_id=str(bundle.published_workflow_version_id)
        if bundle is not None
        else None,
        workflow_run_id=str(run.workflow_run_id),
        run_bundle_id=str(bundle.run_bundle_id) if bundle is not None else None,
        run_status=_runtime_status(_enum_value(run.status)),
        workflow_lineage_id=workflow_lineage_id,
        workflow_key=workflow_key,
        revision="runtime",
        source_digest=bundle.bundle_digest if bundle is not None else None,
        scope_type=run.scope_type,
        tenant_id=str(run.tenant_id) if run.tenant_id else None,
        evidence_counts={},
        generated_at=generated_at or datetime.now(UTC),
    )
    badge = AgentGraphBadge(
        code="runtime.topology.partial",
        severity=AgentGraphBadgeSeverity.WARNING,
        label="Partial runtime graph",
        summary="Runtime run exists, but published topology evidence is unavailable.",
        source=AgentGraphBadgeSource.RUNTIME,
    )
    return AgentCommunicationGraph(
        graph_id=f"runtime_run:{run.workflow_run_id}",
        source=AgentGraphSource.RUNTIME_RUN,
        state=AgentGraphState.PARTIAL,
        partial=True,
        provenance=provenance,
        nodes=(),
        edges=(),
        badges=(badge,),
        accessibility=AgentGraphAccessibility(
            summary="Runtime agent graph is partial with 0 nodes and 0 edges.",
            node_summaries=(),
            edge_summaries=(),
        ),
    )


def _latest_steps_by_key(
    run_steps: Sequence[RunStepRecord],
) -> dict[str, RunStepRecord]:
    latest: dict[str, RunStepRecord] = {}
    for step in run_steps:
        current = latest.get(step.step_key)
        if current is None or step.attempt >= current.attempt:
            latest[step.step_key] = step
    return latest


def _events_by_step(
    events: Sequence[RuntimeTimelineEventRecord],
) -> dict[UUID, tuple[RuntimeTimelineEventRecord, ...]]:
    grouped: dict[UUID, list[RuntimeTimelineEventRecord]] = defaultdict(list)
    for event in events:
        if event.run_step_id is not None:
            grouped[event.run_step_id].append(event)
    return {key: tuple(value) for key, value in grouped.items()}


def _handoffs_by_receiver(
    handoffs: Sequence[HandoffEnvelopeRecord],
) -> dict[str, tuple[HandoffEnvelopeRecord, ...]]:
    grouped: dict[str, list[HandoffEnvelopeRecord]] = defaultdict(list)
    for handoff in handoffs:
        grouped[handoff.receiver_step_key].append(handoff)
    return {key: tuple(value) for key, value in grouped.items()}


def _handoffs_by_sender(
    handoffs: Sequence[HandoffEnvelopeRecord],
) -> dict[UUID, tuple[HandoffEnvelopeRecord, ...]]:
    grouped: dict[UUID, list[HandoffEnvelopeRecord]] = defaultdict(list)
    for handoff in handoffs:
        grouped[handoff.sender_step_id].append(handoff)
    return {key: tuple(value) for key, value in grouped.items()}


def _side_effects_by_step(
    side_effects: Sequence[SideEffectIntentRecord],
) -> dict[UUID, tuple[SideEffectIntentRecord, ...]]:
    grouped: dict[UUID, list[SideEffectIntentRecord]] = defaultdict(list)
    for side_effect in side_effects:
        grouped[side_effect.run_step_id].append(side_effect)
    return {key: tuple(value) for key, value in grouped.items()}


def _approvals_by_step(
    approvals: Sequence[ApprovalGateRecord],
) -> dict[UUID, tuple[ApprovalGateRecord, ...]]:
    grouped: dict[UUID, list[ApprovalGateRecord]] = defaultdict(list)
    for approval in approvals:
        grouped[approval.run_step_id].append(approval)
    return {key: tuple(value) for key, value in grouped.items()}


def _interactions_by_edge(
    interactions: Sequence[RuntimeInteractionEvidenceRecord],
) -> dict[tuple[str, str], tuple[RuntimeInteractionEvidenceRecord, ...]]:
    grouped: dict[tuple[str, str], list[RuntimeInteractionEvidenceRecord]] = (
        defaultdict(list)
    )
    for interaction in interactions:
        if interaction.target_node_key:
            grouped[(interaction.source_node_key, interaction.target_node_key)].append(
                interaction
            )
    return {key: tuple(value) for key, value in grouped.items()}


def _step_status(status: RuntimeStepStatus | None, run_status: str) -> str:
    if status is None:
        if run_status in {"pending", "runnable"}:
            return "queued"
        return "unavailable"
    value = _enum_value(status)
    return {
        "pending": "queued",
        "runnable": "queued",
        "leased": "running",
        "running": "running",
        "paused": "paused",
        "waiting_child": "waiting",
        "retry_scheduled": "retry_scheduled",
        "succeeded": "succeeded",
        "failed": "failed",
        "cancelled": "failed",
        "compensated": "completed",
    }.get(value, "unavailable")


def _runtime_status(status: str) -> str:
    return {
        "pending": "queued",
        "runnable": "queued",
        "running": "running",
        "paused": "paused",
        "waiting_child": "waiting",
        "recoverable_failed": "retry_scheduled",
        "cancelling": "running",
        "cancelled": "failed",
        "succeeded": "completed",
        "failed": "failed",
    }.get(status, status or "unavailable")


def _timeline_status(severity: str) -> str:
    if severity in {"critical", "error"}:
        return "failed"
    if severity == "warning":
        return "waiting"
    return "succeeded"


def _edge_runtime_status(
    *,
    source_step: RunStepRecord | None,
    target_step: RunStepRecord | None,
    target_handoffs: Sequence[HandoffEnvelopeRecord],
    interactions: Sequence[RuntimeInteractionEvidenceRecord],
    source_status: str | None,
    target_status: str | None,
) -> str:
    candidates = [
        item
        for item in (
            source_status,
            target_status,
            _step_status(source_step.status, "") if source_step is not None else None,
            _step_status(target_step.status, "") if target_step is not None else None,
            "succeeded" if target_handoffs else None,
            *(_interaction_status(interaction) for interaction in interactions),
        )
        if item
    ]
    if not candidates:
        return "unavailable"
    return min(candidates, key=lambda item: STATUS_PRECEDENCE.get(item, 99))


def _node_runtime_summary(
    *, node: AgentGraphNode, step: RunStepRecord | None, status: str
) -> str:
    if step is None:
        return f"No runtime step evidence is mapped to {node.label}."
    if status in {"failed", "retry_scheduled"} and step.error_ref:
        return _safe_ref_summary(
            step.error_ref, fallback=f"{node.label} recorded a safe failure summary."
        )
    if status in {"succeeded", "completed"} and step.output_ref:
        return _safe_ref_summary(
            step.output_ref,
            fallback=f"{node.label} completed with safe output evidence.",
        )
    if status in {"running", "queued"} and step.input_ref:
        return _safe_ref_summary(
            step.input_ref, fallback=f"{node.label} has safe input evidence."
        )
    return f"Runtime step {step.step_key} is {status} on attempt {step.attempt}."


def _step_reference(step: RunStepRecord) -> tuple[AgentGraphReferenceSummary, ...]:
    return (
        AgentGraphReferenceSummary(
            reference_id=f"run-step:{step.run_step_id}",
            reference_type=AgentGraphReferenceType.RUN_STEP,
            label=f"Run step {step.step_key}",
            summary=f"Attempt {step.attempt} is {_step_status(step.status, '')}.",
            status=_reference_status(_step_status(step.status, "")),
            href=f"/admin/app/operations?run_id={step.workflow_run_id}&panel=timeline",
        ),
    )


def _timeline_reference(
    event: RuntimeTimelineEventRecord,
) -> AgentGraphReferenceSummary:
    return AgentGraphReferenceSummary(
        reference_id=f"timeline:{event.runtime_timeline_event_id}",
        reference_type=AgentGraphReferenceType.TIMELINE_EVENT,
        label=event.event_type.replace("_", " ").title(),
        summary=_safe_ref_summary(event.payload, fallback=event.event_type),
        status=_reference_status(_timeline_status(event.severity)),
        href=f"/admin/app/operations?run_id={event.workflow_run_id}&panel=timeline",
    )


def _handoff_reference(handoff: HandoffEnvelopeRecord) -> AgentGraphReferenceSummary:
    status = _enum_value(handoff.status)
    return AgentGraphReferenceSummary(
        reference_id=f"handoff:{handoff.handoff_envelope_id}",
        reference_type=AgentGraphReferenceType.HANDOFF,
        label=f"Handoff to {handoff.receiver_step_key}",
        summary=f"Handoff contract {handoff.contract_id} is {status}.",
        status=_reference_status(_runtime_status(status)),
        href=f"/admin/app/operations?run_id={handoff.workflow_run_id}&panel=lineage",
    )


def _side_effect_reference(
    intent: SideEffectIntentRecord,
) -> AgentGraphReferenceSummary:
    summary = _safe_ref_summary(
        intent.result_ref or intent.request_ref or intent.error_ref or {},
        fallback=f"Tool boundary {intent.intent_kind} is {_enum_value(intent.status)}.",
    )
    return AgentGraphReferenceSummary(
        reference_id=f"tool-call:{intent.side_effect_intent_id}",
        reference_type=AgentGraphReferenceType.TOOL_CALL,
        label=intent.intent_kind.replace("_", " ").title(),
        summary=summary,
        status=_reference_status(_runtime_status(_enum_value(intent.status))),
        href=f"/admin/app/operations?run_id={intent.workflow_run_id}&panel=timeline",
    )


def _approval_reference(approval: ApprovalGateRecord) -> AgentGraphReferenceSummary:
    status = _enum_value(approval.status)
    return AgentGraphReferenceSummary(
        reference_id=f"approval:{approval.approval_gate_id}",
        reference_type=AgentGraphReferenceType.APPROVAL,
        label=f"Approval {approval.approval_key}",
        summary=f"Approval gate {approval.approval_key} is {status}.",
        status=_reference_status(_runtime_status(status)),
        href=f"/admin/app/operations?run_id={approval.workflow_run_id}&panel=timeline",
    )


def _interaction_reference(
    interaction: RuntimeInteractionEvidenceRecord,
) -> AgentGraphReferenceSummary:
    status = _interaction_status(interaction)
    kind = _enum_value(interaction.interaction_kind).replace("_", " ")
    return AgentGraphReferenceSummary(
        reference_id=f"interaction:{interaction.interaction_evidence_id}",
        reference_type=AgentGraphReferenceType.INTERACTION_EVIDENCE,
        label=f"Replay {interaction.sequence}: {kind}",
        summary=interaction.safe_summary,
        status=_reference_status(status),
        href=f"/admin/app/operations?run_id={interaction.workflow_run_id}&panel=timeline",
    )


def _interaction_status(interaction: RuntimeInteractionEvidenceRecord) -> str:
    value = _enum_value(interaction.status)
    return {
        "recorded": "running",
        "sent": "succeeded",
        "received": "succeeded",
        "completed": "completed",
        "paused": "paused",
        "failed": "failed",
        "skipped": "skipped",
    }.get(value, "unavailable")


def _partial_reasons(
    *,
    base_graph: AgentCommunicationGraph,
    run_steps: Sequence[RunStepRecord],
    timeline_events: Sequence[RuntimeTimelineEventRecord],
    interactions: Sequence[RuntimeInteractionEvidenceRecord],
    graph_edge_keys: set[tuple[str, str]],
    mapped_node_keys: set[str],
) -> tuple[str, ...]:
    reasons: list[str] = []
    if base_graph.partial:
        reasons.append("topology")
    if not run_steps:
        reasons.append("run_steps")
    if not timeline_events:
        reasons.append("timeline")
    unmapped_steps = [
        step for step in run_steps if step.step_key not in mapped_node_keys
    ]
    if unmapped_steps:
        reasons.append("unmapped_steps")
    if _unmapped_interactions(interactions, graph_edge_keys):
        reasons.append("unmapped_interactions")
    return tuple(dict.fromkeys(reasons))


def _unmapped_interactions(
    interactions: Sequence[RuntimeInteractionEvidenceRecord],
    graph_edge_keys: set[tuple[str, str]],
) -> list[RuntimeInteractionEvidenceRecord]:
    return [
        interaction
        for interaction in interactions
        if not interaction.target_node_key
        or (
            interaction.source_node_key,
            interaction.target_node_key,
        )
        not in graph_edge_keys
    ]


def _partial_reason_summary(reason: str) -> str:
    return {
        "topology": "Published topology evidence is incomplete.",
        "run_steps": "No run step rows were available for this run.",
        "timeline": "No runtime timeline events were available for this run.",
        "unmapped_steps": "Some run steps could not be mapped to graph nodes.",
        "unmapped_interactions": (
            "Some interaction replay evidence could not be mapped to graph edges."
        ),
    }.get(reason, "Runtime evidence is incomplete.")


def _accessibility(
    *,
    nodes: Sequence[AgentGraphNode],
    edges: Sequence[AgentGraphEdge],
    state: AgentGraphState,
) -> AgentGraphAccessibility:
    status_counts = Counter(node.status for node in nodes)
    status_summary = ", ".join(
        f"{count} {status}" for status, count in sorted(status_counts.items())
    )
    summary = (
        f"Runtime agent graph is {state.value} with {len(nodes)} nodes and "
        f"{len(edges)} edges"
    )
    if status_summary:
        summary = f"{summary}; node statuses: {status_summary}."
    else:
        summary = f"{summary}."
    return AgentGraphAccessibility(
        summary=summary,
        node_summaries=tuple(node.accessibility_label for node in nodes),
        edge_summaries=tuple(edge.accessibility_label for edge in edges),
    )


def _safe_ref_summary(ref: Mapping[str, object], *, fallback: str) -> str:
    for key in ("safe_summary", "summary", "status", "category"):
        value = ref.get(key)
        if isinstance(value, str) and value.strip():
            try:
                return safe_agent_graph_text(value, max_length=220)
            except ValueError:
                return "Evidence summary was redacted for safe graph display."
        if isinstance(value, Mapping):
            nested = value.get("summary") or value.get("safe_summary")
            if isinstance(nested, str) and nested.strip():
                try:
                    return safe_agent_graph_text(nested, max_length=220)
                except ValueError:
                    return "Evidence summary was redacted for safe graph display."
    return fallback


def _payload_node_key(payload: Mapping[str, object]) -> str | None:
    value = payload.get("node_key")
    return value if isinstance(value, str) else None


def _node_key_from_id(node_id: str) -> str:
    return node_id.removeprefix("node:")


def _enum_value(value: object) -> str:
    return str(getattr(value, "value", value))


def _runtime_status_label(status: str) -> str:
    return status.replace("_", " ").title()


def _severity_for_status(status: str) -> AgentGraphBadgeSeverity:
    if status in {"failed", "manual_resolution_required"}:
        return AgentGraphBadgeSeverity.CRITICAL
    if status in {"paused", "waiting", "retry_scheduled", "unavailable"}:
        return AgentGraphBadgeSeverity.WARNING
    return AgentGraphBadgeSeverity.INFO


def _reference_status(status: str) -> AgentGraphReferenceStatus:
    if status in {"failed", "manual_resolution_required"}:
        return AgentGraphReferenceStatus.BLOCKED
    if status in {"paused", "waiting", "retry_scheduled", "unavailable"}:
        return AgentGraphReferenceStatus.WARNING
    if status in {"queued"}:
        return AgentGraphReferenceStatus.UNKNOWN
    return AgentGraphReferenceStatus.READY
