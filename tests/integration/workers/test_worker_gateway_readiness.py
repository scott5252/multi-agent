from __future__ import annotations

from dataclasses import replace

from multi_agent_platform.bootstrap.container import build_container
from multi_agent_platform.bootstrap.worker import build_worker_bootstrap
from multi_agent_platform.workers.loops import should_accept_work


async def test_worker_rejects_model_backed_work_when_gateway_not_ready(
    settings,
) -> None:
    container = build_container(settings)
    try:
        broken = replace(container, model_gateway_factory=None)
        bootstrap = build_worker_bootstrap(broken)

        assert should_accept_work(bootstrap, requires_model_gateway=True) is False
        assert should_accept_work(bootstrap, requires_model_gateway=False) is True
    finally:
        await container.dispose()
