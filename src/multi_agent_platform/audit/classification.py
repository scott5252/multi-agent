from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from multi_agent_platform.audit.models import (
    RedactionAction,
    SensitivityLabel,
)
from multi_agent_platform.observability.logging import REDACTED

SECRET_MARKERS = ("secret", "token", "password", "credential", "api_key")
PROMPT_MARKERS = ("prompt", "message", "completion")
MEMORY_MARKERS = ("memory", "content", "embedding")
PROMPT_RUNTIME_SAFE_FIELDS = {
    "prompt_lineage_id",
    "prompt_version_id",
    "agent_profile_version_id",
    "agent_runtime_profile_id",
    "prompt_library_version_id",
    "prompt_library_digest",
    "validation_status",
    "finding_codes",
    "redaction_categories",
    "gateway_operation_id",
    "operation_identity",
    "provider_connection_id",
    "provider_model_definition_id",
    "model_id",
    "retry_category",
    "breaker_scope",
    "usage_available",
    "normalized_error_category",
    "provider_probe_operation_id",
    "catalog_sync_operation_id",
}
SAFE_FIELD_ALLOWLIST = {
    "id",
    "tenant_id",
    "workflow_run_id",
    "run_step_id",
    "trace_id",
    "correlation_id",
    "status",
    "outcome",
    "category",
    "count",
    "digest",
    "duration_ms",
    "policy_outcome",
    "reason_code",
    "safe_reason",
    "safe_summary",
    "version",
}


@dataclass(frozen=True, slots=True)
class RedactionDecision:
    field_name: str
    sensitivity_label: SensitivityLabel
    redaction_action: RedactionAction
    decision_reason: str


def classify_field(field_name: str) -> SensitivityLabel:
    normalized = field_name.lower()
    if any(marker in normalized for marker in SECRET_MARKERS):
        return SensitivityLabel.SECRET
    if normalized in PROMPT_RUNTIME_SAFE_FIELDS:
        return SensitivityLabel.SAFE_METADATA
    if "rendered_preview" in normalized or "template_content" in normalized:
        return SensitivityLabel.PROMPT_CONTENT
    if any(marker in normalized for marker in PROMPT_MARKERS):
        return SensitivityLabel.PROMPT_CONTENT
    if any(marker in normalized for marker in MEMORY_MARKERS):
        return SensitivityLabel.MEMORY_CONTENT
    if normalized in SAFE_FIELD_ALLOWLIST or normalized.endswith("_id"):
        return SensitivityLabel.PUBLIC_IDENTIFIER
    if normalized.startswith("safe_") or normalized.endswith("_ref"):
        return SensitivityLabel.SAFE_METADATA
    return SensitivityLabel.UNKNOWN_DYNAMIC


def decision_for_field(
    field_name: str, *, viewer_role: str = "operator"
) -> RedactionDecision:
    label = classify_field(field_name)
    if label in {SensitivityLabel.PUBLIC_IDENTIFIER, SensitivityLabel.SAFE_METADATA}:
        return RedactionDecision(
            field_name=field_name,
            sensitivity_label=label,
            redaction_action=RedactionAction.ALLOW,
            decision_reason="safe metadata field",
        )
    action = (
        RedactionAction.SUMMARIZE
        if viewer_role in {"admin", "auditor"}
        else RedactionAction.MASK
    )
    return RedactionDecision(
        field_name=field_name,
        sensitivity_label=label,
        redaction_action=action,
        decision_reason="sensitive or unknown dynamic field",
    )


def redact_value(
    field_name: str, value: object, *, viewer_role: str = "operator"
) -> object:
    decision = decision_for_field(field_name, viewer_role=viewer_role)
    if decision.redaction_action is RedactionAction.ALLOW:
        if isinstance(value, Mapping):
            return redact_payload(value, viewer_role=viewer_role)
        if isinstance(value, list):
            return [
                redact_value(field_name, item, viewer_role=viewer_role)
                for item in value
            ]
        return value
    if decision.redaction_action is RedactionAction.SUMMARIZE:
        return summarize_value(value)
    if decision.redaction_action is RedactionAction.DROP:
        return None
    return REDACTED


def summarize_value(value: object) -> dict[str, object]:
    if isinstance(value, Mapping):
        return {"redacted": True, "field_count": len(value)}
    if isinstance(value, list):
        return {"redacted": True, "item_count": len(value)}
    if isinstance(value, str):
        return {"redacted": True, "length": len(value)}
    return {"redacted": True, "type": type(value).__name__}


def redact_payload(
    payload: Mapping[str, Any], *, viewer_role: str = "operator"
) -> dict[str, object]:
    return {
        key: redact_value(key, value, viewer_role=viewer_role)
        for key, value in payload.items()
    }


def redaction_decisions(
    payload: Mapping[str, Any], *, viewer_role: str = "operator"
) -> dict[str, str]:
    return {
        key: decision_for_field(key, viewer_role=viewer_role).redaction_action.value
        for key in payload
    }


def build_safe_summary(
    payload: Mapping[str, Any], *, max_items: int = 12
) -> dict[str, object]:
    safe: dict[str, object] = {}
    for key, value in list(payload.items())[:max_items]:
        decision = decision_for_field(key, viewer_role="auditor")
        if decision.redaction_action is RedactionAction.ALLOW:
            safe[key] = (
                value if not isinstance(value, Mapping) else {"field_count": len(value)}
            )
        else:
            safe[key] = summarize_value(value)
    if len(payload) > max_items:
        safe["truncated_field_count"] = len(payload) - max_items
    return safe


def assert_no_raw_sensitive_values(payload: Mapping[str, Any]) -> None:
    for key, value in payload.items():
        if classify_field(key) in {
            SensitivityLabel.SECRET,
            SensitivityLabel.CREDENTIAL,
            SensitivityLabel.PROMPT_CONTENT,
            SensitivityLabel.MEMORY_CONTENT,
            SensitivityLabel.RAW_PAYLOAD,
        }:
            raise ValueError(f"unsafe audit field: {key}")
        if isinstance(value, Mapping):
            assert_no_raw_sensitive_values(value)
