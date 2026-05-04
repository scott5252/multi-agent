from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from multi_agent_platform.model_providers.models import (
    ErrorCategory,
    HealthState,
    ProviderModel,
    ProviderType,
    TenantVisibility,
    TestOutcome,
    TimeoutPolicy,
    VisibilityMode,
)


class ModelProviderError(BaseModel):
    category: str
    message: str


class ProviderConnectionCreateRequest(BaseModel):
    provider_type: ProviderType
    display_name: str = Field(min_length=1, max_length=255)
    base_url: str | None = Field(default=None, max_length=512)
    timeout_policy: TimeoutPolicy = Field(default_factory=TimeoutPolicy)
    visibility: TenantVisibility = Field(default_factory=TenantVisibility)
    models: tuple[ProviderModel, ...] = Field(min_length=1)
    credential_secret_reference_ids: tuple[str, ...] = Field(default_factory=tuple)
    active: bool = False

    @model_validator(mode="after")
    def validate_secret_refs(self) -> ProviderConnectionCreateRequest:
        normalized: list[str] = []
        seen: set[str] = set()
        for reference in self.credential_secret_reference_ids:
            safe_reference = reference.strip()
            if not safe_reference:
                raise ValueError("credential secret references cannot be blank")
            lowered = safe_reference.lower()
            if any(
                marker in lowered
                for marker in ("sk-", "bearer ", "password", "secret=", "api_key=")
            ):
                raise ValueError("credential fields accept secret references only")
            if safe_reference in seen:
                raise ValueError("credential secret references must be unique")
            seen.add(safe_reference)
            normalized.append(safe_reference)
        self.credential_secret_reference_ids = tuple(normalized)
        return self


class ProviderConnectionUpdateRequest(ProviderConnectionCreateRequest):
    pass


class ProviderConnectionResponse(BaseModel):
    provider_connection_id: UUID
    provider_type: ProviderType
    display_name: str
    base_url_safe: str | None = None
    timeout_policy: TimeoutPolicy
    visibility: TenantVisibility
    active: bool
    health_state: HealthState
    credential_secret_reference_ids: tuple[str, ...]
    models: tuple[ProviderModel, ...] = Field(default_factory=tuple)
    updated_at: datetime | None = None


class ProviderConnectionListItem(BaseModel):
    provider_connection_id: UUID
    provider_type: ProviderType
    display_name: str
    active: bool
    health_state: HealthState
    last_test_outcome: TestOutcome | None = None
    last_test_reason: ErrorCategory | None = None
    model_count: int
    visibility_mode: VisibilityMode
    tenant_count: int
    catalog_sync_status: str
    updated_at: datetime | None = None


class ProviderConnectionListResponse(BaseModel):
    items: tuple[ProviderConnectionListItem, ...]


class ProviderTestResponse(BaseModel):
    outcome: TestOutcome
    normalized_reason: ErrorCategory
    latency_ms: int
    tested_model_id: str | None = None
    safe_diagnostic_summary: str
    completed_at: datetime


class CatalogSyncResponse(BaseModel):
    created: int
    updated: int
    blocked: int
    marked_unavailable: int
    safe_summary: str
