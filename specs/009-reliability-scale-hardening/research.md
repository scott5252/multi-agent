# Research: Reliability And Scale Hardening

**Feature**: Reliability And Scale Hardening  
**Date**: 2026-04-26  
**Status**: Complete

## Sources Checked

- Existing durable runtime plan and research:
  `specs/004-durable-orchestration-runtime/plan.md`,
  `specs/004-durable-orchestration-runtime/research.md`,
  `specs/004-durable-orchestration-runtime/data-model.md`
- Existing production audit/debugging plan:
  `specs/008-production-audit-debugging/plan.md`
- Existing runtime, queue, audit, storage, observability, and worker source
  layout under `src/multi_agent_platform/`
- Project constitution in `.specify/memory/constitution.md`

## Worker Autoscaling Signal Model

**Decision**: Scale workers from durable backlog and health signals rather than
raw request rate. Autoscaling inputs are runnable depth, delayed depth, active
leases, lease renewal lag, retry/recovery backlog, DB pool wait time, artifact
I/O pressure, open breaker work, and fairness debt. Scale out only when backlog
pressure is sustained and dependencies have headroom; scale in only after a
cooldown with no recovery backlog or fairness debt.

**Rationale**: Request rate alone can scale workers into a database or object
store bottleneck and make overload worse. Backlog plus health signals preserve
capacity for recovery and inspection.

**Alternatives considered**: CPU-only scaling, rejected because workflow
workers can be I/O-bound. Queue-depth-only scaling, rejected because it ignores
DB and dependency saturation. Manual-only scaling, rejected because acceptance
requires sustained load handling.

## Lease Tuning And Fencing

**Decision**: Keep the existing recoverable `WorkerLease` pattern, add
tenant/workflow-scoped lease policies, renew at one quarter of expiry, treat
missed renewals past half expiry as at risk, and require a fencing token
(`worker_lease_id` plus `claim_attempt`) on every worker state write.

**Rationale**: Lease expiry enables recovery after worker crashes, while
fencing prevents a stale worker from writing after another worker has recovered
the same work.

**Alternatives considered**: In-process locks, rejected because they do not
survive worker failure. Queue visibility timeout only, rejected because runtime
state is already coordinated in PostgreSQL and needs run/step-level fencing.

## Database Pooling

**Decision**: Use separate bounded async SQLAlchemy pool settings for API,
workers, migrations, and load tests. Admission control observes pool wait p95,
open transaction age, and reserve connection availability. Worker scale-out is
blocked when pool reserve falls below the configured floor.

**Rationale**: Thousands of active users and many workers can exhaust
PostgreSQL connections faster than CPU. Dedicated reserves keep readiness,
admin inspection, and incident remediation available during overload.

**Alternatives considered**: One shared large pool, rejected because it allows
workers to starve admin/API traffic. Unbounded overflow, rejected because it
pushes overload into PostgreSQL and increases tail latency.

## Partitioning Strategy

**Decision**: Partition high-volume append-only reliability tables by time and,
where query distribution requires it, tenant hash. Keep current-state head
tables unpartitioned or lightly partitioned with narrow composite indexes by
tenant, scope, status, and run id.

**Rationale**: Reliability decisions, retry attempts, compensation events,
dead-letter records, and load-test samples grow quickly under failure storms.
Time partitions make retention cheap; tenant hash partitions reduce hot-tenant
contention without making current heads hard to query.

**Alternatives considered**: Partition every table, rejected because small
current-state tables perform better with simple indexes. No partitioning,
rejected because retention and high-volume incident analysis would degrade.

## Retry Policy

**Decision**: Retry only classified retryable failures with bounded exponential
backoff, full jitter, a maximum deadline, and per-tenant retry budgets. Do not
auto-retry authorization, quota, contract, invalid checkpoint, open breaker,
unknown side-effect, or non-repeatable ambiguous failures.

**Rationale**: Retries improve transient availability but become a denial of
service when deterministic or unsafe failures are repeated.

**Alternatives considered**: Unlimited retries, rejected due to retry storms
and unfair tenant impact. No automatic retries, rejected because transient
model, tool, network, and storage failures are expected.

## Circuit Breaker Rules

**Decision**: Implement dependency/operation breakers with closed, open, and
half-open states. Opening conditions include consecutive failures, rolling
failure ratio, latency p95, overload signals, or operator action. Recovery
requires cooldown plus successful health/probe evidence before limited
half-open trial traffic.

**Rationale**: The spec requires protective containment and explicit recovery
evidence. Half-open trial traffic avoids returning a dependency to full load
immediately after recovery.

**Alternatives considered**: Retry-only containment, rejected because it keeps
sending traffic to known-bad dependencies. Manual breaker reset only, rejected
because recovery evidence should safely automate normal incidents.

## Compensation Orchestration

