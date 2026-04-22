from __future__ import annotations

from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from multi_agent_platform.db.base import Base, TimestampMixin


class ArtifactStatus(StrEnum):
    ACTIVE = "active"
    DELETED = "deleted"


class ArtifactRecord(Base, TimestampMixin):
    __tablename__ = "artifacts"

    artifact_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    scope_type: Mapped[str] = mapped_column(String(32))
    provider: Mapped[str] = mapped_column(String(32))
    storage_key: Mapped[str] = mapped_column(String(255))
    media_type: Mapped[str] = mapped_column(
        String(128), default="application/octet-stream"
    )
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    checksum: Mapped[str | None] = mapped_column(String(128), nullable=True)
    retention_class: Mapped[str] = mapped_column(String(32), default="standard")
    status: Mapped[ArtifactStatus] = mapped_column(
        Enum(ArtifactStatus, native_enum=False),
        default=ArtifactStatus.ACTIVE,
    )
