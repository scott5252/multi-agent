from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field

from multi_agent_platform.tenancy.context import ScopeType


class AuthProvider(StrEnum):
    AUTH0 = "auth0"
    LOCAL_PRINCIPAL = "local_principal"
    SYSTEM = "system"


class AuthMode(StrEnum):
    AUTH0 = "auth0"
    LOCAL_PRINCIPAL = "local_principal"


class PrincipalContext(BaseModel):
    principal_identity_id: UUID | None = None
    principal_id: str = "system"
    auth_provider: AuthProvider = AuthProvider.SYSTEM
    auth_mode: AuthMode = AuthMode.LOCAL_PRINCIPAL
    tenant_id: UUID | None = None
    org_id: str | None = None
    role_codes: tuple[str, ...] = Field(default_factory=tuple)
    permission_codes: tuple[str, ...] = Field(default_factory=tuple)
    scope_type: ScopeType = ScopeType.PLATFORM
    support_override_request_id: UUID | None = None
    trace_id: str = "trace"
    request_id: str | None = None
    token_subject: str | None = None
    token_jti: str | None = None
    delegated_credential_link_id: UUID | None = None

    @property
    def is_authenticated(self) -> bool:
        return self.auth_provider is not AuthProvider.SYSTEM

    @property
    def roles(self) -> tuple[str, ...]:
        return self.role_codes


class Principal(PrincipalContext):
    actor_type: str = "user"

    @property
    def is_admin(self) -> bool:
        return any(
            role in self.role_codes
            for role in ("tenant_admin", "platform_admin", "admin", "platform")
        )
