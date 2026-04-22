from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from multi_agent_platform.db.models.audit import AuditActorType, AuditEvent
from multi_agent_platform.db.models.queue import JobKind, JobStatus, QueueJob
from multi_agent_platform.db.models.tenant import (
    Tenant,
    TenantLimitPolicy,
    TenantStatus,
)


def test_tenant_and_policy_defaults() -> None:
    tenant = Tenant(slug="acme", display_name="Acme", status=TenantStatus.ACTIVE)
    policy = TenantLimitPolicy(
        tenant_id=uuid4(),
        enabled=True,
        effective_from=datetime.now(UTC),
    )
    assert tenant.status is TenantStatus.ACTIVE
    assert policy.enabled is True


def test_queue_job_and_audit_defaults() -> None:
    job = QueueJob(
        scope_type="platform",
        job_kind=JobKind.RUNTIME_TASK,
        status=JobStatus.PENDING,
        trace_id="trace",
    )
    event = AuditEvent(
        scope_type="platform",
        actor_type=AuditActorType.SYSTEM,
        actor_id="system",
        action="created",
        entity_type="job",
        entity_id="123",
        trace_id="trace",
    )
    assert job.status is JobStatus.PENDING
    assert event.actor_type is AuditActorType.SYSTEM
