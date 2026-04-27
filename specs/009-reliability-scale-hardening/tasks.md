# Tasks: Reliability And Scale Hardening

**Input**: Design documents from `/Users/scottcornell/src/my-projects/multi-agent/specs/009-reliability-scale-hardening/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`
**Tests**: Required by specification and user request. Write tests before implementation and confirm they fail for missing behavior.
**Organization**: Tasks are grouped by user story so each story can be implemented and tested as an independent increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and does not depend on incomplete tasks
- **[Story]**: User story trace label for story phases only
- Every task includes an exact repository file path

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish file structure, configuration hooks, and review artifacts needed by all later work.

- [ ] T001 Create the reliability package marker in `src/multi_agent_platform/reliability/__init__.py`
- [ ] T002 Create reliability test package markers in `tests/unit/reliability/__init__.py`, `tests/performance/reliability/__init__.py`, and `tests/integration/storage/__init__.py`
- [ ] T003 Add reliability settings placeholders for quotas, leases, retries, breakers, autoscaling, and artifact throughput in `src/multi_agent_platform/config/settings.py`
- [ ] T004 [P] Register the `performance` pytest marker for reliability load profiles in `pyproject.toml`
- [ ] T005 [P] Create the operator documentation stub in `docs/reliability-scale-hardening.md`
- [ ] T006 [P] Create the PR review notes stub in `docs/reliability-scale-hardening-pr-notes.md`
- [ ] T007 [P] Create the reviewer testing instructions stub in `docs/reliability-scale-hardening-testing.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Durable state, repository boundaries, schemas, authorization, and metrics required before any user story implementation.

**CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T008 Create SQLAlchemy reliability models for policies, admission decisions, quota counters, fairness windows, capacity snapshots, retry schedules, circuit breakers, compensation requests, dead letters, control changes, artifact windows, and failure injection records in `src/multi_agent_platform/db/models/reliability.py`
- [ ] T009 Register reliability models with metadata imports in `src/multi_agent_platform/db/models/__init__.py`
- [ ] T010 Create Alembic migration for reliability tables, indexes, uniqueness constraints, and partition-ready timestamp/tenant columns in `alembic/versions/0009_reliability_scale_hardening.py`
- [ ] T011 Implement partition-aware reliability repository methods for policy heads, decision inserts, quota counter updates, breaker heads, compensation uniqueness, dead-letter actions, and bounded inspection queries in `src/multi_agent_platform/db/repositories/reliability.py`
- [ ] T012 Implement partition helper utilities for tenant/time query windows, partition naming, retention detach/drop planning, and validation in `src/multi_agent_platform/reliability/partitioning.py`
- [ ] T013 [P] Add unit tests for reliability partition helper utilities in `tests/unit/reliability/test_partitioning.py`
- [ ] T014 Create reliability domain enums, value objects, policy settings, decision records, worker context, and failure classification models in `src/multi_agent_platform/reliability/models.py`
- [ ] T015 Implement policy validation for unsafe settings, override requirements, prospective policy versions, and scoped tenant/global control rules in `src/multi_agent_platform/reliability/policies.py`
- [ ] T016 Create the reliability orchestration facade that wires repositories, audit, metrics, auth scope checks, and runtime services in `src/multi_agent_platform/reliability/service.py`
- [ ] T017 Create Pydantic API schemas matching `contracts/reliability-scale.openapi.yaml` in `src/multi_agent_platform/api/schemas/reliability.py`
- [ ] T018 [P] Add worker reliability protocol compatibility tests for lease claims, recovery handoff, side-effect metadata, breaker events, and compensation envelopes in `tests/contract/test_worker_reliability_protocol.py`
- [ ] T019 [P] Add semantic validation tests for worker reliability protocol versioning and in-flight compatibility rules in `tests/contract/test_worker_reliability_semantics.py`
- [ ] T020 Create the reliability controls router with empty authorized handlers for dashboard, policies, decisions, breakers, retries, compensations, dead letters, and load-test reports in `src/multi_agent_platform/api/routers/reliability_controls.py`
- [ ] T021 Register the reliability controls router in `src/multi_agent_platform/api/main.py`
- [ ] T022 Implement scoped reliability authorization helpers for global admins, tenant operators, auditors, denied attempts, and local-principal tests in `src/multi_agent_platform/reliability/authorization.py`
- [ ] T023 Add low-cardinality reliability metrics for admission decisions, quota outcomes, fairness debt, leases, retries, breakers, compensation, dead letters, pool pressure, and artifact throughput in `src/multi_agent_platform/observability/metrics.py`
- [ ] T024 Add structured reliability log fields for admission, quota, fairness, lease, retry, breaker, compensation, dead-letter, artifact, and control-change paths in `src/multi_agent_platform/observability/logging.py`
- [ ] T025 Add workflow timeline and lineage event emission for reliability decisions, recovery attempts, compensation outcomes, and dead-letter transitions in `src/multi_agent_platform/audit/service.py`
- [ ] T026 [P] Add replay/debug reference tests proving reliability inspection records link to workflow run, step, trace, policy version, and artifact refs without storing large payloads in PostgreSQL in `tests/integration/runtime/test_reliability_replay_references.py`
- [ ] T027 [P] Add reusable reliability fixtures for tenants, policies, worker contexts, capacity snapshots, side-effect intents, and local principals in `tests/fixtures/reliability.py`
- [ ] T028 Add migration coverage for the reliability schema and critical indexes in `tests/integration/db/test_reliability_partitioning.py`

**Checkpoint**: Durable reliability state, schemas, authorization, and shared wiring are ready for user story work.

---

## Phase 3: User Story 1 - Sustain Reliable Service Under Load (Priority: P1) MVP

**Goal**: Admit, queue, delay, throttle, or reject tenant work under load while preserving quota enforcement and fair scheduling.

**Independent Test**: Simulate many tenants submitting and monitoring workflow work, then verify explicit overload statuses, tenant quota enforcement, fair-share scheduling, and 95 percent throughput retention for compliant tenants during a burst.

### Tests for User Story 1

- [ ] T029 [P] [US1] Add admission and backpressure unit tests for accepted, queued, delayed, throttled, rejected, and retry-eligible outcomes in `tests/unit/reliability/test_admission.py`
- [ ] T030 [P] [US1] Add tenant-quota enforcement unit tests for submitted work, active work, retry volume, recovery work, and operational-action budgets in `tests/unit/reliability/test_quotas.py`
- [ ] T031 [P] [US1] Add fair scheduling unit tests for weighted tenant shares, fairness debt repayment, burst debt, and starvation prevention in `tests/unit/reliability/test_fairness.py`
- [ ] T032 [P] [US1] Add autoscaling and database pool pressure unit tests for scale-out, scale-in, and blocked scale-out decisions in `tests/unit/reliability/test_autoscaling.py`
- [ ] T033 [P] [US1] Add API integration tests for admission-decision search and dashboard overload status responses in `tests/integration/api/test_reliability_controls_api.py`
- [ ] T034 [P] [US1] Create the deterministic reliability load-test harness with seed, tenant distribution, workload mix, policy versions, pool settings, worker counts, latency stats, and artifact refs in `tests/performance/reliability/harness.py`
- [ ] T035 [P] [US1] Add mixed lifecycle load profile for 5,000 active users across 50 tenants in `tests/performance/reliability/test_mixed_lifecycle_load.py`
- [ ] T036 [P] [US1] Add tenant burst fairness profile proving compliant tenants retain at least 95 percent throughput in `tests/performance/reliability/test_tenant_burst_fairness.py`

### Implementation for User Story 1

- [ ] T037 [US1] Implement tenant-aware admission and backpressure decisions in `src/multi_agent_platform/reliability/admission.py`
- [ ] T038 [US1] Implement quota counter reservation, release, denial reasons, and audit-visible quota decisions in `src/multi_agent_platform/reliability/quotas.py`
- [ ] T039 [US1] Implement weighted fair-share scheduling, fairness debt, burst debt, and tenant starvation prevention in `src/multi_agent_platform/reliability/fairness.py`
- [ ] T040 [US1] Implement capacity snapshots and worker autoscaling recommendation rules in `src/multi_agent_platform/reliability/autoscaling.py`
- [ ] T041 [US1] Implement database pool wait and connection-reserve helpers for admission and autoscaling in `src/multi_agent_platform/reliability/pooling.py`
- [ ] T042 [US1] Implement deterministic load profile builders and report metadata capture in `src/multi_agent_platform/reliability/load_profiles.py`
- [ ] T043 [US1] Integrate admission, tenant quotas, eligibility time, and fair scheduling into queue submission and claim ordering in `src/multi_agent_platform/runtime/queue/service.py`
- [ ] T044 [US1] Extend reliability repository writes for atomic quota updates, admission decisions, fairness windows, capacity snapshots, and scaling decisions in `src/multi_agent_platform/db/repositories/reliability.py`
- [ ] T045 [US1] Implement dashboard and admission-decision API responses in `src/multi_agent_platform/api/routers/reliability_controls.py`
- [ ] T046 [US1] Emit metrics and structured trace fields for backpressure, quota, fairness, pool pressure, and scaling decisions in `src/multi_agent_platform/observability/metrics.py`

**Checkpoint**: User Story 1 supports load-aware admission, quotas, fair scheduling, and acceptance load evidence independently.

---

## Phase 4: User Story 2 - Recover Work Safely After Worker Interruptions (Priority: P2)

**Goal**: Recover interrupted work using durable leases, fencing tokens, pinned bundles, checkpoints, and side-effect safety gates.

**Independent Test**: Crash or interrupt workers at required boundaries and verify lease expiry handling, stale write suppression, safe resume, duplicate suppression, compensation/dead-letter/intervention routing, and recovery eligibility within 2x lease timeout.

### Tests for User Story 2

- [ ] T047 [P] [US2] Add lease expiry handling unit tests for renewal deadlines, expiry calculation, stale renewals, and fencing token rejection in `tests/unit/reliability/test_leases.py`
- [ ] T048 [P] [US2] Add side-effect repeatability and duplicate-suppression unit tests for repeatable, non-repeatable, compensatable, and ambiguous side-effect intents in `tests/unit/reliability/test_side_effect_safety.py`
- [ ] T049 [P] [US2] Add PostgreSQL-backed worker recovery integration tests for crashed workers, expired leases, competing recovery, and stale worker return in `tests/integration/runtime/test_reliability_worker_recovery.py`
- [ ] T050 [P] [US2] Add resume-after-failure under load integration tests for all required failure injection points in `tests/integration/runtime/test_resume_after_failure_under_load.py`
- [ ] T051 [P] [US2] Add orchestration worker tests for pinned bundle resume, checkpoint loading, intervention-required outcomes, and suppressed duplicate terminal writes in `tests/integration/workers/test_orchestration_worker.py`

### Implementation for User Story 2

- [ ] T052 [US2] Implement lease policy math, renewal deadlines, expiry eligibility, recovery outcomes, and stale token suppression in `src/multi_agent_platform/reliability/leases.py`
- [ ] T053 [US2] Integrate tuned lease policies and fencing tokens into orchestration lease handling in `src/multi_agent_platform/runtime/orchestration/leasing.py`
- [ ] T054 [US2] Extend runtime repository writes to require worker lease id, claim attempt, bundle digest, policy version, and stale-token rejection in `src/multi_agent_platform/runtime/orchestration/repository.py`
- [ ] T055 [US2] Implement side-effect repeatability metadata gates, non-repeatable defaults, and operator-intervention routing in `src/multi_agent_platform/runtime/orchestration/side_effects.py`
- [ ] T056 [US2] Integrate recovery context loading, pinned bundle validation, checkpoint resume, and recovery outcome recording in `src/multi_agent_platform/workers/orchestration.py`
- [ ] T057 [US2] Extend queue claim and renewal flows for recoverable ownership, active lease uniqueness, terminal run exclusion, and open-breaker-blocked work suppression in `src/multi_agent_platform/runtime/queue/service.py`
- [ ] T058 [US2] Add reliability repository methods for lease heads, recovery attempts, suppressed writes, failure injection records, and recovery inspection summaries in `src/multi_agent_platform/db/repositories/reliability.py`
- [ ] T059 [US2] Add failure injection fixtures for after-claim, after-checkpoint, after-side-effect-intent, after-side-effect-applied-before-state-advance, after-retry-scheduled, during-compensation, and during-artifact-export in `tests/fixtures/reliability.py`

**Checkpoint**: User Story 2 recovers or safely stops interrupted work without duplicate irreversible side effects.

---

## Phase 5: User Story 3 - Control Failures With Circuit Breakers And Compensation (Priority: P3)

**Goal**: Contain repeated failures with retry budgets, circuit breaker state transitions, compensation hooks, dead-letter routing, and artifact throughput controls.

**Independent Test**: Force dependency failures, retry exhaustion, breaker cooldown/probe recovery, compensation success/failure/timeouts, and dead-letter routing, then verify protective decisions and inspectable outcomes.

### Tests for User Story 3

- [ ] T060 [P] [US3] Add retry backoff unit tests for classification, exponential backoff, full jitter bounds, deadlines, max attempts, and tenant retry budget exhaustion in `tests/unit/reliability/test_retries.py`
- [ ] T061 [P] [US3] Add circuit breaker transition unit tests for closed-to-open thresholds, open blocking, cooldown plus probe half-open, half-open success close, half-open failure reopen, and authorized reset audit data in `tests/unit/reliability/test_breakers.py`
- [ ] T062 [P] [US3] Add compensation invocation unit tests for at-most-once automatic requests, manual reattempt authorization, status outcomes, and idempotency in `tests/unit/reliability/test_compensation.py`
- [ ] T063 [P] [US3] Add dead-letter routing unit tests for exhausted retry, unsafe recovery, unavailable compensation, breaker-blocked work, artifact evidence failure, and recommended actions in `tests/unit/reliability/test_dead_letters.py`
- [ ] T064 [P] [US3] Add artifact throughput unit tests for per-tenant/global concurrency, object-store breaker decisions, partial evidence states, and export throttling in `tests/unit/storage/test_throughput.py`
- [ ] T065 [P] [US3] Add artifact throughput integration tests for throttled object storage and large export metadata-only database records in `tests/integration/storage/test_artifact_throughput_controls.py`
- [ ] T066 [P] [US3] Add retry-storm and breaker-transition performance profile for a degraded dependency in `tests/performance/reliability/test_retry_storm_breaker.py`
- [ ] T067 [P] [US3] Add compensation and dead-letter performance profile for success, failure, timeout, and manual-follow-up outcomes in `tests/performance/reliability/test_compensation_dead_letter_load.py`
- [ ] T068 [P] [US3] Add artifact export throughput performance profile for object-storage throttling, metadata-only records, partial states, and export rate limits in `tests/performance/reliability/test_artifact_export_throughput.py`

### Implementation for User Story 3

- [ ] T069 [US3] Implement retry classification, exponential backoff with full jitter, retry budget consumption, deadline stops, and safe stop reasons in `src/multi_agent_platform/reliability/retries.py`
- [ ] T070 [US3] Implement circuit breaker state machine, sample recording, cooldown/probe evidence, half-open trial tokens, blocking decisions, and reset validation in `src/multi_agent_platform/reliability/breakers.py`
- [ ] T071 [US3] Implement compensation request orchestration, at-most-once uniqueness, status transitions, durable work enqueueing, and manual reattempt handling in `src/multi_agent_platform/reliability/compensation.py`
- [ ] T072 [US3] Implement dead-letter creation, safe latest-state summaries, artifact references, recommended actions, and audited operator transitions in `src/multi_agent_platform/reliability/dead_letters.py`
- [ ] T073 [US3] Implement artifact throughput windows, operation budgets, object-store breaker integration, partial/unavailable states, and export rate limits in `src/multi_agent_platform/storage/throughput.py`
- [ ] T074 [US3] Integrate retry scheduling, breaker checks, compensation work, and dead-letter routing into orchestration worker execution in `src/multi_agent_platform/workers/orchestration.py`
- [ ] T075 [US3] Extend reliability repository writes for retry schedules, breaker events, compensation requests, dead-letter records, artifact windows, and operator actions in `src/multi_agent_platform/db/repositories/reliability.py`
- [ ] T076 [US3] Implement retries, breakers, compensations, and dead-letter API responses and action handlers in `src/multi_agent_platform/api/routers/reliability_controls.py`
- [ ] T077 [US3] Emit retry, breaker, compensation, dead-letter, and artifact throughput metrics in `src/multi_agent_platform/observability/metrics.py`

**Checkpoint**: User Story 3 contains repeated failures and exposes compensation/dead-letter outcomes for operators.

---

## Phase 6: User Story 4 - Inspect And Tune Operational Controls (Priority: P4)

**Goal**: Give authorized admins, tenant operators, and auditors safe APIs and admin views for reliability control inspection, tuning, authorization, and auditability.

**Independent Test**: Inspect current reliability state, change scoped controls with authorized actors, verify denied attempts are audited, and filter inspection data by tenant, workflow, failure category, decision, recovery state, quota decision, breaker state, and time range.

### Tests for User Story 4

- [ ] T078 [P] [US4] Add OpenAPI contract tests for all reliability controls endpoints in `tests/contract/test_reliability_controls_contract.py`
- [ ] T079 [P] [US4] Add API authorization tests for global admins, tenant operators, auditors, unauthorized users, denied attempts, and unsafe override validation in `tests/integration/api/test_reliability_controls_api.py`
- [ ] T080 [P] [US4] Add admin UI route tests for dashboard, breaker, and dead-letter pages with empty, partial, delayed, unavailable, and redacted states in `tests/integration/api/test_reliability_controls_ui.py`
- [ ] T081 [P] [US4] Add failure-inspection lookup performance tests seeding failed, delayed, throttled, recovered, and compensation-required runs, then asserting authorized lookup p95 <= 5 seconds in `tests/performance/reliability/test_failure_inspection_lookup.py`

### Implementation for User Story 4

- [ ] T082 [US4] Implement policy list/create, control change validation, unsafe override requirements, and load-test report API handlers in `src/multi_agent_platform/api/routers/reliability_controls.py`
- [ ] T083 [US4] Implement reliability API response models for dashboard, policy, control change, inspection filters, redacted states, and load-test reports in `src/multi_agent_platform/api/schemas/reliability.py`
- [ ] T084 [US4] Implement admin UI route helpers for reliability pages in `src/multi_agent_platform/api/ui/reliability_controls.py`
- [ ] T085 [US4] Add the reliability dashboard admin template with bounded tables and filter controls in `src/multi_agent_platform/web_admin/templates/reliability/index.html`
- [ ] T086 [US4] Add the breaker inspection and reset admin template in `src/multi_agent_platform/web_admin/templates/reliability/breakers.html`
- [ ] T087 [US4] Add the dead-letter inspection and action admin template in `src/multi_agent_platform/web_admin/templates/reliability/dead_letters.html`
- [ ] T088 [US4] Add reliability admin JavaScript for filters, scoped actions, loading states, partial states, and error states in `src/multi_agent_platform/web_admin/static/reliability_controls.js`
- [ ] T089 [US4] Add audit capture for operational control changes, denied attempts, breaker resets, dead-letter actions, and manual compensation retries in `src/multi_agent_platform/audit/service.py`
- [ ] T090 [US4] Implement inspection query windows, p95 lookup support, authorization-aware redaction, and capture-gap states in `src/multi_agent_platform/reliability/service.py`

**Checkpoint**: User Story 4 lets authorized operators inspect and tune controls while preserving auditability and tenant isolation.

---

## Phase 7: User Story 5 - Review Delivery Evidence (Priority: P5)

**Goal**: Provide coverage evidence, PR review notes, testing instructions, README guidance, and docs tests so reviewers can verify and operate the feature.

**Independent Test**: Review delivery materials and confirm they cover load handling, worker recovery, duplicate suppression, retry stop conditions, breaker transitions, compensation outcomes, backpressure, quotas, fairness, failure inspection, authorization failures, audit records, and README guidance.

### Tests for User Story 5

- [ ] T091 [P] [US5] Add documentation coverage tests for reliability operator guidance, testing instructions, PR notes, and required review evidence in `tests/docs/test_reliability_scale_hardening_docs.py`
- [ ] T092 [P] [US5] Add README documentation tests for reliability controls, tuning, quotas, fairness, breaker response, recovery, compensation, and escalation guidance in `tests/docs/test_readme_reliability_scale_hardening.py`
- [ ] T093 [P] [US5] Add incident next-action documentation coverage tests for at least 10 representative reliability incidents in `tests/docs/test_reliability_incident_next_actions.py`

### Implementation for User Story 5

- [ ] T094 [US5] Complete operator guidance for inspecting reliability state, interpreting backpressure and quota decisions, tuning retries and breakers, reviewing recovery and compensation, understanding fairness, and escalating incidents in `docs/reliability-scale-hardening.md`
- [ ] T095 [US5] Complete reviewer testing instructions with commands for load handling, worker interruption recovery, duplicate suppression, retry stop conditions, breaker transitions, compensation outcomes, quotas, fairness, authorization failures, audit records, partial inspection data, and README checks in `docs/reliability-scale-hardening-testing.md`
- [ ] T096 [US5] Complete PR review notes covering scale assumptions, accepted load targets, recovery guarantees, duplicate suppression, retry and breaker thresholds, compensation coverage and gaps, quota and fairness rules, authorization boundaries, auditability, operational risks, and known limitations in `docs/reliability-scale-hardening-pr-notes.md`
- [ ] T097 [US5] Update operator-facing README sections for reliability state inspection, safe tuning, quotas, fairness, breaker events, recovery and compensation outcomes, and unresolved failure escalation in `README.md`
- [ ] T098 [US5] Sync quickstart review evidence commands and report expectations with implemented test paths in `specs/009-reliability-scale-hardening/quickstart.md`
- [ ] T099 [US5] Record coverage, load-test, tenant-burst, resume-after-failure, breaker, compensation, dead-letter, artifact-throughput, README, and docs evidence placeholders in `docs/reliability-scale-hardening-pr-notes.md`

**Checkpoint**: User Story 5 makes the feature review-ready and operable after merge.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Validate quality gates, tighten integration, and record final evidence across all stories.

- [ ] T100 [P] Add or update package exports for reliability modules in `src/multi_agent_platform/reliability/__init__.py`
- [ ] T101 [P] Add final migration rollback/import coverage for reliability metadata registration in `tests/integration/db/test_migration_rollback.py`
- [ ] T102 [P] Add final API schema unit coverage for reliability Pydantic validation and redaction behavior in `tests/unit/api/test_reliability_schemas.py`
- [ ] T103 Run `uv run ruff check .` and record the result in `docs/reliability-scale-hardening-testing.md`
- [ ] T104 Run `uv run ruff format --check .` and record the result in `docs/reliability-scale-hardening-testing.md`
- [ ] T105 Run `uv run mypy src` and record the result in `docs/reliability-scale-hardening-testing.md`
- [ ] T106 Run `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90` and record the coverage result in `docs/reliability-scale-hardening-pr-notes.md`
- [ ] T107 Run focused performance acceptance commands for mixed lifecycle load, tenant burst fairness, resume-after-failure under load, failure-inspection lookup, retry-storm breaker transition, compensation/dead-letter load, and artifact export throughput, then record report artifact refs in `docs/reliability-scale-hardening-pr-notes.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; can start immediately.
- **Phase 2 Foundational**: Depends on Phase 1; blocks all user stories.
- **Phase 3 US1**: Depends on Phase 2; delivers MVP load-aware admission, quotas, and fairness.
- **Phase 4 US2**: Depends on Phase 2 and benefits from US1 queue integration; can be developed in parallel with US3 after foundation if file ownership is coordinated.
- **Phase 5 US3**: Depends on Phase 2 and uses US2 side-effect metadata for full recovery safety; can start with retry/breaker/compensation state machines independently.
- **Phase 6 US4**: Depends on foundational schemas and is most useful after US1-US3 services expose state.
- **Phase 7 US5**: Depends on implemented behavior and test paths from US1-US4.
- **Phase 8 Polish**: Depends on the desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Foundation only. This is the MVP scope.
- **US2 (P2)**: Foundation plus queue/lease integration; independently testable through worker interruption and recovery flows.
- **US3 (P3)**: Foundation plus side-effect metadata for compensation safety; retry and breaker unit work can proceed independently.
- **US4 (P4)**: Foundation plus service state from US1-US3.
- **US5 (P5)**: Delivery evidence depends on completed or nearly completed US1-US4 behavior.

