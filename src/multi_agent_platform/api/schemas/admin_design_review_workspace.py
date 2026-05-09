from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from multi_agent_platform.api.schemas.admin_patterns import AdminAction, safe_text
from multi_agent_platform.api.schemas.admin_react import (
    ReactAdminEmptyStateMetadata,
    ReactAdminPageProvenance,
    ReactAdminScope,
    ReactAdminShellState,
)
from multi_agent_platform.api.schemas.design_review import (
    DesignDevelopmentHandoffResponse,
    DesignManualDecisionResponse,
    DesignQuorumDecisionResponse,
    DesignReviewCoordinatorStateResponse,
    DesignReviewerAssignmentResponse,
    DesignReviewerVerdictResponse,
    DesignReviewRoundResponse,
    DesignReviewSessionResponse,
    DesignRevisionResponse,
)

DESIGN_REVIEW_UNSAFE_MARKERS = (
    "raw prompt",
    "raw completion",
    "provider payload",
    "authorization:",
    "bearer ",
    "secret value",
    "private message",
    "memory contents",
    "tool payload",
    "fixture",
    "mock",
    "jinja",
    "fastapi",
    "pydantic",
    "sqlalchemy",
    "react",
)


def safe_design_workspace_text(value: str, *, max_length: int = 240) -> str:
    normalized = safe_text(value, max_length=max_length)
    lowered = normalized.lower()
    if any(marker in lowered for marker in DESIGN_REVIEW_UNSAFE_MARKERS):
        raise ValueError("unsafe design review workspace text cannot be rendered")
    return normalized


class DesignReviewWorkspaceStatusCard(BaseModel):
    model_config = ConfigDict(extra="forbid")

    card_id: str
    label: str
    value: str
    summary: str
    tone: str = "neutral"

    @field_validator("label", "value", "summary", "tone")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_design_workspace_text(value, max_length=180)


class DesignReviewWorkflowOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workflow_version_bundle_id: UUID
    label: str
    workflow_key: str
    display_version: str
    tenant_id: UUID | None = None
    status: str

    @field_validator("label", "workflow_key", "display_version", "status")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_design_workspace_text(value, max_length=160)


class DesignReviewQuorumPolicyOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    policy_key: str
    label: str
    summary: str
    reviewer_count: int
    approval_count: int

    @field_validator("policy_key", "label", "summary")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_design_workspace_text(value, max_length=180)


class DesignReviewWorkspaceTemplateSetup(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    template_key: str
    publish_gate_status: str
    required_evidence_status: str
    safe_summary: str
    workflow_draft_id: UUID | None = None
    workflow_lineage_id: UUID | None = None
    workflow_draft_revision_id: UUID | None = None
    workflow_key: str | None = None
    display_name: str | None = None
    agent_test_suite_id: UUID | None = None
    latest_run_id: UUID | None = None
    deterministic_run_id: UUID | None = None
    model_safe_run_id: UUID | None = None
    evidence_modes: tuple[str, ...] = Field(default_factory=tuple)
    ready_to_publish: bool = False
    install_action: AdminAction

    @field_validator(
        "status",
        "template_key",
        "publish_gate_status",
        "required_evidence_status",
        "safe_summary",
        "workflow_key",
        "display_name",
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return safe_design_workspace_text(value, max_length=220)

    @field_validator("evidence_modes")
    @classmethod
    def evidence_modes_are_safe(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(safe_design_workspace_text(item, max_length=120) for item in value)


class DesignReviewWorkspaceRoundDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    round: DesignReviewRoundResponse
    assignments: tuple[DesignReviewerAssignmentResponse, ...] = Field(
        default_factory=tuple
    )
    verdicts: tuple[DesignReviewerVerdictResponse, ...] = Field(default_factory=tuple)
    quorum_decision: DesignQuorumDecisionResponse


class DesignReviewWorkspaceSessionDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session: DesignReviewSessionResponse
    revisions: tuple[DesignRevisionResponse, ...] = Field(default_factory=tuple)
    rounds: tuple[DesignReviewWorkspaceRoundDetail, ...] = Field(default_factory=tuple)
    manual_decisions: tuple[DesignManualDecisionResponse, ...] = Field(
        default_factory=tuple
    )
    handoff: DesignDevelopmentHandoffResponse
    coordinator: DesignReviewCoordinatorStateResponse | None = None


class DesignReviewWorkspaceActions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    create_session: AdminAction
    refresh: AdminAction
    launch_round: AdminAction | None = None
    manual_decision: AdminAction | None = None


class DesignReviewWorkspaceEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: str
    active_scope: ReactAdminScope
    state: ReactAdminShellState
    provenance: ReactAdminPageProvenance
    empty_state: ReactAdminEmptyStateMetadata | None = None
    summary_cards: tuple[DesignReviewWorkspaceStatusCard, ...] = Field(
        default_factory=tuple
    )
    sessions: tuple[DesignReviewSessionResponse, ...] = Field(default_factory=tuple)
    selected_session: DesignReviewWorkspaceSessionDetail | None = None
    workflow_options: tuple[DesignReviewWorkflowOption, ...] = Field(
        default_factory=tuple
    )
    quorum_policies: tuple[DesignReviewQuorumPolicyOption, ...] = Field(
        default_factory=tuple
    )
    template_setup: DesignReviewWorkspaceTemplateSetup
    actions: DesignReviewWorkspaceActions

    @field_validator("title", "description")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_design_workspace_text(value, max_length=220)
