from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from multi_agent_platform.db.base import Base, TimestampMixin, utcnow


class AgentTestTargetType(StrEnum):
    PROMPT_VERSION = "prompt_version"
    AGENT_PROFILE_VERSION = "agent_profile_version"
    WORKFLOW_DRAFT = "workflow_draft"
    PUBLISHED_SUBWORKFLOW = "published_subworkflow"
    PUBLISHED_WORKFLOW = "published_workflow"


class AgentTestSafeMode(StrEnum):
    MOCK_MODEL = "mock_model"
    MOCK_TOOLS = "mock_tools"
    REAL_MODEL_SIDE_EFFECTS_DISABLED = "real_model_side_effects_disabled"
    APPROVED_REAL_PROBE = "approved_real_probe"


class AgentTestStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class AgentTestRunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    ERROR = "error"


class AgentTestAssertionKind(StrEnum):
    DETERMINISTIC = "deterministic"
    EVALUATOR = "evaluator"


class AgentTestSuite(Base, TimestampMixin):
    __tablename__ = "agent_test_suites"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_agent_test_suites_tenant_name"),
        Index(
            "ix_agent_test_suites_tenant_target",
            "tenant_id",
            "target_type",
            "target_id",
        ),
        Index("ix_agent_test_suites_required", "tenant_id", "is_required_for_publish"),
    )

    agent_test_suite_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    target_type: Mapped[AgentTestTargetType] = mapped_column(
        Enum(AgentTestTargetType, native_enum=False),
        nullable=False,
    )
    target_id: Mapped[str] = mapped_column(String(255), nullable=False)
    target_version: Mapped[str | None] = mapped_column(String(128), nullable=True)
    default_safe_mode: Mapped[AgentTestSafeMode] = mapped_column(
        Enum(AgentTestSafeMode, native_enum=False),
        default=AgentTestSafeMode.MOCK_MODEL,
    )
    model_mode: Mapped[str] = mapped_column(String(64), default="mock")
    tool_mode: Mapped[str] = mapped_column(String(64), default="mock")
    pass_threshold: Mapped[float] = mapped_column(Float, default=1.0)
    is_required_for_publish: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[AgentTestStatus] = mapped_column(
        Enum(AgentTestStatus, native_enum=False),
        default=AgentTestStatus.ACTIVE,
    )
    revision: Mapped[int] = mapped_column(Integer, default=1)
    created_by_principal_id: Mapped[str] = mapped_column(String(255), nullable=False)
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class AgentTestCase(Base, TimestampMixin):
    __tablename__ = "agent_test_cases"
    __table_args__ = (
        Index("ix_agent_test_cases_suite_order", "agent_test_suite_id", "case_order"),
    )

    agent_test_case_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    agent_test_suite_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_test_suites.agent_test_suite_id", ondelete="CASCADE"),
        nullable=False,
    )
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    fixture_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    fixture_artifact_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("artifacts.artifact_id"), nullable=True
    )
    expected_contract_shape: Mapped[dict[str, object]] = mapped_column(
        JSON, default=dict
    )
    model_mode: Mapped[str] = mapped_column(String(64), default="inherit")
    tool_mode: Mapped[str] = mapped_column(String(64), default="inherit")
    evaluator_prompt_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pass_threshold: Mapped[float] = mapped_column(Float, default=1.0)
    case_order: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[AgentTestStatus] = mapped_column(
        Enum(AgentTestStatus, native_enum=False),
        default=AgentTestStatus.ACTIVE,
    )
    revision: Mapped[int] = mapped_column(Integer, default=1)
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class AgentTestAssertion(Base, TimestampMixin):
    __tablename__ = "agent_test_assertions"
    __table_args__ = (Index("ix_agent_test_assertions_case", "agent_test_case_id"),)

    agent_test_assertion_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    agent_test_case_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_test_cases.agent_test_case_id", ondelete="CASCADE"),
        nullable=False,
    )
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=False
    )
    kind: Mapped[AgentTestAssertionKind] = mapped_column(
        Enum(AgentTestAssertionKind, native_enum=False),
        default=AgentTestAssertionKind.DETERMINISTIC,
    )
    path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    comparator: Mapped[str | None] = mapped_column(String(64), nullable=True)
    expected_value: Mapped[object | None] = mapped_column(JSON, nullable=True)
    expected_schema: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    threshold: Mapped[float | None] = mapped_column(Float, nullable=True)
    severity: Mapped[str] = mapped_column(String(64), default="blocking")
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)