### Within Each User Story

- Write tests first and confirm they fail for missing behavior.
- Implement domain models and state machines before repositories or API handlers.
- Implement repositories before service facades that depend on durable state.
- Implement service facades before API/admin UI integration.
- Complete each story checkpoint before treating the story as done.

---

## Parallel Opportunities

- Setup tasks T004, T005, T006, and T007 can run in parallel after T001-T003 ownership is clear.
- Foundational contract tests T018-T019 and fixture task T027 can run in parallel with schema/model work after task names are agreed.
- US1 test tasks T029-T036 can run in parallel, and implementation tasks T037-T042 can be split across separate reliability modules before queue/API integration.
- US2 test tasks T047-T051 can run in parallel, and implementation tasks T052, T053, T055, and T059 can be split by lease, orchestration, side-effect, and fixture ownership.
- US3 test tasks T060-T068 can run in parallel, and implementation tasks T069-T073 can be split by retry, breaker, compensation, dead-letter, and storage ownership.
- US4 tests T078-T081 can run in parallel, and templates T085-T087 can be built in parallel with API schema/router work.
- US5 docs tests T091-T093 can run in parallel with docs authoring T094-T097 after required headings are agreed.

---

## Parallel Example: User Story 1

```bash
Task: "T029 [US1] Add admission and backpressure unit tests in tests/unit/reliability/test_admission.py"
Task: "T030 [US1] Add tenant-quota enforcement unit tests in tests/unit/reliability/test_quotas.py"
Task: "T031 [US1] Add fair scheduling unit tests in tests/unit/reliability/test_fairness.py"
Task: "T034 [US1] Create load-test harness in tests/performance/reliability/harness.py"
```

