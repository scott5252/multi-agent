from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from multi_agent_platform.api.schemas.workflow_registry import WorkflowDraftDocument
from multi_agent_platform.db.models.runtime_orchestration import (
    ApprovalGateRecord,
    HandoffEnvelopeRecord,
    RunStepRecord,
    RuntimeApprovalStatus,
    RuntimeExecutionBundleRecord,
    RuntimeHandoffStatus,
    RuntimeInteractionEvidenceRecord,
    RuntimeInteractionKind,
    RuntimeInteractionStatus,
    RuntimeRunStatus,
    RuntimeSideEffectStatus,
    RuntimeStepStatus,
    RuntimeTimelineEventRecord,
    SideEffectIntentRecord,
    WorkflowRunRecord,
)
from multi_agent_platform.db.models.workflow_registry import (
    WorkflowDraftRevision,
    WorkflowVersionBundle,
)


def runtime_graph_document_dict() -> dict[str, object]:
    return {
        "workflow_key": "runtime-agent-review",
        "display_name": "Runtime Agent Review",
        "description": "Coordinate a runtime specialist review.",
        "workflow_kind": "main_workflow",
        "entry_node_key": "coordinator",
        "roles": [
            {
                "role_key": "coordinator",
                "display_name": "Coordinator",
                "role_kind": "agent",
                "purpose": "Coordinate specialist work.",
                "input_contract_key": "request",
                "output_contract_key": "brief",
                "skill_bindings": [
                    {
                        "binding_key": "safe-lookup",
                        "skill_slug": "safe-lookup",
                        "skill_version": "2026.05.0",
                        "purpose": "Load safe context.",
                    }
                ],
                "graph_node_keys": ["coordinator"],
            },
            {
                "role_key": "specialist",
                "display_name": "Specialist",
                "role_kind": "subagent",
                "purpose": "Review the runtime request.",
                "input_contract_key": "brief",
                "output_contract_key": "result",
                "graph_node_keys": ["specialist"],
            },
        ],
        "contracts": [
            {"contract_key": "request", "json_schema": {"type": "object"}},
            {"contract_key": "brief", "json_schema": {"type": "object"}},
            {"contract_key": "result", "json_schema": {"type": "object"}},
        ],
        "nodes": [
            {
                "node_key": "coordinator",
                "node_type": "role",
                "display_name": "Coordinator",
                "role_key": "coordinator",
            },
            {
                "node_key": "specialist",
                "node_type": "role",
                "display_name": "Specialist",
                "role_key": "specialist",
            },
            {
                "node_key": "approval",
                "node_type": "approval",
                "display_name": "Approval",
                "approval_gate_key": "manager",
            },
            {
                "node_key": "done",
                "node_type": "terminal",
                "display_name": "Done",
            },
        ],
        "edges": [
            {
                "edge_key": "edge-coordinator-specialist",
                "source_node_key": "coordinator",
                "target_node_key": "specialist",
                "contract_key": "brief",
            },
            {
                "edge_key": "edge-specialist-approval",
                "source_node_key": "specialist",
                "target_node_key": "approval",
                "contract_key": "result",
            },
            {
                "edge_key": "edge-approval-done",
                "source_node_key": "approval",
                "target_node_key": "done",
            },
        ],
        "approval_gates": [
            {
                "approval_gate_key": "manager",
                "display_name": "Manager approval",
                "approver_scope": "tenant_admin",
                "resume_behavior": "resume_origin",
            }
        ],
    }


def runtime_graph_document() -> WorkflowDraftDocument:
    return WorkflowDraftDocument.model_validate(runtime_graph_document_dict())


