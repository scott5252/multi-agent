from __future__ import annotations

from pydantic import BaseModel, Field

from multi_agent_platform.api.schemas.workflow_editor import (
    EditorLookupResponse,
    GraphPreviewResponse,
    PublishGateResponse,
    WorkflowEditorMetadataResponse,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    DraftRevisionListResponse,
    ValidationResultResponse,
    WorkflowDraftResponse,
    WorkflowRegistryItem,
    WorkflowVersionResponse,
)
from multi_agent_platform.api.ui.admin_console import FilterProfile, filter_profiles


class WorkflowRegistryPageModel(BaseModel):
    items: list[WorkflowRegistryItem] = Field(default_factory=list)
    create_endpoint: str = "/admin/workflows"
    create_page_path: str = "/admin/workflows/new"
    editor_base_path: str = "/admin/workflows/drafts"
    version_base_path: str = "/admin/workflows/versions"
    scope_filters: list[str] = Field(
        default_factory=lambda: ["all", "tenant", "platform"]
    )
    status_filters: list[str] = Field(
        default_factory=lambda: [
            "draft",
            "validation_failed",
            "publish_ready",
            "published",
            "hidden",
            "retired",
        ]
    )


class WorkflowDraftEditorPageModel(BaseModel):
    draft: WorkflowDraftResponse
    metadata: WorkflowEditorMetadataResponse
    document_json: str
    save_endpoint: str
    validate_endpoint: str
    publish_endpoint: str
    publish_gate_endpoint: str
    revision_history_path: str
    graph_preview: GraphPreviewResponse
    lookups: EditorLookupResponse
    publish_ready: bool = False
    latest_validation: ValidationResultResponse | None = None
    validation_groups: dict[str, list[str]] = Field(default_factory=dict)
    conflict_message: str | None = None


class WorkflowVersionDetailPageModel(BaseModel):
    version: WorkflowVersionResponse
    source_revision_id: str | None = None
    publish_gate_digest: str | None = None
    pin_summary: dict[str, object] = Field(default_factory=dict)


class WorkflowDraftCreatePageModel(BaseModel):
    metadata: WorkflowEditorMetadataResponse
    create_endpoint: str = "/admin/workflows"


class WorkflowDraftRevisionHistoryPageModel(BaseModel):
    draft: WorkflowDraftResponse
    revisions: DraftRevisionListResponse
    restore_endpoint: str
    copy_endpoint: str


class WorkflowPublishGatePageModel(BaseModel):
    draft: WorkflowDraftResponse
    gate: PublishGateResponse
    publish_endpoint: str


def build_workflow_registry_page_model(
    items: list[WorkflowRegistryItem],
) -> WorkflowRegistryPageModel:
    return WorkflowRegistryPageModel(items=items)


def build_workflow_draft_editor_model(
    *,
    draft: WorkflowDraftResponse,
    metadata: WorkflowEditorMetadataResponse,
    graph_preview: GraphPreviewResponse | None = None,
    lookups: EditorLookupResponse | None = None,
    conflict_message: str | None = None,
) -> WorkflowDraftEditorPageModel:
    latest_validation = draft.latest_validation
    return WorkflowDraftEditorPageModel(
        draft=draft,
        metadata=metadata,
        document_json=draft.document.model_dump_json(indent=2),
        save_endpoint=f"/admin/workflows/drafts/{draft.workflow_draft_id}",
        validate_endpoint=f"/admin/workflows/drafts/{draft.workflow_draft_id}/validate",
        publish_endpoint=f"/admin/workflows/drafts/{draft.workflow_draft_id}/publish",
        publish_gate_endpoint=(
            f"/admin/workflows/drafts/{draft.workflow_draft_id}/publish-gate"
        ),
        revision_history_path=(
            f"/admin/workflows/drafts/{draft.workflow_draft_id}/revisions/ui"
        ),
        graph_preview=graph_preview or GraphPreviewResponse(),
        lookups=lookups or EditorLookupResponse(),
        publish_ready=(
            latest_validation is not None
            and latest_validation.status == "passed"
            and latest_validation.blocking_issue_count == 0
        ),
        latest_validation=latest_validation,
        validation_groups=_validation_groups(latest_validation),
        conflict_message=conflict_message,
    )


def build_workflow_version_detail_model(
    *,
    version: WorkflowVersionResponse,
) -> WorkflowVersionDetailPageModel:
    summary = version.summary_json
    raw_source_revision_id = summary.get("source_draft_revision_id")
    raw_publish_gate_digest = summary.get("publish_gate_digest")
    pin_summary = {
        "prompt_profile_pins": summary.get("prompt_profile_pins", []),
        "model_routing_provenance": summary.get("model_routing_provenance", []),
        "skill_installation_pins": summary.get("skill_installation_pins", []),
        "subworkflow_bundle_pins": summary.get("subworkflow_bundle_pins", []),
        "required_test_evidence": summary.get("required_test_evidence", {}),
    }
    return WorkflowVersionDetailPageModel(
        version=version,
        source_revision_id=raw_source_revision_id
        if isinstance(raw_source_revision_id, str)
        else None,
        publish_gate_digest=raw_publish_gate_digest
        if isinstance(raw_publish_gate_digest, str)
        else None,
        pin_summary=pin_summary,
    )


def build_workflow_draft_create_page_model(
    metadata: WorkflowEditorMetadataResponse,
) -> WorkflowDraftCreatePageModel:
    return WorkflowDraftCreatePageModel(metadata=metadata)


def build_workflow_revision_history_model(
    *,
    draft: WorkflowDraftResponse,
    revisions: DraftRevisionListResponse,
) -> WorkflowDraftRevisionHistoryPageModel:
    return WorkflowDraftRevisionHistoryPageModel(
        draft=draft,
        revisions=revisions,
        restore_endpoint=f"/admin/workflows/drafts/{draft.workflow_draft_id}/restore",
        copy_endpoint=f"/admin/workflows/drafts/{draft.workflow_draft_id}/copy",
    )


def build_workflow_publish_gate_model(
    *,
    draft: WorkflowDraftResponse,
    gate: PublishGateResponse,
) -> WorkflowPublishGatePageModel:
    return WorkflowPublishGatePageModel(
        draft=draft,
        gate=gate,
        publish_endpoint=f"/admin/workflows/drafts/{draft.workflow_draft_id}/publish",
    )


def workflow_filter_profile() -> FilterProfile:
    return filter_profiles()["workflows"]


def _validation_groups(
    validation: ValidationResultResponse | None,
) -> dict[str, list[str]]:
    if validation is None:
        return {}
    grouped: dict[str, list[str]] = {}
    for finding in validation.findings:
        section = finding.section_key or finding.category
        grouped.setdefault(section, []).append(finding.message)
    return grouped
