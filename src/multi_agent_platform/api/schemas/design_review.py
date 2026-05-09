from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DesignReviewState(BaseModel):
    kind: Literal["ready", "empty", "pending", "denied", "unavailable"]
    summary: str


class DesignReviewTemplateInstallRequest(BaseModel):
    tenant_id: UUID
    template_key: str = Field(
        default="design-reviewer-council",
        min_length=1,
        max_length=160,
    )
    idempotency_key: str = Field(min_length=1, max_length=160)
    run_required_tests: bool = True
    safe_mode: Literal["deterministic", "model_backed_safe", "both"] = "both"


class DesignReviewTemplateActionResponse(BaseModel):
    label: str
    href: str
    method: str = "post"


class DesignReviewTemplateInstallResponse(BaseModel):
    template_key: str
    tenant_id: UUID
    workflow_draft_id: UUID | None = None
    workflow_lineage_id: UUID | None = None
    workflow_draft_revision_id: UUID | None = None
    workflow_key: str | None = None
    display_name: str | None = None
    agent_test_suite_id: UUID | None = None
    agent_test_run_id: UUID | None = None
    deterministic_run_id: UUID | None = None
    model_safe_run_id: UUID | None = None
    required_evidence_status: str
    publish_gate_status: str
    ready_to_publish: bool
    evidence_modes: list[str] = Field(default_factory=list)
    replayed: bool = False
    safe_summary: str
    actions: list[DesignReviewTemplateActionResponse] = Field(default_factory=list)


class DesignRevisionCreateMetadata(BaseModel):
    author_role_key: str = Field(default="requester", max_length=120)
    safe_summary: str | None = Field(default=None, max_length=4000)
    artifact_id: UUID | None = None
    payload_digest: str | None = Field(default=None, max_length=128)


class DesignReviewSessionCreateRequest(BaseModel):
    tenant_id: UUID
    request_summary: str = Field(min_length=1, max_length=4000)
    quorum_policy_key: str = Field(min_length=1, max_length=120)
    workflow_version_bundle_id: UUID | None = None
    initial_revision: DesignRevisionCreateMetadata | None = None
    idempotency_key: str = Field(min_length=1, max_length=160)


class DesignRevisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    design_revision_id: UUID
    revision_number: int
    author_role_key: str
    safe_summary: str
    artifact_id: UUID | None = None
    payload_digest: str
    previous_revision_id: UUID | None = None


class DesignReviewSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    design_review_session_id: UUID
    tenant_id: UUID
    status: str
    request_summary: str
    active_revision_number: int
    quorum_policy_key: str
    workflow_version_bundle_id: UUID | None = None
    owner_principal_id: str
    replayed: bool = False
    current_revision: DesignRevisionResponse | None = None


class DesignReviewSessionListResponse(BaseModel):
    items: list[DesignReviewSessionResponse]
    state: DesignReviewState


class DesignReviewerAssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    design_reviewer_assignment_id: UUID
    reviewer_key: str
    role_key: str
    prompt_version_id: UUID | None = None
    profile_version_id: UUID | None = None
    provider_reference: str | None = None
    enabled: bool


class DesignReviewCoordinatorReviewerRequest(BaseModel):
    reviewer_key: str = Field(min_length=1, max_length=120)
    role_key: str = Field(min_length=1, max_length=120)
    prompt_version_id: UUID | None = None
    profile_version_id: UUID | None = None
    provider_reference: str | None = Field(default=None, max_length=255)
    enabled: bool = True


class DesignReviewerVerdictResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    design_reviewer_verdict_id: UUID
    reviewer_key: str
    verdict: str
    score: int
    blocking_issue_count: int
    safe_feedback_summary: str
    artifact_id: UUID | None = None
    output_digest: str
    usage_summary: dict[str, object] = Field(default_factory=dict)
    replayed: bool = False


class DesignReviewCoordinatorVerdictRequest(BaseModel):
    reviewer_key: str = Field(min_length=1, max_length=120)
    verdict: Literal["approved", "changes_requested", "blocked", "skipped", "failed"]
    score: int = Field(ge=0, le=5)
    blocking_issue_count: int = Field(ge=0)
    safe_feedback_summary: str = Field(min_length=1, max_length=4000)
    artifact_id: UUID | None = None
    output_digest: str = Field(min_length=1, max_length=128)
    usage_summary: dict[str, object] = Field(default_factory=dict)


class DesignQuorumDecisionResponse(BaseModel):
    state: DesignReviewState
    design_quorum_decision_id: UUID | None = None
    status: str | None = None
    approval_count: int | None = None
    blocking_issue_count: int | None = None
    next_action: str | None = None
    policy_version: str | None = None
    safe_rationale: str | None = None


class DesignReviewRoundResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    design_review_round_id: UUID
    design_review_session_id: UUID
    design_revision_id: UUID
    round_number: int
    status: str
    workflow_run_id: UUID | None = None
    reviewer_count: int
    quorum_count: int


