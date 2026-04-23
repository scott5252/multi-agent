"""Database model registration."""

from multi_agent_platform.db.models.access_control import (
    AccessDecision,
    AccessDecisionRecord,
    AccessReasonCode,
    AuthProviderType,
    GrantSource,
    PrincipalIdentity,
    PrincipalIdentityStatus,
    RoleCode,
    RoleGrant,
    RoleGrantStatus,
    RoleScopeType,
    SupportOverrideRequest,
    SupportOverrideStatus,
)
from multi_agent_platform.db.models.artifact import ArtifactRecord
from multi_agent_platform.db.models.audit import AuditActorType, AuditEvent
from multi_agent_platform.db.models.delegated_credential import (
    DelegatedCredentialLink,
    DelegatedCredentialStatus,
)
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
    _ = (
        ArtifactRecord,
        AccessDecision,
        AccessDecisionRecord,
        AccessReasonCode,
        AuditActorType,
        AuditEvent,
        AuthProviderType,
        DelegatedCredentialLink,
        DelegatedCredentialStatus,
        GrantSource,
        JobKind,
        JobLease,
        JobStatus,
        PrincipalIdentity,
        PrincipalIdentityStatus,
        QueueJob,
        RoleCode,
        RoleGrant,
        RoleGrantStatus,
        RoleScopeType,
        SecretReference,
        SecretReferenceStatus,
        SupportOverrideRequest,
        SupportOverrideStatus,
        Tenant,
        TenantLimitPolicy,
        TenantStatus,
    )
    return None


__all__ = [
    "ArtifactRecord",
    "AccessDecision",
    "AccessDecisionRecord",
    "AccessReasonCode",
    "AuditActorType",
    "AuditEvent",
    "AuthProviderType",
    "DelegatedCredentialLink",
    "DelegatedCredentialStatus",
    "GrantSource",
    "JobKind",
    "JobLease",
    "JobStatus",
    "PrincipalIdentity",
    "PrincipalIdentityStatus",
    "QueueJob",
    "RoleCode",
    "RoleGrant",
    "RoleGrantStatus",
    "RoleScopeType",
    "SecretReference",
    "SecretReferenceStatus",
    "SupportOverrideRequest",
    "SupportOverrideStatus",
    "Tenant",
    "TenantLimitPolicy",
    "TenantStatus",
    "import_models",
]
