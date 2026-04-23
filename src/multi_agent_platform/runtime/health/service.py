from __future__ import annotations

from multi_agent_platform.bootstrap.container import Container
from multi_agent_platform.runtime.health.checks import (
    check_auth_configuration,
    check_configuration,
    check_database,
    check_migrations,
    check_worker_dependencies,
)
from multi_agent_platform.runtime.health.models import (
    DependencyHealthCheck,
    DependencyStatus,
    DependencyStatusReport,
    ReadinessReport,
    ReadinessStatus,
)


class HealthService:
    def __init__(self, container: Container) -> None:
        self.container = container

    async def dependency_checks(self) -> list[DependencyHealthCheck]:
        return [
            await check_configuration(self.container),
            await check_auth_configuration(self.container),
            await check_database(self.container),
            await check_migrations(self.container),
            await check_worker_dependencies(self.container),
        ]

    async def readiness(self) -> ReadinessReport:
        checks = await self.dependency_checks()
        ready = all(
            check.status is DependencyStatus.READY for check in checks if check.required
        )
        return ReadinessReport(
            service=self.container.settings.app_name,
            status=ReadinessStatus.READY if ready else ReadinessStatus.NOT_READY,
            checks=checks,
        )

    async def dependency_status(self) -> DependencyStatusReport:
        checks = await self.dependency_checks()
        if any(
            check.status is DependencyStatus.UNAVAILABLE
            for check in checks
            if check.required
        ):
            overall = "not_ready"
        elif any(check.status is DependencyStatus.DEGRADED for check in checks):
            overall = "degraded"
        else:
            overall = "ready"
        return DependencyStatusReport(
            service=self.container.settings.app_name,
            status=overall,
            dependencies=checks,
        )
