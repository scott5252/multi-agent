from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, Boolean, DateTime, Enum, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from multi_agent_platform.db.base import Base, TimestampMixin, utcnow
from multi_agent_platform.model_providers.models import (
    ErrorCategory,
    HealthState,
    ProviderType,
    SyncAction,
    TestOutcome,
    VisibilityMode,
)


class ModelProviderConnection(Base, TimestampMixin):
    __tablename__ = "model_provider_connections"
    __table_args__ = (
        Index("ix_model_provider_connections_status", "active", "health_state"),
        Index("ix_model_provider_connections_type", "provider_type"),
    )

    provider_connection_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    provider_type: Mapped[ProviderType] = mapped_column(
        Enum(ProviderType, native_enum=False)
    )
    display_name: Mapped[str] = mapped_column(String(255))
    base_url_safe: Mapped[str | None] = mapped_column(String(512), nullable=True)
    timeout_policy: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    visibility_mode: Mapped[VisibilityMode] = mapped_column(
        Enum(VisibilityMode, native_enum=False),
        default=VisibilityMode.PLATFORM_DEFAULT,
    )
    active: Mapped[bool] = mapped_column(Boolean, default=False)
    health_state: Mapped[HealthState] = mapped_column(
        Enum(HealthState, native_enum=False),
        default=HealthState.UNTESTED,
    )
    credential_secret_reference_ids: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
    )
    safe_metadata: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    allowlist_decision_hash: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )
    created_by_principal_id: Mapped[str] = mapped_column(String(128))
    updated_by_principal_id: Mapped[str] = mapped_column(String(128))
    deactivated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class ProviderModelDefinition(Base, TimestampMixin):
    __tablename__ = "provider_model_definitions"
    __table_args__ = (
        Index(
            "ix_provider_model_definitions_connection_model",
            "provider_connection_id",
            "model_id",
            unique=True,
        ),
    )

    provider_model_definition_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    provider_connection_id: Mapped[UUID] = mapped_column(
        ForeignKey("model_provider_connections.provider_connection_id")
    )
    model_id: Mapped[str] = mapped_column(String(128))
    display_name: Mapped[str] = mapped_column(String(255))
    capability_metadata: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    cost_metadata: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    default_parameters: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    available: Mapped[bool] = mapped_column(Boolean, default=True)


class ConnectionTenantVisibility(Base):
    __tablename__ = "connection_tenant_visibility"
    __table_args__ = (
        Index(
            "ix_connection_tenant_visibility_scope",
            "provider_connection_id",
            "tenant_id",
            "visible",
        ),
    )

    connection_tenant_visibility_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    provider_connection_id: Mapped[UUID] = mapped_column(
        ForeignKey("model_provider_connections.provider_connection_id")
    )
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.tenant_id"))
    visible: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by_principal_id: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class ConnectionTestResult(Base):
    __tablename__ = "connection_test_results"
    __table_args__ = (
        Index(
            "ix_connection_test_results_latest",
            "provider_connection_id",
            "completed_at",
        ),
    )

    connection_test_result_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    provider_connection_id: Mapped[UUID] = mapped_column(
        ForeignKey("model_provider_connections.provider_connection_id")
    )
    provider_model_definition_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("provider_model_definitions.provider_model_definition_id"),
        nullable=True,
    )
    actor_principal_id: Mapped[str] = mapped_column(String(128))
    source: Mapped[str] = mapped_column(String(64), default="admin_user")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    latency_ms: Mapped[int] = mapped_column(Integer)
    outcome: Mapped[TestOutcome] = mapped_column(Enum(TestOutcome, native_enum=False))
    normalized_reason: Mapped[ErrorCategory] = mapped_column(
        Enum(ErrorCategory, native_enum=False)
    )
    tested_model_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    safe_diagnostic_summary: Mapped[str] = mapped_column(String(500))
    safe_provider_request_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    http_status_class: Mapped[str | None] = mapped_column(String(16), nullable=True)
    timeout_policy: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )


