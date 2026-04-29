from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class FieldHelpDefinition(BaseModel):
    field_key: str
    label: str
    title: str
    explanation: str
    runtime_impact: str
    example: str | None = None
    validation_hint: str | None = None


class EditorOption(BaseModel):
    value: str
    label: str
    description: str | None = None
    disabled: bool = False


class EditorSectionDefinition(BaseModel):
    section_key: str
    label: str
    description: str
    field_paths: list[str] = Field(default_factory=list)


class EditorFieldDefinition(BaseModel):
    field_path: str
    label: str
    section_key: str
    input_type: str = "text"
    required: bool = False
    lookup_source: str | None = None
    help_key: str | None = None


class EditorCapability(BaseModel):
    capability_key: str
    allowed: bool
    reason: str | None = None


class EditorActionUrls(BaseModel):
    create_draft: str = "/admin/workflows"
    editor_metadata: str = "/admin/workflows/editor-metadata"
    editor_lookups: str = "/admin/workflows/editor-lookups"
    draft_base: str = "/admin/workflows/drafts"
    registry_ui: str = "/admin/workflows/ui"
    create_ui: str = "/admin/workflows/new"


class ValidationCodeMapping(BaseModel):
    code: str
    section_key: str
    field_path_template: str
    blocking: bool = True
    remediation: str


class EditorLookupOption(BaseModel):
    option_id: str
    label: str
    value: str
    lookup_kind: str
    scope_type: str
    tenant_id: str | None = None
    status: str = "available"
    description: str | None = None
    detail_url: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class EditorLookupGroup(BaseModel):
    lookup_kind: str
    label: str
    options: list[EditorLookupOption] = Field(default_factory=list)


class EditorLookupResponse(BaseModel):
    groups: list[EditorLookupGroup] = Field(default_factory=list)
    denied_count: int = 0
    safe_denial_message: str | None = None


class GraphValidationBadge(BaseModel):
    code: str
    severity: str
    message: str
    blocking: bool = True


class GraphPreviewNode(BaseModel):
    id: str
    node_key: str
    node_type: str
    label: str
    field_path: str
    role_key: str | None = None
    terminal: bool = False
    badges: list[GraphValidationBadge] = Field(default_factory=list)


class GraphPreviewEdge(BaseModel):
    id: str
    edge_key: str
    source: str
    target: str
    label: str
    field_path: str
    contract_key: str | None = None
    edge_type: str = "success"
    badges: list[GraphValidationBadge] = Field(default_factory=list)


class GraphPreviewSummary(BaseModel):
    entry_node_id: str | None = None
    terminal_node_ids: list[str] = Field(default_factory=list)
    node_count: int = 0
    edge_count: int = 0
    disconnected_node_ids: list[str] = Field(default_factory=list)
    cycle_summaries: list[str] = Field(default_factory=list)
    join_summaries: list[str] = Field(default_factory=list)
    approval_loop_summaries: list[str] = Field(default_factory=list)


class GraphPreviewResponse(BaseModel):
    nodes: list[GraphPreviewNode] = Field(default_factory=list)
    edges: list[GraphPreviewEdge] = Field(default_factory=list)
    summary: GraphPreviewSummary = Field(default_factory=GraphPreviewSummary)
    field_to_graph: dict[str, str] = Field(default_factory=dict)


class BuilderValidationFinding(BaseModel):
    category: str
    severity: str
    message: str
    field_path: str | None = None
    section_key: str | None = None
    code: str | None = None
    remediation: str | None = None
    blocking: bool = False
    graph_element_id: str | None = None
    reference_type: str | None = None
    reference_id: str | None = None
    safe_links: list[str] = Field(default_factory=list)


class ReferenceReadinessSnapshot(BaseModel):
    reference_type: str
    reference_key: str
    status: str
    blocking: bool = False
    detail_url: str | None = None
    safe_summary: str | None = None
    pin_payload: dict[str, Any] = Field(default_factory=dict)


class RequiredTestSummary(BaseModel):
    required_count: int = 0
    passing_count: int = 0
    failing_count: int = 0
    missing_count: int = 0
    stale_count: int = 0


class PublishGateRequest(BaseModel):
    validation_result_id: str | None = None
    reason: str | None = None


class PublishGateResponse(BaseModel):
    publish_gate_id: str
    workflow_draft_id: str
    workflow_draft_revision_id: str
    document_sha256: str
    validation_result_id: str | None = None
    status: str
    blocking_issue_count: int = 0
    advisory_issue_count: int = 0
    findings: list[BuilderValidationFinding] = Field(default_factory=list)
    reference_readiness: list[ReferenceReadinessSnapshot] = Field(default_factory=list)
    pin_summary: dict[str, Any] = Field(default_factory=dict)
    required_test_summary: RequiredTestSummary = Field(
        default_factory=RequiredTestSummary
    )
    expires_at: datetime | None = None
    digest: str


class ConflictResponse(BaseModel):
    conflict_type: str
    message: str
    current_revision_number: int | None = None
    current_revision_id: str | None = None
    refresh_url: str | None = None


class WorkflowEditorMetadataResponse(BaseModel):
    field_help: dict[str, FieldHelpDefinition] = Field(default_factory=dict)
    scope_options: list[EditorOption] = Field(default_factory=list)
    workflow_kind_options: list[EditorOption] = Field(default_factory=list)
    section_order: list[str] = Field(default_factory=list)
    sections: list[EditorSectionDefinition] = Field(default_factory=list)
    fields: list[EditorFieldDefinition] = Field(default_factory=list)
    lookup_sources: dict[str, str] = Field(default_factory=dict)
    capabilities: list[EditorCapability] = Field(default_factory=list)
    action_urls: EditorActionUrls = Field(default_factory=EditorActionUrls)
    validation_codes: list[ValidationCodeMapping] = Field(default_factory=list)
