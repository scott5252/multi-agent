from __future__ import annotations

from multi_agent_platform.channels.models import TerminalOutcome, UserVisibleRunState
from multi_agent_platform.runtime.orchestration.models import RunStatus


def map_runtime_state(
    status: RunStatus | str, *, has_waiting_prompt: bool = False
) -> UserVisibleRunState:
    value = status.value if isinstance(status, RunStatus) else status
    if has_waiting_prompt:
        return UserVisibleRunState.WAITING_FOR_INPUT
    if value in {RunStatus.PENDING.value, RunStatus.RUNNABLE.value}:
        return UserVisibleRunState.QUEUED
    if value in {
        RunStatus.RUNNING.value,
        RunStatus.WAITING_CHILD.value,
        RunStatus.RECOVERABLE_FAILED.value,
        RunStatus.CANCELLING.value,
        RunStatus.PAUSED.value,
    }:
        return UserVisibleRunState.RUNNING
    if value == RunStatus.SUCCEEDED.value:
        return UserVisibleRunState.COMPLETED
    if value == RunStatus.FAILED.value:
        return UserVisibleRunState.FAILED
    if value == RunStatus.CANCELLED.value:
        return UserVisibleRunState.CANCELED
    return UserVisibleRunState.RUNNING


def terminal_outcome_for_state(state: UserVisibleRunState) -> TerminalOutcome:
    if state is UserVisibleRunState.COMPLETED:
        return TerminalOutcome.COMPLETED
    if state is UserVisibleRunState.FAILED:
        return TerminalOutcome.FAILED
    if state is UserVisibleRunState.CANCELED:
        return TerminalOutcome.CANCELED
    return TerminalOutcome.NONE


def permitted_actions_for_state(state: UserVisibleRunState) -> tuple[str, ...]:
    base = ["status", "timeline", "result", "subscribe"]
    if state in {UserVisibleRunState.QUEUED, UserVisibleRunState.RUNNING}:
        base.append("cancel")
    if state is UserVisibleRunState.WAITING_FOR_INPUT:
        base.extend(["approve", "reject", "resume", "cancel"])
    if state is UserVisibleRunState.COMPLETED:
        base.append("artifacts")
    return tuple(base)
