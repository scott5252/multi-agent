from __future__ import annotations

import asyncio

from multi_agent_platform.bootstrap.container import build_container
from multi_agent_platform.bootstrap.worker import build_worker_bootstrap
from multi_agent_platform.config.settings import Settings
from multi_agent_platform.workers.loops import run_polling_loop


async def main(iterations: int | None = None) -> None:
    container = build_container(Settings())
    bootstrap = build_worker_bootstrap(container)
    try:
        await run_polling_loop(bootstrap, iterations=iterations)
    finally:
        await container.dispose()


if __name__ == "__main__":
    asyncio.run(main())
