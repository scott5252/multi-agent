from __future__ import annotations

import time
from uuid import uuid4

import pytest

from multi_agent_platform.runtime.orchestration.contracts import (
    HandoffContract,
    PinnedContractValidator,
)


@pytest.mark.performance
def test_handoff_validation_under_latency_target() -> None:
    contract = HandoffContract(
        contract_id="handoff",
        contract_version="1",
        json_schema={
            "type": "object",
            "required": ["message"],
            "properties": {"message": {"type": "string"}},
        },
    )
    validator = PinnedContractValidator({"handoff": contract})
    start = time.perf_counter()

    result = validator.validate(
        contract_id="handoff",
        expected_digest=contract.digest,
        payload={"message": str(uuid4())},
    )

    assert result.valid
    assert time.perf_counter() - start < 0.1
