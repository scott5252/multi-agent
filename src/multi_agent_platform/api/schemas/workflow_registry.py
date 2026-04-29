from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from enum import StrEnum
from typing import Any
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


class WorkflowContractKind(StrEnum):
    WORKFLOW_INPUT = "workflow_input"
    WORKFLOW_OUTPUT = "workflow_output"
    HANDOFF = "handoff"
    ARTIFACT = "artifact"
    MEMORY = "memory"
    TOOL_ACCESS = "tool_access"
    APPROVAL_DECISION = "approval_decision"
    FAILURE_OUTCOME = "failure_outcome"
    DATA_CONTRACT = "data_contract"


def _ensure_unique_keys(
    items: Sequence[BaseModel],
    attribute: str,
    label: str,
) -> None:
    values = [getattr(item, attribute) for item in items]
    if len(values) != len(set(values)):
        raise ValueError(f"{label} keys must be unique")


class WorkflowBuilderMetadata(BaseModel):
    name: str | None = None
    description: str | None = None
    owner_principal_id: str | None = None
    scope_type: WorkflowScopeType | None = None
    tenant_id: UUID | None = None
    status: str = "draft"
    tags: list[str] = Field(default_factory=list)
    publication_intent: str | None = None
    reviewer_notes: str | None = None

    @model_validator(mode="after")
    def validate_scope(self) -> WorkflowBuilderMetadata:
        if self.scope_type == WorkflowScopeType.TENANT and self.tenant_id is None:
            raise ValueError("tenant_id is required for tenant-scoped metadata")
        if self.scope_type == WorkflowScopeType.PLATFORM and self.tenant_id is not None:
            raise ValueError("tenant_id must be omitted for platform metadata")
        return self


class ModelRoutingPreviewReference(BaseModel):
    preview_key: str
    scope: str | None = None
    model_routing_version_id: UUID | None = None
    provider_connection_id: UUID | None = None
    provider_catalog_entry_id: UUID | None = None
    model_id: str | None = None
    health_state: str = "unknown"
    policy_status: str = "unknown"
    preview_url: str | None = None
    evaluated_version_ids: list[str] = Field(default_factory=list)
    safe_summary: str | None = None


class PromptProfileReference(BaseModel):
    reference_key: str
    role_key: str | None = None
    agent_key: str | None = None
    agent_kind: str = "agent"
    agent_profile_version_id: UUID | None = None
    prompt_reference_version_ids: list[UUID] = Field(default_factory=list)
    prompt_version_ids: list[UUID] = Field(default_factory=list)
    source_scope: str | None = None
    resolution_digest: str | None = None
    model_routing_preview: ModelRoutingPreviewReference | None = None
    readiness_status: str = "unknown"


class SkillInstallationReference(BaseModel):
    skill_installation_key: str
    skill_slug: str
    skill_version: str
    scope_type: WorkflowScopeType = WorkflowScopeType.TENANT
    tenant_id: UUID | None = None
    binding_mode: SkillBindingMode = SkillBindingMode.REQUIRED
    compatibility_expectation: str | None = None
    credential_requirement_status: str = "unknown"
    policy_notes: str | None = None
    tool_policy_refs: list[str] = Field(default_factory=list)
    outbound_policy_refs: list[str] = Field(default_factory=list)
    secret_reference_ids: list[str] = Field(default_factory=list)


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
    responsibilities: list[str] = Field(default_factory=list)
    allowed_references: list[str] = Field(default_factory=list)
    profile_reference_key: str | None = None
    prompt_reference_keys: list[str] = Field(default_factory=list)
    input_contract_key: str | None = None
    output_contract_key: str | None = None
    skill_bindings: list[SkillBinding] = Field(default_factory=list)
    skill_installation_keys: list[str] = Field(default_factory=list)
    allowed_tool_policy_refs: tuple[str, ...] = Field(default_factory=tuple)
    handoff_expectations: str | None = None
    graph_node_keys: list[str] = Field(default_factory=list)
    review_notes: str | None = None
    notes_markdown: str | None = None


class ContractSchemaDefinition(BaseModel):
    contract_key: str
    display_name: str | None = None
    semantic_version: str = "1.0.0"
    contract_kind: WorkflowContractKind | str = WorkflowContractKind.DATA_CONTRACT
    json_schema: dict[str, object] = Field(default_factory=dict)
    example_payload: dict[str, object] = Field(default_factory=dict)
    compatibility_notes: str | None = None
    producer_keys: list[str] = Field(default_factory=list)
    consumer_keys: list[str] = Field(default_factory=list)


class WorkflowNodeDefinition(BaseModel):
    node_key: str
    node_type: WorkflowNodeType
    display_name: str
    description: str | None = None
    role_key: str | None = None
    subworkflow_alias: str | None = None
    join_policy_key: str | None = None
    approval_gate_key: str | None = None
    active: bool = True
    retry_policy_key: str | None = None
    editor_position: dict[str, float] = Field(default_factory=dict)


class WorkflowEdgeDefinition(BaseModel):
    edge_key: str
    source_node_key: str
    target_node_key: str
    contract_key: str | None = None
    edge_type: str = "success"
    branch_condition: str | None = None
    failure_path: bool = False
    loop_type: str | None = None
    max_attempts: int | None = None
    timeout_seconds: int | None = None


class JoinPolicyDefinition(BaseModel):
    join_policy_key: str
    strategy: str
    inbound_edge_keys: list[str] = Field(default_factory=list)
    required_branches: tuple[str, ...] = Field(default_factory=tuple)
    quorum_count: int | None = None
    timeout_seconds: int | None = None
    failure_behavior: str = "block"
    output_merge_contract_key: str | None = None


