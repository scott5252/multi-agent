from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

SafeMode = Literal[
    "mock_model",
    "mock_tools",
    "real_model_side_effects_disabled",
    "approved_real_probe",
]
TargetType = Literal[
    "prompt_version",
    "agent_profile_version",
    "workflow_draft",
    "published_subworkflow",
    "published_workflow",
]
AssertionKindValue = Literal["deterministic", "evaluator"]


class AgentTestAssertionPayload(BaseModel):
    kind: AssertionKindValue = "deterministic"
    path: str | None = None
    comparator: str | None = "equals"
    expected_value: Any = None
    expected_schema: dict[str, Any] = Field(default_factory=dict)
    threshold: float | None = None
    severity: str = "blocking"
    weight: float = Field(default=1.0, ge=0)
    description: str | None = None


class AgentTestSuiteCreateRequest(BaseModel):
    tenant_id: UUID
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    target_type: TargetType
    target_id: str = Field(min_length=1, max_length=255)
    target_version: str | None = None
    default_safe_mode: SafeMode = "mock_model"
    model_mode: str = "mock"
    tool_mode: str = "mock"
    pass_threshold: float = Field(default=1.0, ge=0, le=1)
    required_for_publish: bool = False


class AgentTestSuiteUpdateRequest(AgentTestSuiteCreateRequest):
    revision: int = Field(ge=1)


class AgentTestCaseCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    fixture: dict[str, Any] = Field(default_factory=dict)
    expected_contract_shape: dict[str, Any] = Field(default_factory=dict)
    assertions: list[AgentTestAssertionPayload] = Field(default_factory=list)
    evaluator_prompt_ref: str | None = None
    model_mode: str = "inherit"
    tool_mode: str = "inherit"
    pass_threshold: float = Field(default=1.0, ge=0, le=1)
    case_order: int = 0


class AgentTestCaseUpdateRequest(AgentTestCaseCreateRequest):
    revision: int = Field(ge=1)


class AgentTestRunCreateRequest(BaseModel):
    safe_mode: SafeMode = "mock_model"
    target_version: str | None = None
    idempotency_key: str | None = None
    run_reason: str | None = None
    approved_probe_reference: str | None = None

    @field_validator("approved_probe_reference")
    @classmethod
    def no_real_secret_values(cls, value: str | None) -> str | None:
        if value and any(
            marker in value.lower() for marker in ("secret", "token", "key=")
        ):
            raise ValueError("approved probe reference must not contain secret values")
        return value


class AgentTestAssertionResponse(BaseModel):
    assertion_id: UUID | str | None = None
    kind: str
    path: str | None = None
    comparator: str | None = None
    expected_value: Any = None
    expected_schema: dict[str, Any] = Field(default_factory=dict)
    threshold: float | None = None
    severity: str = "blocking"
    description: str | None = None


class AgentTestCaseResponse(BaseModel):
    case_id: UUID | str
    suite_id: UUID | str
    tenant_id: UUID | str
    name: str
    description: str | None = None
    fixture_summary: dict[str, Any] = Field(default_factory=dict)
    expected_contract_shape: dict[str, Any] = Field(default_factory=dict)
    assertions: list[AgentTestAssertionResponse] = Field(default_factory=list)
    pass_threshold: float
    status: str
    revision: int


class AgentTestSuiteResponse(BaseModel):
    suite_id: UUID | str
    tenant_id: UUID | str
    name: str
    description: str | None = None
    target_type: str
    target_id: str
    target_version: str | None = None
    default_safe_mode: str
    model_mode: str
    tool_mode: str
    pass_threshold: float
    required_for_publish: bool
    status: str
    revision: int
    case_count: int = 0
    latest_run_status: str | None = None


class AgentTestRunStepResponse(BaseModel):
    step_id: UUID | str
    run_id: UUID | str
    case_id: UUID | str | None = None
    step_name: str
    status: str
    sequence: int
    model_provider: str | None = None
    model_id: str | None = None
    prompt_version_id: str | None = None
    profile_version_id: str | None = None
    skill_version_refs: list[str] = Field(default_factory=list)
    workflow_version_ref: str | None = None
    latency_ms: int = 0
    token_usage: dict[str, Any] = Field(default_factory=dict)
    contract_validation: dict[str, Any] = Field(default_factory=dict)
    assertion_results: list[dict[str, Any]] = Field(default_factory=list)
    blocked_side_effects: list[dict[str, Any]] = Field(default_factory=list)
    redacted_transcript: dict[str, Any] = Field(default_factory=dict)
    artifact_refs: list[str] = Field(default_factory=list)
    failure_reason: str | None = None


class AgentTestRunResponse(BaseModel):
    run_id: UUID | str
    tenant_id: UUID | str
    suite_id: UUID | str
    target_type: str
    target_id: str
    target_version: str | None = None
    safe_mode: str
    status: str
    pass_status: str
    trace_id: str | None = None
    usage_summary: dict[str, Any] = Field(default_factory=dict)
    latency_ms: int = 0
    redaction_summary: dict[str, Any] = Field(default_factory=dict)
    artifact_summary: dict[str, Any] = Field(default_factory=dict)
    blocked_side_effect_count: int = 0
    failure_summary: str | None = None
    steps: list[AgentTestRunStepResponse] = Field(default_factory=list)


class PublishGateEvaluateRequest(BaseModel):
    tenant_id: UUID
    target_type: TargetType
    target_id: str
    target_version: str | None = None


class AgentTestPublishGateSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: Literal["ready", "blocked"]
    required_count: int = 0
    passing_count: int = 0
    failing_count: int = 0
    missing_count: int = 0
    stale_count: int = 0
    required_suite_ids: list[str] = Field(default_factory=list)
    passing_run_ids: list[str] = Field(default_factory=list)
    stale_run_ids: list[str] = Field(default_factory=list)
    safe_reasons: list[str] = Field(default_factory=list)
