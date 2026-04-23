from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class WorkflowScopeType(StrEnum):
    TENANT = "tenant"
    PLATFORM = "platform"


class WorkflowKind(StrEnum):
    MAIN_WORKFLOW = "main_workflow"
    SUBWORKFLOW = "subworkflow"


class WorkflowVisibilityStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    HIDDEN = "hidden"
    RETIRED = "retired"


class RoleKind(StrEnum):
    AGENT = "agent"
    SUBAGENT = "subagent"


class SkillBindingMode(StrEnum):
    REQUIRED = "required"
    OPTIONAL = "optional"


class WorkflowNodeType(StrEnum):
    ROLE = "role"
    SUBWORKFLOW = "subworkflow"
    APPROVAL = "approval"
    JOIN = "join"
    TERMINAL = "terminal"


def _ensure_unique_keys(
    items: Sequence[BaseModel],
    attribute: str,
    label: str,
) -> None:
    values = [getattr(item, attribute) for item in items]
    if len(values) != len(set(values)):
        raise ValueError(f"{label} keys must be unique")


class SkillBinding(BaseModel):
    binding_key: str
    skill_slug: str
    skill_version: str
    binding_mode: SkillBindingMode = SkillBindingMode.REQUIRED
    purpose: str
    expected_runtime_refs: tuple[str, ...] = Field(default_factory=tuple)


class AgentRoleDefinition(BaseModel):
    role_key: str
    display_name: str
    role_kind: RoleKind = RoleKind.AGENT
    purpose: str
    input_contract_key: str | None = None
    output_contract_key: str | None = None
    skill_bindings: list[SkillBinding] = Field(default_factory=list)
    allowed_tool_policy_refs: tuple[str, ...] = Field(default_factory=tuple)
    notes_markdown: str | None = None


class ContractSchemaDefinition(BaseModel):
    contract_key: str
    semantic_version: str = "1.0.0"
    contract_kind: str = "data_contract"
    json_schema: dict[str, object] = Field(default_factory=dict)
    example_payload: dict[str, object] = Field(default_factory=dict)


class WorkflowNodeDefinition(BaseModel):
    node_key: str
    node_type: WorkflowNodeType
    display_name: str
    role_key: str | None = None
    subworkflow_alias: str | None = None
    join_policy_key: str | None = None
    approval_gate_key: str | None = None


class WorkflowEdgeDefinition(BaseModel):
    edge_key: str
    source_node_key: str
    target_node_key: str
    contract_key: str | None = None


class JoinPolicyDefinition(BaseModel):
    join_policy_key: str
    strategy: str
    required_branches: tuple[str, ...] = Field(default_factory=tuple)
    quorum_count: int | None = None
    failure_behavior: str = "block"


class ApprovalGateDefinition(BaseModel):
    approval_gate_key: str
    display_name: str
    approver_scope: str
    approver_role_code: str | None = None
    decision_contract_key: str | None = None
    timeout_policy: str | None = None
    instructions: str | None = None


class SubworkflowReference(BaseModel):
    alias: str
    workflow_version_ref: str
    input_contract_key: str | None = None
    output_contract_key: str | None = None


class WorkflowDraftDocument(BaseModel):
    workflow_key: str
    display_name: str
    description: str | None = None
    workflow_kind: WorkflowKind
    entry_node_key: str
    roles: list[AgentRoleDefinition] = Field(default_factory=list)
    contracts: list[ContractSchemaDefinition] = Field(default_factory=list)
    nodes: list[WorkflowNodeDefinition] = Field(default_factory=list)
    edges: list[WorkflowEdgeDefinition] = Field(default_factory=list)
    join_policies: list[JoinPolicyDefinition] = Field(default_factory=list)
    approval_gates: list[ApprovalGateDefinition] = Field(default_factory=list)
    subworkflow_refs: list[SubworkflowReference] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_document(self) -> WorkflowDraftDocument:
        _ensure_unique_keys(self.roles, "role_key", "role")
        _ensure_unique_keys(self.contracts, "contract_key", "contract")
        _ensure_unique_keys(self.nodes, "node_key", "node")
        _ensure_unique_keys(self.edges, "edge_key", "edge")
        _ensure_unique_keys(self.join_policies, "join_policy_key", "join policy")
        _ensure_unique_keys(self.approval_gates, "approval_gate_key", "approval gate")
        _ensure_unique_keys(self.subworkflow_refs, "alias", "subworkflow reference")
        if self.nodes:
            node_keys = {node.node_key for node in self.nodes}
            if self.entry_node_key not in node_keys:
                raise ValueError("entry_node_key must reference an existing node")
            for edge in self.edges:
                if (
                    edge.source_node_key not in node_keys
                    or edge.target_node_key not in node_keys
                ):
                    raise ValueError("edges must reference existing nodes")
        return self