class ApprovalGateDefinition(BaseModel):
    approval_gate_key: str
    display_name: str
    approver_scope: str
    approver_role_code: str | None = None
    reason: str | None = None
    decision_contract_key: str | None = None
    resume_behavior: str | None = None
    timeout_policy: str | None = None
    blocked_state_visibility: str | None = None
    instructions: str | None = None
    reviewer_instructions: str | None = None


class SubworkflowReference(BaseModel):
    alias: str
    workflow_version_ref: str
    display_name: str | None = None
    input_contract_key: str | None = None
    output_contract_key: str | None = None
    compatibility_status: str = "unknown"


class TestSuiteRequirement(BaseModel):
    requirement_key: str
    suite_id: str
    target_type: str = "workflow_revision"
    freshness_policy: str = "latest_revision"
    latest_result_id: str | None = None
    latest_result_status: str = "missing"
    executed_at: datetime | None = None
    safe_summary: str | None = None


class BuilderEditorAnnotations(BaseModel):
    section_notes: dict[str, str] = Field(default_factory=dict)
    graph_layout: dict[str, dict[str, float]] = Field(default_factory=dict)
    collapsed_sections: list[str] = Field(default_factory=list)


class WorkflowDraftDocument(BaseModel):
    workflow_key: str
    display_name: str
    description: str | None = None
    workflow_kind: WorkflowKind
    metadata: WorkflowBuilderMetadata | None = None
    entry_node_key: str
    roles: list[AgentRoleDefinition] = Field(default_factory=list)
    prompt_profile_references: list[PromptProfileReference] = Field(
        default_factory=list
    )
    skill_installations: list[SkillInstallationReference] = Field(default_factory=list)
    contracts: list[ContractSchemaDefinition] = Field(default_factory=list)
    nodes: list[WorkflowNodeDefinition] = Field(default_factory=list)
    edges: list[WorkflowEdgeDefinition] = Field(default_factory=list)
    join_policies: list[JoinPolicyDefinition] = Field(default_factory=list)
    approval_gates: list[ApprovalGateDefinition] = Field(default_factory=list)
    subworkflow_refs: list[SubworkflowReference] = Field(default_factory=list)
    test_requirements: list[TestSuiteRequirement] = Field(default_factory=list)
    editor_annotations: BuilderEditorAnnotations = Field(
        default_factory=BuilderEditorAnnotations
    )

    @model_validator(mode="after")
    def validate_document(self) -> WorkflowDraftDocument:
        _ensure_unique_keys(self.roles, "role_key", "role")
        _ensure_unique_keys(
            self.prompt_profile_references,
            "reference_key",
            "prompt/profile reference",
        )
        _ensure_unique_keys(
            self.skill_installations,
            "skill_installation_key",
            "skill installation",
        )
        _ensure_unique_keys(self.contracts, "contract_key", "contract")
        _ensure_unique_keys(self.nodes, "node_key", "node")
        _ensure_unique_keys(self.edges, "edge_key", "edge")
        _ensure_unique_keys(self.join_policies, "join_policy_key", "join policy")
        _ensure_unique_keys(self.approval_gates, "approval_gate_key", "approval gate")
        _ensure_unique_keys(self.subworkflow_refs, "alias", "subworkflow reference")
        _ensure_unique_keys(self.test_requirements, "requirement_key", "test")
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
            active_node_keys = {node.node_key for node in self.nodes if node.active}
            for role in self.roles:
                for node_key in role.graph_node_keys:
                    if node_key not in active_node_keys:
                        raise ValueError("role graph_node_keys must reference nodes")
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
    changed_sections: list[str] = Field(default_factory=list)


class WorkflowBuilderStatusSummary(BaseModel):
    latest_validation_status: str | None = None
    publish_readiness_status: str = "not_evaluated"
    blocking_issue_count: int = 0
    advisory_issue_count: int = 0


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
    builder_status: WorkflowBuilderStatusSummary = Field(
        default_factory=WorkflowBuilderStatusSummary
    )
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
    latest_validation_status: str | None = None
    publish_readiness_status: str = "not_evaluated"
    updated_at: datetime


class WorkflowRegistryListResponse(BaseModel):
    items: list[WorkflowRegistryItem]


class ValidationFindingResponse(BaseModel):
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


class ValidationResultResponse(BaseModel):
    validation_result_id: UUID
    status: str
    blocking_issue_count: int
    advisory_issue_count: int
    findings: list[ValidationFindingResponse] = Field(default_factory=list)
    rule_set_version: str | None = None
    draft_revision_id: UUID | None = None
    reference_readiness: list[dict[str, Any]] = Field(default_factory=list)
    graph_summary: dict[str, Any] = Field(default_factory=dict)
    required_test_summary: dict[str, Any] = Field(default_factory=dict)
    publish_blocking: bool = False


class PublishDraftRequest(BaseModel):
    validation_result_id: UUID
    publish_gate_id: str | None = None
    reason: str | None = None


class DraftRevisionListResponse(BaseModel):
    workflow_draft_id: UUID
    current_revision_number: int
    revisions: list[WorkflowDraftRevisionResponse] = Field(default_factory=list)


class RestoreRevisionRequest(BaseModel):
    revision_number: int
    base_revision_number: int
    change_summary: str | None = "Restore historical revision"


class CopyDraftRequest(BaseModel):
    source_revision_number: int | None = None
    new_slug: str
    display_name: str
    description: str | None = None
    scope_type: WorkflowScopeType | None = None
    tenant_id: UUID | None = None
    change_summary: str | None = "Copied workflow draft"


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
