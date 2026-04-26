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
