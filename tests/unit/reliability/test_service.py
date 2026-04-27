from __future__ import annotations

from uuid import UUID

import pytest

from multi_agent_platform.reliability.models import CapacitySnapshot
from multi_agent_platform.reliability.service import ReliabilityService

TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")


class FakeRepository:
    def __init__(self) -> None:
        self.decisions: list[object] = []

    async def latest_capacity_snapshot(self, *, tenant_id: UUID | None) -> None:
        assert tenant_id == TENANT_ID
        return None

    async def insert_admission_decision(self, decision: object) -> object:
        self.decisions.append(decision)
        return decision


@pytest.mark.asyncio
async def test_reliability_service_dashboard_and_admission() -> None:
    service = ReliabilityService(session=object())  # type: ignore[arg-type]
    fake = FakeRepository()
    service.repository = fake  # type: ignore[assignment]
    dashboard = await service.dashboard(tenant_id=TENANT_ID)
    assert dashboard["status"] == "available"
    decision = await service.admit(
        tenant_id=TENANT_ID,
        snapshot=CapacitySnapshot(db_pool_available=2),
        submitted_count=0,
        active_count=0,
        trace_id="trace-1",
    )
    assert decision.reason_code == "capacity_available"
    assert fake.decisions == [decision]