class AgentTestRun(Base):
    __tablename__ = "agent_test_runs"
    __table_args__ = (
        Index(
            "ix_agent_test_runs_tenant_suite_status",
            "tenant_id",
            "agent_test_suite_id",
            "status",
        ),
        Index(
            "ix_agent_test_runs_target_version",
            "tenant_id",
            "target_type",
            "target_id",
            "target_version",
        ),
        Index(
            "ix_agent_test_runs_idempotency",
            "tenant_id",
            "idempotency_key",
            unique=True,
        ),
    )

    agent_test_run_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=False
    )
    agent_test_suite_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_test_suites.agent_test_suite_id"),
        nullable=False,
    )
    target_type: Mapped[AgentTestTargetType] = mapped_column(
        Enum(AgentTestTargetType, native_enum=False),
        nullable=False,
    )
    target_id: Mapped[str] = mapped_column(String(255), nullable=False)
    target_version: Mapped[str | None] = mapped_column(String(128), nullable=True)
    safe_mode: Mapped[AgentTestSafeMode] = mapped_column(
        Enum(AgentTestSafeMode, native_enum=False),
        default=AgentTestSafeMode.MOCK_MODEL,
    )
    status: Mapped[AgentTestRunStatus] = mapped_column(
        Enum(AgentTestRunStatus, native_enum=False),
        default=AgentTestRunStatus.QUEUED,
    )
    pass_status: Mapped[str] = mapped_column(String(64), default="pending")
    triggered_by_principal_id: Mapped[str] = mapped_column(String(255), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False)
    trace_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    usage_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    redaction_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    artifact_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    blocked_side_effect_count: Mapped[int] = mapped_column(Integer, default=0)
    failure_summary: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class AgentTestRunStep(Base):
    __tablename__ = "agent_test_run_steps"
    __table_args__ = (
        Index("ix_agent_test_run_steps_run_sequence", "agent_test_run_id", "sequence"),
    )

    agent_test_run_step_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    agent_test_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_test_runs.agent_test_run_id", ondelete="CASCADE"),
        nullable=False,
    )
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=False
    )
    agent_test_case_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("agent_test_cases.agent_test_case_id"), nullable=True
    )
    step_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[AgentTestRunStatus] = mapped_column(
        Enum(AgentTestRunStatus, native_enum=False),
        default=AgentTestRunStatus.QUEUED,
    )
    sequence: Mapped[int] = mapped_column(Integer, default=0)
    model_provider: Mapped[str | None] = mapped_column(String(128), nullable=True)
    model_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    prompt_version_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    profile_version_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    skill_version_refs: Mapped[list[str]] = mapped_column(JSON, default=list)
    workflow_version_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    token_usage: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    contract_validation: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    assertion_results: Mapped[list[dict[str, object]]] = mapped_column(
        JSON, default=list
    )
    blocked_side_effects: Mapped[list[dict[str, object]]] = mapped_column(
        JSON, default=list
    )
    redacted_transcript: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    artifact_refs: Mapped[list[str]] = mapped_column(JSON, default=list)
    failure_reason: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class AgentTestArtifact(Base):
    __tablename__ = "agent_test_artifacts"
    __table_args__ = (Index("ix_agent_test_artifacts_run", "agent_test_run_id"),)

    agent_test_artifact_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=False
    )
    agent_test_run_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("agent_test_runs.agent_test_run_id"), nullable=True
    )
    agent_test_case_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("agent_test_cases.agent_test_case_id"), nullable=True
    )
    artifact_type: Mapped[str] = mapped_column(String(64), nullable=False)
    storage_uri: Mapped[str | None] = mapped_column(String(512), nullable=True)
    checksum_sha256: Mapped[str | None] = mapped_column(String(128), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    redaction_classification: Mapped[str] = mapped_column(
        String(64), default="safe_summary"
    )
    retention_state: Mapped[str] = mapped_column(String(64), default="retained")
    safe_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class AgentTestPublicationRequirement(Base, TimestampMixin):
    __tablename__ = "agent_test_publication_requirements"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "target_type",
            "target_id",
            "agent_test_suite_id",
            name="uq_agent_test_publication_requirement",
        ),
        Index("ix_agent_test_pub_req_target", "tenant_id", "target_type", "target_id"),
    )

    agent_test_publication_requirement_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=False
    )
    target_type: Mapped[AgentTestTargetType] = mapped_column(
        Enum(AgentTestTargetType, native_enum=False),
        nullable=False,
    )
    target_id: Mapped[str] = mapped_column(String(255), nullable=False)
    agent_test_suite_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_test_suites.agent_test_suite_id"),
        nullable=False,
    )
    required: Mapped[bool] = mapped_column(Boolean, default=True)
    minimum_pass_status: Mapped[str] = mapped_column(String(64), default="passed")
    created_by_principal_id: Mapped[str] = mapped_column(String(255), nullable=False)
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