class DesignReviewRoundDetailResponse(DesignReviewRoundResponse):
    assignments: list[DesignReviewerAssignmentResponse] = Field(default_factory=list)
    verdicts: list[DesignReviewerVerdictResponse] = Field(default_factory=list)
    quorum_decision: DesignQuorumDecisionResponse


class DesignManualDecisionCreateRequest(BaseModel):
    tenant_id: UUID
    round_id: UUID | None = None
    decision_type: Literal["revise", "approve_exception", "retry", "cancel"]
    safe_rationale: str = Field(min_length=1, max_length=4000)
    accepted_risk: bool = False
    idempotency_key: str = Field(min_length=1, max_length=160)


class DesignManualDecisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    design_manual_decision_id: UUID
    design_review_session_id: UUID
    design_review_round_id: UUID | None = None
    decision_type: str
    actor_principal_id: str
    safe_rationale: str
    accepted_risk: bool
    replayed: bool = False


class DesignManualDecisionListResponse(BaseModel):
    items: list[DesignManualDecisionResponse]
    state: DesignReviewState


class DesignDevelopmentHandoffResponse(BaseModel):
    state: DesignReviewState
    design_development_handoff_id: UUID | None = None
    approved_revision_id: UUID | None = None
    artifact_id: UUID | None = None
    safe_summary: str | None = None
    output_digest: str | None = None
    status: str | None = None


class DesignReviewSessionDetailResponse(DesignReviewSessionResponse):
    revisions: list[DesignRevisionResponse] = Field(default_factory=list)
    rounds: list[DesignReviewRoundResponse] = Field(default_factory=list)
    manual_decisions: list[DesignManualDecisionResponse] = Field(default_factory=list)
    handoff: DesignDevelopmentHandoffResponse


class DesignRevisionListResponse(BaseModel):
    items: list[DesignRevisionResponse]


class DesignReviewRoundListResponse(BaseModel):
    items: list[DesignReviewRoundResponse]


class DesignReviewCoordinatorStateResponse(BaseModel):
    state: DesignReviewState
    session: DesignReviewSessionResponse
    active_revision: DesignRevisionResponse | None = None
    latest_round: DesignReviewRoundResponse | None = None
    latest_quorum_decision: DesignQuorumDecisionResponse
    handoff: DesignDevelopmentHandoffResponse
    manual_resolution_required: bool = False
    next_action: str = "none"


class DesignReviewCoordinatorLaunchRequest(BaseModel):
    tenant_id: UUID
    workflow_version_bundle_id: UUID | None = None
    reviewers: list[DesignReviewCoordinatorReviewerRequest] = Field(
        default_factory=list
    )
    max_rounds: int = Field(default=3, ge=1, le=10)
    execution_mode: str = Field(default="deterministic", max_length=120)
    idempotency_key: str = Field(min_length=1, max_length=160)


class DesignReviewCoordinatorLaunchResponse(BaseModel):
    state: DesignReviewState
    session: DesignReviewSessionResponse
    active_revision: DesignRevisionResponse | None = None
    round: DesignReviewRoundResponse
    workflow_run_id: UUID | None = None
    replayed: bool = False
    next_action: str = "none"


class DesignReviewCoordinatorCompleteRequest(BaseModel):
    tenant_id: UUID
    verdicts: list[DesignReviewCoordinatorVerdictRequest] = Field(default_factory=list)
    safe_synthesis_summary: str = Field(min_length=1, max_length=4000)
    next_revision_summary: str | None = Field(default=None, max_length=4000)
    max_rounds: int = Field(default=3, ge=1, le=10)
    idempotency_key: str = Field(min_length=1, max_length=160)


class DesignReviewCoordinatorCompleteResponse(BaseModel):
    state: DesignReviewState
    session: DesignReviewSessionResponse
    round: DesignReviewRoundResponse
    active_revision: DesignRevisionResponse | None = None
    created_revision: DesignRevisionResponse | None = None
    quorum_decision: DesignQuorumDecisionResponse
    handoff: DesignDevelopmentHandoffResponse
    workflow_run_id: UUID | None = None
    replayed: bool = False
    next_action: str = "none"


class DesignReviewCoordinatorManualDecisionRequest(BaseModel):
    tenant_id: UUID
    round_id: UUID | None = None
    decision_type: Literal["revise", "approve_exception", "retry", "cancel"]
    safe_rationale: str = Field(min_length=1, max_length=4000)
    accepted_risk: bool = False
    next_revision_summary: str | None = Field(default=None, max_length=4000)
    idempotency_key: str = Field(min_length=1, max_length=160)


class DesignReviewCoordinatorManualDecisionResponse(BaseModel):
    state: DesignReviewState
    session: DesignReviewSessionResponse
    active_revision: DesignRevisionResponse | None = None
    created_revision: DesignRevisionResponse | None = None
    manual_decision: DesignManualDecisionResponse
    handoff: DesignDevelopmentHandoffResponse
    replayed: bool = False
    next_action: str = "none"
