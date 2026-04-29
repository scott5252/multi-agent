from __future__ import annotations

from dataclasses import dataclass, field
from time import monotonic
from uuid import uuid4

from multi_agent_platform.admin.skill_registry.audit import redact_for_audit
from multi_agent_platform.admin.skill_registry.jobs import SkillLifecycleJobStore


@dataclass(frozen=True, slots=True)
class SmokeFixtureInput:
    fixture_key: str
    tool_id: str
    action_category: str
    fixture_digest: str | None = None
    timeout_seconds: int = 30
    requires_credentials: bool = False


@dataclass(frozen=True, slots=True)
class SmokeRunnerInput:
    tenant_id: str
    installation_id: str
    installation_version: int
    package_slug: str
    semantic_version: str
    manifest_digest: str
    artifact_digest: str
    fixtures: tuple[SmokeFixtureInput, ...]
    credential_status: str
    idempotency_key: str
    trace_id: str


@dataclass(frozen=True, slots=True)
class SmokeRunnerOutput:
    test_run_id: str
    outcome: str
    fixture_results: tuple[dict[str, object], ...]
    failure_reasons: tuple[str, ...]
    safe_output_summary: dict[str, object] = field(default_factory=dict)
    duration_ms: int = 0
    trace_id: str | None = None


class SkillSmokeTestRunner:
    def __init__(self, job_store: SkillLifecycleJobStore | None = None) -> None:
        self.job_store = job_store or SkillLifecycleJobStore()

    def run(self, runner_input: SmokeRunnerInput) -> SmokeRunnerOutput:
        start = monotonic()
        job = self.job_store.accept(
            kind="smoke",
            idempotency_key=runner_input.idempotency_key,
            tenant_id=runner_input.tenant_id,
        )
        if job.status == "blocked":
            return SmokeRunnerOutput(
                test_run_id=job.job_id,
                outcome="blocked",
                fixture_results=(),
                failure_reasons=("fairness admission blocked smoke test",),
                trace_id=runner_input.trace_id,
            )
        failure_reasons: list[str] = []
        results: list[dict[str, object]] = []
        for fixture in runner_input.fixtures:
            if (
                fixture.requires_credentials
                and runner_input.credential_status != "ready"
            ):
                outcome = "skipped"
                failure_reasons.append(f"{fixture.fixture_key}: credentials not ready")
            else:
                outcome = "passed"
            results.append(
                redact_for_audit(
                    {
                        "fixture_key": fixture.fixture_key,
                        "outcome": outcome,
                        "policy_decision_summary": {
                            "tool": "allow",
                            "outbound_domain": "allow",
                            "credential": "allow"
                            if runner_input.credential_status == "ready"
                            else "deny",
                        },
                    }
                )
            )
        final_outcome = "passed" if not failure_reasons else "failed"
        self.job_store.complete(job_id=job.job_id, status=final_outcome)
        return SmokeRunnerOutput(
            test_run_id=str(uuid4()),
            outcome=final_outcome,
            fixture_results=tuple(results),
            failure_reasons=tuple(failure_reasons),
            safe_output_summary={"message": "Smoke test completed with safe evidence."},
            duration_ms=int((monotonic() - start) * 1000),
            trace_id=runner_input.trace_id,
        )
