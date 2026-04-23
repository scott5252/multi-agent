from __future__ import annotations

from multi_agent_platform.audit.access import AccessAuditRecorder
from multi_agent_platform.audit.service import AuditService
from multi_agent_platform.auth.policy import (
    AuthorizationDecision,
    SurfaceClassification,
)
from multi_agent_platform.auth.principal import PrincipalContext
from multi_agent_platform.db.models.access_control import AccessReasonCode
from multi_agent_platform.db.repositories.access_control import AccessControlRepository
from multi_agent_platform.db.repositories.audit import AuditRepository


async def test_access_audit_recorder_persists_decision_and_audit_event(session) -> None:
    access_repository = AccessControlRepository(session)
    audit_repository = AuditRepository(session)
    recorder = AccessAuditRecorder(access_repository, AuditService(audit_repository))

    await recorder.record_decision(
        principal=PrincipalContext(principal_id="tenant-admin", trace_id="trace-1"),
        decision=AuthorizationDecision(
            surface_key="GET:/auth/me",
            requested_action="read_principal_context",
            classification=SurfaceClassification.AUTHENTICATED,
            allowed=True,
            reason_code=AccessReasonCode.UNAUTHENTICATED,
        ),
        auth_mode="local_principal",
        trace_id="trace-1",
        request_id="req-1",
    )

    decisions = await access_repository.list_access_decisions_by_trace("trace-1")
    events = await audit_repository.list_by_trace("trace-1")

    assert decisions[0].surface_key == "GET:/auth/me"
    assert events[0].entity_type == "access_decision"
