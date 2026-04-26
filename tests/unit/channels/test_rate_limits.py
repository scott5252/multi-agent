from __future__ import annotations

from uuid import uuid4

import pytest

from multi_agent_platform.channels.errors import ChannelError
from multi_agent_platform.channels.models import ChannelActor, ChannelType
from multi_agent_platform.channels.service import ChannelService
from multi_agent_platform.config.settings import Settings


@pytest.mark.asyncio
async def test_rate_limit_is_scoped_by_tenant_identity_and_action() -> None:
    service = ChannelService(
        settings=Settings(
            _env_file=None,
            app_env="test",
            channel_rate_limit_per_minute=1,
        )
    )
    tenant_id = uuid4()
    actor = ChannelActor(tenant_id, "user-1", ChannelType.WEB_API, "trace-1")
    other_actor = ChannelActor(tenant_id, "user-2", ChannelType.WEB_API, "trace-2")

    await service.start_run(
        actor=actor,
        workflow_id="demo-1",
        inputs={"topic": "first"},
        idempotency_key="idem-rate-a",
    )
    await service.start_run(
        actor=other_actor,
        workflow_id="demo-2",
        inputs={"topic": "second"},
        idempotency_key="idem-rate-b",
    )

    with pytest.raises(ChannelError):
        await service.start_run(
            actor=actor,
            workflow_id="demo-3",
            inputs={"topic": "third"},
            idempotency_key="idem-rate-c",
        )
