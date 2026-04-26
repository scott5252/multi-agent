from __future__ import annotations

import pytest

from multi_agent_platform.workers.loops import (
    ChannelDeliveryLeaseManager,
    run_channel_delivery_once,
)


@pytest.mark.asyncio
async def test_channel_delivery_budget_prevents_tenant_starvation() -> None:
    manager = ChannelDeliveryLeaseManager(default_limit=1)
    budget = manager.budget_for(tenant_id="tenant-1", delivery_kind="telegram")

    assert budget.try_claim() is True
    assert (
        await run_channel_delivery_once(
            manager,
            tenant_id="tenant-1",
            delivery_kind="telegram",
        )
        is False
    )
    budget.release()
    assert (
        await run_channel_delivery_once(
            manager,
            tenant_id="tenant-1",
            delivery_kind="telegram",
        )
        is True
    )
