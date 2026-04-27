# Implementation Plan: Reliability And Scale Hardening

**Branch**: `009-reliability-scale-hardening` | **Date**: 2026-04-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/009-reliability-scale-hardening/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See
`.specify/templates/commands/plan.md` for project-specific planning rules.

## Summary

Add reliability and scale hardening for the multi-tenant workflow runtime so the
platform can sustain at least 5,000 active users across at least 50 tenants in a
mixed submit-and-monitor workload without exhausting shared capacity or
duplicating irreversible work. The design extends the existing Python/FastAPI,
PostgreSQL, LangGraph, worker, queue, audit, storage, and web-admin modules with
tenant-aware admission control, fair scheduling, worker autoscaling signals,
lease tuning, bounded retry budgets, circuit breakers, compensation
orchestration, dead-letter handling, operational dashboards, load-test
fixtures, and artifact-throughput controls. PostgreSQL remains the
transactional source of truth; large debug exports and replay artifacts remain
in object storage with PostgreSQL metadata.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: FastAPI, Starlette response handling, Pydantic v2,
Pydantic Settings, SQLAlchemy 2.x async ORM, Alembic, PostgreSQL 16+,
psycopg 3, Auth0 JWT validation plus local-principal test mode, LangChain
1.2.15, LangGraph 1.1.9, langgraph-checkpoint-postgres 3.0.5,
prometheus-client, httpx, pytest, pytest-asyncio, Ruff, mypy, uv  
**Storage**: PostgreSQL for reliability policies, worker leases, queue state,
quota counters, fairness windows, retry schedules, circuit breaker state,
compensation requests, dead-letter records, operational snapshots, audit
events, and artifact metadata; object storage for large replay evidence,
load-test reports, and failure-inspection exports  
**Testing**: pytest unit tests for admission, fair scheduling, quotas, lease
math, retry classifiers, breaker transitions, compensation state machines,
dead-letter routing, artifact-throughput controls, dashboard projections, and
authorization; PostgreSQL-backed integration tests for concurrent claiming,
stale lease suppression, resume-after-failure, recovery races, partition-aware
queries, pool pressure, compensation idempotency, replay/debug references, and
dead-letter inspection; FastAPI contract tests for operational control and
inspection endpoints plus worker reliability protocol compatibility;
performance/load tests for 5,000 active users across 50 tenants, burst/failure
storms, failure-inspection lookup, compensation/dead-letter load, and artifact
export throughput; coverage enforced at >=90 percent  
**Target Platform**: Linux container deployment for FastAPI API and background
workers with local macOS/Linux development; PostgreSQL-backed runtime under the
existing platform bootstrap model  
**Project Type**: Multi-tenant backend platform with FastAPI JSON APIs,
minimal server-rendered/admin UI views, durable workflow workers, PostgreSQL
storage, object-storage artifact handling, and operator-facing documentation  
**Performance Goals**: Sustain acceptance testing with 5,000 active users
across 50 tenants in mixed submit/status-monitor load; compliant tenants retain
at least 95 percent normal accepted-work throughput during one tenant's burst;
100 percent overload paths return accepted, queued, delayed, throttled,
rejected, or retry-eligible status; failure inspection lookup p95 <= 5 seconds;
no duplicate irreversible side effects in crash/retry/recovery races; worker
lease recovery p95 <= 2x configured lease timeout after simulated crash  
**Constraints**: Backpressure must queue or delay tenant-scoped work before
throttling/rejecting after scoped queue or budget exhaustion; workers must not
repeat non-repeatable side effects without explicit repeatability metadata or
operator authorization; circuit breaker recovery requires cooldown plus
successful configured health/probe evidence before half-open trial traffic;
settings that disable recovery safety, quotas, fairness, or containment are
rejected or require explicit authorized override; all control changes and
denied attempts are audited; PostgreSQL must not store large blob payloads;
resume uses the pinned execution bundle unless an audited migration path exists  
**Scale/Scope**: 5,000 active users, 50 tenants, mixed lifecycle submit and run
status monitoring, tenant bursts, retry storms, worker crashes, stale workers,
compensation paths, dead-letter queues, operational dashboards, and artifact
exports. Initial implementation targets a single regional PostgreSQL cluster
with partitioned high-volume tables and application-level fair scheduling; no
cross-region active-active scheduler is in scope.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Durable By Default | PASS | Worker ownership, queue state, retry decisions, breaker transitions, compensation requests, dead-letter records, and recovery progress are durable and crash-resumable. |
| Immutable State And Memory | PASS | Control decisions, policy changes, failure records, compensation outcomes, and audit records are append-only; mutable operational heads are derived projections. |
| Contract-First Agent Coordination | PASS | Operational APIs, worker lease protocol, side-effect classification, breaker events, and compensation contracts are defined before implementation. |
| Security With Practical Development Ergonomics | PASS | Auth0/local-principal authorization gates global controls, tenant controls, inspection, dashboards, overrides, and denied-access audits. |
| Operability Is A Product Requirement | PASS | Dashboards, metrics, logs, traces, inspection APIs, load-test reports, failure-mode records, and README/operator guidance are first-class deliverables. |
| Spec-Driven Delivery | PASS | Spec, plan, research, data model, contracts, quickstart, and future tasks trace directly to reliability and scale outcomes. |
| Test And Documentation Discipline | PASS | Plan requires >=90 percent coverage, reviewer instructions, PR notes, README updates, docs tests, and automated load/recovery validation. |
| Clear Ownership And Small Safe Changes | PASS | Work is split across runtime reliability services, queue/repository updates, admin APIs/views, observability, storage, migrations, and focused tests. |
| Tenant Isolation And Fair Scheduling | PASS | Admission, queueing, workers, retries, breaker scopes, compensation, dead letters, dashboards, and artifacts carry tenant scope and enforce quota/fairness rules. |
| Version-Pinned Execution | PASS | Resume-after-failure uses the original run bundle; policy versions are recorded with each decision and apply prospectively to new decisions. |
| Secret Hygiene And Controlled Tool Access | PASS | Failure inspection and dead-letter payloads store safe summaries, secret references, or artifact references only; raw secrets and credentials are rejected. |
| Tiered Storage For Large Payloads | PASS | PostgreSQL stores transactional state and metadata; large replay evidence, load reports, and exports use object storage with retention/audit metadata. |
| Human Approval Is Durable State | PASS | Non-repeatable ambiguous recovery, manual compensation, breaker resets, and unsafe override paths create durable intervention records before resume. |

