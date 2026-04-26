from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from multi_agent_platform.runtime.orchestration.contracts import (
    PinnedContractValidator,
    sha256_digest,
)
from multi_agent_platform.runtime.orchestration.models import now_utc


class HandoffStatus(StrEnum):
    CREATED = "created"
    VALIDATING = "validating"
    VALID = "valid"
    INVALID = "invalid"
    CONSUMED = "consumed"
    FAILED_ROUTE_APPLIED = "failed_route_applied"


@dataclass(slots=True)
class HandoffEnvelope:
    tenant_id: UUID | None
    workflow_run_id: UUID
    sender_step_id: UUID
    receiver_step_key: str
    contract_id: str
    contract_version: str
    contract_digest: str
    payload_ref: dict[str, object]
    handoff_envelope_id: UUID = field(default_factory=uuid4)
    status: HandoffStatus = HandoffStatus.CREATED
    payload_hash: str = ""
    validation_errors: tuple[str, ...] = field(default_factory=tuple)
    created_at: datetime = field(default_factory=now_utc)
    validated_at: datetime | None = None
    consumed_at: datetime | None = None

    def validate(self, validator: PinnedContractValidator) -> None:
        self.status = HandoffStatus.VALIDATING
        result = validator.validate(
            contract_id=self.contract_id,
            expected_digest=self.contract_digest,
            payload=self.payload_ref,
        )
        self.payload_hash = sha256_digest(self.payload_ref)
        self.validation_errors = result.errors
        self.validated_at = now_utc()
        self.status = HandoffStatus.VALID if result.valid else HandoffStatus.INVALID

    def consume(self) -> None:
        if self.status is not HandoffStatus.VALID:
            raise ValueError("only valid handoff envelopes can be consumed")
        self.status = HandoffStatus.CONSUMED
        self.consumed_at = now_utc()

    def apply_failure_route(self) -> None:
        if self.status is not HandoffStatus.INVALID:
            raise ValueError("failure routes apply to invalid envelopes")
        self.status = HandoffStatus.FAILED_ROUTE_APPLIED


def handoff_audit_metadata(envelope: HandoffEnvelope) -> dict[str, object]:
    return {
        "source_agent_key": str(envelope.sender_step_id),
        "destination_agent_key": envelope.receiver_step_key,
        "handoff_contract_ref": f"{envelope.contract_id}:{envelope.contract_version}",
        "handoff_outcome": envelope.status.value,
        "payload_digest": envelope.payload_hash,
        "validation_error_count": len(envelope.validation_errors),
    }
