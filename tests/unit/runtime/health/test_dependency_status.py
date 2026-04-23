from __future__ import annotations

from multi_agent_platform.bootstrap.container import build_container
from multi_agent_platform.runtime.health.service import HealthService


async def test_dependency_status_aggregates_required_failures(settings) -> None:
    container = build_container(settings)
    try:
        report = await HealthService(container).dependency_status()
        assert report.status == "not_ready"
        assert {item.name for item in report.dependencies} >= {
            "config",
            "auth",
            "postgres",
            "migrations",
            "worker",
        }
    finally:
        await container.dispose()
