from __future__ import annotations

from pydantic import BaseModel, Field

from multi_agent_platform.api.schemas.workflow_editor import (
    WorkflowEditorMetadataResponse,
)
from multi_agent_platform.api.schemas.workflow_registry import (
    WorkflowDraftResponse,
    WorkflowRegistryItem,
)


class WorkflowRegistryPageModel(BaseModel):
    items: list[WorkflowRegistryItem] = Field(default_factory=list)
    create_endpoint: str = "/admin/workflows"
    editor_base_path: str = "/admin/workflows/drafts"


class WorkflowDraftEditorPageModel(BaseModel):
    draft: WorkflowDraftResponse
    metadata: WorkflowEditorMetadataResponse
    document_json: str
    save_endpoint: str
    conflict_message: str | None = None


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
        conflict_message=conflict_message,
    )
