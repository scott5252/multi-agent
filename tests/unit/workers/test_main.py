from __future__ import annotations

from types import SimpleNamespace

import multi_agent_platform.workers.main as workers_main


async def test_worker_main_builds_container_and_disposes(monkeypatch) -> None:
    events: list[str] = []

    class FakeContainer:
        async def dispose(self) -> None:
            events.append("dispose")

    fake_container = FakeContainer()

    def fake_build_container(_settings):
        events.append("build_container")
        return fake_container

    def fake_build_worker_bootstrap(container):
        assert container is fake_container
        events.append("build_bootstrap")
        return SimpleNamespace(container=container, worker_id="worker-1")

    async def fake_run_polling_loop(bootstrap, iterations=None):
        assert bootstrap.worker_id == "worker-1"
        assert iterations == 1
        events.append("run_loop")

    monkeypatch.setattr(workers_main, "build_container", fake_build_container)
    monkeypatch.setattr(
        workers_main,
        "build_worker_bootstrap",
        fake_build_worker_bootstrap,
    )
    monkeypatch.setattr(workers_main, "run_polling_loop", fake_run_polling_loop)

    await workers_main.main(iterations=1)

    assert events == ["build_container", "build_bootstrap", "run_loop", "dispose"]
