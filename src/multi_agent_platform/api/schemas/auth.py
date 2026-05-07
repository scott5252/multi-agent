from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ErrorResponse(BaseModel):
    detail: str


class PrincipalContextResponse(BaseModel):
    principal_id: str
    auth_mode: str
    auth_provider: str
    tenant_id: UUID | None = None
    org_id: str | None = None
    role_codes: list[str] = Field(default_factory=list)
    permission_codes: list[str] = Field(default_factory=list)
    scope_type: str
    support_override_request_id: UUID | None = None


class LocalPrincipalOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    catalog_key: str
    label: str
    scope_type: Literal["platform", "tenant"]
    tenant_id: UUID | None = None
    tenant_label: str | None = None
    role_codes: tuple[str, ...] = Field(default_factory=tuple)

    @field_validator("label", "tenant_label")
    @classmethod
    def safe_label(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = " ".join(value.strip().split())
        if not value:
            raise ValueError("label is required")
        return value[:80]


class LocalLoginEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    auth_mode: Literal["local_principal"]
    principals: tuple[LocalPrincipalOption, ...] = Field(default_factory=tuple)
    current_principal_key: str | None = None
    redirect_to: str
    action_token: str


class LocalLoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    principal_key: str
    redirect_to: str = "/admin/app"
    action_token: str


class RoleGrantResponse(BaseModel):
    role_grant_id: UUID
    principal_identity_id: UUID
    scope_type: str
    tenant_id: UUID | None = None
    role_code: str
    status: str


class RoleGrantUpsertRequest(BaseModel):
    principal_identity_id: UUID
    scope_type: str
    tenant_id: UUID | None = None
    role_code: str


class SupportOverrideCreateRequest(BaseModel):
    tenant_id: UUID
    justification: str
    idempotency_key: str


class SupportOverrideApproveRequest(BaseModel):
    expires_in_hours: int = 1


class SupportOverrideResponse(BaseModel):
    support_override_request_id: UUID
    requester_principal_id: UUID
    target_tenant_id: UUID
    status: str
    approver_principal_id: UUID | None = None
    expires_at: datetime | None = None