class WorkflowDraftCreateRequest(BaseModel):
    scope_type: WorkflowScopeType
    tenant_id: UUID | None = None
    workflow_kind: WorkflowKind
    slug: str
    display_name: str
    description: str | None = None
    created_from_version_id: UUID | None = None
    document: WorkflowDraftDocument


class WorkflowDraftSaveRequest(BaseModel):
    base_revision_number: int
    display_name: str
    description: str | None = None
    document: WorkflowDraftDocument
    change_summary: str | None = None


class WorkflowDraftRevisionResponse(BaseModel):
    workflow_draft_revision_id: UUID
    revision_number: int
    document_sha256: str
    change_summary: str | None = None
    created_at: datetime


class WorkflowDraftResponse(BaseModel):
    workflow_draft_id: UUID
    workflow_lineage_id: UUID
    slug: str
    display_name: str
    description: str | None = None
    scope_type: WorkflowScopeType
    tenant_id: UUID | None = None
    workflow_kind: WorkflowKind
    status: str
    current_revision_number: int
    created_from_version_id: UUID | None = None
    latest_revision: WorkflowDraftRevisionResponse
    latest_validation: ValidationResultResponse | None = None
    document: WorkflowDraftDocument
    updated_at: datetime


class WorkflowRegistryItem(BaseModel):
    workflow_lineage_id: UUID
    workflow_draft_id: UUID | None = None
    workflow_version_bundle_id: UUID | None = None
    slug: str
    display_name: str
    workflow_kind: WorkflowKind
    scope_type: WorkflowScopeType
    tenant_id: UUID | None = None
    visibility_status: WorkflowVisibilityStatus
    current_revision_number: int | None = None
    display_version: str | None = None
    updated_at: datetime


class WorkflowRegistryListResponse(BaseModel):
    items: list[WorkflowRegistryItem]


class ValidationFindingResponse(BaseModel):
    category: str
    severity: str
    message: str
    field_path: str | None = None


class ValidationResultResponse(BaseModel):
    validation_result_id: UUID
    status: str
    blocking_issue_count: int
    advisory_issue_count: int
    findings: list[ValidationFindingResponse] = Field(default_factory=list)


class PublishDraftRequest(BaseModel):
    validation_result_id: UUID


class WorkflowVersionResponse(BaseModel):
    workflow_version_bundle_id: UUID
    workflow_lineage_id: UUID
    slug: str
    display_name: str
    display_version: str
    scope_type: WorkflowScopeType
    tenant_id: UUID | None = None
    status: str
    compiled_bundle_digest: str | None = None
    compiler_version: str | None = None
    published_from_draft_id: UUID
    published_from_revision_id: UUID
    previous_version_bundle_id: UUID | None = None
    compiled_bundle_artifact_id: UUID | None = None
    summary_json: dict[str, object] = Field(default_factory=dict)
    sharing_grants: list[RegistrySharingGrantResponse] = Field(default_factory=list)
    published_at: datetime


class RegistrySharingGrantCreateRequest(BaseModel):
    grantee_tenant_id: UUID


class RegistrySharingGrantResponse(BaseModel):
    registry_sharing_grant_id: UUID
    workflow_version_bundle_id: UUID
    grantee_tenant_id: UUID
    status: str
    created_at: datetime
