from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from multi_agent_platform.reliability.models import CompensationStatus


@dataclass(slots=True)
class CompensationRequest:
    tenant_id: UUID
    workflow_run_id: UUID
    run_step_id: UUID
    side_effect_intent_id: UUID
    hook_ref: str
    compensation_request_id: UUID = field(default_factory=uuid4)
    status: CompensationStatus = CompensationStatus.REQUESTED

    @property
    def uniqueness_key(self) -> tuple[UUID, UUID, str]:
        return (self.tenant_id, self.side_effect_intent_id, self.hook_ref)


def request_compensation(
    *,
    existing: set[tuple[UUID, UUID, str]],
    request: CompensationRequest,
) -> CompensationRequest:
    if request.uniqueness_key in existing:
        raise ValueError("automatic compensation request already exists")
    existing.add(request.uniqueness_key)
    request.status = CompensationStatus.QUEUED
    return request


def transition_compensation(
    request: CompensationRequest, status: CompensationStatus, *, manual: bool = False
) -> CompensationRequest:
    if (
        request.status
        in {
            CompensationStatus.SUCCEEDED,
            CompensationStatus.SKIPPED_BY_POLICY,
        }
        and not manual
    ):
        raise ValueError("terminal compensation cannot transition automatically")
    request.status = status
    return request
