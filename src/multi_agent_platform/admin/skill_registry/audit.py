from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from multi_agent_platform.db.base import utcnow

SENSITIVE_KEY_FRAGMENTS = (
    "secret",
    "token",
    "credential_value",
    "raw_credential",
    "password",
    "api_key",
    "apikey",
    "raw",
    "payload",
)


@dataclass(frozen=True, slots=True)
class SkillAuditEvent:
    audit_record_id: UUID
    event_type: str
    actor_principal_id: str
    outcome: str
    safe_summary: dict[str, Any]
    tenant_id: str | None = None
    package_slug: str | None = None
    package_version: str | None = None
    installation_id: str | None = None
    trace_id: str | None = None
    created_at: datetime = field(default_factory=utcnow)


def redact_for_audit(value: Any) -> Any:
    if isinstance(value, Mapping):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            lowered = str(key).lower()
            if any(fragment in lowered for fragment in SENSITIVE_KEY_FRAGMENTS):
                redacted[str(key)] = "[REDACTED]"
            else:
                redacted[str(key)] = redact_for_audit(item)
        return redacted
    if isinstance(value, list | tuple):
        return [redact_for_audit(item) for item in value]
    if isinstance(value, str) and _looks_sensitive(value):
        return "[REDACTED]"
    return value


def build_lifecycle_audit_event(
    *,
    event_type: str,
    actor_principal_id: str,
    outcome: str,
    summary: Mapping[str, Any],
    tenant_id: str | None = None,
    package_slug: str | None = None,
    package_version: str | None = None,
    installation_id: str | None = None,
    trace_id: str | None = None,
) -> SkillAuditEvent:
    return SkillAuditEvent(
        audit_record_id=uuid4(),
        event_type=event_type,
        actor_principal_id=actor_principal_id,
        outcome=outcome,
        safe_summary=redact_for_audit(dict(summary)),
        tenant_id=tenant_id,
        package_slug=package_slug,
        package_version=package_version,
        installation_id=installation_id,
        trace_id=trace_id,
    )


def safe_export(events: list[SkillAuditEvent]) -> list[dict[str, Any]]:
    return [
        {
            "audit_record_id": str(event.audit_record_id),
            "event_type": event.event_type,
            "actor_principal_id": event.actor_principal_id,
            "outcome": event.outcome,
            "tenant_id": event.tenant_id,
            "package_slug": event.package_slug,
            "package_version": event.package_version,
            "installation_id": event.installation_id,
            "trace_id": event.trace_id,
            "safe_summary": event.safe_summary,
            "created_at": event.created_at.isoformat(),
        }
        for event in events
    ]


def _looks_sensitive(value: str) -> bool:
    lowered = value.lower()
    return (
        "bearer " in lowered
        or lowered.startswith("sk-")
        or any(fragment in lowered for fragment in ("password=", "token="))
    )
