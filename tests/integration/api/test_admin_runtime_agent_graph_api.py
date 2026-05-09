from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from multi_agent_platform.api.main import create_app
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
from tests.fixtures.runtime_agent_graph import runtime_graph_document_dict
from tests.integration.api.test_admin_agent_graph_api import configure_env


def _seed_runtime_run(
    *,
    database_path: Path,
    tenant_id: UUID,
    workflow_version_bundle_id: UUID,
    status: RuntimeRunStatus = RuntimeRunStatus.RUNNING,
    specialist_status: RuntimeStepStatus = RuntimeStepStatus.RETRY_SCHEDULED,
) -> UUID:
    engine = create_engine(f"sqlite:///{database_path}")
    workflow_run_id = uuid4()
    run_bundle_id = uuid4()
    now = datetime.now(UTC)
    coordinator_step_id = uuid4()
    specialist_step_id = uuid4()
    approval_step_id = uuid4()
    document = runtime_graph_document_dict()
    with Session(engine) as session:
        session.add(
            RuntimeExecutionBundleRecord(
                run_bundle_id=run_bundle_id,
                tenant_id=tenant_id,
                workflow_run_id=workflow_run_id,
                published_workflow_version_id=workflow_version_bundle_id,
                bundle_digest="d" * 64,
                workflow_version={
                    "display_name": "Runtime Agent Review",
                    "document": document,
                    "workflow_key": "runtime-agent-review",
                    "workflow_lineage_id": str(uuid4()),
                },
                created_at=now,
            )
        )
        session.add(
            WorkflowRunRecord(
                workflow_run_id=workflow_run_id,
                tenant_id=tenant_id,
                scope_type="tenant",
                initiating_principal_id="tenant-admin-acme",
                run_bundle_id=run_bundle_id,
                status=status,
                idempotency_key=f"runtime-graph-api-{workflow_run_id}",
                trace_id=f"trace-{workflow_run_id}",
                started_at=now,
            )
        )
        steps = [
            RunStepRecord(
                run_step_id=coordinator_step_id,
                workflow_run_id=workflow_run_id,
                tenant_id=tenant_id,
                step_key="coordinator",
                step_type="role",
                status=RuntimeStepStatus.SUCCEEDED,
                attempt=1,
                output_ref={"safe_summary": "Coordinator produced safe evidence."},
            ),
            RunStepRecord(
                run_step_id=specialist_step_id,
                workflow_run_id=workflow_run_id,
                tenant_id=tenant_id,
                step_key="specialist",
                step_type="role",
                status=specialist_status,
                attempt=1,
                error_ref={"safe_summary": "Specialist has safe retry evidence."},
            ),
            RunStepRecord(
                run_step_id=approval_step_id,
                workflow_run_id=workflow_run_id,
                tenant_id=tenant_id,
                step_key="approval",
                step_type="approval",
                status=RuntimeStepStatus.PAUSED,
                attempt=1,
                input_ref={"safe_summary": "Approval is waiting safely."},
            ),
            RunStepRecord(
                run_step_id=uuid4(),
                workflow_run_id=workflow_run_id,
                tenant_id=tenant_id,
                step_key="done",
                step_type="terminal",
                status=RuntimeStepStatus.PENDING,
                attempt=1,
            ),
        ]
        session.add_all(steps)
        session.add_all(
            [
                RuntimeTimelineEventRecord(
                    runtime_timeline_event_id=uuid4(),
                    tenant_id=tenant_id,
                    workflow_run_id=workflow_run_id,
                    run_step_id=step.run_step_id,
                    event_type=f"{step.step_key}_status",
                    severity="warning"
                    if step.status
                    in {RuntimeStepStatus.PAUSED, RuntimeStepStatus.RETRY_SCHEDULED}
                    else "info",
                    payload={
                        "safe_summary": f"{step.step_key} has safe runtime evidence."
                    },
                    trace_id=f"trace-{workflow_run_id}",
                    created_at=now,
                )
                for step in steps
            ]
        )
        session.add(
            HandoffEnvelopeRecord(
                handoff_envelope_id=uuid4(),
                tenant_id=tenant_id,
                workflow_run_id=workflow_run_id,
                sender_step_id=coordinator_step_id,
                receiver_step_key="specialist",
                contract_id="brief",
                contract_version="1.0.0",
                contract_digest="e" * 64,
                status=RuntimeHandoffStatus.VALID,
                payload_hash="f" * 64,
                payload_ref={"safe_summary": "Safe handoff evidence is available."},
                created_at=now,
            )
        )
        session.add(
            SideEffectIntentRecord(
                side_effect_intent_id=uuid4(),
                tenant_id=tenant_id,
                workflow_run_id=workflow_run_id,
                run_step_id=coordinator_step_id,
                intent_kind="read_only_lookup",
                idempotency_key="runtime-agent-graph-api-tool",
                status=RuntimeSideEffectStatus.APPLIED,
                tool_policy_ref="tool-policy:safe-lookup",
                result_ref={"safe_summary": "Tool evidence was summarized safely."},
            )
        )
        session.add(
            ApprovalGateRecord(
                approval_gate_id=uuid4(),
                tenant_id=tenant_id,
                workflow_run_id=workflow_run_id,
                run_step_id=approval_step_id,
                status=RuntimeApprovalStatus.PENDING,
                approval_key="manager",
                requested_action={"safe_summary": "Manager approval is pending."},
                created_at=now,
            )
        )
        session.add(
            RuntimeInteractionEvidenceRecord(
                interaction_evidence_id=uuid4(),
                tenant_id=tenant_id,
                workflow_run_id=workflow_run_id,
                source_node_key="coordinator",
                target_node_key="specialist",
                source_run_step_id=coordinator_step_id,
                interaction_kind=RuntimeInteractionKind.HANDOFF,
                status=RuntimeInteractionStatus.SENT,
                sequence=1,
                safe_summary="Coordinator sent safe context to Specialist.",
                classification="safe-summary",
                payload_digest="a" * 64,
                artifact_refs=[],
                provenance={"edge_key": "edge-coordinator-specialist"},
                idempotency_key="interaction-runtime-agent-graph-api",
                occurred_at=now,
                created_at=now,
            )
        )
        session.commit()
    return workflow_run_id


