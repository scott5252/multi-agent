from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from multi_agent_platform.reliability.models import BreakerState, now_utc


@dataclass(slots=True)
class CircuitBreaker:
    scope_key: str
    state: BreakerState = BreakerState.CLOSED
    failure_count: int = 0
    failure_threshold: int = 5
    cooldown_seconds: int = 60
    cooldown_until: datetime | None = None
    half_open_tokens: int = 0
    reason_code: str = "initial"


def record_success(breaker: CircuitBreaker) -> BreakerState:
    breaker.failure_count = 0
    breaker.reason_code = "success"
    if breaker.state is BreakerState.HALF_OPEN:
        breaker.state = BreakerState.CLOSED
        breaker.half_open_tokens = 0
    return breaker.state


def record_failure(
    breaker: CircuitBreaker, *, now: datetime | None = None
) -> BreakerState:
    current = now or now_utc()
    breaker.failure_count += 1
    breaker.reason_code = "failure_threshold"
    if (
        breaker.state is BreakerState.HALF_OPEN
        or breaker.failure_count >= breaker.failure_threshold
    ):
        breaker.state = BreakerState.OPEN
        breaker.cooldown_until = current + timedelta(seconds=breaker.cooldown_seconds)
        breaker.half_open_tokens = 0
    return breaker.state


def maybe_enter_half_open(
    breaker: CircuitBreaker, *, probe_success: bool, now: datetime | None = None
) -> BreakerState:
    current = now or now_utc()
    if breaker.state is not BreakerState.OPEN:
        return breaker.state
    if breaker.cooldown_until and current < breaker.cooldown_until:
        return BreakerState.OPEN
    if not probe_success:
        return BreakerState.OPEN
    breaker.state = BreakerState.HALF_OPEN
    breaker.half_open_tokens = 1
    breaker.reason_code = "probe_success"
    return breaker.state


def allow_protected_work(breaker: CircuitBreaker) -> bool:
    if breaker.state is BreakerState.CLOSED:
        return True
    if breaker.state is BreakerState.HALF_OPEN and breaker.half_open_tokens > 0:
        breaker.half_open_tokens -= 1
        return True
    return False


def gateway_breaker_scope(
    *,
    provider_connection_id: str,
    model_id: str,
    provider_model_definition_id: str | None = None,
) -> str:
    identity = provider_model_definition_id or model_id
    return f"provider_connection:{provider_connection_id}:model:{identity}"


def gateway_breaker_summary(
    *,
    provider_connection_id: str,
    model_id: str,
    provider_model_definition_id: str | None = None,
    state: BreakerState = BreakerState.CLOSED,
    tenant_id: str | None = None,
    workflow_run_id: str | None = None,
    workflow_run_step_id: str | None = None,
    trace_id: str | None = None,
) -> dict[str, object]:
    breaker = CircuitBreaker(
        scope_key=gateway_breaker_scope(
            provider_connection_id=provider_connection_id,
            model_id=model_id,
            provider_model_definition_id=provider_model_definition_id,
        ),
        state=state,
    )
    return {
        "scope": breaker.scope_key,
        "state": breaker.state.value,
        "allowed": allow_protected_work(breaker),
        "evidence": {
            "tenant_id": tenant_id,
            "workflow_run_id": workflow_run_id,
            "workflow_run_step_id": workflow_run_step_id,
            "trace_id": trace_id,
        },
    }


def reset_breaker(
    breaker: CircuitBreaker, *, actor_id: str, reason: str
) -> CircuitBreaker:
    if not actor_id or not reason:
        raise ValueError("breaker reset requires actor and reason")
    breaker.state = BreakerState.CLOSED
    breaker.failure_count = 0
    breaker.cooldown_until = None
    breaker.half_open_tokens = 0
    breaker.reason_code = "operator_reset"
    return breaker
