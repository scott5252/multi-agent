from __future__ import annotations

from uuid import uuid4

from multi_agent_platform.runtime.orchestration.contracts import (
    HandoffContract,
    PinnedContractValidator,
)
from multi_agent_platform.runtime.orchestration.handoffs import (
    HandoffEnvelope,
    HandoffStatus,
)


def test_handoff_envelope_validates_and_consumes(
    handoff_contract: HandoffContract,
) -> None:
    envelope = HandoffEnvelope(
        tenant_id=uuid4(),
        workflow_run_id=uuid4(),
        sender_step_id=uuid4(),
        receiver_step_key="receiver",
        contract_id="handoff",
        contract_version="1",
        contract_digest=handoff_contract.digest,
        payload_ref={"message": "ok"},
    )

    envelope.validate(PinnedContractValidator({"handoff": handoff_contract}))
    envelope.consume()

    assert envelope.status is HandoffStatus.CONSUMED
    assert envelope.payload_hash


def test_invalid_handoff_applies_failure_route(
    handoff_contract: HandoffContract,
) -> None:
    envelope = HandoffEnvelope(
        tenant_id=uuid4(),
        workflow_run_id=uuid4(),
        sender_step_id=uuid4(),
        receiver_step_key="receiver",
        contract_id="handoff",
        contract_version="1",
        contract_digest=handoff_contract.digest,
        payload_ref={"message": 123},
    )

    envelope.validate(PinnedContractValidator({"handoff": handoff_contract}))
    envelope.apply_failure_route()

    assert envelope.status is HandoffStatus.FAILED_ROUTE_APPLIED
