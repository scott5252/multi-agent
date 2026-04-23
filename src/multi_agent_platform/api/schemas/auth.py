from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


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
