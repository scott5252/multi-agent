from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from multi_agent_platform.db.base import Base


class DelegatedCredentialStatus(StrEnum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class DelegatedCredentialLink(Base):
    __tablename__ = "delegated_credential_links"

    delegated_credential_link_id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4
    )
    secret_reference_id: Mapped[UUID] = mapped_column(
        ForeignKey("secret_references.secret_reference_id")
    )
    owner_principal_id: Mapped[UUID] = mapped_column(
        ForeignKey("principal_identities.principal_identity_id")
    )
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.tenant_id"))
    approved_tool_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    granted_scopes: Mapped[list[str]] = mapped_column(JSON, default=list)
    status: Mapped[DelegatedCredentialStatus] = mapped_column(
        Enum(DelegatedCredentialStatus, native_enum=False),
        default=DelegatedCredentialStatus.ACTIVE,
    )
    provider_subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