## Parallel Example: User Story 2

```bash
Task: "T047 [US2] Add lease expiry handling unit tests in tests/unit/reliability/test_leases.py"
Task: "T048 [US2] Add side-effect safety unit tests in tests/unit/reliability/test_side_effect_safety.py"
Task: "T049 [US2] Add worker recovery integration tests in tests/integration/runtime/test_reliability_worker_recovery.py"
Task: "T050 [US2] Add resume-after-failure under load tests in tests/integration/runtime/test_resume_after_failure_under_load.py"
```

## Parallel Example: User Story 3

```bash
Task: "T060 [US3] Add retry backoff unit tests in tests/unit/reliability/test_retries.py"
Task: "T061 [US3] Add circuit breaker transition unit tests in tests/unit/reliability/test_breakers.py"
Task: "T062 [US3] Add compensation invocation unit tests in tests/unit/reliability/test_compensation.py"
Task: "T063 [US3] Add dead-letter routing unit tests in tests/unit/reliability/test_dead_letters.py"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 setup.
2. Complete Phase 2 foundational schema, repository, schemas, auth, and metrics.
3. Complete Phase 3 US1.
4. Validate US1 with admission, quota, fairness, dashboard, and performance harness tests.
5. Demo load-aware admission and tenant fairness before adding recovery and failure containment.

### Incremental Delivery

1. Add US1 to protect shared capacity under load.
2. Add US2 to make worker ownership and recovery safe.
3. Add US3 to contain repeated failures and side-effect cleanup.
4. Add US4 to expose operator controls and inspection.
5. Add US5 to finalize review evidence, docs, and README guidance.

### Parallel Team Strategy

1. One group owns durable schema, repository, and partitioning tasks T008-T013.
2. One group owns reliability domain/service tasks T014-T016 and observability/replay tasks T023-T026.
3. One group owns API/schema/auth tasks T017-T022.
4. After Phase 2, split by story and file ownership: US1 admission/fairness/load, US2 leases/recovery, US3 retries/breakers/compensation, US4 controls/UI, US5 evidence/docs.

---

## Notes

- Keep all reliability records tenant-scoped unless explicitly global.
- PostgreSQL stores transactional state and metadata only; large evidence, load reports, and replay artifacts use object storage references.
- Policy versions apply prospectively and must be recorded on every decision they govern.
- Unsafe recovery, missing side-effect repeatability metadata, and ambiguous duplicate risk route to operator intervention.
- Every control change, denied access attempt, breaker reset, dead-letter action, and manual compensation retry must be auditable.
