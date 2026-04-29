from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.api.schemas.workflow_editor import (
    WorkflowEditorMetadataResponse,
)
from multi_agent_platform.api.schemas.workflow_registry import WorkflowDraftResponse
from multi_agent_platform.api.ui.admin_workflows import (
    build_workflow_draft_editor_model,
    build_workflow_registry_page_model,
)


def test_registry_page_model_builds_default_paths() -> None:
    page = build_workflow_registry_page_model([])
    assert page.create_endpoint == "/admin/workflows"
    assert page.editor_base_path.endswith("/drafts")
    assert page.active_scope_filter == "all"
    assert page.active_status_filter == "all"


def test_registry_page_model_preserves_active_filters() -> None:
    page = build_workflow_registry_page_model(
        [],
        scope_filter="tenant",
        status_filter="publish_ready",
        search_query="triage",
    )
    assert page.active_scope_filter == "tenant"
    assert page.active_status_filter == "publish_ready"
    assert page.search_query == "triage"


def test_draft_editor_model_serializes_document(sample_workflow_document) -> None:
    draft = WorkflowDraftResponse(
        workflow_draft_id=uuid4(),
        workflow_lineage_id=uuid4(),
        slug="customer-intake",
        display_name="Customer Intake",
        description="Example",
        scope_type="platform",
        tenant_id=None,
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
    page = build_workflow_draft_editor_model(
        draft=draft,
        metadata=WorkflowEditorMetadataResponse(),
        conflict_message="Reload required",
    )
    assert "customer-intake" in page.document_json
    assert page.conflict_message == "Reload required"