**Decision**: Treat compensation as durable runtime work created from a
side-effect intent. Use uniqueness constraints to issue at most one automatic
compensation request per affected intent/hook. Compensation has its own lease,
retry budget, breaker checks, outcomes, audit timeline, and dead-letter path.

**Rationale**: Compensation needs the same durability, tenant scoping, and
inspection as primary work. Exactly-once request creation prevents cleanup
storms after repeated worker crashes.

**Alternatives considered**: Inline best-effort compensation inside failed
steps, rejected because crash recovery would lose or duplicate cleanup. Manual
only compensation, rejected because declared safe hooks should run
automatically.

## Dead-Letter Handling

**Decision**: Add inspectable dead-letter records for exhausted or unsafe work,
including queue jobs, run steps, retry attempts, compensation requests, and
artifact exports. Operators can requeue, compensate, mark resolved, or
escalate through authorized audited actions.

**Rationale**: Dead letters are the point where automated recovery stops and
human response begins; they must preserve enough safe state to act.

**Alternatives considered**: Terminal failure only on the run, rejected because
operators need category, policy, latest state, and recommended action. Hidden
dead-letter queues, rejected because the spec requires inspection.

## Load Testing

**Decision**: Implement deterministic pytest performance profiles rather than a
separate load-test service in the first iteration. Profiles simulate mixed
submit/status polling, tenant bursts, worker crashes, stale workers, retry
storms, breaker recovery, compensation outcomes, and artifact throttling.

**Rationale**: Pytest profiles fit the existing repo workflow and can validate
acceptance scenarios in CI-like environments while preserving seeds and
reports for review.

**Alternatives considered**: External-only load testing, rejected because it
would be harder to keep alongside coverage and PR evidence. Unit-only scale
tests, rejected because PostgreSQL pooling, leases, and partitions need
integration pressure.

## Operational Dashboards

**Decision**: Build dashboard projections from low-cardinality metrics,
structured logs/traces, and durable operational snapshots. Fleet views use
snapshots; tenant/run drilldowns use bounded indexed queries.

**Rationale**: Direct dashboard scans over high-volume event tables would
create load during incidents. Snapshots keep the operator view responsive while
preserving drilldown accuracy.

**Alternatives considered**: Dashboard directly from event tables, rejected for
tail latency and database pressure. Metrics only, rejected because operators
need run-level inspection and actions.

## Tenant Fairness Controls

**Decision**: Use weighted fair scheduling with per-tenant token buckets and
fairness debt. Budgets cover submission, active work, recovery, retries,
compensation, artifact exports, and selected operational actions.

**Rationale**: The spec requires delay/queue before reject and preservation of
compliant tenants during bursts. Token buckets bound each tenant; fairness debt
prevents long-term starvation.

**Alternatives considered**: Global FIFO queue, rejected because one tenant can
dominate shared capacity. Static per-tenant worker pools, rejected because it
wastes capacity when tenants are idle.

## Artifact Storage Throughput

**Decision**: Apply per-tenant and global concurrency limits to large artifact
reads/writes and exports. Store only artifact metadata, checksums, retention,
access policy, and audit refs in PostgreSQL; stream large payloads through
object storage.

**Rationale**: Load reports, replay evidence, and failure exports can become
large during incidents. They must not exhaust database storage or worker I/O.

**Alternatives considered**: Store reports in PostgreSQL JSON/blob columns,
rejected by the constitution. Unbounded artifact generation, rejected because
it can starve normal workflow artifact I/O.

## Failure-Mode Research

**Decision**: Validate the following failure modes as first-class acceptance
cases: worker crash after claim; worker crash after checkpoint; side effect
applied before state advance; stale worker returns after another worker
recovers; database pool exhaustion; partition hot spot; retry storm; breaker
false recovery; compensation timeout; dead-letter requeue race; object storage
throttling; dashboard query under incident load; tenant burst during recovery;
policy change during active load.

**Rationale**: These are the failure boundaries where reliability systems most
often lose state, duplicate side effects, or starve compliant tenants.

**Alternatives considered**: Validate only happy-path load and single-worker
crashes, rejected because the spec requires recovery-safe behavior under load
and failure inspection.

## Resume-After-Failure Validation Strategy

**Decision**: Run deterministic failure injection while the 5,000-user mixed
lifecycle load profile is active. For each injected failure, assert that work
resumes from the pinned bundle and latest checkpoint, stale writes are
suppressed by fencing, side-effect intents are not duplicated, and the outcome
is one of resumed, duplicate-suppressed, compensated, dead-lettered, or
operator-intervention-required.

**Rationale**: Resume correctness must hold while queues, leases, retries,
breakers, and DB pools are under pressure, not only in isolated tests.

**Alternatives considered**: Manual chaos testing only, rejected because it is
not repeatable enough for regression coverage. Mock-only recovery tests,
rejected because database locks, connection pools, and checkpoint persistence
are central to the behavior.
