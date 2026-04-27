from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import pytest

from multi_agent_platform.db.models.reliability import (
    CapacitySnapshotRecord,
    CircuitBreakerRecord,
    DeadLetterRecordModel,
    ReliabilityPolicyRecord,
    RetryScheduleRecord,
    TenantQuotaCounterRecord,
)
from multi_agent_platform.db.repositories.reliability import ReliabilityRepository
from multi_agent_platform.reliability.models import (
    AdmissionDecision,
    AdmissionDecisionKind,
)

TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")


class FakeScalarResult:
    def __init__(self, value: object | None = None, values: list[object] | None = None):
        self.value = value
        self.values = values or []

    def scalar_one_or_none(self) -> object | None:
        return self.value

    def scalars(self) -> FakeScalarResult:
        return self

    def all(self) -> list[object]:
        return self.values


class FakeSession:
    def __init__(self, result: FakeScalarResult) -> None:
        self.result = result
        self.added: list[object] = []
        self.flushed = False

    async def execute(self, stmt: object) -> FakeScalarResult:
        assert stmt is not None
        return self.result

    def add(self, record: object) -> None:
        self.added.append(record)

    async def flush(self) -> None:
        self.flushed = True


@pytest.mark.asyncio
async def test_repository_inserts_admission_decision() -> None:
    session = FakeSession(FakeScalarResult())
    repository = ReliabilityRepository(session)  # type: ignore[arg-type]
    decision = AdmissionDecision(
        tenant_id=TENANT_ID,
        decision=AdmissionDecisionKind.ACCEPTED,
        reason_code="capacity_available",
        policy_id=UUID("00000000-0000-0000-0000-000000000002"),
        policy_version=1,
    )
    record = await repository.insert_admission_decision(decision)
    assert session.flushed
    assert session.added == [record]
    assert record.reason_code == "capacity_available"


@pytest.mark.asyncio
async def test_repository_lookup_methods_return_expected_records() -> None:
    policy = ReliabilityPolicyRecord(
        tenant_id=TENANT_ID,
        scope_type="tenant",
        policy_version=1,
        settings={},
    )
    session = FakeSession(FakeScalarResult(policy))
    repository = ReliabilityRepository(session)  # type: ignore[arg-type]
    assert (
        await repository.active_policy_head(
            tenant_id=TENANT_ID,
            scope_type="tenant",
            scope_key=None,
        )
        is policy
    )

    snapshot = CapacitySnapshotRecord(tenant_id=TENANT_ID)
    session.result = FakeScalarResult(snapshot)
    assert await repository.latest_capacity_snapshot(tenant_id=TENANT_ID) is snapshot

    breaker = CircuitBreakerRecord(scope_type="dependency", scope_key="model")
    session.result = FakeScalarResult(breaker)
    assert (
        await repository.breaker_head(
            tenant_id=None,
            scope_type="dependency",
            scope_key="model",
        )
        is breaker
    )


@pytest.mark.asyncio
async def test_repository_lists_and_updates_records() -> None:
    quota = TenantQuotaCounterRecord(
        tenant_id=TENANT_ID,
        resource_kind="active_work",
        limit_value=10,
        used_value=1,
        window_start=datetime(2026, 4, 26, tzinfo=UTC),
        window_end=datetime(2026, 4, 26, 0, 1, tzinfo=UTC),
    )
    session = FakeSession(FakeScalarResult(quota))
    repository = ReliabilityRepository(session)  # type: ignore[arg-type]
    updated = await repository.update_quota_counter(
        tenant_id=TENANT_ID,
        resource_kind="active_work",
        window_start=quota.window_start,
        amount=2,
    )
    assert updated is quota
    assert quota.used_value == 3

    retry = RetryScheduleRecord(
        tenant_id=TENANT_ID,
        failure_category="timeout",
    )
    session.result = FakeScalarResult(values=[retry])
    assert await repository.list_retry_schedules(tenant_id=TENANT_ID) == [retry]

    dead_letter = DeadLetterRecordModel(
        tenant_id=TENANT_ID,
        source_kind="run_step",
        source_id=UUID("00000000-0000-0000-0000-000000000003"),
        failure_category="timeout",
        latest_state={"status": "failed"},
        recommended_action="requeue",
    )
    session.result = FakeScalarResult(values=[dead_letter])
    assert await repository.list_dead_letters(tenant_id=TENANT_ID) == [dead_letter]
