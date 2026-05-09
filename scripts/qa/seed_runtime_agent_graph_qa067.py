#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from multi_agent_platform.db.models.access_control import (
    AuthProviderType,
    PrincipalIdentity,
    PrincipalIdentityStatus,
)
from multi_agent_platform.db.models.runtime_orchestration import (
    ApprovalGateRecord,
    HandoffEnvelopeRecord,
    RunStepRecord,
    RuntimeApprovalStatus,
    RuntimeExecutionBundleRecord,
    RuntimeHandoffStatus,
    RuntimeRunStatus,
    RuntimeSideEffectStatus,
    RuntimeStepStatus,
    RuntimeTimelineEventRecord,
    SideEffectIntentRecord,
    WorkflowRunRecord,
)
from multi_agent_platform.db.models.tenant import Tenant, TenantStatus
from multi_agent_platform.db.models.workflow_registry import (
    WorkflowDraft,
    WorkflowDraftRevision,
    WorkflowDraftStatus,
    WorkflowKind,
    WorkflowLineage,
    WorkflowLineageStatus,
    WorkflowVersionBundle,
    WorkflowVersionStatus,
)

ACME_TENANT_ID = UUID("11111111-1111-1111-1111-111111111111")
QA067_DRAFT_ID = UUID("67676767-1111-4767-8767-000000000067")
QA067_LINEAGE_ID = UUID("67676767-2222-4767-8767-000000000067")
QA067_REVISION_ID = UUID("67676767-3333-4767-8767-000000000067")
QA067_VERSION_ID = UUID("67676767-4444-4767-8767-000000000067")
QA067_BUNDLE_ID = UUID("67676767-5555-4767-8767-000000000067")
QA067_RUN_ID = UUID("67676767-6666-4767-8767-000000000067")
QA067_COORDINATOR_STEP_ID = UUID("67676767-7101-4767-8767-000000000067")
QA067_SPECIALIST_STEP_ID = UUID("67676767-7102-4767-8767-000000000067")
QA067_APPROVAL_STEP_ID = UUID("67676767-7103-4767-8767-000000000067")
QA067_DONE_STEP_ID = UUID("67676767-7104-4767-8767-000000000067")
EVIDENCE_PATH = Path(
    ".data/qa067-artifacts/evidence/qa067-runtime-agent-graph-seed.json"
)