Post-Phase-1 re-check: design artifacts keep every constitution gate in `PASS`
status with no exceptions required.

## Project Structure

### Documentation (this feature)

```text
specs/009-reliability-scale-hardening/
+-- plan.md
+-- research.md
+-- data-model.md
+-- quickstart.md
+-- contracts/
|   +-- reliability-scale.openapi.yaml
|   +-- worker-reliability-protocol.md
+-- tasks.md
```

### Source Code (repository root)

```text
src/
+-- multi_agent_platform/
    +-- api/
    |   +-- routers/
    |   |   +-- reliability_controls.py       # control, inspection, breaker, dead-letter APIs
    |   +-- schemas/
    |       +-- reliability.py                # API request/response schemas
    +-- db/
    |   +-- models/
    |   |   +-- reliability.py                # policies, quotas, breakers, dead letters
    |   +-- repositories/
    |       +-- reliability.py                # partition-aware queries and state transitions
    +-- reliability/
    |   +-- admission.py                      # tenant-aware admission/backpressure
    |   +-- autoscaling.py                    # worker scaling signals and capacity snapshots
    |   +-- breakers.py                       # circuit breaker state machine
    |   +-- compensation.py                   # compensation request orchestration
    |   +-- dead_letters.py                   # terminal inspection queues
    |   +-- fairness.py                       # tenant fair-share scheduling
    |   +-- leases.py                         # lease policy and stale worker suppression
    |   +-- load_profiles.py                  # deterministic load/failure scenarios
    |   +-- models.py                         # domain value objects
    |   +-- partitioning.py                   # table partition helpers and query windows
    |   +-- pooling.py                        # DB pool settings and telemetry helpers
    |   +-- retries.py                        # retry classifier and budget resolver
    |   +-- service.py                        # orchestration facade
    +-- runtime/
    |   +-- queue/
    |   |   +-- service.py                    # tenant-aware leasing order and backpressure
    |   +-- orchestration/
    |       +-- leasing.py                    # integrate tuned lease policies
    |       +-- side_effects.py               # repeatability/compensation metadata gates
    +-- storage/
    |   +-- throughput.py                     # artifact concurrency and rate controls
    +-- audit/
    |   +-- service.py                        # timeline, lineage, and control-change audit events
    +-- observability/
    |   +-- metrics.py                        # reliability metrics/dashboard exports
    |   +-- logging.py                        # reliability structured log fields
    +-- web_admin/
        +-- static/
        |   +-- reliability_controls.js
        +-- templates/
            +-- reliability/
                +-- index.html
                +-- breakers.html
                +-- dead_letters.html
alembic/versions/
+-- 0009_reliability_scale_hardening.py
tests/
+-- contract/
|   +-- test_reliability_controls_contract.py
|   +-- test_worker_reliability_protocol.py
|   +-- test_worker_reliability_semantics.py
+-- integration/
|   +-- api/
|   |   +-- test_reliability_controls_api.py
|   +-- db/
|   |   +-- test_reliability_partitioning.py
|   +-- runtime/
|   |   +-- test_reliability_replay_references.py
|   |   +-- test_resume_after_failure_under_load.py
|   |   +-- test_reliability_worker_recovery.py
|   +-- storage/
|       +-- test_artifact_throughput_controls.py
+-- performance/
|   +-- reliability/
|       +-- test_artifact_export_throughput.py
|       +-- test_compensation_dead_letter_load.py
|       +-- test_failure_inspection_lookup.py
|       +-- test_mixed_lifecycle_load.py
|       +-- test_retry_storm_breaker.py
|       +-- test_tenant_burst_fairness.py
+-- docs/
|   +-- test_readme_reliability_scale_hardening.py
|   +-- test_reliability_incident_next_actions.py
|   +-- test_reliability_scale_hardening_docs.py
+-- unit/
    +-- reliability/
    |   +-- test_admission.py
    |   +-- test_autoscaling.py
    |   +-- test_breakers.py
    |   +-- test_compensation.py
    |   +-- test_dead_letters.py
    |   +-- test_fairness.py
    |   +-- test_leases.py
    |   +-- test_partitioning.py
    |   +-- test_pooling.py
    |   +-- test_retries.py
    +-- storage/
        +-- test_throughput.py
README.md
docs/quickstart.md
docs/reliability-scale-hardening.md
```

