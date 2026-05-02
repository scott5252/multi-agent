from __future__ import annotations

from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class AgentBenchTargetType(StrEnum):
    PROMPT_VERSION = "prompt_version"
    AGENT_PROFILE_VERSION = "agent_profile_version"
    WORKFLOW_DRAFT = "workflow_draft"
    PUBLISHED_SUBWORKFLOW = "published_subworkflow"
    PUBLISHED_WORKFLOW = "published_workflow"


class AgentBenchSafeMode(StrEnum):
    MOCK_MODEL = "mock_model"
    MOCK_TOOLS = "mock_tools"
    REAL_MODEL_SIDE_EFFECTS_DISABLED = "real_model_side_effects_disabled"
    APPROVED_REAL_PROBE = "approved_real_probe"


class AgentBenchRunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    ERROR = "error"


class AgentBenchPassStatus(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    ERROR = "error"


class AgentBenchSuiteStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class AssertionKind(StrEnum):
    DETERMINISTIC = "deterministic"
    EVALUATOR = "evaluator"


class AssertionComparator(StrEnum):
    EQUALS = "equals"
    CONTAINS = "contains"
    MATCHES_REGEX = "matches_regex"
    JSON_SCHEMA = "json_schema"
    STATUS_IS = "status_is"
    LATENCY_UNDER_MS = "latency_under_ms"
    USAGE_UNDER_TOKENS = "usage_under_tokens"


class AssertionEvaluation(BaseModel):
    assertion_id: str | None = None
    kind: AssertionKind
    comparator: AssertionComparator | None = None
    path: str | None = None
    passed: bool
    expected: Any = None
    actual: Any = None
    safe_message: str
    severity: str = "blocking"


class ContractValidationResult(BaseModel):
    passed: bool
    expected_shape: dict[str, Any] = Field(default_factory=dict)
    actual_shape: dict[str, Any] = Field(default_factory=dict)
    failures: list[str] = Field(default_factory=list)


class BlockedSideEffect(BaseModel):
    tool_name: str
    reason: str
    safe_summary: dict[str, Any] = Field(default_factory=dict)


class SandboxStepResult(BaseModel):
    case_id: UUID | None = None
    step_name: str
    status: AgentBenchRunStatus
    sequence: int
    model_provider: str
    model_id: str
    prompt_version_id: str | None = None
    profile_version_id: str | None = None
    skill_version_refs: list[str] = Field(default_factory=list)
    workflow_version_ref: str | None = None
    latency_ms: int = 0
    token_usage: dict[str, int] = Field(default_factory=dict)
    contract_validation: ContractValidationResult = Field(
        default_factory=lambda: ContractValidationResult(passed=True)
    )
    assertion_results: list[AssertionEvaluation] = Field(default_factory=list)
    blocked_side_effects: list[BlockedSideEffect] = Field(default_factory=list)
    redacted_transcript: dict[str, Any] = Field(default_factory=dict)
    artifact_refs: list[str] = Field(default_factory=list)
    failure_reason: str | None = None

    @property
    def passed(self) -> bool:
        return self.status is AgentBenchRunStatus.PASSED


class SandboxRunResult(BaseModel):
    status: AgentBenchRunStatus
    pass_status: AgentBenchPassStatus
    usage_summary: dict[str, Any] = Field(default_factory=dict)
    latency_ms: int = 0
    redaction_summary: dict[str, Any] = Field(default_factory=dict)
    artifact_summary: dict[str, Any] = Field(default_factory=dict)
    blocked_side_effect_count: int = 0
    failure_summary: str | None = None
    steps: list[SandboxStepResult] = Field(default_factory=list)


class SuiteEvidenceSummary(BaseModel):
    required_count: int = 0
    passing_count: int = 0
    failing_count: int = 0
    missing_count: int = 0
    stale_count: int = 0
    required_suite_ids: list[str] = Field(default_factory=list)
    passing_run_ids: list[str] = Field(default_factory=list)
    stale_run_ids: list[str] = Field(default_factory=list)

    @property
    def ready(self) -> bool:
        return self.required_count == self.passing_count and self.missing_count == 0
