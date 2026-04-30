from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime

from multi_agent_platform.db.base import utcnow


@dataclass(frozen=True, slots=True)
class TenantLifecycleQuota:
    max_active_validation_jobs: int = 2
    max_active_smoke_jobs: int = 2
    max_queued_jobs: int = 25
    max_artifact_bytes_per_window: int = 50_000_000


@dataclass(frozen=True, slots=True)
class FairnessDecision:
    allowed: bool
    reason: str
    tenant_id: str
    safe_summary: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class QueuedLifecycleJob:
    job_id: str
    tenant_id: str
    kind: str
    created_at: datetime = field(default_factory=utcnow)


class TenantFairnessController:
    def __init__(self, quota: TenantLifecycleQuota | None = None) -> None:
        self.quota = quota or TenantLifecycleQuota()
        self.active_by_tenant: dict[str, dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        self.queued_by_tenant: dict[str, deque[QueuedLifecycleJob]] = defaultdict(deque)
        self.artifact_bytes_by_tenant: dict[str, int] = defaultdict(int)

    def admit(
        self,
        *,
        tenant_id: str,
        job_kind: str,
        artifact_bytes: int = 0,
    ) -> FairnessDecision:
        active_limit = (
            self.quota.max_active_validation_jobs
            if job_kind == "validation"
            else self.quota.max_active_smoke_jobs
        )
        active = self.active_by_tenant[tenant_id][job_kind]
        queued = len(self.queued_by_tenant[tenant_id])
        if active >= active_limit and queued >= self.quota.max_queued_jobs:
            return FairnessDecision(False, "tenant_queue_limit", tenant_id)
        if (
            self.artifact_bytes_by_tenant[tenant_id] + artifact_bytes
            > self.quota.max_artifact_bytes_per_window
        ):
            return FairnessDecision(False, "artifact_throughput_limit", tenant_id)
        return FairnessDecision(
            True,
            "admitted",
            tenant_id,
            {"active": active, "queued": queued, "job_kind": job_kind},
        )

    def enqueue(self, job: QueuedLifecycleJob) -> None:
        self.queued_by_tenant[job.tenant_id].append(job)

    def next_job(self) -> QueuedLifecycleJob | None:
        tenants = sorted(self.queued_by_tenant)
        candidates = [
            self.queued_by_tenant[tenant][0]
            for tenant in tenants
            if self.queued_by_tenant[tenant]
        ]
        if not candidates:
            return None
        selected = min(candidates, key=lambda job: job.created_at)
        self.queued_by_tenant[selected.tenant_id].popleft()
        return selected