**Structure Decision**: Keep reliability hardening inside the existing
Python/FastAPI backend. Add a focused `multi_agent_platform.reliability`
package for policy/state-machine logic, extend queue/runtime/storage modules
only at the integration boundaries, add SQLAlchemy models/repositories for
durable state, expose thin FastAPI/admin UI surfaces, and reuse existing audit,
auth, observability, and artifact storage primitives.

## Reliability And Scale Decisions

### Worker Autoscaling

- Emit capacity snapshots every 15 seconds per worker pool with runnable depth,
  delayed depth, active leases, lease renewal lag, CPU/memory headroom if
  available, DB pool wait time, artifact I/O wait time, breaker-open work, and
  tenant fairness debt.
- Scale out when effective runnable depth per healthy worker exceeds the
  configured target for 3 consecutive windows and database pool headroom remains
  above the minimum reserve.
- Scale in only after runnable depth, delayed depth, and recovery backlog remain
  below target for 10 minutes and no tenant has unpaid fairness debt.
- Do not scale out into an unhealthy dependency: open breakers, high DB pool
  wait, migration lag, or artifact throttling convert demand into queue/delay
  rather than additional workers.

### Lease Tuning And Recovery

- Keep the durable `WorkerLease` model but make lease policy tenant/workflow
  scoped with defaults of 120 second expiry, renewal every 30 seconds, and
  renewal deadline at 50 percent of expiry.
