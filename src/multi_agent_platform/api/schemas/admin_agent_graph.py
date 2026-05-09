from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from multi_agent_platform.api.schemas.admin_patterns import safe_text

AGENT_GRAPH_UNSAFE_MARKERS = (
    "raw prompt",
    "raw completion",
    "memory contents",
    "private channel message",
    "provider payload",
    "provider response",
    "authorization:",
    "bearer ",
    "credential",
    "secret value",
    "raw tool",
    "tool payload",
    "traceback",
    "/users/",
    "file://",
)


def safe_agent_graph_text(value: str, *, max_length: int = 220) -> str:
    normalized = safe_text(value, max_length=max_length)
    lowered = normalized.lower()
    if any(marker in lowered for marker in AGENT_GRAPH_UNSAFE_MARKERS):
        raise ValueError("unsafe agent graph text cannot be rendered")
    return normalized


def safe_optional_agent_graph_text(
    value: str | None, *, max_length: int = 220
) -> str | None:
    if value is None:
        return None
    return safe_agent_graph_text(value, max_length=max_length)


class AgentGraphSource(StrEnum):
    DRAFT = "draft"
    PUBLISHED_VERSION = "published_version"
    RUNTIME_RUN = "runtime_run"


class AgentGraphState(StrEnum):
    READY = "ready"
    EMPTY = "empty"
    PARTIAL = "partial"
    DENIED = "denied"


class AgentGraphNodeCategory(StrEnum):
    COORDINATOR_AGENT = "coordinator_agent"
    SUB_AGENT = "sub_agent"
    TOOL = "tool"
    JOIN = "join"
    APPROVAL = "approval"
    HANDOFF = "handoff"
    TERMINAL = "terminal"
    SUBWORKFLOW = "subworkflow"
    UNKNOWN = "unknown"


class AgentGraphEdgeCategory(StrEnum):
    DELEGATES_TO = "delegates_to"
    SENDS_CONTEXT_TO = "sends_context_to"
    RETURNS_RESULT_TO = "returns_result_to"
    JOINS_AT = "joins_at"
    HANDS_OFF_TO = "hands_off_to"
    FAILURE_ROUTES_TO = "failure_routes_to"
    RETRIES = "retries"
    APPROVAL_RESUMES = "approval_resumes"
    TRANSITIONS_TO = "transitions_to"


class AgentGraphBadgeSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    BLOCKING = "blocking"
    CRITICAL = "critical"


class AgentGraphBadgeSource(StrEnum):
    STATUS = "status"
    VALIDATION = "validation"
    REFERENCE = "reference"
    PROVENANCE = "provenance"
    RUNTIME = "runtime"


class AgentGraphReferenceType(StrEnum):
    ROLE = "role"
    PROMPT_PROFILE = "prompt_profile"
    PROMPT = "prompt"
    PROFILE = "profile"
    PROVIDER = "provider"
    SKILL = "skill"
    CONTRACT = "contract"
    SUBWORKFLOW = "subworkflow"
    JOIN_POLICY = "join_policy"
    APPROVAL_GATE = "approval_gate"
    WORKFLOW_VERSION = "workflow_version"
    RUN_STEP = "run_step"
    TIMELINE_EVENT = "timeline_event"
    HANDOFF = "handoff"
    APPROVAL = "approval"
    GATEWAY_ATTEMPT = "gateway_attempt"
    TOOL_CALL = "tool_call"
    DELIVERY = "delivery"
    ARTIFACT = "artifact"
    LINEAGE = "lineage"
    BUNDLE = "bundle"
    INTERACTION_EVIDENCE = "interaction_evidence"


class AgentGraphReferenceStatus(StrEnum):
    READY = "ready"
    WARNING = "warning"
    BLOCKED = "blocked"
    MISSING = "missing"
    UNKNOWN = "unknown"


class AgentGraphLayoutHint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x: int = 0
    y: int = 0


