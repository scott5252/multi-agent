from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.api.schemas.workflow_editor import (
    GraphPreviewResponse,
    PublishGateResponse,
    RequiredTestSummary,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    DraftRevisionListResponse,
    WorkflowDraftResponse,
    WorkflowDraftRevisionResponse,
)
from multi_agent_platform.api.ui.admin_workflows import (
    build_workflow_draft_editor_model,
    build_workflow_publish_gate_model,
    build_workflow_revision_history_model,
)


def _draft(sample_workflow_document) -> WorkflowDraftResponse:
    return WorkflowDraftResponse(
        workflow_draft_id=uuid4(),
        workflow_lineage_id=uuid4(),
        slug="customer-intake",
        display_name="Customer Intake",
        scope_type="platform",
        workflow_kind="main_workflow",
        status="active",
        current_revision_number=1,
        latest_revision={
            "workflow_draft_revision_id": uuid4(),
            "revision_number": 1,
            "document_sha256": "abc",
            "created_at": "2026-04-23T00:00:00+00:00",
        },
        document=sample_workflow_document,
        updated_at="2026-04-23T00:00:00+00:00",
    )


def test_editor_model_includes_builder_action_urls(sample_workflow_document) -> None:
    draft = _draft(sample_workflow_document)
    page = build_workflow_draft_editor_model(
        draft=draft,
        metadata={},
        graph_preview=GraphPreviewResponse(),
    )

    assert page.validate_endpoint.endswith("/validate")
    assert page.publish_gate_endpoint.endswith("/publish-gate")
    assert page.revision_history_path.endswith("/revisions/ui")


def test_revision_and_publish_gate_models(sample_workflow_document) -> None:
    draft = _draft(sample_workflow_document)
    revision = WorkflowDraftRevisionResponse(
        workflow_draft_revision_id=draft.latest_revision.workflow_draft_revision_id,
        revision_number=1,
        document_sha256="abc",
        created_at=draft.latest_revision.created_at,
    )
    revisions = DraftRevisionListResponse(
        workflow_draft_id=draft.workflow_draft_id,
        current_revision_number=1,
        revisions=[revision],
    )
    history = build_workflow_revision_history_model(draft=draft, revisions=revisions)
    gate = PublishGateResponse(
        publish_gate_id="gate",
        workflow_draft_id=str(draft.workflow_draft_id),
        workflow_draft_revision_id=str(revision.workflow_draft_revision_id),
        document_sha256="abc",
        status="ready",
        required_test_summary=RequiredTestSummary(),
        digest="digest",
    )
    publish = build_workflow_publish_gate_model(draft=draft, gate=gate)

    assert history.restore_endpoint.endswith("/restore")
    assert publish.publish_endpoint.endswith("/publish")