- Compute expiry as `max(2 * p99 step heartbeat interval, 30 seconds)` and cap
  default interactive work at 5 minutes unless explicitly configured.
- Stale workers must use fencing tokens (`claim_attempt` plus lease id) on
  every state write. Repository writes reject stale tokens even if a lost worker
  returns.
- Recovery workers load the pinned execution bundle, latest checkpoint ref,
  side-effect intent state, retry history, and breaker/policy version before
  resuming. Unknown side-effect repeatability routes to intervention.

### Database Pooling

- Separate API, worker, migration, and load-test database engine settings.
  Workers use bounded async pools with per-process defaults sized from
  deployment configuration, not worker count alone.
- Reserve at least 20 percent of PostgreSQL connections for admin, migration,
  readiness, and incident inspection traffic.
- Admission control watches pool wait p95 and open transaction age. If pool
  wait exceeds threshold, new work is delayed before workers scale out.
- Long-running load-test and dashboard reads use bounded pages, tenant/time
  filters, and read-only transactions; they never hold locks across streaming
  responses.

### Partitioning Strategy

- Partition high-volume append-only tables by time and tenant hash where access
  patterns require both dimensions: reliability decisions, retry attempts,
  compensation events, dead-letter records, operational snapshots, and load-test
  samples.
- Keep current-state tables small and indexed by `(tenant_id, scope, status)`
  or `(tenant_id, workflow_run_id)`: active policies, breaker heads, quota
  heads, fairness windows, active leases, and active queues.
- Default monthly partitions for audit-like rows, daily partitions for
  high-volume load-test samples, and retention-driven detach/drop jobs with
  audit records.
- All partitioned tables must include tenant id, occurred/created timestamp,
  run id when available, policy version, and trace id.

### Retry Policy

- Classify failures as transient, overload, dependency_unavailable,
  deterministic, authorization, quota, breaker_open, non_repeatable_ambiguous,
  compensation_required, or unknown.
- Default transient retry budget is 3 attempts with exponential backoff,
  full jitter, per-tenant retry budget, and a maximum retry deadline.
- Do not auto-retry authorization denials, contract violations, quota denials,
  open-breaker decisions, invalid checkpoints, unknown side-effect state, or
  non-repeatable steps without an applied intent/result.
- Retry storms consume tenant retry budget and can trigger tenant-scoped or
  dependency-scoped breakers before shared capacity is harmed.

### Circuit Breaker Rules

- Breakers can be scoped by platform dependency, tenant/dependency,
  workflow/step/dependency, or artifact store operation.
- Closed -> open when rolling failure ratio, consecutive failures, latency p95,
  overload signals, or explicit operator action crosses configured thresholds.
- Open -> half_open only after cooldown plus successful configured health/probe
  evidence. Half-open allows limited trial traffic with a token bucket.
- Half-open -> closed only after the configured success count and latency
  target are met; half-open -> open on the first protected failure.
- Authorized reset records actor, reason, previous state, new state, policy
  version, and effective time. Unsafe reset during active failure requires
  explicit override.

### Compensation Orchestration

- Side-effecting steps must declare repeatability and optional compensation
  metadata. Missing metadata defaults to non-repeatable and
  intervention-required.
- Compensation requests are created at most once per affected side-effect
  intent using a unique `(tenant_id, side_effect_intent_id, hook_ref)` key.
