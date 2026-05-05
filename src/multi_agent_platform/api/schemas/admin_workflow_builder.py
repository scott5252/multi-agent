from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from multi_agent_platform.api.schemas.admin_patterns import (
    AdminAction,
    AdminMutationStatus,
    ConfirmationRequirement,
    MutationResult,
    RefreshHint,
    RevisionConflict,
    safe_text,
)
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminScope,
    ReactAdminShellState,
)

WORKFLOW_BUILDER_UNSAFE_MARKERS = (
    "qa030-secret-value",
    "raw prompt",
    "raw completion",
    "memory contents",
    "private channel message",
    "provider authorization",
    "raw provider response",
    "telegram update payload",
    "raw tool result",
)


def safe_builder_text(value: str, *, max_length: int = 240) -> str:
    normalized = safe_text(value, max_length=max_length)
    lowered = normalized.lower()
    if any(marker in lowered for marker in WORKFLOW_BUILDER_UNSAFE_MARKERS):
        raise ValueError("unsafe workflow builder text cannot be rendered")
    return normalized


class WorkflowBuilderStatus(StrEnum):
    READY = "ready"
    DIRTY = "dirty"
    VALIDATING = "validating"
    BLOCKED = "blocked"
    WARNING = "warning"
    STALE = "stale"
    PUBLISHED = "published"
    UNAVAILABLE = "unavailable"


class WorkflowBuilderSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    BLOCKING = "blocking"
    CRITICAL = "critical"


class BuilderSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    section_id: str
    label: str
    status: WorkflowBuilderStatus
    summary: str
    href: str | None = None

    @field_validator("label", "summary")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_builder_text(value, max_length=180)


class WorkflowReferenceOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reference_id: str
    label: str
    kind: str
    readiness_status: WorkflowBuilderStatus
    tenant_eligible: bool = True
    version_label: str | None = None
    safe_summary: str
    href: str | None = None

    @field_validator("label", "kind", "version_label", "safe_summary")
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_builder_text(value, max_length=180)


