from __future__ import annotations

import pytest

from multi_agent_platform.channels.models import (
    ChannelActor,
    ChannelType,
    PromptAction,
    UserVisibleRunState,
)
from multi_agent_platform.channels.service import ChannelService
from multi_agent_platform.config.settings import Settings


@pytest.mark.asyncio
async def test_rejecting_waiting_prompt_preserves_first_valid_decision() -> None:
    service = ChannelService(settings=Settings(_env_file=None, app_env="test"))
    actor = ChannelActor(None, "reviewer-1", ChannelType.WEB_API, "trace-1")
    run = await service.start_run(
        actor=actor,
        workflow_id="approval-result",
        inputs={"topic": "approval", "_channel_state": "waiting"},
        idempotency_key="idem-approval-start",
    )
    status = service.get_status(actor=actor, run_id=run.run_id)
    assert status.waiting_prompt is not None

    rejected = service.decide_prompt(
        actor=actor,
        run_id=run.run_id,
        prompt_id=status.waiting_prompt.prompt_id,
        action=PromptAction.REJECT,
        prompt_version=status.waiting_prompt.prompt_version,
        decision_payload={},
        idempotency_key="idem-approval-reject",
    )
    stale = service.decide_prompt(
        actor=actor,
        run_id=run.run_id,
        prompt_id=status.waiting_prompt.prompt_id,
        action=PromptAction.APPROVE,
        prompt_version=status.waiting_prompt.prompt_version,
        decision_payload={},
        idempotency_key="idem-approval-stale",
    )

    assert rejected.accepted is True
    assert rejected.run_status.state == UserVisibleRunState.FAILED
    assert stale.accepted is False
    assert stale.run_status.state == UserVisibleRunState.FAILED
