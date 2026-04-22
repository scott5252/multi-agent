"""Database model registration."""

from multi_agent_platform.db.models.artifact import ArtifactRecord
from multi_agent_platform.db.models.audit import AuditActorType, AuditEvent
from multi_agent_platform.db.models.queue import JobKind, JobLease, JobStatus, QueueJob
from multi_agent_platform.db.models.secret_reference import (
    SecretReference,
    SecretReferenceStatus,
)
from multi_agent_platform.db.models.tenant import (
    Tenant,
    TenantLimitPolicy,
    TenantStatus,
)


def import_models() -> None:
    """Import models for metadata registration."""


__all__ = [
    "ArtifactRecord",
    "AuditActorType",
    "AuditEvent",
    "JobKind",
    "JobLease",
    "JobStatus",
    "QueueJob",
    "SecretReference",
    "SecretReferenceStatus",
    "Tenant",
    "TenantLimitPolicy",
    "TenantStatus",
    "import_models",
]
