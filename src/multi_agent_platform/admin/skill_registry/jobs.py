from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import uuid4

from multi_agent_platform.admin.skill_registry.fairness import (
    FairnessDecision,
    TenantFairnessController,
)
from multi_agent_platform.db.base import utcnow


class LifecycleJobError(RuntimeError):
    pass


@dataclass(slots=True)
class SkillLifecycleJob:
    job_id: str
    tenant_id: str | None
    kind: str
    idempotency_key: str
    status: str = "queued"
    attempts: int = 0
    lease_owner: str | None = None
    leased_until: datetime | None = None
    failure_summary: dict[str, object] = field(default_factory=dict)
    fairness_decision: FairnessDecision | None = None
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)

    @property
    def terminal(self) -> bool:
        return self.status in {"passed", "failed", "skipped", "errored", "blocked"}


class SkillLifecycleJobStore:
    def __init__(self, fairness: TenantFairnessController | None = None) -> None:
        self.jobs_by_id: dict[str, SkillLifecycleJob] = {}
        self.jobs_by_idempotency_key: dict[str, str] = {}
        self.fairness = fairness or TenantFairnessController()

    def accept(
        self,
        *,
        kind: str,
        idempotency_key: str,
        tenant_id: str | None = None,
    ) -> SkillLifecycleJob:
        existing_id = self.jobs_by_idempotency_key.get(idempotency_key)
        if existing_id is not None:
            return self.jobs_by_id[existing_id]
        decision = self.fairness.admit(tenant_id=tenant_id or "platform", job_kind=kind)
        status = "queued" if decision.allowed else "blocked"
        job = SkillLifecycleJob(
            job_id=str(uuid4()),
            tenant_id=tenant_id,
            kind=kind,
            idempotency_key=idempotency_key,
            status=status,
            fairness_decision=decision,
        )
        self.jobs_by_id[job.job_id] = job
        self.jobs_by_idempotency_key[idempotency_key] = job.job_id
        return job

    def lease(
        self,
        *,
        job_id: str,
        owner: str,
        lease_seconds: int = 120,
        now: datetime | None = None,
    ) -> SkillLifecycleJob:
        current_time = now or utcnow()
        job = self.jobs_by_id[job_id]
        if job.terminal:
            raise LifecycleJobError("terminal jobs cannot be leased")
        if job.leased_until is not None and job.leased_until > current_time:
            raise LifecycleJobError("job is already leased")
        job.lease_owner = owner
        job.leased_until = current_time + timedelta(seconds=lease_seconds)
        job.status = "running"
        job.attempts += 1
        job.updated_at = current_time
        return job

    def complete(
        self,
        *,
        job_id: str,
        status: str,
        failure_summary: dict[str, object] | None = None,
    ) -> SkillLifecycleJob:
        job = self.jobs_by_id[job_id]
        job.status = status
        job.failure_summary = failure_summary or {}
        job.leased_until = None
        job.lease_owner = None
        job.updated_at = utcnow()
        return job