class AgentGraphBadge(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    severity: AgentGraphBadgeSeverity = AgentGraphBadgeSeverity.INFO
    label: str
    summary: str
    blocking: bool = False
    source: AgentGraphBadgeSource = AgentGraphBadgeSource.STATUS

    @field_validator("code", "label", "summary")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_agent_graph_text(value, max_length=220)


class AgentGraphReferenceSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reference_id: str
    reference_type: AgentGraphReferenceType
    label: str
    summary: str
    status: AgentGraphReferenceStatus = AgentGraphReferenceStatus.UNKNOWN
    href: str | None = None

    @field_validator("reference_id", "label", "summary", "href")
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        return safe_optional_agent_graph_text(value, max_length=240)


class AgentGraphNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_id: str
    node_key: str
    category: AgentGraphNodeCategory
    label: str
    summary: str
    status: str = "ready"
    role_key: str | None = None
    layout: AgentGraphLayoutHint = Field(default_factory=AgentGraphLayoutHint)
    references: tuple[AgentGraphReferenceSummary, ...] = Field(default_factory=tuple)
    badges: tuple[AgentGraphBadge, ...] = Field(default_factory=tuple)
    accessibility_label: str

    @field_validator(
        "node_id",
        "node_key",
        "label",
        "summary",
        "status",
        "role_key",
        "accessibility_label",
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        return safe_optional_agent_graph_text(value, max_length=260)


class AgentGraphEdge(BaseModel):
    model_config = ConfigDict(extra="forbid")

    edge_id: str
    edge_key: str
    source_node_id: str
    target_node_id: str
    category: AgentGraphEdgeCategory
    label: str
    summary: str
    contract_key: str | None = None
    status: str = "ready"
    references: tuple[AgentGraphReferenceSummary, ...] = Field(default_factory=tuple)
    badges: tuple[AgentGraphBadge, ...] = Field(default_factory=tuple)
    accessibility_label: str

    @field_validator(
        "edge_id",
        "edge_key",
        "source_node_id",
        "target_node_id",
        "label",
        "summary",
        "contract_key",
        "status",
        "accessibility_label",
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        return safe_optional_agent_graph_text(value, max_length=260)


class AgentGraphProvenance(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_type: AgentGraphSource
    workflow_draft_id: str | None = None
    workflow_version_bundle_id: str | None = None
    workflow_run_id: str | None = None
    run_bundle_id: str | None = None
    run_status: str | None = None
    workflow_lineage_id: str
    workflow_key: str
    revision: str
    source_revision_id: str | None = None
    source_digest: str | None = None
    scope_type: str
    tenant_id: str | None = None
    evidence_counts: dict[str, int] = Field(default_factory=dict)
    generated_at: datetime

    @field_validator(
        "workflow_draft_id",
        "workflow_version_bundle_id",
        "workflow_run_id",
        "run_bundle_id",
        "run_status",
        "workflow_lineage_id",
        "workflow_key",
        "revision",
        "source_revision_id",
        "source_digest",
        "scope_type",
        "tenant_id",
    )
    @classmethod
    def optional_text_is_safe(cls, value: str | None) -> str | None:
        return safe_optional_agent_graph_text(value, max_length=240)


class AgentGraphAccessibility(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str
    node_summaries: tuple[str, ...] = Field(default_factory=tuple)
    edge_summaries: tuple[str, ...] = Field(default_factory=tuple)

    @field_validator("summary")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_agent_graph_text(value, max_length=260)

    @field_validator("node_summaries", "edge_summaries")
    @classmethod
    def summaries_are_safe(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(safe_agent_graph_text(item, max_length=260) for item in value)


class AgentCommunicationGraph(BaseModel):
    model_config = ConfigDict(extra="forbid")

    graph_id: str
    source: AgentGraphSource
    state: AgentGraphState
    partial: bool = False
    provenance: AgentGraphProvenance
    nodes: tuple[AgentGraphNode, ...] = Field(default_factory=tuple)
    edges: tuple[AgentGraphEdge, ...] = Field(default_factory=tuple)
    badges: tuple[AgentGraphBadge, ...] = Field(default_factory=tuple)
    accessibility: AgentGraphAccessibility

    @field_validator("graph_id")
    @classmethod
    def text_is_safe(cls, value: str) -> str:
        return safe_agent_graph_text(value, max_length=220)
