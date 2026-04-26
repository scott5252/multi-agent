from __future__ import annotations

import time

import pytest

from multi_agent_platform.channels.models import ChannelActor, ChannelType
from multi_agent_platform.channels.service import ChannelService
from multi_agent_platform.config.settings import Settings


@pytest.mark.asyncio
async def test_channel_status_lookup_stays_well_under_contract_budget() -> None:
    service = ChannelService(settings=Settings(_env_file=None, app_env="test"))
    actor = ChannelActor(None, "user-1", ChannelType.WEB_API, "trace-1")
    run = await service.start_run(
        actor=actor,
        workflow_id="latency-demo",
        inputs={"topic": "latency"},
        idempotency_key="idem-latency",
    )

    started = time.perf_counter()
    status = service.get_status(actor=actor, run_id=run.run_id)
    elapsed_ms = (time.perf_counter() - started) * 1000

    assert status.run_id == run.run_id
    assert elapsed_ms < 300