def _published_workflow_version(client: TestClient, headers: dict[str, str]) -> UUID:
    created = client.post(
        "/admin/workflows",
        headers=headers,
        json={
            "scope_type": "tenant",
            "workflow_kind": "main_workflow",
            "slug": f"runtime-agent-review-{uuid4()}",
            "display_name": "Runtime Agent Review",
            "document": runtime_graph_document_dict(),
        },
    )
    validated = client.post(
        f"/admin/workflows/drafts/{created.json()['workflow_draft_id']}/validate",
        headers=headers,
    )
    published = client.post(
        f"/admin/workflows/drafts/{created.json()['workflow_draft_id']}/publish",
        headers=headers,
        json={"validation_result_id": validated.json()["validation_result_id"]},
    )
    return UUID(published.json()["workflow_version_bundle_id"])


def test_runtime_agent_graph_route_returns_safe_runtime_projection(
    tmp_path,
    monkeypatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    database_path = tmp_path / "agent-graph-api.db"
    app = create_app()
    headers = {"X-Local-Principal": "tenant-admin-acme"}

    with TestClient(app) as client:
        version_id = _published_workflow_version(client, headers)
        workflow_run_id = _seed_runtime_run(
            database_path=database_path,
            tenant_id=tenant_id,
            workflow_version_bundle_id=version_id,
        )
        response = client.get(
            f"/admin/runs/{workflow_run_id}/agent-graph?tenant_id={tenant_id}",
            headers=headers,
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "runtime_run"
    assert payload["provenance"]["workflow_run_id"] == str(workflow_run_id)
    assert payload["provenance"]["evidence_counts"]["run_steps"] == 4
    assert payload["provenance"]["evidence_counts"]["interaction_evidence"] == 1
    assert "retry_scheduled" in {node["status"] for node in payload["nodes"]}
    assert "paused" in {node["status"] for node in payload["nodes"]}
    assert any(
        reference["reference_type"] == "interaction_evidence"
        for edge in payload["edges"]
        for reference in edge["references"]
    )
    assert "raw prompt" not in json.dumps(payload).lower()
    assert "provider payload" not in json.dumps(payload).lower()


def test_runtime_agent_graph_route_fails_closed_for_denied_and_missing_runs(
    tmp_path,
    monkeypatch,
) -> None:
    tenant_id = uuid4()
    other_tenant_id = uuid4()
    configure_env(monkeypatch, tmp_path, tenant_id, other_tenant_id)
    database_path = tmp_path / "agent-graph-api.db"
    app = create_app()
    headers = {"X-Local-Principal": "tenant-admin-acme"}
    with TestClient(app) as client:
        version_id = _published_workflow_version(client, headers)
        workflow_run_id = _seed_runtime_run(
            database_path=database_path,
            tenant_id=tenant_id,
            workflow_version_bundle_id=version_id,
        )
        denied = client.get(
            f"/admin/runs/{workflow_run_id}/agent-graph?tenant_id={tenant_id}",
            headers={"X-Local-Principal": "tenant-admin-globex"},
        )
        missing = client.get(
            f"/admin/runs/{uuid4()}/agent-graph?tenant_id={tenant_id}",
            headers=headers,
        )

    assert denied.status_code == 403
    assert missing.status_code == 404
    assert "Runtime Agent Review" not in denied.text
