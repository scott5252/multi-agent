from __future__ import annotations

from multi_agent_platform.runtime.orchestration.contracts import (
    HandoffContract,
    PinnedContractValidator,
)


def test_contract_validation_accepts_payload(handoff_contract: HandoffContract) -> None:
    validator = PinnedContractValidator({"handoff": handoff_contract})

    result = validator.validate(
        contract_id="handoff",
        expected_digest=handoff_contract.digest,
        payload={"message": "ok"},
    )

    assert result.valid
    assert result.errors == ()


def test_contract_validation_reports_digest_mismatch(
    handoff_contract: HandoffContract,
) -> None:
    validator = PinnedContractValidator({"handoff": handoff_contract})

    result = validator.validate(
        contract_id="handoff",
        expected_digest="wrong",
        payload={"message": "ok"},
    )

    assert not result.valid
    assert result.errors == ("contract digest mismatch",)


def test_contract_validation_reports_schema_errors(
    handoff_contract: HandoffContract,
) -> None:
    validator = PinnedContractValidator({"handoff": handoff_contract})

    result = validator.validate(
        contract_id="handoff",
        expected_digest=handoff_contract.digest,
        payload={"message": 123},
    )

    assert not result.valid
    assert result.errors == ("message must be a string",)


def test_contract_validation_reports_missing_contract_and_type_errors() -> None:
    validator = PinnedContractValidator({})

    unavailable = validator.validate(
        contract_id="missing",
        expected_digest="digest",
        payload={},
    )

    assert unavailable.errors == ("contract unavailable",)

    contract = HandoffContract(
        contract_id="typed",
        contract_version="1",
        json_schema={
            "type": "object",
            "required": ["name"],
            "properties": {
                "name": {"type": "string"},
                "count": {"type": "integer"},
                "meta": {"type": "object"},
                "items": {"type": "array"},
                "ok": {"type": "boolean"},
            },
        },
    )
    typed = PinnedContractValidator({"typed": contract}).validate(
        contract_id="typed",
        expected_digest=contract.digest,
        payload={"count": "1", "meta": [], "items": {}, "ok": "yes"},
    )

    assert typed.errors == (
        "name is required",
        "count must be an integer",
        "meta must be an object",
        "items must be an array",
        "ok must be a boolean",
    )
