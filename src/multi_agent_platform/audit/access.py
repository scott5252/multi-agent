from __future__ import annotations

from multi_agent_platform.audit.models import AuditEventCreate
from multi_agent_platform.audit.service import AuditService
from multi_agent_platform.auth.policy import AuthorizationDecision
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.models.access_control import (
    AccessDecision,
    AccessDecisionRecord,
)
from multi_agent_platform.db.repositories.access_control import AccessControlRepository


class AccessAuditRecorder:
    def __init__(
        self,
        access_repository: AccessControlRepository,
        audit_service: AuditService,
    ) -> None:
        self.access_repository = access_repository
        self.audit_service = audit_service

    async def record_decision(
        self,
        *,
        principal: PrincipalContext | None,
        decision: AuthorizationDecision,
        auth_mode: str,
        trace_id: str,
        request_id: str | None,
    ) -> None:
        record = AccessDecisionRecord(
            principal_identity_id=(
                None if principal is None else principal.principal_identity_id
            ),
            scope_type="tenant"
            if decision.target_tenant_id is not None
            else "platform",
            tenant_id=decision.target_tenant_id,
            surface_key=decision.surface_key,
            requested_action=decision.requested_action,
            decision=AccessDecision.ALLOW if decision.allowed else AccessDecision.DENY,
            reason_code=decision.reason_code,
            auth_mode=auth_mode,
            token_subject=None if principal is None else principal.token_subject,
            token_jti=None if principal is None else principal.token_jti,
            support_override_request_id=decision.support_override_request_id,
            delegated_credential_link_id=None
            if principal is None
            else principal.delegated_credential_link_id,
            trace_id=trace_id,
            request_id=request_id,
            classification=decision.classification.value,
            required_roles=list(decision.required_roles),
            required_permissions=list(decision.required_permissions),
        )
        await self.access_repository.record_access_decision(record)
        await self.audit_service.record(
            AuditEventCreate(
                tenant_id=decision.target_tenant_id,
                scope_type="tenant"
                if decision.target_tenant_id is not None
                else "platform",
                actor_id="system" if principal is None else principal.principal_id,
                action=decision.requested_action,
                entity_type="access_decision",
                entity_id=record.access_decision_record_id.hex,
                trace_id=trace_id,
                request_id=request_id,
                payload_redacted={
                    "surface_key": decision.surface_key,
                    "allowed": str(decision.allowed).lower(),
                    "reason_code": decision.reason_code.value,
                },
            )
        )
