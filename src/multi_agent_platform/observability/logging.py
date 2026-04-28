from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from typing import Any

REDACTED = "***REDACTED***"
SECRET_KEYS = ("secret", "token", "password", "api_key", "authorization")


def redact_mapping(payload: Mapping[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in payload.items():
        if any(marker in key.lower() for marker in SECRET_KEYS):
            redacted[key] = REDACTED
        elif isinstance(value, Mapping):
            redacted[key] = redact_mapping(value)
        else:
            redacted[key] = value
    return redacted


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        if hasattr(record, "extra") and isinstance(record.extra, Mapping):
            payload.update(redact_mapping(record.extra))
        return json.dumps(payload, default=str)


def configure_logging(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("multi_agent_platform")
    logger.handlers.clear()
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(level.upper())
    return logger


def workflow_log_context(
    *,
    action: str,
    scope_type: str,
    trace_id: str,
    workflow_lineage_id: str | None = None,
    workflow_draft_id: str | None = None,
    principal_id: str | None = None,
) -> dict[str, dict[str, str]]:
    payload = {
        "action": action,
        "scope_type": scope_type,
        "trace_id": trace_id,
    }
    if workflow_lineage_id is not None:
        payload["workflow_lineage_id"] = workflow_lineage_id
    if workflow_draft_id is not None:
        payload["workflow_draft_id"] = workflow_draft_id
    if principal_id is not None:
        payload["principal_id"] = principal_id
    return {"extra": payload}


def memory_log_context(
    *,
    action: str,
    trace_id: str,
    tenant_id: str | None = None,
    memory_scope_id: str | None = None,
    memory_version_id: str | None = None,
    content_sha256: str | None = None,
    conflict_type: str | None = None,
    latency_ms: float | None = None,
) -> dict[str, dict[str, str]]:
    payload: dict[str, str] = {"action": action, "trace_id": trace_id}
    if tenant_id is not None:
        payload["tenant_id"] = tenant_id
    if memory_scope_id is not None:
        payload["memory_scope_id"] = memory_scope_id
    if memory_version_id is not None:
        payload["memory_version_id"] = memory_version_id
    if content_sha256 is not None:
        payload["content_sha256"] = content_sha256
    if conflict_type is not None:
        payload["conflict_type"] = conflict_type
    if latency_ms is not None:
        payload["latency_ms"] = str(latency_ms)
    return {"extra": payload}


def channel_log_context(
    *,
    action: str,
    channel: str,
    trace_id: str,
    outcome: str,
    tenant_id: str | None = None,
    run_id: str | None = None,
) -> dict[str, dict[str, str]]:
    payload = {
        "action": action,
        "channel": channel,
        "trace_id": trace_id,
        "outcome": outcome,
    }
    if tenant_id is not None:
        payload["tenant_id"] = tenant_id
    if run_id is not None:
        payload["run_id"] = run_id
    return {"extra": payload}


def model_skill_policy_log_context(
    *,
    action: str,
    decision_category: str,
    outcome: str,
    trace_id: str | None = None,
    tenant_id: str | None = None,
    denial_category: str | None = None,
    evaluated_version_count: int | None = None,
) -> dict[str, dict[str, str]]:
    payload = {
        "action": action,
        "decision_category": decision_category,
        "outcome": outcome,
    }
    if trace_id is not None:
        payload["trace_id"] = trace_id
    if tenant_id is not None:
        payload["tenant_id"] = tenant_id
    if denial_category is not None:
        payload["denial_category"] = denial_category
    if evaluated_version_count is not None:
        payload["evaluated_version_count"] = str(evaluated_version_count)
    return {"extra": payload}


def audit_log_context(
    *,
    action: str,
    tenant_id: str | None = None,
    workflow_run_id: str | None = None,
    trace_id: str | None = None,
    timeline_event_id: str | None = None,
    event_category: str | None = None,
    actor_type: str | None = None,
    policy_outcome: str | None = None,
    status: str | None = None,
    outcome: str | None = None,
    duration_ms: float | None = None,
) -> dict[str, dict[str, str]]:
    payload = {"action": action}
    optional = {
        "tenant_id": tenant_id,
        "workflow_run_id": workflow_run_id,
        "trace_id": trace_id,
        "timeline_event_id": timeline_event_id,
        "event_category": event_category,
        "actor_type": actor_type,
        "policy_outcome": policy_outcome,
        "status": status,
        "outcome": outcome,
        "duration_ms": str(duration_ms) if duration_ms is not None else None,
    }
    payload.update({key: value for key, value in optional.items() if value is not None})
    return {"extra": payload}


def admin_shell_log_context(
    *,
    action: str,
    outcome: str,
    reason: str,
    trace_id: str | None = None,
    tenant_id: str | None = None,
    principal_id: str | None = None,
    request_path: str | None = None,
) -> dict[str, dict[str, str]]:
    payload = {
        "action": action,
        "outcome": outcome,
        "reason": reason,
    }
    optional = {
        "trace_id": trace_id,
        "tenant_id": tenant_id,
        "principal_id": principal_id,
        "request_path": request_path,
    }
    payload.update({key: value for key, value in optional.items() if value is not None})
    return {"extra": redact_mapping(payload)}


def reliability_log_context(
    *,
    action: str,
    reason_code: str,
    tenant_id: str | None = None,
    workflow_run_id: str | None = None,
    trace_id: str | None = None,
    policy_version: int | None = None,
    decision: str | None = None,
    breaker_state: str | None = None,
    retry_status: str | None = None,
    artifact_operation: str | None = None,
) -> dict[str, dict[str, str]]:
    payload = {"action": action, "reason_code": reason_code}
    optional = {
        "tenant_id": tenant_id,
        "workflow_run_id": workflow_run_id,
        "trace_id": trace_id,
        "policy_version": str(policy_version) if policy_version is not None else None,
        "decision": decision,
        "breaker_state": breaker_state,
        "retry_status": retry_status,
        "artifact_operation": artifact_operation,
    }
    payload.update({key: value for key, value in optional.items() if value is not None})
    return {"extra": payload}


def model_provider_log_context(
    *,
    action: str,
    outcome: str,
    provider_type: str | None = None,
    connection_id: str | None = None,
    model_id: str | None = None,
    tenant_id: str | None = None,
    reason: str | None = None,
    latency_ms: int | None = None,
) -> dict[str, dict[str, str]]:
    payload = {"action": action, "outcome": outcome}
    optional = {
        "provider_type": provider_type,
        "connection_id": connection_id,
        "model_id": model_id,
        "tenant_id": tenant_id,
        "reason": reason,
        "latency_ms": str(latency_ms) if latency_ms is not None else None,
    }
    payload.update({key: value for key, value in optional.items() if value is not None})
    return {"extra": redact_mapping(payload)}
