from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from multi_agent_platform.db.base import Base, TimestampMixin


class TenantStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"


class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"

    tenant_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    slug: Mapped[str] = mapped_column(String(128), unique=True)
    display_name: Mapped[str] = mapped_column(String(255))
    status: Mapped[TenantStatus] = mapped_column(
        Enum(TenantStatus, native_enum=False),
        default=TenantStatus.ACTIVE,
    )

    limit_policies: Mapped[list[TenantLimitPolicy]] = relationship(
        back_populates="tenant"
    )


class TenantLimitPolicy(Base):
    __tablename__ = "tenant_limit_policies"
    __table_args__ = (UniqueConstraint("tenant_id", "effective_from"),)

    policy_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey("tenants.tenant_id", ondelete="CASCADE")
    )
    max_concurrent_jobs: Mapped[int] = mapped_column(Integer, default=5)
    max_api_rps: Mapped[int] = mapped_column(Integer, default=10)
    max_artifact_bytes: Mapped[int] = mapped_column(Integer, default=10_000_000)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    effective_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    tenant: Mapped[Tenant] = relationship(back_populates="limit_policies")
