from __future__ import annotations

from multi_agent_platform.bootstrap.container import build_container
from multi_agent_platform.runtime.health.service import HealthService


async def test_health_service_is_not_ready_without_migrations(settings) -> None:
    container = build_container(settings)
    try:
        report = await HealthService(container).readiness()
        assert report.status == "not_ready"
    finally:
        await container.dispose()
