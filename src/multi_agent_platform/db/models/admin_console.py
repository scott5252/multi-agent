from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import JSON, CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from multi_agent_platform.db.base import Base, TimestampMixin


class AdminSavedFilterScope(StrEnum):
    PLATFORM = "platform"
    TENANT = "tenant"


class AdminSavedFilterArea(StrEnum):
    WORKFLOWS = "workflows"
    MODEL_SKILL_HISTORY = "model_skill_history"
    RUN_INSPECTION = "run_inspection"
    RELIABILITY_BREAKERS = "reliability_breakers"
    RELIABILITY_DEAD_LETTERS = "reliability_dead_letters"


class AdminSavedFilter(Base, TimestampMixin):
    __tablename__ = "admin_saved_filters"
    __table_args__ = (
        CheckConstraint(
            "(scope_type = 'platform' AND tenant_id IS NULL) OR "
            "(scope_type = 'tenant' AND tenant_id IS NOT NULL)",
            name="scope_tenant",
        ),
        UniqueConstraint(
            "principal_identity_id",
            "principal_id",
            "admin_area",
            "filter_key",
            "scope_type",
            "tenant_id",
            "display_name",
            name="uq_admin_saved_filters_scope_name",
        ),
    )

    admin_saved_filter_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    principal_identity_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("principal_identities.principal_identity_id", ondelete="CASCADE"),
        nullable=True,
    )
    principal_id: Mapped[str] = mapped_column(String(128))
    admin_area: Mapped[str] = mapped_column(String(64))
    filter_key: Mapped[str] = mapped_column(String(128))
    scope_type: Mapped[str] = mapped_column(String(32))
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    display_name: Mapped[str] = mapped_column(String(120))
    criteria: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    safe_summary: Mapped[dict[str, str]] = mapped_column(JSON, default=dict)
    criteria_schema_version: Mapped[str] = mapped_column(
        String(32), default="2026-04-27"
    )
    last_restored_at: Mapped[datetime | None] = mapped_column(nullable=True)