class RuntimeGraphFakeRepository:
    def __init__(
        self,
        *,
        run: WorkflowRunRecord,
        bundle: RuntimeExecutionBundleRecord | None,
        run_steps: list[RunStepRecord],
        timeline_events: list[RuntimeTimelineEventRecord],
        handoffs: list[HandoffEnvelopeRecord] | None = None,
        side_effects: list[SideEffectIntentRecord] | None = None,
        approvals: list[ApprovalGateRecord] | None = None,
        interactions: list[RuntimeInteractionEvidenceRecord] | None = None,
        version: WorkflowVersionBundle | None = None,
        draft_revision: WorkflowDraftRevision | None = None,
    ) -> None:
        self.run = run
        self.bundle = bundle
        self.run_steps = run_steps
        self.timeline_events = timeline_events
        self.handoffs = handoffs or []
        self.side_effects = side_effects or []
        self.approvals = approvals or []
        self.interactions = interactions or []
        self.version = version
        self.draft_revision = draft_revision

    async def get_run(
        self, *, workflow_run_id: UUID, tenant_id: UUID | None
    ) -> WorkflowRunRecord | None:
        if (
            self.run.workflow_run_id == workflow_run_id
            and self.run.tenant_id == tenant_id
        ):
            return self.run
        return None

    async def get_execution_bundle(
        self, *, run_bundle_id: UUID
    ) -> RuntimeExecutionBundleRecord | None:
        if self.bundle is not None and self.bundle.run_bundle_id == run_bundle_id:
            return self.bundle
        return None

    async def get_workflow_version_bundle(self, *, workflow_version_bundle_id: UUID):
        if (
            self.version is not None
            and self.version.workflow_version_bundle_id == workflow_version_bundle_id
        ):
            return self.version
        return None

    async def get_workflow_draft_revision(self, *, workflow_draft_revision_id: UUID):
        if (
            self.draft_revision is not None
            and self.draft_revision.workflow_draft_revision_id
            == workflow_draft_revision_id
        ):
            return self.draft_revision
        return None

    async def list_run_steps(
        self, *, workflow_run_id: UUID, tenant_id: UUID | None
    ) -> list[RunStepRecord]:
        return [
            step
            for step in self.run_steps
            if step.workflow_run_id == workflow_run_id and step.tenant_id == tenant_id
        ]

    async def list_timeline(
        self, *, workflow_run_id: UUID, tenant_id: UUID | None, limit: int = 100
    ) -> list[RuntimeTimelineEventRecord]:
        _ = limit
        return [
            event
            for event in self.timeline_events
            if event.workflow_run_id == workflow_run_id and event.tenant_id == tenant_id
        ]

    async def list_handoff_envelopes(
        self, *, workflow_run_id: UUID, tenant_id: UUID | None
    ) -> list[HandoffEnvelopeRecord]:
        return [
            handoff
            for handoff in self.handoffs
            if handoff.workflow_run_id == workflow_run_id
            and handoff.tenant_id == tenant_id
        ]

    async def list_side_effect_intents(
        self, *, workflow_run_id: UUID, tenant_id: UUID | None
    ) -> list[SideEffectIntentRecord]:
        return [
            intent
            for intent in self.side_effects
            if intent.workflow_run_id == workflow_run_id
            and intent.tenant_id == tenant_id
        ]

    async def list_approval_gates(
        self, *, workflow_run_id: UUID, tenant_id: UUID | None
    ) -> list[ApprovalGateRecord]:
        return [
            approval
            for approval in self.approvals
            if approval.workflow_run_id == workflow_run_id
            and approval.tenant_id == tenant_id
        ]

    async def list_interaction_evidence(
        self, *, workflow_run_id: UUID, tenant_id: UUID | None
    ) -> list[RuntimeInteractionEvidenceRecord]:
        return [
            interaction
            for interaction in self.interactions
            if interaction.workflow_run_id == workflow_run_id
            and interaction.tenant_id == tenant_id
        ]