def main() -> int:
    now = datetime.now(UTC)
    engine = create_engine(_database_url())
    with Session(engine) as session:
        _upsert_tenant(session)
        principal = _upsert_principal(session)
        _upsert_workflow(session, principal)
        _upsert_runtime(session, now)
        session.commit()

    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_text(
        json.dumps(
            {
                "tenant_id": str(ACME_TENANT_ID),
                "workflow_run_id": str(QA067_RUN_ID),
                "workflow_version_bundle_id": str(QA067_VERSION_ID),
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    print("Seeded QA067 runtime agent graph run")
    print(f"tenant_id={ACME_TENANT_ID}")
    print(f"workflow_run_id={QA067_RUN_ID}")
    print(f"workflow_version_bundle_id={QA067_VERSION_ID}")
    print(f"evidence_path={EVIDENCE_PATH}")
    return 0


def _database_url() -> str:
    value = os.environ.get("DATABASE_URL")
    if value is None:
        value = _env_file_value("DATABASE_URL")
    if value is None:
        raise RuntimeError("DATABASE_URL is required for QA067 seed")
    return value.replace("sqlite+aiosqlite://", "sqlite://", 1)


def _env_file_value(key: str) -> str | None:
    env_path = Path(".env")
    if not env_path.exists():
        return None
    prefix = f"{key}="
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return None


def _upsert_tenant(session: Session) -> None:
    tenant = session.get(Tenant, ACME_TENANT_ID)
    if tenant is None:
        tenant = Tenant(tenant_id=ACME_TENANT_ID)
        session.add(tenant)
    tenant.slug = "acme"
    tenant.display_name = "Acme"
    tenant.status = TenantStatus.ACTIVE


def _upsert_principal(session: Session) -> PrincipalIdentity:
    principal = session.scalar(
        select(PrincipalIdentity).where(
            PrincipalIdentity.external_subject == "local|qa067-publisher"
        )
    )
    if principal is None:
        principal = PrincipalIdentity(
            auth_provider=AuthProviderType.LOCAL_PRINCIPAL,
            external_subject="local|qa067-publisher",
        )
        session.add(principal)
    principal.display_name = "QA067 Publisher"
    principal.email = "qa067.publisher@example.test"
    principal.status = PrincipalIdentityStatus.ACTIVE
    session.flush()
    return principal


def _upsert_workflow(session: Session, principal: PrincipalIdentity) -> None:
    lineage = session.get(WorkflowLineage, QA067_LINEAGE_ID)
    if lineage is None:
        lineage = WorkflowLineage(
            workflow_lineage_id=QA067_LINEAGE_ID,
            scope_type="tenant",
            tenant_id=ACME_TENANT_ID,
            slug="qa067-runtime-agent-graph",
            display_name="QA067 Runtime Agent Graph",
            workflow_kind=WorkflowKind.MAIN_WORKFLOW,
            created_by_principal_id=principal.principal_identity_id,
        )
        session.add(lineage)
    lineage.status = WorkflowLineageStatus.PUBLISHED
    lineage.description = "Workflow for QA067 runtime graph evidence."

    draft = session.get(WorkflowDraft, QA067_DRAFT_ID)
    if draft is None:
        draft = WorkflowDraft(
            workflow_draft_id=QA067_DRAFT_ID,
            workflow_lineage_id=QA067_LINEAGE_ID,
            scope_type="tenant",
            tenant_id=ACME_TENANT_ID,
            created_by_principal_id=principal.principal_identity_id,
            last_edited_by_principal_id=principal.principal_identity_id,
        )
        session.add(draft)
    draft.status = WorkflowDraftStatus.ACTIVE
    draft.current_revision_number = 1

    revision = session.get(WorkflowDraftRevision, QA067_REVISION_ID)
    if revision is None:
        revision = WorkflowDraftRevision(
            workflow_draft_revision_id=QA067_REVISION_ID,
            workflow_draft_id=QA067_DRAFT_ID,
            revision_number=1,
            created_by_principal_id=principal.principal_identity_id,
        )
        session.add(revision)
    revision.authoring_document_json = _workflow_document()
    revision.document_sha256 = "7" * 64
    revision.change_summary = "QA067 runtime agent graph seed revision."
    session.flush()
    draft.latest_revision_id = QA067_REVISION_ID

    version = session.get(WorkflowVersionBundle, QA067_VERSION_ID)
    if version is None:
        version = WorkflowVersionBundle(
            workflow_version_bundle_id=QA067_VERSION_ID,
            workflow_lineage_id=QA067_LINEAGE_ID,
            scope_type="tenant",
            tenant_id=ACME_TENANT_ID,
            version_sequence=1,
            display_version="qa067-v1",
            status=WorkflowVersionStatus.PUBLISHED,
            published_from_draft_id=QA067_DRAFT_ID,
            published_from_revision_id=QA067_REVISION_ID,
            published_by_principal_id=principal.principal_identity_id,
        )
        session.add(version)
    version.compiled_bundle_digest = "7" * 64
    version.compiler_version = "qa067"
    version.summary_json = {
        "document": _workflow_document(),
        "workflow_key": "qa067-runtime-agent-graph",
    }
    lineage.latest_published_version_id = QA067_VERSION_ID
    session.flush()


def _upsert_runtime(session: Session, now: datetime) -> None:
    session.merge(
        RuntimeExecutionBundleRecord(
            run_bundle_id=QA067_BUNDLE_ID,
            tenant_id=ACME_TENANT_ID,
            workflow_run_id=QA067_RUN_ID,
            published_workflow_version_id=QA067_VERSION_ID,
            bundle_digest="7" * 64,
            workflow_version={
                "display_name": "QA067 Runtime Agent Graph",
                "document": _workflow_document(),
                "workflow_key": "qa067-runtime-agent-graph",
                "workflow_lineage_id": str(QA067_LINEAGE_ID),
            },
            created_at=now,
        )
    )
    session.merge(
        WorkflowRunRecord(
            workflow_run_id=QA067_RUN_ID,
            tenant_id=ACME_TENANT_ID,
            scope_type="tenant",
            initiating_principal_id="tenant-admin-acme",
            run_bundle_id=QA067_BUNDLE_ID,
            status=RuntimeRunStatus.PAUSED,
            current_step_id=QA067_APPROVAL_STEP_ID,
            pause_reason="Waiting for manager approval.",
            idempotency_key="qa067-runtime-agent-graph",
            trace_id="trace-qa067-runtime-agent-graph",
            started_at=now,
        )
    )
    for record in _runtime_steps(now):
        session.merge(record)
    for record in _timeline_events(now):
        session.merge(record)
    session.merge(
        HandoffEnvelopeRecord(
            handoff_envelope_id=UUID("67676767-8201-4767-8767-000000000067"),
            tenant_id=ACME_TENANT_ID,
            workflow_run_id=QA067_RUN_ID,
            sender_step_id=QA067_COORDINATOR_STEP_ID,
            receiver_step_key="specialist",
            contract_id="brief",
            contract_version="1.0.0",
            contract_digest="8" * 64,
            status=RuntimeHandoffStatus.VALID,
            payload_hash="9" * 64,
            payload_ref={
                "safe_summary": "Coordinator sent safe context to Specialist."
            },
            created_at=now,
            validated_at=now,
        )
    )
    session.merge(
        SideEffectIntentRecord(
            side_effect_intent_id=UUID("67676767-8301-4767-8767-000000000067"),
            tenant_id=ACME_TENANT_ID,
            workflow_run_id=QA067_RUN_ID,
            run_step_id=QA067_COORDINATOR_STEP_ID,
            intent_kind="read_only_lookup",
            idempotency_key="qa067-safe-lookup",
            status=RuntimeSideEffectStatus.APPLIED,
            tool_policy_ref="tool-policy:safe-lookup",
            result_ref={"safe_summary": "Read only lookup produced safe evidence."},
            created_at=now,
        )
    )
    session.merge(
        ApprovalGateRecord(
            approval_gate_id=UUID("67676767-8401-4767-8767-000000000067"),
            tenant_id=ACME_TENANT_ID,
            workflow_run_id=QA067_RUN_ID,
            run_step_id=QA067_APPROVAL_STEP_ID,
            status=RuntimeApprovalStatus.PENDING,
            approval_key="manager",
            requested_action={"safe_summary": "Manager approval is pending."},
            created_at=now,
        )
    )


def _runtime_steps(now: datetime) -> list[RunStepRecord]:
    return [
        RunStepRecord(
            run_step_id=QA067_COORDINATOR_STEP_ID,
            tenant_id=ACME_TENANT_ID,
            workflow_run_id=QA067_RUN_ID,
            step_key="coordinator",
            step_type="role",
            status=RuntimeStepStatus.SUCCEEDED,
            attempt=1,
            output_ref={"safe_summary": "Coordinator produced safe runtime evidence."},
            finished_at=now,
            created_at=now,
        ),
        RunStepRecord(
            run_step_id=QA067_SPECIALIST_STEP_ID,
            tenant_id=ACME_TENANT_ID,
            workflow_run_id=QA067_RUN_ID,
            step_key="specialist",
            step_type="role",
            status=RuntimeStepStatus.RETRY_SCHEDULED,
            attempt=2,
            error_ref={
                "safe_summary": "Specialist is retry scheduled with safe evidence."
            },
            next_retry_at=now,
            created_at=now,
        ),
        RunStepRecord(
            run_step_id=QA067_APPROVAL_STEP_ID,
            tenant_id=ACME_TENANT_ID,
            workflow_run_id=QA067_RUN_ID,
            step_key="approval",
            step_type="approval",
            status=RuntimeStepStatus.PAUSED,
            attempt=1,
            input_ref={"safe_summary": "Approval is waiting for a manager decision."},
            created_at=now,
        ),
        RunStepRecord(
            run_step_id=QA067_DONE_STEP_ID,
            tenant_id=ACME_TENANT_ID,
            workflow_run_id=QA067_RUN_ID,
            step_key="done",
            step_type="terminal",
            status=RuntimeStepStatus.PENDING,
            attempt=1,
            created_at=now,
        ),
    ]


def _timeline_events(now: datetime) -> list[RuntimeTimelineEventRecord]:
    return [
        RuntimeTimelineEventRecord(
            runtime_timeline_event_id=UUID("67676767-8101-4767-8767-000000000067"),
            tenant_id=ACME_TENANT_ID,
            workflow_run_id=QA067_RUN_ID,
            run_step_id=QA067_COORDINATOR_STEP_ID,
            event_type="coordinator_completed",
            severity="info",
            payload={"safe_summary": "Coordinator completed with safe evidence."},
            trace_id="trace-qa067-runtime-agent-graph",
            created_at=now,
        ),
        RuntimeTimelineEventRecord(
            runtime_timeline_event_id=UUID("67676767-8102-4767-8767-000000000067"),
            tenant_id=ACME_TENANT_ID,
            workflow_run_id=QA067_RUN_ID,
            run_step_id=QA067_SPECIALIST_STEP_ID,
            event_type="specialist_retry_scheduled",
            severity="warning",
            payload={"safe_summary": "Specialist retry was scheduled safely."},
            trace_id="trace-qa067-runtime-agent-graph",
            created_at=now,
        ),
        RuntimeTimelineEventRecord(
            runtime_timeline_event_id=UUID("67676767-8103-4767-8767-000000000067"),
            tenant_id=ACME_TENANT_ID,
            workflow_run_id=QA067_RUN_ID,
            run_step_id=QA067_APPROVAL_STEP_ID,
            event_type="approval_paused",
            severity="warning",
            payload={"safe_summary": "Approval is paused for manager review."},
            trace_id="trace-qa067-runtime-agent-graph",
            created_at=now,
        ),
        RuntimeTimelineEventRecord(
            runtime_timeline_event_id=UUID("67676767-8104-4767-8767-000000000067"),
            tenant_id=ACME_TENANT_ID,
            workflow_run_id=QA067_RUN_ID,
            run_step_id=None,
            event_type="unmapped_summary",
            severity="info",
            payload={
                "safe_summary": "Graph-level partial evidence is retained safely."
            },
            trace_id="trace-qa067-runtime-agent-graph",
            created_at=now,
        ),
    ]


def _workflow_document() -> dict[str, object]:
    return {
        "workflow_key": "qa067-runtime-agent-graph",
        "display_name": "QA067 Runtime Agent Graph",
        "description": "Workflow for runtime communication graph QA.",
        "workflow_kind": "main_workflow",
        "entry_node_key": "coordinator",
        "roles": [
            {
                "role_key": "coordinator",
                "display_name": "Coordinator",
                "role_kind": "agent",
                "purpose": "Coordinate runtime work.",
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
                "purpose": "Review runtime context.",
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


if __name__ == "__main__":
    raise SystemExit(main())
