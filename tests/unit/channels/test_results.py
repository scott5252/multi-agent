from __future__ import annotations

import pytest

from multi_agent_platform.channels.models import (
    ChannelActor,
    ChannelType,
    ResultAvailability,
)
from multi_agent_platform.channels.service import ChannelService
from multi_agent_platform.config.settings import Settings


@pytest.mark.asyncio
async def test_result_view_distinguishes_available_and_unavailable() -> None:
    service = ChannelService(settings=Settings(_env_file=None, app_env="test"))
    actor = ChannelActor(None, "user-1", ChannelType.WEB_API, "trace-1")
    active = await service.start_run(
        actor=actor,
        workflow_id="active-result",
        inputs={"topic": "active"},
        idempotency_key="idem-result-active",
    )
    completed = await service.start_run(
        actor=actor,
        workflow_id="completed-result",
        inputs={"topic": "done", "_channel_state": "completed"},
        idempotency_key="idem-result-completed",
    )

    assert (
        service.get_result(actor=actor, run_id=active.run_id).availability
        == ResultAvailability.UNAVAILABLE
    )
    assert (
        service.get_result(actor=actor, run_id=completed.run_id).availability
        == ResultAvailability.AVAILABLE
    )
