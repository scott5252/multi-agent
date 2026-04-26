from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def sha256_digest(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(slots=True, frozen=True)
class HandoffContract:
    contract_id: str
    contract_version: str
    json_schema: dict[str, object]
    contract_digest: str | None = None

    @property
    def digest(self) -> str:
        return self.contract_digest or sha256_digest(self.json_schema)


@dataclass(slots=True, frozen=True)
class ContractValidationResult:
    valid: bool
    errors: tuple[str, ...] = field(default_factory=tuple)


class PinnedContractValidator:
    def __init__(self, contracts: dict[str, HandoffContract]) -> None:
        self.contracts = contracts

    def validate(
        self,
        *,
        contract_id: str,
        expected_digest: str,
        payload: dict[str, object],
    ) -> ContractValidationResult:
        contract = self.contracts.get(contract_id)
        if contract is None:
            return ContractValidationResult(False, ("contract unavailable",))
        if contract.digest != expected_digest:
            return ContractValidationResult(False, ("contract digest mismatch",))
        errors = tuple(_validate_object_schema(contract.json_schema, payload))
        return ContractValidationResult(valid=not errors, errors=errors)


def _validate_object_schema(
    schema: dict[str, object], payload: dict[str, object]
) -> list[str]:
    errors: list[str] = []
    if schema.get("type") == "object" and not isinstance(payload, dict):
        return ["payload must be an object"]
    required = schema.get("required", [])
    if isinstance(required, list):
        for key in required:
            if isinstance(key, str) and key not in payload:
                errors.append(f"{key} is required")
    properties = schema.get("properties", {})
    if isinstance(properties, dict):
        for key, spec in properties.items():
            if (
                not isinstance(key, str)
                or key not in payload
                or not isinstance(spec, dict)
            ):
                continue
            expected_type = spec.get("type")
            if expected_type == "string" and not isinstance(payload[key], str):
                errors.append(f"{key} must be a string")
            elif expected_type == "integer" and not isinstance(payload[key], int):
                errors.append(f"{key} must be an integer")
            elif expected_type == "object" and not isinstance(payload[key], dict):
                errors.append(f"{key} must be an object")
            elif expected_type == "array" and not isinstance(payload[key], list):
                errors.append(f"{key} must be an array")
            elif expected_type == "boolean" and not isinstance(payload[key], bool):
                errors.append(f"{key} must be a boolean")
    return errors


def contract_validation_audit_summary(
    *,
    contract_id: str,
    contract_version: str,
    result: ContractValidationResult,
) -> dict[str, object]:
    return {
        "contract_name": contract_id,
        "contract_version": contract_version,
        "validation_outcome": "pass" if result.valid else "fail",
        "error_count": len(result.errors),
        "prioritized_error_codes": tuple(
            error.split(" ")[0] for error in result.errors
        ),
    }
