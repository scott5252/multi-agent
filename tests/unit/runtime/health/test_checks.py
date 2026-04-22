from __future__ import annotations

from multi_agent_platform.bootstrap.container import build_container
from multi_agent_platform.runtime.health.checks import (
    check_configuration,
    check_migrations,
)


async def test_health_checks_report_ready_when_bootstrapped(settings) -> None:
    container = build_container(settings)
    try:
        config_check = await check_configuration(container)
        assert config_check.status == "ready"
    finally:
        await container.dispose()


async def test_migration_check_detects_missing_table(settings) -> None:
    container = build_container(settings)
    try:
        check = await check_migrations(container)
        assert check.status == "unavailable"
    finally:
        await container.dispose()
