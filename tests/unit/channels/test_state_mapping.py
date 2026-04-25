from __future__ import annotations

from multi_agent_platform.channels.models import UserVisibleRunState
from multi_agent_platform.channels.state_mapping import (
    map_runtime_state,
    permitted_actions_for_state,
)
from multi_agent_platform.runtime.orchestration.models import RunStatus


def test_runtime_states_map_to_six_user_visible_states() -> None:
    assert map_runtime_state(RunStatus.PENDING) == UserVisibleRunState.QUEUED
    assert map_runtime_state(RunStatus.RUNNABLE) == UserVisibleRunState.QUEUED
    assert map_runtime_state(RunStatus.RUNNING) == UserVisibleRunState.RUNNING
    assert map_runtime_state(RunStatus.PAUSED) == UserVisibleRunState.RUNNING
    assert map_runtime_state(RunStatus.SUCCEEDED) == UserVisibleRunState.COMPLETED
    assert map_runtime_state(RunStatus.FAILED) == UserVisibleRunState.FAILED
    assert map_runtime_state(RunStatus.CANCELLED) == UserVisibleRunState.CANCELED
    assert (
        map_runtime_state(RunStatus.PAUSED, has_waiting_prompt=True)
        == UserVisibleRunState.WAITING_FOR_INPUT
    )


def test_permitted_actions_follow_visible_state() -> None:
    assert "cancel" in permitted_actions_for_state(UserVisibleRunState.RUNNING)
    assert "approve" in permitted_actions_for_state(
        UserVisibleRunState.WAITING_FOR_INPUT
    )
    assert "artifacts" in permitted_actions_for_state(UserVisibleRunState.COMPLETED)
