from __future__ import annotations

from uuid import UUID

from multi_agent_platform.admin.support_overrides import build_override_expiration
from multi_agent_platform.audit.access import AccessAuditRecorder
from multi_agent_platform.db.models.access_control import (
    GrantSource,
    RoleGrant,
    SupportOverrideRequest,
)
from multi_agent_platform.db.models.tenant import TenantLimitPolicy
from multi_agent_platform.db.repositories.access_control import AccessControlRepository
from multi_agent_platform.db.repositories.tenant_limits import TenantLimitRepository


class AdminService:
    def __init__(
        self,
        repository: TenantLimitRepository | None = None,
        access_repository: AccessControlRepository | None = None,
        audit_recorder: AccessAuditRecorder | None = None,
    ) -> None:
        self.repository = repository
        self.access_repository = access_repository
        self.audit_recorder = audit_recorder

    async def update_limits(self, policy: TenantLimitPolicy) -> TenantLimitPolicy:
        if self.repository is None:
            raise RuntimeError("tenant limit repository is not configured")
        return await self.repository.upsert(policy)

    async def list_role_grants_for_tenant(self, tenant_id: UUID) -> list[RoleGrant]:
        if self.access_repository is None:
            raise RuntimeError("access repository is not configured")
        return await self.access_repository.list_role_grants_for_tenant(tenant_id)

    async def upsert_role_grant(self, grant: RoleGrant) -> RoleGrant:
        if self.access_repository is None:
            raise RuntimeError("access repository is not configured")
        if grant.grant_source is None:  # pragma: no cover - ORM default fallback
            grant.grant_source = GrantSource.ADMIN_ASSIGNMENT
        return await self.access_repository.upsert_role_grant(grant)

    async def create_support_override(
        self,
        *,
        requester_principal_id: UUID,
        target_tenant_id: UUID,
        justification: str,
        trace_id: str,
        idempotency_key: str,
    ) -> SupportOverrideRequest:
        if self.access_repository is None:
            raise RuntimeError("access repository is not configured")
        request = SupportOverrideRequest(
            requester_principal_id=requester_principal_id,
            target_tenant_id=target_tenant_id,
            justification=justification,
            request_trace_id=trace_id,
            idempotency_key=idempotency_key,
        )
        return await self.access_repository.create_support_override(request)

    async def approve_support_override(
        self,
        *,
        support_override_request_id: UUID,
        approver_principal_id: UUID,
        expires_in_hours: int = 1,
    ) -> SupportOverrideRequest | None:
        if self.access_repository is None:
            raise RuntimeError("access repository is not configured")
        existing = await self.access_repository.get_support_override(
            support_override_request_id
        )
        if existing is None:
            return None
        if existing.requester_principal_id == approver_principal_id:
            raise ValueError("requester cannot approve their own support override")
        return await self.access_repository.approve_support_override(
            support_override_request_id,
            approver_principal_id=approver_principal_id,
            expires_at=build_override_expiration(hours=expires_in_hours),
        )
