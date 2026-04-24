from __future__ import annotations

from multi_agent_platform.bootstrap.container import build_container
from multi_agent_platform.bootstrap.worker import (
    WorkerBootstrap,
    build_worker_bootstrap,
)


async def test_build_worker_bootstrap_assigns_process_scoped_identity(settings) -> None:
    container = build_container(settings)
    try:
        bootstrap = build_worker_bootstrap(container)

        assert isinstance(bootstrap, WorkerBootstrap)
        assert bootstrap.container is container
        assert bootstrap.worker_id.startswith("worker-")
        assert len(bootstrap.worker_id) == len("worker-") + 12
    finally:
        await container.dispose()
