from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.db.repositories.audit_debugging import (
    AuditDebuggingRepository,
)
from multi_agent_platform.secrets.base import secret_access_audit_metadata


async def test_secret_access_audit_metadata_never_contains_raw_secret(session) -> None:
    metadata = secret_access_audit_metadata(
        requester_type="tool",
        requester_ref="tool:email",
        secret_reference_id="secret-ref",
        policy_outcome="deny",
        access_outcome="blocked",
        reason_code="scope_denied",
    )
    assert "value" not in metadata
    repository = AuditDebuggingRepository(session)
    record = await repository.create_secret_access_record(
        tenant_id=uuid4(),
        workflow_run_id=uuid4(),
        requester_type="tool",
        requester_ref="tool:email",
        secret_reference_id="secret-ref",
        policy_outcome="deny",
        access_outcome="blocked",
        reason_code="scope_denied",
        safe_reason="credential scope denied",
        trace_id="trace",
    )
    assert record.safe_reason == "credential scope denied"
    assert "raw" not in str(record.__dict__).lower()