class ConnectionHealthSnapshot(Base):
    __tablename__ = "connection_health_snapshots"
    __table_args__ = (
        Index(
            "ix_connection_health_snapshots_latest",
            "provider_connection_id",
            "derived_at",
        ),
    )

    connection_health_snapshot_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    provider_connection_id: Mapped[UUID] = mapped_column(
        ForeignKey("model_provider_connections.provider_connection_id")
    )
    health_state: Mapped[HealthState] = mapped_column(
        Enum(HealthState, native_enum=False)
    )
    latest_test_result_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("connection_test_results.connection_test_result_id"),
        nullable=True,
    )
    derived_reason: Mapped[str] = mapped_column(String(255))
    derived_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    selectable: Mapped[bool] = mapped_column(Boolean, default=False)


class CatalogSyncRecord(Base):
    __tablename__ = "catalog_sync_records"
    __table_args__ = (
        Index("ix_catalog_sync_records_connection", "provider_connection_id"),
    )

    catalog_sync_record_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    provider_connection_id: Mapped[UUID] = mapped_column(
        ForeignKey("model_provider_connections.provider_connection_id")
    )
    provider_model_definition_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("provider_model_definitions.provider_model_definition_id"),
        nullable=True,
    )
    model_provider_entry_id: Mapped[UUID | None] = mapped_column(nullable=True)
    tenant_id: Mapped[UUID | None] = mapped_column(nullable=True)
    sync_action: Mapped[SyncAction] = mapped_column(Enum(SyncAction, native_enum=False))
    outcome: Mapped[TestOutcome] = mapped_column(Enum(TestOutcome, native_enum=False))
    normalized_reason: Mapped[ErrorCategory] = mapped_column(
        Enum(ErrorCategory, native_enum=False),
        default=ErrorCategory.NONE,
    )
    safe_summary: Mapped[str] = mapped_column(String(500))
    actor_principal_id: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )


class GatewayInvocationAttempt(Base):
    __tablename__ = "gateway_invocation_attempts"
    __table_args__ = (
        Index("ix_gateway_invocation_attempts_tenant_time", "tenant_id", "created_at"),
        Index(
            "ix_gateway_invocation_attempts_run",
            "workflow_run_id",
            "test_bench_run_id",
        ),
    )

    gateway_invocation_attempt_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    tenant_id: Mapped[UUID | None] = mapped_column(nullable=True)
    workflow_run_id: Mapped[UUID | None] = mapped_column(nullable=True)
    test_bench_run_id: Mapped[UUID | None] = mapped_column(nullable=True)
    trace_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    model_provider_entry_id: Mapped[UUID | None] = mapped_column(nullable=True)
    provider_connection_id: Mapped[UUID | None] = mapped_column(nullable=True)
    provider_model_definition_id: Mapped[UUID | None] = mapped_column(nullable=True)
    provider_type: Mapped[ProviderType] = mapped_column(
        Enum(ProviderType, native_enum=False)
    )
    model_id: Mapped[str] = mapped_column(String(128))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    latency_ms: Mapped[int] = mapped_column(Integer)
    outcome: Mapped[TestOutcome] = mapped_column(Enum(TestOutcome, native_enum=False))
    normalized_error_category: Mapped[ErrorCategory] = mapped_column(
        Enum(ErrorCategory, native_enum=False),
        default=ErrorCategory.NONE,
    )
    retry_attempt_number: Mapped[int] = mapped_column(Integer, default=0)
    retry_decision_summary: Mapped[dict[str, object]] = mapped_column(
        JSON,
        default=dict,
    )
    breaker_scope: Mapped[str | None] = mapped_column(String(255), nullable=True)
    breaker_decision_summary: Mapped[dict[str, object]] = mapped_column(
        JSON,
        default=dict,
    )
    usage_metadata: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    usage_available: Mapped[bool] = mapped_column(Boolean, default=False)
    safe_audit_summary: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
    )
