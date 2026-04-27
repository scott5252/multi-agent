# Quickstart: Reliability And Scale Hardening

**Feature**: Reliability And Scale Hardening  
**Date**: 2026-04-26

## Prerequisites

- Python 3.12
- `uv`
- PostgreSQL 16+
- Object storage provider configured for artifact tests, or the existing
  filesystem provider for local development
- Auth0 settings for production-like authorization, or deterministic local
  principals for tests

## Setup

```bash
uv sync
uv run alembic upgrade head
```

Run the API and workers in separate terminals:

```bash
uv run uvicorn multi_agent_platform.api.main:app --reload
uv run python -m multi_agent_platform.workers.main
```

## Validation Commands

Run formatting, static checks, and the full test suite:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

## Focused Reliability Checks

Run unit coverage for policy/state-machine behavior:

```bash
uv run pytest tests/unit/reliability tests/unit/storage/test_throughput.py
```

Run PostgreSQL-backed recovery, lease, partition, and artifact checks:

```bash
uv run pytest \
  tests/integration/runtime/test_reliability_worker_recovery.py \
  tests/integration/runtime/test_resume_after_failure_under_load.py \
  tests/integration/db/test_reliability_partitioning.py \
  tests/integration/storage/test_artifact_throughput_controls.py
```

Run API contract checks:

```bash
uv run pytest tests/contract/test_reliability_controls_contract.py
uv run pytest tests/integration/api/test_reliability_controls_api.py
```

Run acceptance performance profiles:

```bash
uv run pytest -m performance tests/performance/reliability/test_mixed_lifecycle_load.py
uv run pytest -m performance tests/performance/reliability/test_tenant_burst_fairness.py
uv run pytest -m performance tests/performance/reliability/test_retry_storm_breaker.py
uv run pytest -m performance tests/performance/reliability/test_compensation_dead_letter_load.py
uv run pytest -m performance tests/performance/reliability/test_artifact_export_throughput.py
uv run pytest -m performance tests/performance/reliability/test_failure_inspection_lookup.py
```

## Resume-After-Failure Under Load

The acceptance validation must run deterministic failure injection while the
mixed lifecycle load profile is active.

Required injection points:

- `after_claim`
- `after_checkpoint`
- `after_side_effect_intent`
- `after_side_effect_applied_before_state_advance`
- `after_retry_scheduled`
- `during_compensation`
- `during_artifact_export`

Required assertions:

- Work resumes from the pinned execution bundle and latest valid checkpoint.
- Stale worker writes are suppressed by lease fencing.
- Non-repeatable side effects are not duplicated.
- Ambiguous side-effect state enters operator intervention.
- Compensation is requested at most once per affected intent unless manually
  retried by an authorized operator.
- Dead-letter records include safe reason, latest state, recommended action,
  and artifact refs where needed.
- Compliant tenants retain at least 95 percent normal accepted-work throughput
  during a burst or retry storm from another tenant.
- Recovery eligibility p95 is within 2x the configured lease timeout.

## Operational Smoke Checks

After starting the API, inspect reliability state:

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/admin/reliability/dashboard"

curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/admin/reliability/admission-decisions?limit=20"

curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/admin/reliability/breakers"

curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/admin/reliability/dead-letters?status=open"
```

Tenant operators must include `tenant_id` and can only see or adjust
tenant-scoped controls. Auditors can inspect authorized scopes but cannot
change control state.

## Review Evidence

Feature delivery is review-ready only when the PR includes:

- Coverage evidence showing at least 90 percent unit-test coverage.
- Load-test report for 5,000 active users across at least 50 tenants.
- Tenant burst report showing compliant tenants retain at least 95 percent
  normal accepted-work throughput.
- Resume-after-failure report with all required injection points.
- Circuit breaker transition evidence including cooldown and probe recovery.
- Compensation and dead-letter outcome evidence.
- Artifact-throughput evidence for throttled object storage.
- README and operator guidance updates.
- PR notes covering scale assumptions, recovery guarantees, retry/breaker
  behavior, compensation coverage, quotas, fairness, authorization, auditability,
  operational risks, and known limitations.

Current local evidence command:

```bash
uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90
```

Latest recorded result: 430 passed, coverage 90.18 percent.
