from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.admin.workflow_registry.publish_gate import (
    PUBLISH_GATE_BLOCKED,
    PUBLISH_GATE_READY,
    evaluate_publish_gate,
)
from multi_agent_platform.api.schemas.workflow_editor import (
    ReferenceReadinessSnapshot,
    RequiredTestSummary,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    ValidationFindingResponse,
    ValidationResultResponse,
)


def test_publish_gate_is_ready_for_current_passing_validation() -> None:
    validation_id = uuid4()
    gate = evaluate_publish_gate(
        workflow_draft_id=str(uuid4()),
        workflow_draft_revision_id=str(uuid4()),
        document_sha256="a" * 64,
        validation=ValidationResultResponse(
            validation_result_id=validation_id,
            status="passed",
            blocking_issue_count=0,
            advisory_issue_count=0,
        ),
        reference_readiness=[],
        required_test_summary=RequiredTestSummary(),
        current_validation_result_id=str(validation_id),
        requested_validation_result_id=str(validation_id),
    )

    assert gate.status == PUBLISH_GATE_READY
    assert gate.digest


def test_publish_gate_blocks_failed_validation() -> None:
    validation_id = uuid4()
    gate = evaluate_publish_gate(
        workflow_draft_id=str(uuid4()),
        workflow_draft_revision_id=str(uuid4()),
        document_sha256="a" * 64,
        validation=ValidationResultResponse(
            validation_result_id=validation_id,
            status="failed",
            blocking_issue_count=1,
            advisory_issue_count=0,
        ),
        reference_readiness=[],
        required_test_summary=RequiredTestSummary(),
        current_validation_result_id=str(validation_id),
        requested_validation_result_id=str(validation_id),
    )

    assert gate.status == PUBLISH_GATE_BLOCKED
    assert gate.blocking_issue_count >= 1


def test_publish_gate_blocks_missing_validation_and_keeps_validation_findings() -> None:
    missing = evaluate_publish_gate(
        workflow_draft_id=str(uuid4()),
        workflow_draft_revision_id=str(uuid4()),
        document_sha256="c" * 64,
        validation=None,
        reference_readiness=[],
        required_test_summary=RequiredTestSummary(),
    )
    failed_validation = evaluate_publish_gate(
        workflow_draft_id=str(uuid4()),
        workflow_draft_revision_id=str(uuid4()),
        document_sha256="d" * 64,
        validation=ValidationResultResponse(
            validation_result_id=uuid4(),
            status="failed",
            blocking_issue_count=1,
            advisory_issue_count=0,
            findings=[
                ValidationFindingResponse(
                    category="graph",
                    severity="blocking",
                    message="Missing edge",
                    field_path="nodes[0]",
                    blocking=True,
                )
            ],
        ),
        reference_readiness=[],
        required_test_summary=RequiredTestSummary(),
    )

    assert missing.status == PUBLISH_GATE_BLOCKED
    assert any(
        finding.code == "publish_gate.validation.missing"
        for finding in missing.findings
    )
    assert failed_validation.status == PUBLISH_GATE_BLOCKED
    assert any(
        finding.message == "Missing edge" for finding in failed_validation.findings
    )


def test_publish_gate_reports_unauthorized_stale_and_reference_blocks() -> None:
    validation_id = uuid4()
    validation = ValidationResultResponse(
        validation_result_id=validation_id,
        status="passed",
        blocking_issue_count=0,
        advisory_issue_count=0,
    )

    unauthorized = evaluate_publish_gate(
        workflow_draft_id=str(uuid4()),
        workflow_draft_revision_id=str(uuid4()),
        document_sha256="b" * 64,
        validation=validation,
        reference_readiness=[],
        required_test_summary=RequiredTestSummary(),
        authorized=False,
    )
    stale = evaluate_publish_gate(
        workflow_draft_id=str(uuid4()),
        workflow_draft_revision_id=str(uuid4()),
        document_sha256="b" * 64,
        validation=validation,
        reference_readiness=[],
        required_test_summary=RequiredTestSummary(),
        current_validation_result_id=str(uuid4()),
    )
    blocked = evaluate_publish_gate(
        workflow_draft_id=str(uuid4()),
        workflow_draft_revision_id=str(uuid4()),
        document_sha256="b" * 64,
        validation=validation,
        reference_readiness=[
            ReferenceReadinessSnapshot(
                reference_type="skill",
                reference_key="triage",
                status="blocked",
                blocking=True,
            )
        ],
        required_test_summary=RequiredTestSummary(required_count=1, missing_count=1),
    )

    assert unauthorized.status == "unauthorized"
    assert stale.status == "stale"
    assert blocked.status == "blocked"
    assert any(finding.reference_type == "skill" for finding in blocked.findings)
