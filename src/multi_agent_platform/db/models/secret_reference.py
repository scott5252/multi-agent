from __future__ import annotations

from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import JSON, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from multi_agent_platform.db.base import Base, TimestampMixin


class SecretReferenceStatus(StrEnum):
    ACTIVE = "active"
    REVOKED = "revoked"


class SecretReference(Base, TimestampMixin):
    __tablename__ = "secret_references"

    secret_reference_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("tenants.tenant_id"), nullable=True
    )
    scope_type: Mapped[str] = mapped_column(String(32))
    name: Mapped[str] = mapped_column(String(128))
    provider_key: Mapped[str] = mapped_column(String(255))
    access_policy: Mapped[dict[str, str]] = mapped_column(JSON, default=dict)
    status: Mapped[SecretReferenceStatus] = mapped_column(
        Enum(SecretReferenceStatus, native_enum=False),
        default=SecretReferenceStatus.ACTIVE,
    )
