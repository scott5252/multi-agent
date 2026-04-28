from __future__ import annotations

from pydantic import BaseModel, Field

from multi_agent_platform.api.schemas.workflow_editor import (
    WorkflowEditorMetadataResponse,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    ValidationResultResponse,
    WorkflowDraftResponse,
    WorkflowRegistryItem,
    WorkflowVersionResponse,
)
from multi_agent_platform.api.ui.admin_console import FilterProfile, filter_profiles


class WorkflowRegistryPageModel(BaseModel):
    items: list[WorkflowRegistryItem] = Field(default_factory=list)
    create_endpoint: str = "/admin/workflows"
    editor_base_path: str = "/admin/workflows/drafts"
    version_base_path: str = "/admin/workflows/versions"


class WorkflowDraftEditorPageModel(BaseModel):
    draft: WorkflowDraftResponse
    metadata: WorkflowEditorMetadataResponse
    document_json: str
    save_endpoint: str
    publish_endpoint: str
    publish_ready: bool = False
    latest_validation: ValidationResultResponse | None = None
    conflict_message: str | None = None


class WorkflowVersionDetailPageModel(BaseModel):
    version: WorkflowVersionResponse


def build_workflow_registry_page_model(
    items: list[WorkflowRegistryItem],
) -> WorkflowRegistryPageModel:
    return WorkflowRegistryPageModel(items=items)


def build_workflow_draft_editor_model(
    *,
    draft: WorkflowDraftResponse,
    metadata: WorkflowEditorMetadataResponse,
    conflict_message: str | None = None,
) -> WorkflowDraftEditorPageModel:
    return WorkflowDraftEditorPageModel(
        draft=draft,
        metadata=metadata,
        document_json=draft.document.model_dump_json(indent=2),
        save_endpoint=f"/admin/workflows/drafts/{draft.workflow_draft_id}",
        publish_endpoint=f"/admin/workflows/drafts/{draft.workflow_draft_id}/publish",
        publish_ready=(
            draft.latest_validation is not None
            and draft.latest_validation.status == "passed"
        ),
        latest_validation=draft.latest_validation,
        conflict_message=conflict_message,
    )


def build_workflow_version_detail_model(
    *,
    version: WorkflowVersionResponse,
) -> WorkflowVersionDetailPageModel:
    return WorkflowVersionDetailPageModel(version=version)


def workflow_filter_profile() -> FilterProfile:
    return filter_profiles()["workflows"]
