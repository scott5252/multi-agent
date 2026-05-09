from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from multi_agent_platform.runtime.orchestration.graph_redaction import (
    contains_sensitive_key,
    graph_payload_digest,
    redact_graph_value,
)

MAX_INLINE_ROLE_OUTPUT_BYTES = 4096
UNSAFE_TEXT_MARKERS = (
    "sk-",
    "authorization:",
    "bearer ",
    "begin private key",
    "traceback",
    "raw prompt",
    "raw completion",
    "memory contents",
    "provider payload",
    "tool payload",
    "/users/",
)


@dataclass(slots=True, frozen=True)
class RoleOutputValidation:
    structured_output: dict[str, object]
    safe_summary: str
    payload_digest: str
    inline_size_bytes: int
    requires_artifact: bool = False


class RoleOutputContractError(ValueError):
    def __init__(self, code: str, safe_summary: str) -> None:
        super().__init__(safe_summary)
        self.code = code
        self.safe_summary = safe_summary


def parse_model_output_content(content: str | None) -> dict[str, object]:
    if content is None or not content.strip():
        raise RoleOutputContractError(
            "model_output_contract_invalid",
            "Model-backed role output was empty.",
        )
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise RoleOutputContractError(
            "model_output_contract_invalid",
            "Model-backed role output was not valid JSON.",
        ) from exc
    if not isinstance(payload, Mapping):
        raise RoleOutputContractError(
            "model_output_contract_invalid",
            "Model-backed role output must be a JSON object.",
        )
    return dict(payload)


def validate_role_output(
    payload: Mapping[str, object],
    *,
    contract_schema: Mapping[str, object] | None = None,
    inline_limit_bytes: int = MAX_INLINE_ROLE_OUTPUT_BYTES,
) -> RoleOutputValidation:
    if contains_sensitive_key(payload):
        raise RoleOutputContractError(
            "model_output_redaction_failed",
            "Model-backed role output contained unsafe field names.",
        )
    required_fields = _required_fields(contract_schema)
    missing = [field for field in required_fields if field not in payload]
    if missing:
        raise RoleOutputContractError(
            "model_output_contract_invalid",
            f"Model-backed role output omitted required field {missing[0]}.",
        )
    safe_value = redact_graph_value(dict(payload))
    if not isinstance(safe_value, dict):
        raise RoleOutputContractError(
            "model_output_contract_invalid",
            "Model-backed role output could not be represented safely.",
        )
    _assert_no_unsafe_text(safe_value)
    summary = _safe_summary(safe_value)
    encoded = json.dumps(safe_value, sort_keys=True, default=str).encode("utf-8")
    return RoleOutputValidation(
        structured_output=safe_value,
        safe_summary=summary,
        payload_digest=graph_payload_digest(safe_value),
        inline_size_bytes=len(encoded),
        requires_artifact=len(encoded) > inline_limit_bytes,
    )


def _required_fields(contract_schema: Mapping[str, object] | None) -> tuple[str, ...]:
    if contract_schema:
        required = contract_schema.get("required")
        if isinstance(required, Sequence) and not isinstance(
            required, (str, bytes, bytearray)
        ):
            safe_required = tuple(str(item) for item in required if str(item).strip())
            if safe_required:
                return safe_required
    return ("summary", "status")


def _safe_summary(payload: Mapping[str, object]) -> str:
    summary = payload.get("summary")
    if isinstance(summary, str) and summary.strip():
        return _normalize_safe_text(summary, max_length=240)
    return "Model-backed role output validated."


def _assert_no_unsafe_text(value: object) -> None:
    if isinstance(value, str):
        _normalize_safe_text(value)
        return
    if isinstance(value, Mapping):
        for item in value.values():
            _assert_no_unsafe_text(item)
        return
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        for item in value:
            _assert_no_unsafe_text(item)


def _normalize_safe_text(value: str, *, max_length: int = 1000) -> str:
    normalized = " ".join(value.strip().split())
    if not normalized:
        raise RoleOutputContractError(
            "model_output_contract_invalid",
            "Model-backed role output included empty required text.",
        )
    lowered = normalized.lower()
    if any(marker in lowered for marker in UNSAFE_TEXT_MARKERS):
        raise RoleOutputContractError(
            "model_output_redaction_failed",
            "Model-backed role output contained unsafe text.",
        )
    return normalized[:max_length]


def json_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, default=str).encode("utf-8")
