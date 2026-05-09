from __future__ import annotations

import json

import pytest

from multi_agent_platform.runtime.orchestration.role_output_contracts import (
    RoleOutputContractError,
    parse_model_output_content,
    validate_role_output,
)


def test_parse_model_output_content_accepts_json_object() -> None:
    payload = parse_model_output_content(
        json.dumps({"summary": "Safe reviewer summary.", "status": "approved"})
    )

    assert payload["summary"] == "Safe reviewer summary."


def test_parse_model_output_content_rejects_non_json() -> None:
    with pytest.raises(RoleOutputContractError) as exc:
        parse_model_output_content("not-json")

    assert exc.value.code == "model_output_contract_invalid"


def test_validate_role_output_accepts_safe_required_fields() -> None:
    result = validate_role_output(
        {"summary": "Safe reviewer summary.", "status": "approved", "findings": []},
        contract_schema={"required": ["summary", "status"]},
    )

    assert result.safe_summary == "Safe reviewer summary."
    assert result.structured_output["status"] == "approved"
    assert result.payload_digest


def test_validate_role_output_rejects_missing_required_field() -> None:
    with pytest.raises(RoleOutputContractError) as exc:
        validate_role_output({"summary": "Safe reviewer summary."})

    assert exc.value.code == "model_output_contract_invalid"


def test_validate_role_output_rejects_unsafe_field_names_and_text() -> None:
    with pytest.raises(RoleOutputContractError) as key_exc:
        validate_role_output(
            {
                "summary": "Safe reviewer summary.",
                "status": "approved",
                "raw_prompt": "hidden",
            }
        )
    with pytest.raises(RoleOutputContractError) as text_exc:
        validate_role_output(
            {
                "summary": "raw completion copied here",
                "status": "approved",
            }
        )

    assert key_exc.value.code == "model_output_redaction_failed"
    assert text_exc.value.code == "model_output_redaction_failed"


def test_validate_role_output_marks_oversized_allowed_payload_for_artifact() -> None:
    result = validate_role_output(
        {
            "summary": "Safe reviewer summary.",
            "status": "approved",
            "recommendations": ["safe " * 30],
        },
        inline_limit_bytes=80,
    )

    assert result.requires_artifact is True
