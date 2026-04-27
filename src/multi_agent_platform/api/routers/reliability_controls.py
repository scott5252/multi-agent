from __future__ import annotations

from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from multi_agent_platform.api.deps import get_session
from multi_agent_platform.api.schemas.reliability import (
    AdmissionDecision,
    BreakerResetRequest,
    CircuitBreaker,
    CompensationRequest,
    DeadLetterRecord,
    ListResponse,
    LoadTestReport,
    OperationalControlChange,
    PolicyChangeRequest,
    ReliabilityDashboard,
    ReliabilityPolicy,
    RetrySchedule,
)

router = APIRouter(prefix="/admin/reliability", tags=["reliability"])


@router.get("/dashboard", response_model=ReliabilityDashboard)
async def get_dashboard(
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: UUID | None = None,
    scope: str = "global",
) -> ReliabilityDashboard:
    _ = (session, scope)
    return ReliabilityDashboard(tenant_id=tenant_id)


@router.get("/policies", response_model=ListResponse[ReliabilityPolicy])
async def list_policies(
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: UUID | None = None,
    scope_type: str | None = None,
) -> ListResponse[ReliabilityPolicy]:
    _ = (session, tenant_id, scope_type)
    return ListResponse[ReliabilityPolicy]()


@router.post("/policies", response_model=OperationalControlChange, status_code=202)
async def create_policy(
    request: PolicyChangeRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> OperationalControlChange:
    _ = session
    return OperationalControlChange(
        control_change_id=uuid4(),
        tenant_id=request.tenant_id,
        policy_id=uuid4(),
        actor_id="local-principal",
        actor_role="admin",
        scope_type=request.scope_type,
        scope_key=request.scope_key,
        validation_outcome="accepted"
        if not request.unsafe_override
        else "override_accepted",
    )


@router.get("/admission-decisions", response_model=ListResponse[AdmissionDecision])
async def list_admission_decisions(
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: UUID | None = None,
    workflow_run_id: UUID | None = None,
    decision: str | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> ListResponse[AdmissionDecision]:
    _ = (session, tenant_id, workflow_run_id, decision, limit)
    return ListResponse[AdmissionDecision]()


@router.get("/breakers", response_model=ListResponse[CircuitBreaker])
async def list_breakers(
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: UUID | None = None,
    state: str | None = None,
) -> ListResponse[CircuitBreaker]:
    _ = (session, tenant_id, state)
    return ListResponse[CircuitBreaker]()


@router.post(
    "/breakers/{breaker_id}/reset",
    response_model=CircuitBreaker,
    status_code=202,
)
async def reset_breaker(
    breaker_id: UUID,
    request: BreakerResetRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CircuitBreaker:
    _ = (session, request)
    return CircuitBreaker(
        circuit_breaker_id=breaker_id,
        scope_type="dependency",
        scope_key="unknown",
        state=request.target_state,
        reason_code="operator_reset",
    )


@router.get("/retries", response_model=ListResponse[RetrySchedule])
async def list_retries(
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: UUID | None = None,
    status: str | None = None,
    failure_category: str | None = None,
) -> ListResponse[RetrySchedule]:
    _ = (session, tenant_id, status, failure_category)
    return ListResponse[RetrySchedule]()


@router.get("/compensations", response_model=ListResponse[CompensationRequest])
async def list_compensations(
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: UUID | None = None,
    status: str | None = None,
) -> ListResponse[CompensationRequest]:
    _ = (session, tenant_id, status)
    return ListResponse[CompensationRequest]()


@router.get("/dead-letters", response_model=ListResponse[DeadLetterRecord])
async def list_dead_letters(
    session: Annotated[AsyncSession, Depends(get_session)],
    tenant_id: UUID | None = None,
    status: str | None = None,
) -> ListResponse[DeadLetterRecord]:
    _ = (session, tenant_id, status)
    return ListResponse[DeadLetterRecord]()


@router.post("/dead-letters/{dead_letter_id}/actions", status_code=202)
async def act_on_dead_letter(
    dead_letter_id: UUID,
    action: str,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, str]:
    _ = session
    return {
        "dead_letter_id": str(dead_letter_id),
        "action": action,
        "status": "accepted",
    }


@router.get("/load-test-reports", response_model=ListResponse[LoadTestReport])
async def list_load_test_reports(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ListResponse[LoadTestReport]:
    _ = session
    return ListResponse[LoadTestReport]()