- Compensation executes as normal durable runtime work with its own run step,
  lease, retry budget, breaker checks, and audit timeline.
- Outcomes are `succeeded`, `failed`, `unavailable`, `timed_out`,
  `skipped_by_policy`, or `manual_follow_up_required`.

### Dead-Letter Handling

- Runs, steps, retry attempts, compensation requests, and queue jobs move to
  dead-letter state only after policy says automated recovery is unsafe or
  exhausted.
- Dead-letter records include safe failure reason, latest state, policy version,
  recommended action, owning tenant, related run/step/intent, and artifact refs
  for large evidence.
- Authorized operators can requeue, compensate, mark resolved, or escalate from
  dead-letter inspection. Every action is audited and uses current policy
  prospectively.

### Tenant Fairness Controls

- Admission and leasing use per-tenant token buckets plus weighted fair-share
  scheduling by tenant tier and workflow priority.
- Per-tenant budgets cover submitted work, active work, worker leases, recovery
  work, retry attempts, compensation work, artifact export throughput, and
  operational actions.
- Fairness debt is recorded when a tenant receives less than its configured
  share during contention; later scheduling repays debt without starving other
  tenants.
- Burst tenants are delayed/throttled once scoped queue and budget limits are
  exhausted. Compliant tenants must retain at least 95 percent normal
  accepted-work throughput in acceptance testing.

### Artifact Storage Throughput

- Artifact reads/writes use per-tenant and global concurrency limits plus
  object-store operation breakers.
- Large replay evidence, load reports, and exports stream through object
  storage and store only metadata, checksums, retention, access policy, and
  audit references in PostgreSQL.
- Artifact queue pressure feeds admission/backpressure decisions for work that
  would create large artifacts.
- Export generation is rate-limited per tenant and actor, supports safe retry,
  and records partial/unavailable states when object storage is degraded.

### Operational Dashboards

- Dashboards expose global and tenant views for accepted/queued/delayed/
  throttled/rejected work, active leases, stale leases, recovery backlog,
  retry budget usage, breaker state, compensation outcomes, dead-letter counts,
  DB pool pressure, partition health, artifact throughput, and fairness debt.
- Metrics use low-cardinality labels for tenant tier, dependency, workflow
  class, decision outcome, failure category, and breaker state. High-cardinality
  run ids remain in logs/traces/audit records, not Prometheus labels.
- Dashboard queries use precomputed operational snapshots for fleet views and
  bounded tenant/run drilldowns for inspection.

### Load Test Approach

- Provide deterministic pytest performance scenarios for:
  - 5,000 active users across 50 tenants with mixed submit and status polling.
  - One burst tenant exceeding fair share while compliant tenants continue.
  - Worker crash, lease expiry, stale worker return, and recovery race under
    concurrent load.
  - Retry storm against a degraded dependency and breaker transition.
  - Compensation success/failure/timeouts and dead-letter routing.
  - Artifact export throughput with object storage throttling.
  - Failure inspection lookup p95 <= 5 seconds for failed, delayed,
    throttled, recovered, and compensation-required runs.
- Load fixtures must record seed, tenant distribution, workload mix, policy
  versions, DB pool settings, worker counts, observed p50/p95/p99, failure
  counts, and generated artifact refs for review.

### Resume-After-Failure Validation Under Load

- Inject deterministic failure points after claim, after checkpoint, after
  side-effect intent creation, after side-effect applied before state advance,
  after retry scheduling, during compensation, and during artifact export.
- Run failure injection while the mixed lifecycle load profile is active.
- Validate that each interrupted unit resumes, suppresses duplicate work,
  compensates, dead-letters, or enters operator intervention with inspectable
  state.
- Assert zero duplicate irreversible side effects, no stale-worker commits, no
  lost terminal states, and p95 recovery eligibility within 2x lease timeout.

## Complexity Tracking

No constitution violations or complexity exceptions are required.
