from __future__ import annotations

import pytest
from pydantic import ValidationError

from multi_agent_platform.api.schemas.admin_workflow_builder import (
    ValidationFinding,
    WorkflowBuilderSeverity,
    WorkflowBuilderStatus,
    WorkflowEvidenceSummary,
    WorkflowGraphNode,
    WorkflowJsonInspector,
    WorkflowPublishReadiness,
    WorkflowReferenceOption,
    WorkflowValidationSummary,
)


def test_workflow_builder_reference_text_rejects_unsafe_markers() -> None:
    option = WorkflowReferenceOption(
        reference_id="prompt-safe",
        label="Daily briefing prompt",
        kind="prompt",
        readiness_status=WorkflowBuilderStatus.READY,
        safe_summary="Published prompt reference is available.",
    )

    assert option.safe_summary == "Published prompt reference is available."

    with pytest.raises(ValidationError):
        WorkflowReferenceOption(
            reference_id="prompt-unsafe",
            label="Daily briefing prompt",
            kind="prompt",
            readiness_status=WorkflowBuilderStatus.READY,
            safe_summary="raw prompt copied into React",
        )


def test_graph_and_validation_reject_raw_payload_markers() -> None:
    with pytest.raises(ValidationError):
        WorkflowGraphNode(
            node_id="node-unsafe",
            label="Unsafe node",
            node_type="tool",
            status=WorkflowBuilderStatus.WARNING,
            summary="raw tool result was displayed",
        )

    with pytest.raises(ValidationError):
        ValidationFinding(
            finding_id="finding-unsafe",
            severity=WorkflowBuilderSeverity.BLOCKING,
            category="validation",
            section="Graph",
            message="private channel message copied into finding",
            recommended_action="Remove the payload.",
        )


def test_publish_evidence_rejects_local_artifact_paths() -> None:
    evidence = WorkflowEvidenceSummary(
        evidence_id="evidence-safe",
        label="Required suite",
        status=WorkflowBuilderStatus.READY,
        summary="Repository-backed evidence is current.",
        artifact_reference_id="artifact-ref-qa030-ready-evidence",
    )

    assert evidence.artifact_reference_id == "artifact-ref-qa030-ready-evidence"

    with pytest.raises(ValidationError):
        WorkflowEvidenceSummary(
            evidence_id="evidence-unsafe",
            label="Required suite",
            status=WorkflowBuilderStatus.READY,
            summary="Repository-backed evidence is current.",
            artifact_reference_id="/Users/scott/raw-evidence.json",
        )


def test_json_inspector_and_publish_readiness_are_safe() -> None:
    inspector = WorkflowJsonInspector(
        summary="Advanced JSON is read-only and redacted.",
        redaction_summary="Prompts, memory, credentials, and payloads are summarized.",
        safe_document_preview={"workflow": "Daily briefing workflow"},
        artifact_reference_id="artifact-ref-qa030-json-preview",
    )
    readiness = WorkflowPublishReadiness(
        decision="validation_error",
        revision="draft-rev-qa030-current",
        summary="Publish is blocked until evidence is current.",
        blockers=("Required evidence is stale.",),
        required_evidence=(),
    )
    validation = WorkflowValidationSummary(
        validation_id="validation-qa030",
        status=WorkflowBuilderStatus.BLOCKED,
        revision="draft-rev-qa030-current",
        generated_at_label="Generated for QA030",
        summary="Validation found publish blockers.",
    )

    assert inspector.safe_document_preview["workflow"] == "Daily briefing workflow"
    assert readiness.blockers == ("Required evidence is stale.",)
    assert validation.findings == ()

    with pytest.raises(ValidationError):
        WorkflowJsonInspector(
            summary="Advanced JSON is read-only.",
            redaction_summary="provider authorization header is visible",
            safe_document_preview={"workflow": "Daily briefing workflow"},
        )
