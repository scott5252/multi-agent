from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from uuid import UUID

from multi_agent_platform.db.models.runtime_orchestration import (
    RuntimeInteractionEvidenceRecord,
    RuntimeInteractionKind,
    RuntimeInteractionStatus,
)
from multi_agent_platform.db.repositories.runtime_orchestration import (
    RuntimeOrchestrationRepository,
)
from multi_agent_platform.runtime.orchestration.contracts import sha256_digest
from multi_agent_platform.runtime.orchestration.graph_redaction import (
    contains_sensitive_key,
    redact_graph_value,
)

MAX_SAFE_SUMMARY_LENGTH = 280
MAX_ARTIFACT_REFS = 12
SENSITIVE_SUMMARY_MARKERS = (
    "authorization:",
    "bearer ",
    "completion:",
    "credential:",
    "memory:",
    "password:",
    "provider response:",
    "raw prompt:",
    "raw tool output:",
    "secret:",
    "stack trace:",
    "traceback",
)


def interaction_idempotency_key(
    *,
    workflow_run_id: UUID,
    source_node_key: str,
    target_node_key: str | None,
    interaction_kind: RuntimeInteractionKind,
    stable_ref: object,
) -> str:
    digest = sha256_digest(
        {
            "workflow_run_id": str(workflow_run_id),
            "source_node_key": source_node_key,
            "target_node_key": target_node_key,
            "interaction_kind": interaction_kind.value,
            "stable_ref": stable_ref,
        }
    )
    return f"interaction:{digest}"


async def record_runtime_interaction(
    repository: RuntimeOrchestrationRepository,
    *,
    tenant_id: UUID | None,
    workflow_run_id: UUID,
    source_node_key: str,
    target_node_key: str | None,
    interaction_kind: RuntimeInteractionKind,
    status: RuntimeInteractionStatus,
    safe_summary: str,
    idempotency_key: str,
    metadata: Mapping[str, object] | None = None,
    artifact_refs: Sequence[object] | None = None,
    source_run_step_id: UUID | None = None,
    target_run_step_id: UUID | None = None,
    timeline_event_id: UUID | None = None,
    occurred_at: datetime | None = None,
) -> RuntimeInteractionEvidenceRecord:
    provenance, classification = safe_interaction_provenance(metadata or {})
    return await repository.record_interaction_evidence(
        tenant_id=tenant_id,
        workflow_run_id=workflow_run_id,
        source_node_key=safe_node_key(source_node_key),
        target_node_key=safe_node_key(target_node_key) if target_node_key else None,
        source_run_step_id=source_run_step_id,
        target_run_step_id=target_run_step_id,
        timeline_event_id=timeline_event_id,
        interaction_kind=interaction_kind,
        status=status,
        safe_summary=safe_interaction_summary(safe_summary),
        classification=classification,
        payload_digest=sha256_digest(metadata or {}),
        artifact_refs=safe_artifact_refs(artifact_refs or ()),
        provenance=provenance,
        idempotency_key=idempotency_key,
        occurred_at=occurred_at,
    )


def safe_interaction_summary(value: str) -> str:
    normalized = " ".join(str(value or "Interaction evidence recorded.").split())
    if _contains_sensitive_marker(normalized):
        return "Interaction evidence recorded with sensitive details redacted."
    if len(normalized) > MAX_SAFE_SUMMARY_LENGTH:
        return normalized[: MAX_SAFE_SUMMARY_LENGTH - 1].rstrip() + "..."
    return normalized


def safe_interaction_provenance(
    metadata: Mapping[str, object],
) -> tuple[dict[str, object], str]:
    redacted = redact_graph_value(dict(metadata))
    classification = (
        "redacted-summary" if contains_sensitive_key(metadata) else "safe-summary"
    )
    if not isinstance(redacted, dict):
        return {"metadata": redacted}, classification
    return redacted, classification


def safe_artifact_refs(values: Sequence[object]) -> list[object]:
    refs: list[object] = []
    for value in values[:MAX_ARTIFACT_REFS]:
        if isinstance(value, Mapping):
            refs.append(redact_graph_value(value))
        else:
            refs.append(str(value))
    return refs


def safe_node_key(value: str) -> str:
    normalized = "".join(
        character for character in str(value or "unknown") if character.isprintable()
    )
    return normalized[:128] or "unknown"


def _contains_sensitive_marker(value: str) -> bool:
    lower = value.lower()
    return any(marker in lower for marker in SENSITIVE_SUMMARY_MARKERS)