def runtime_graph_records(
    *,
    run_status: RuntimeRunStatus = RuntimeRunStatus.RUNNING,
    step_statuses: dict[str, RuntimeStepStatus] | None = None,
    include_timeline: bool = True,
    include_unmapped_step: bool = False,
    include_interactions: bool = False,
    include_unmapped_interaction: bool = False,
) -> tuple[UUID, UUID, RuntimeGraphFakeRepository]:
    tenant_id = uuid4()
    workflow_run_id = uuid4()
    run_bundle_id = uuid4()
    workflow_version_bundle_id = uuid4()
    workflow_lineage_id = uuid4()
    now = datetime.now(UTC)
    document = runtime_graph_document_dict()
    bundle = RuntimeExecutionBundleRecord(
        run_bundle_id=run_bundle_id,
        tenant_id=tenant_id,
        workflow_run_id=workflow_run_id,
        published_workflow_version_id=workflow_version_bundle_id,
        bundle_digest="a" * 64,
        workflow_version={
            "display_name": "Runtime Agent Review",
            "document": document,
            "workflow_key": "runtime-agent-review",
            "workflow_lineage_id": str(workflow_lineage_id),
        },
        created_at=now,
    )
    run = WorkflowRunRecord(
        workflow_run_id=workflow_run_id,
        tenant_id=tenant_id,
        scope_type="tenant",
        initiating_principal_id="tenant-admin-acme",
        run_bundle_id=run_bundle_id,
        status=run_status,
        idempotency_key=f"runtime-graph-{workflow_run_id}",
        trace_id=f"trace-{workflow_run_id}",
        started_at=now,
    )
    statuses = {
        "coordinator": RuntimeStepStatus.SUCCEEDED,
        "specialist": RuntimeStepStatus.RUNNING,
        "approval": RuntimeStepStatus.PENDING,
        "done": RuntimeStepStatus.PENDING,
        **(step_statuses or {}),
    }
    run_steps = [
        RunStepRecord(
            run_step_id=uuid4(),
            workflow_run_id=workflow_run_id,
            tenant_id=tenant_id,
            step_key=step_key,
            step_type="role" if step_key in {"coordinator", "specialist"} else step_key,
            status=status,
            attempt=1,
            input_ref={"safe_summary": f"{step_key} received safe input evidence."},
            output_ref={"safe_summary": f"{step_key} produced safe output evidence."},
            error_ref={"safe_summary": f"{step_key} recorded a safe issue."}
            if status in {RuntimeStepStatus.FAILED, RuntimeStepStatus.RETRY_SCHEDULED}
            else None,
            created_at=now,
        )
        for step_key, status in statuses.items()
    ]
    if include_unmapped_step:
        run_steps.append(
            RunStepRecord(
                run_step_id=uuid4(),
                workflow_run_id=workflow_run_id,
                tenant_id=tenant_id,
                step_key="legacy-node",
                step_type="role",
                status=RuntimeStepStatus.SUCCEEDED,
                attempt=1,
                output_ref={"safe_summary": "Legacy evidence was retained safely."},
                created_at=now,
            )
        )
    events = (
        [
            RuntimeTimelineEventRecord(
                runtime_timeline_event_id=uuid4(),
                tenant_id=tenant_id,
                workflow_run_id=workflow_run_id,
                run_step_id=step.run_step_id,
                event_type=f"{step.step_key}_status",
                severity="error" if step.status == RuntimeStepStatus.FAILED else "info",
                payload={
                    "safe_summary": f"{step.step_key} has safe timeline evidence."
                },
                trace_id=f"trace-{workflow_run_id}",
                created_at=now,
            )
            for step in run_steps
        ]
        if include_timeline
        else []
    )
    coordinator_step = next(
        step for step in run_steps if step.step_key == "coordinator"
    )
    approval_step = next(step for step in run_steps if step.step_key == "approval")
    handoffs = [
        HandoffEnvelopeRecord(
            handoff_envelope_id=uuid4(),
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_id,
            sender_step_id=coordinator_step.run_step_id,
            receiver_step_key="specialist",
            contract_id="brief",
            contract_version="1.0.0",
            contract_digest="b" * 64,
            status=RuntimeHandoffStatus.VALID,
            payload_hash="c" * 64,
            payload_ref={"safe_summary": "Safe handoff summary is available."},
            created_at=now,
            validated_at=now,
        )
    ]
    side_effects = [
        SideEffectIntentRecord(
            side_effect_intent_id=uuid4(),
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_id,
            run_step_id=coordinator_step.run_step_id,
            intent_kind="read_only_lookup",
            idempotency_key="runtime-graph-tool",
            status=RuntimeSideEffectStatus.APPLIED,
            tool_policy_ref="tool-policy:safe-lookup",
            result_ref={"safe_summary": "Read only lookup produced safe evidence."},
            created_at=now,
        )
    ]
    approvals = [
        ApprovalGateRecord(
            approval_gate_id=uuid4(),
            tenant_id=tenant_id,
            workflow_run_id=workflow_run_id,
            run_step_id=approval_step.run_step_id,
            status=RuntimeApprovalStatus.PENDING,
            approval_key="manager",
            requested_action={"safe_summary": "Manager approval is pending."},
            created_at=now,
        )
    ]
    interactions: list[RuntimeInteractionEvidenceRecord] = []
    if include_interactions:
        interactions.append(
            RuntimeInteractionEvidenceRecord(
                interaction_evidence_id=uuid4(),
                tenant_id=tenant_id,
                workflow_run_id=workflow_run_id,
                source_node_key="coordinator",
                target_node_key="specialist",
                source_run_step_id=coordinator_step.run_step_id,
                interaction_kind=RuntimeInteractionKind.HANDOFF,
                status=RuntimeInteractionStatus.SENT,
                sequence=1,
                safe_summary="Coordinator sent safe context to Specialist.",
                classification="safe-summary",
                payload_digest="d" * 64,
                artifact_refs=[],
                provenance={"edge_key": "edge-coordinator-specialist"},
                idempotency_key="interaction-coordinator-specialist",
                occurred_at=now,
                created_at=now,
            )
        )
    if include_unmapped_interaction:
        interactions.append(
            RuntimeInteractionEvidenceRecord(
                interaction_evidence_id=uuid4(),
                tenant_id=tenant_id,
                workflow_run_id=workflow_run_id,
                source_node_key="legacy-node",
                target_node_key="missing-node",
                interaction_kind=RuntimeInteractionKind.RESULT_RETURN,
                status=RuntimeInteractionStatus.COMPLETED,
                sequence=2,
                safe_summary="Legacy interaction was retained safely.",
                classification="safe-summary",
                payload_digest="e" * 64,
                artifact_refs=[],
                provenance={"source": "legacy"},
                idempotency_key="interaction-unmapped",
                occurred_at=now,
                created_at=now,
            )
        )
    return (
        workflow_run_id,
        tenant_id,
        RuntimeGraphFakeRepository(
            run=run,
            bundle=bundle,
            run_steps=run_steps,
            timeline_events=events,
            handoffs=handoffs,
            side_effects=side_effects,
            approvals=approvals,
            interactions=interactions,
        ),
    )