class WorkflowReferenceCatalog(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt_options: tuple[WorkflowReferenceOption, ...] = Field(default_factory=tuple)
    profile_options: tuple[WorkflowReferenceOption, ...] = Field(default_factory=tuple)
    provider_options: tuple[WorkflowReferenceOption, ...] = Field(default_factory=tuple)
    skill_options: tuple[WorkflowReferenceOption, ...] = Field(default_factory=tuple)
    test_suite_options: tuple[WorkflowReferenceOption, ...] = Field(
        default_factory=tuple
    )
    subworkflow_options: tuple[WorkflowReferenceOption, ...] = Field(
        default_factory=tuple
    )


class WorkflowGraphNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_id: str
    label: str
    node_type: str
    status: WorkflowBuilderStatus
    role_label: str | None = None
    summary: str
    x: int = 0
    y: int = 0

    @field_validator("label", "node_type", "role_label", "summary")
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_builder_text(value, max_length=180)


class WorkflowGraphEdge(BaseModel):
    model_config = ConfigDict(extra="forbid")

    edge_id: str
    source: str
    target: str
    label: str | None = None
    condition_category: str | None = None

    @field_validator("label", "condition_category")
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_builder_text(value, max_length=140)


class WorkflowJoinPolicySummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    policy_id: str
    label: str
    summary: str
    required_branch_count: int = Field(default=1, ge=0)

    @field_validator("label", "summary")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_builder_text(value, max_length=180)


class WorkflowGraphPreview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    layout_revision: str
    layout_is_authoritative: bool = False
    nodes: tuple[WorkflowGraphNode, ...] = Field(default_factory=tuple)
    edges: tuple[WorkflowGraphEdge, ...] = Field(default_factory=tuple)
    join_policies: tuple[WorkflowJoinPolicySummary, ...] = Field(default_factory=tuple)
    accessibility_summary: str

    @field_validator("accessibility_summary")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_builder_text(value, max_length=220)


class ValidationFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    finding_id: str
    severity: WorkflowBuilderSeverity
    category: str
    section: str
    message: str
    recommended_action: str
    href: str | None = None
    evidence_reference_id: str | None = None

    @field_validator("category", "section", "message", "recommended_action")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_builder_text(value, max_length=220)


class WorkflowValidationSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    validation_id: str
    status: WorkflowBuilderStatus
    revision: str
    generated_at_label: str
    summary: str
    findings: tuple[ValidationFinding, ...] = Field(default_factory=tuple)
    artifact_reference_ids: tuple[str, ...] = Field(default_factory=tuple)

    @field_validator("generated_at_label", "summary")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_builder_text(value, max_length=220)


class WorkflowEvidenceSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_id: str
    label: str
    status: WorkflowBuilderStatus
    summary: str
    artifact_reference_id: str | None = None
    href: str | None = None

    @field_validator("label", "summary")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_builder_text(value, max_length=180)

    @field_validator("artifact_reference_id")
    @classmethod
    def reference_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if value.startswith("/") or "/users/" in value.lower():
            raise ValueError("artifact reference must not be a local path")
        return safe_builder_text(value, max_length=120)


class WorkflowPublishReadiness(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: AdminMutationStatus
    revision: str
    summary: str
    blockers: tuple[str, ...] = Field(default_factory=tuple)
    warnings: tuple[str, ...] = Field(default_factory=tuple)
    required_evidence: tuple[WorkflowEvidenceSummary, ...] = Field(
        default_factory=tuple
    )
    confirmation: ConfirmationRequirement | None = None
    published_bundle_summary: str | None = None

    @field_validator("summary", "published_bundle_summary")
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_builder_text(value, max_length=220)

    @field_validator("blockers", "warnings")
    @classmethod
    def text_tuple_is_safe(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(safe_builder_text(item, max_length=180) for item in value)


class WorkflowRevisionSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    revision: str
    created_at_label: str
    actor_label: str
    change_category: str
    summary: str
    audit_reference_id: str | None = None
    compare_href: str | None = None
    current: bool = False

    @field_validator("created_at_label", "actor_label", "change_category", "summary")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_builder_text(value, max_length=180)


class WorkflowJsonInspector(BaseModel):
    model_config = ConfigDict(extra="forbid")

    collapsed_by_default: bool = True
    summary: str
    redaction_summary: str
    safe_document_preview: dict[str, str] = Field(default_factory=dict)
    artifact_reference_id: str | None = None

    @field_validator("summary", "redaction_summary")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_builder_text(value, max_length=220)

    @field_validator("safe_document_preview")
    @classmethod
    def preview_is_safe(cls, value: dict[str, str]) -> dict[str, str]:
        return {
            safe_builder_text(key, max_length=80): safe_builder_text(
                detail, max_length=180
            )
            for key, detail in value.items()
        }


class WorkflowDraftDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workflow_draft_id: str
    workflow_lineage_id: str
    revision: str
    name: str
    description: str
    status: WorkflowBuilderStatus
    tenant_label: str | None = None
    metadata_summary: str
    roles_summary: str
    references_summary: str
    graph: WorkflowGraphPreview

    @field_validator(
        "name",
        "description",
        "tenant_label",
        "metadata_summary",
        "roles_summary",
        "references_summary",
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_builder_text(value, max_length=220)


class WorkflowDraftSaveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    revision: str
    idempotency_key: str
    name: str
    description: str
    selected_prompt_ref: str | None = None
    selected_profile_ref: str | None = None
    join_policy: str = "wait_for_required_branches"
    force_stale: bool = False

    @field_validator(
        "name",
        "description",
        "selected_prompt_ref",
        "selected_profile_ref",
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_builder_text(value, max_length=180)


class WorkflowPublishRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    revision: str
    confirmed: bool = False
    idempotency_key: str
    ready_fixture: bool = False


class BuilderMutationResult(MutationResult):
    revision: str | None = None
    validation: WorkflowValidationSummary | None = None
    publish_readiness: WorkflowPublishReadiness | None = None

    @field_validator("summary", "audit_reference_id")
    @classmethod
    def inherited_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_builder_text(value, max_length=220)


class WorkflowBuilderEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page_id: str
    title: str
    description: str
    scope: ReactAdminScope
    draft: WorkflowDraftDocument
    sections: tuple[BuilderSection, ...] = Field(default_factory=tuple)
    reference_catalog: WorkflowReferenceCatalog
    validation: WorkflowValidationSummary
    publish_readiness: WorkflowPublishReadiness
    revisions: tuple[WorkflowRevisionSummary, ...] = Field(default_factory=tuple)
    json_inspector: WorkflowJsonInspector
    actions: tuple[AdminAction, ...] = Field(default_factory=tuple)
    state: ReactAdminShellState | None = None
    refresh: RefreshHint | None = None

    @field_validator("title", "description")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_builder_text(value, max_length=220)


class WorkflowBuilderStaleConflict(RevisionConflict):
    pass
