from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from multi_agent_platform.bootstrap.container import Container


@dataclass(slots=True)
class WorkerBootstrap:
    container: Container
    worker_id: str


def build_worker_bootstrap(container: Container) -> WorkerBootstrap:
    return WorkerBootstrap(container=container, worker_id=f"worker-{uuid4().hex[:12]}")
