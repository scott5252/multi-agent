from __future__ import annotations

import pytest
from pydantic import ValidationError

from multi_agent_platform.api.schemas.admin_patterns import (
    AdminAction,
    AdminActionMethod,
    PaginationState,
    SortField,
    SortingState,
)
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminEmptyStateMetadata,
    ReactAdminEmptyStateReason,
    ReactAdminPageActionVariant,
    ReactAdminPageProvenance,
    ReactAdminScope,
    ReactAdminScopeType,
    ReactAdminSourceKind,
)
from multi_agent_platform.api.schemas.admin_workflow_builder import (
    ValidationFinding,
    WorkflowBuilderSeverity,
    WorkflowBuilderStatus,
    WorkflowCreateEnvelope,
    WorkflowEvidenceSummary,
    WorkflowGraphNode,
    WorkflowJsonInspector,
    WorkflowPublishReadiness,
    WorkflowReferenceOption,
    WorkflowRegistryEnvelope,
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
            safe_summary="raw prompt copied into Admin",
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


def test_registry_and_create_envelopes_accept_live_metadata() -> None:
    scope = ReactAdminScope(
        scope_type=ReactAdminScopeType.TENANT,
        tenant_id="11111111-1111-1111-1111-111111111111",
        label="Acme",
    )
    provenance = ReactAdminPageProvenance(
        source_kind=ReactAdminSourceKind.EMPTY_LIVE_STATE,
        source_label="Workflow registry records",
        source_detail="Read from durable workflow registry tables.",
    )
    empty_state = ReactAdminEmptyStateMetadata(
        reason=ReactAdminEmptyStateReason.NO_LIVE_ROWS,
        title="No workflows found",
        summary="No authorized workflow records exist for this scope.",
        setup_hint="Create a workflow draft to populate the registry.",
        provenance=provenance,
    )
    create_action = AdminAction(
        action_id="workflow-create",
        label="Create workflow",
        method=AdminActionMethod.GET,
        href="/admin/app/workflows/new",
        variant=ReactAdminPageActionVariant.PRIMARY,
    )

    registry = WorkflowRegistryEnvelope(
        page_id="workflow-registry-react",
        title="Workflow registry",
        summary="Live workflow registry.",
        scope=scope,
        pagination=PaginationState(page_size=10, total_items=0),
        sorting=SortingState(
            active=SortField(key="updated_desc", label="Latest updated")
        ),
        create_action=create_action,
        provenance=provenance,
        empty_state=empty_state,
    )
    create = WorkflowCreateEnvelope(
        page_id="workflow-create-react",
        title="Create workflow",
        summary="Start a durable workflow draft.",
        create_action=create_action,
        provenance=provenance,
        empty_state=empty_state,
    )

    assert registry.pagination is not None
    assert registry.pagination.total_items == 0
    assert registry.empty_state == empty_state
    assert create.provenance == provenance
