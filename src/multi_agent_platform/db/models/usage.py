from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from multi_agent_platform.db.base import Base, TimestampMixin, utcnow
from multi_agent_platform.model_providers.models import UsageValueStatus
from multi_agent_platform.usage.models import (
    UsageEventStatus,
    UsageExportStatus,
    UsageScopeType,
)


class LlmUsageEvent(Base, TimestampMixin):
    __tablename__ = "llm_usage_events"
    __table_args__ = (
        Index("ix_llm_usage_events_tenant_time", "tenant_id", "recorded_at"),
        Index("ix_llm_usage_events_provider_model", "provider_key", "model_id"),
        Index(
            "ix_llm_usage_events_workflow",
            "tenant_id",
            "workflow_lineage_id",
            "workflow_version_id",
        ),
        Index("ix_llm_usage_events_agent", "tenant_id", "agent_key", "sub_agent_key"),
        Index("ix_llm_usage_events_principal", "tenant_id", "principal_id"),
        Index(
            "ix_llm_usage_events_idempotency",
            "tenant_id",
            "idempotency_key",
            "provider_key",
            "model_id",
            unique=True,
        ),
    )

    llm_usage_event_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.tenant_id"))
    principal_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    workflow_run_id: Mapped[UUID | None] = mapped_column(nullable=True)
    workflow_run_step_id: Mapped[UUID | None] = mapped_column(nullable=True)
    workflow_lineage_id: Mapped[UUID | None] = mapped_column(nullable=True)
    workflow_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    agent_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    sub_agent_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    provider_key: Mapped[str] = mapped_column(String(128))
    provider_connection_id: Mapped[UUID | None] = mapped_column(nullable=True)
    model_id: Mapped[str] = mapped_column(String(128))
    prompt_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    agent_profile_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    execution_mode: Mapped[str] = mapped_column(String(64), default="production")
    operation_identity: Mapped[str | None] = mapped_column(String(255), nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    trace_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cached_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reasoning_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    provider_billable_units: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    input_status: Mapped[UsageValueStatus] = mapped_column(
        Enum(UsageValueStatus, native_enum=False),
        default=UsageValueStatus.UNAVAILABLE,
    )
    output_status: Mapped[UsageValueStatus] = mapped_column(
        Enum(UsageValueStatus, native_enum=False),
        default=UsageValueStatus.UNAVAILABLE,
    )
    cached_status: Mapped[UsageValueStatus] = mapped_column(
        Enum(UsageValueStatus, native_enum=False),
        default=UsageValueStatus.NOT_APPLICABLE,
    )
    reasoning_status: Mapped[UsageValueStatus] = mapped_column(
        Enum(UsageValueStatus, native_enum=False),
        default=UsageValueStatus.NOT_APPLICABLE,
    )
    total_status: Mapped[UsageValueStatus] = mapped_column(
        Enum(UsageValueStatus, native_enum=False),
        default=UsageValueStatus.UNAVAILABLE,
    )
    billable_status: Mapped[UsageValueStatus] = mapped_column(
        Enum(UsageValueStatus, native_enum=False),
        default=UsageValueStatus.UNAVAILABLE,
    )
    cost_status: Mapped[UsageValueStatus] = mapped_column(
        Enum(UsageValueStatus, native_enum=False),
        default=UsageValueStatus.UNAVAILABLE,
    )
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    estimated_cost_micros: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pricing_version_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("llm_pricing_versions.llm_pricing_version_id"),
        nullable=True,
    )
    usage_status: Mapped[UsageEventStatus] = mapped_column(
        Enum(UsageEventStatus, native_enum=False),
        default=UsageEventStatus.UNAVAILABLE,
    )
    source_gateway_attempt_id: Mapped[UUID | None] = mapped_column(nullable=True)
    safe_attribution: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class LlmPricingVersion(Base):
    __tablename__ = "llm_pricing_versions"
    __table_args__ = (
        Index(
            "ix_llm_pricing_versions_lookup",
            "provider_key",
            "model_id",
            "currency",
            "effective_from",
        ),
    )

    llm_pricing_version_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    provider_key: Mapped[str] = mapped_column(String(128))
    model_id: Mapped[str] = mapped_column(String(128))
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    input_token_micros: Mapped[int] = mapped_column(Integer, default=1)
    output_token_micros: Mapped[int] = mapped_column(Integer, default=3)
    cached_token_micros: Mapped[int] = mapped_column(Integer, default=0)
    reasoning_token_micros: Mapped[int] = mapped_column(Integer, default=3)
    billable_unit_micros: Mapped[int | None] = mapped_column(Integer, nullable=True)
    calculation_method: Mapped[str] = mapped_column(String(64), default="per_token")
    effective_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )
    effective_to: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    source_note: Mapped[str] = mapped_column(
        String(255), default="default internal QA pricing"
    )
    created_by_principal_id: Mapped[str] = mapped_column(String(255), default="system")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class LlmUsageRollup(Base):
    __tablename__ = "llm_usage_rollups"
    __table_args__ = (
        Index("ix_llm_usage_rollups_bucket", "tenant_id", "bucket_start", "bucket_end"),
    )

    llm_usage_rollup_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.tenant_id"))
    bucket_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    bucket_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    bucket_granularity: Mapped[str] = mapped_column(String(32))
    provider_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    model_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    workflow_lineage_id: Mapped[UUID | None] = mapped_column(nullable=True)
    agent_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    sub_agent_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    prompt_version_id: Mapped[UUID | None] = mapped_column(nullable=True)
    execution_mode: Mapped[str | None] = mapped_column(String(64), nullable=True)
    principal_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    event_count: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost_micros: Mapped[int] = mapped_column(Integer, default=0)
    estimated_event_count: Mapped[int] = mapped_column(Integer, default=0)
    confirmed_event_count: Mapped[int] = mapped_column(Integer, default=0)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )


class UsageExportRequest(Base):
    __tablename__ = "usage_export_requests"
    __table_args__ = (
        Index(
            "ix_usage_export_requests_scope", "scope_type", "tenant_id", "created_at"
        ),
    )

    usage_export_request_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"),
        nullable=True,
    )
    requested_by_principal_id: Mapped[str] = mapped_column(String(255))
    scope_type: Mapped[UsageScopeType] = mapped_column(
        Enum(UsageScopeType, native_enum=False),
    )
    filters: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    status: Mapped[UsageExportStatus] = mapped_column(
        Enum(UsageExportStatus, native_enum=False),
        default=UsageExportStatus.PENDING,
    )
    row_count: Mapped[int] = mapped_column(Integer, default=0)
    artifact_uri: Mapped[str | None] = mapped_column(String(512), nullable=True)
    artifact_sha256: Mapped[str | None] = mapped_column(String(128), nullable=True)
    artifact_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    denial_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class UsageReconciliationRecord(Base):
    __tablename__ = "usage_reconciliation_records"
    __table_args__ = (
        Index(
            "ix_usage_reconciliation_event",
            "llm_usage_event_id",
            "created_at",
        ),
    )

    usage_reconciliation_record_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    llm_usage_event_id: Mapped[UUID] = mapped_column(
        ForeignKey("llm_usage_events.llm_usage_event_id"),
    )
    source: Mapped[str] = mapped_column(String(128))
    previous_values: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    confirmed_values: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    reconciled_by_principal_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
