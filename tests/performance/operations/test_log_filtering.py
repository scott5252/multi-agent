from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from multi_agent_platform.bootstrap.container import build_container
from multi_agent_platform.db.models.audit_debugging import AuditTimelineEventRecord
from multi_agent_platform.operations.models import (
    OperationsAccessScope,
    OperationsLogFilters,
    OperationsRole,
)
from multi_agent_platform.operations.service import OperationsConsoleService


@pytest.mark.asyncio
async def test_operations_log_time_range_query_is_bounded(session, settings) -> None:
    tenant_id = settings.local_principal_catalog_json["tenant-admin-acme"].tenant_id
    run_id = uuid4()
    base = datetime(2026, 5, 3, tzinfo=UTC)
    session.add_all(
        [
            AuditTimelineEventRecord(
                tenant_id=tenant_id,
                workflow_run_id=run_id,
                sequence=index + 1,
                event_category="runtime",
                run_status_after="running",
                origin_type="system",
                trace_id=f"trace-{index % 10}",
                source_event_id=f"source-{index}",
                criticality="diagnostic",
                safe_summary=f"Safe event {index}",
                safe_details={"dependency": "queue"},
                occurred_at=base + timedelta(seconds=index),
            )
            for index in range(10_000)
        ]
    )
    await session.flush()
    container = build_container(settings)
    try:
        service = OperationsConsoleService(session=session, container=container)
        access_scope = OperationsAccessScope(
            principal_id="platform-admin",
            role=OperationsRole.PLATFORM_ADMIN,
        )
        filters = OperationsLogFilters(
            start=base + timedelta(minutes=10),
            end=base + timedelta(minutes=20),
            component="runtime",
            dependency="queue",
            limit=100,
        )

        rows = await service.query_logs(access_scope=access_scope, filters=filters)

        assert 1 <= len(rows) <= 100
        assert all(filters.start <= row.occurred_at < filters.end for row in rows)
    finally:
        await container.dispose()
