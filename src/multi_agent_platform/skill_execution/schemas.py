from __future__ import annotations

from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ExecutionMode(StrEnum):
    MOCK = "mock"
    LIVE_PROBE = "live_probe"


class ExecutionStatus(StrEnum):
    SUCCEEDED = "succeeded"
    DENIED = "denied"
    FAILED = "failed"


class DiagnosticReadiness(StrEnum):
    READY = "ready"
    BLOCKED = "blocked"
    NOT_CONFIGURED = "not_configured"


class ToolPolicyDecision(BaseModel):
    model_config = ConfigDict(frozen=True)

    check: str
    allowed: bool
    reason: str
    policy_ref: str | None = None


class CredentialResolutionSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    required: bool
    credential_kind: str
    tenant_id: UUID
    reference: str
    available: bool
    safe_label: str | None = None


class SkillToolExecutionRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    tenant_id: UUID
    actor_id: str
    skill_package: str
    skill_version: str
    tool_name: str
    execution_mode: ExecutionMode = ExecutionMode.MOCK
    input: dict[str, Any] = Field(default_factory=dict)
    workflow_run_id: UUID | None = None
    role_node_id: str | None = None
    required_credential_kind: str | None = None
    outbound_domains: tuple[str, ...] = Field(default_factory=tuple)
    side_effect_requested: bool = False
    contract_version: str = "v1"
    policy_refs: dict[str, str] = Field(default_factory=dict)
    credential_reference: str | None = None


class AdapterExecutionResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    tool_name: str
    contract_version: str = "v1"
    output: dict[str, Any]
    response_summary: str
    artifact_refs: tuple[str, ...] = Field(default_factory=tuple)


class SkillToolExecutionResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: ExecutionStatus
    tool_name: str
    execution_mode: ExecutionMode
    output: dict[str, Any] = Field(default_factory=dict)
    request_summary: str
    response_summary: str
    policy_decisions: tuple[ToolPolicyDecision, ...] = Field(default_factory=tuple)
    credential_summary: CredentialResolutionSummary | None = None
    artifact_refs: tuple[str, ...] = Field(default_factory=tuple)
    latency_ms: int = 0
    error_code: str | None = None
    error_message: str | None = None


class SkillToolDiagnosticRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    tool_name: str
    display_name: str
    mode: ExecutionMode
    readiness: DiagnosticReadiness
    requires_credential: bool
    allowed_domains: tuple[str, ...] = Field(default_factory=tuple)
    latest_status: ExecutionStatus | None = None
    latest_summary: str | None = None
    latest_denial: str | None = None
