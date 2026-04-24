# Tasks: Durable Orchestration Runtime

**Input**: Design documents from `/specs/004-durable-orchestration-runtime/`
**Prerequisites**: `plan.md` (required), `spec.md` (required), `research.md`,
`data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Test-first tasks are REQUIRED for checkpoint persistence, resume
after crash, worker lease expiry and exclusivity, contract-gated routing,
version-bundle pinning, nested subworkflow lineage, approval pause-resume
behavior, idempotent retry handling, tenant isolation, and retention policy
defaults.

**Organization**: Tasks are grouped by user story to enable independent
implementation, testing, and review.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no direct dependency)
- **[Story]**: Which user story this task belongs to (e.g., `US1`, `US2`,
  `US3`)
- Include exact file paths in every implementation or documentation task

## Constitution-Driven Task Rules

- Include test-first tasks before implementation tasks where practical.
- Include documentation tasks, `README.md` update tasks, quickstart
  validation, PR review guidance, and testing-instruction updates.
- Include explicit tasks for tenant isolation, version pinning, secret and
  tool-policy hygiene, artifact references, approval/resume behavior, side
  effect idempotency, and parent-child lineage because those concerns are in
  scope.
- Include operational validation tasks for background workers, checkpoint
  recovery, lease expiry, metrics, audit events, and retention behavior.
- Keep tasks dependency-ordered, file-specific, and safe for small, reviewable
  changes.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create durable runtime scaffolding, dependency updates, QA
artifacts, and test fixtures needed before shared implementation begins.

- [ ] T001 Create durable runtime source and test scaffolding in `src/multi_agent_platform/runtime/orchestration/__init__.py`, `src/multi_agent_platform/runtime/orchestration/models.py`, `src/multi_agent_platform/runtime/orchestration/state.py`, `src/multi_agent_platform/runtime/orchestration/events.py`, `src/multi_agent_platform/runtime/orchestration/repository.py`, `src/multi_agent_platform/runtime/orchestration/service.py`, `src/multi_agent_platform/runtime/orchestration/checkpointing.py`, `src/multi_agent_platform/runtime/orchestration/leasing.py`, `src/multi_agent_platform/runtime/orchestration/contracts.py`, `src/multi_agent_platform/runtime/orchestration/handoffs.py`, `src/multi_agent_platform/runtime/orchestration/approvals.py`, `src/multi_agent_platform/runtime/orchestration/lineage.py`, `src/multi_agent_platform/runtime/orchestration/side_effects.py`, `src/multi_agent_platform/runtime/orchestration/compiler.py`, `src/multi_agent_platform/api/routers/runtime_runs.py`, `src/multi_agent_platform/api/schemas/runtime_runs.py`, `src/multi_agent_platform/db/models/runtime_orchestration.py`, `src/multi_agent_platform/db/repositories/runtime_orchestration.py`, `src/multi_agent_platform/workers/orchestration.py`, `tests/unit/runtime/orchestration/test_service.py`, `tests/unit/runtime/orchestration/test_leasing.py`, `tests/unit/runtime/orchestration/test_contracts.py`, `tests/unit/runtime/orchestration/test_approvals.py`, `tests/unit/runtime/orchestration/test_lineage.py`, `tests/unit/runtime/orchestration/test_side_effects.py`, `tests/unit/api/test_runtime_run_schemas.py`, `tests/unit/db/test_runtime_orchestration_models.py`, `tests/contract/test_runtime_orchestration_contract.py`, `tests/integration/runtime/test_langgraph_checkpoint_resume.py`, `tests/integration/runtime/test_orchestration_crash_resume.py`, `tests/integration/runtime/test_runtime_api_flows.py`, and `tests/integration/workers/test_orchestration_worker.py`
- [ ] T002 [P] Update LangChain, LangGraph, Postgres checkpointer, and lockfile dependencies in `pyproject.toml` and `uv.lock`
- [ ] T003 [P] Add runtime worker and checkpoint configuration settings in `src/multi_agent_platform/config/settings.py` and `tests/unit/config/test_settings.py`
- [ ] T004 [P] Extend runtime fixtures, fake bundles, fake checkpointer hooks, and local principals in `tests/conftest.py`, `tests/fixtures/config.py`, `tests/fixtures/db.py`, `tests/fixtures/providers.py`, and `tests/fixtures/runtime_orchestration.py`
- [ ] T005 [P] Add QA and Postman testing artifacts for runtime validation in `specs/004-durable-orchestration-runtime/qa004.md`, `specs/004-durable-orchestration-runtime/.env.qa004`, `specs/004-durable-orchestration-runtime/.env.qa003`, and `specs/004-durable-orchestration-runtime/qa004_collection.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared persistence, repository, auth, bundle, worker,
checkpoint, and observability foundations that MUST be complete before any user
story implementation begins.

**CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T006 Add foundational migration and model tests for runtime runs, steps, bundles, checkpoint refs, leases, handoffs, side-effect intents, approvals, lineage, timeline events, and retention metadata in `tests/unit/db/test_runtime_orchestration_models.py` and `tests/integration/db/test_migrations.py`
- [ ] T007 Implement runtime persistence models, metadata registration, and Alembic migration in `src/multi_agent_platform/db/models/runtime_orchestration.py`, `src/multi_agent_platform/db/models/__init__.py`, and `alembic/versions/0004_durable_orchestration_runtime.py`
- [ ] T008 [P] Add repository tests for tenant-scoped writes, row-level lease claiming, checkpoint reference writes, immutable bundle persistence, and retention defaults in `tests/unit/runtime/orchestration/test_repository.py` and `tests/integration/runtime/test_runtime_repository.py`
- [ ] T009 Implement SQLAlchemy repository operations for runtime runs, run steps, bundles, leases, checkpoints, handoffs, side-effect intents, approvals, lineage, timeline events, and retention in `src/multi_agent_platform/db/repositories/runtime_orchestration.py` and `src/multi_agent_platform/runtime/orchestration/repository.py`
- [ ] T010 [P] Add API schema tests for run start, run status, timeline, lineage, handoff, side-effect, approval, cancellation, and error payloads in `tests/unit/api/test_runtime_run_schemas.py`
- [ ] T011 [P] Implement runtime API Pydantic schemas and OpenAPI-aligned error models in `src/multi_agent_platform/api/schemas/runtime_runs.py` and `specs/004-durable-orchestration-runtime/contracts/runtime-orchestration.openapi.yaml`
- [ ] T012 [P] Add version-bundle pinning tests for immutable per-run bundle cloning, bundle digest verification, and resume using the original bundle in `tests/unit/runtime/orchestration/test_service.py` and `tests/unit/runtime/test_versioning.py`
- [ ] T013 Implement execution bundle cloning and compatibility checks in `src/multi_agent_platform/runtime/orchestration/compiler.py`, `src/multi_agent_platform/runtime/workflow_bundle.py`, `src/multi_agent_platform/runtime/versioning.py`, and `src/multi_agent_platform/admin/workflow_registry/service.py`
- [ ] T014 [P] Add tenant, authorization, quota, delegated-credential, secret-reference, and tool-policy guard tests for runtime actions in `tests/unit/runtime/orchestration/test_service.py`, `tests/integration/runtime/test_runtime_api_flows.py`, and `tests/integration/auth/test_delegated_credentials.py`
- [ ] T015 Implement auth, tenant, quota, delegated-credential, secret-reference, and tool-policy enforcement for runtime start, worker execution, handoff, subworkflow, approval, and cancellation in `src/multi_agent_platform/auth/policy.py`, `src/multi_agent_platform/tenancy/guards.py`, `src/multi_agent_platform/runtime/orchestration/service.py`, `src/multi_agent_platform/runtime/orchestration/side_effects.py`, and `src/multi_agent_platform/api/routers/runtime_runs.py`
- [ ] T016 [P] Add worker loop bootstrap tests for orchestration worker readiness, worker identity, polling, and graceful shutdown in `tests/integration/workers/test_orchestration_worker.py` and `tests/unit/bootstrap/test_worker.py`
- [ ] T017 Implement orchestration worker bootstrap and routing in `src/multi_agent_platform/workers/orchestration.py`, `src/multi_agent_platform/workers/loops.py`, `src/multi_agent_platform/workers/main.py`, and `src/multi_agent_platform/bootstrap/worker.py`
- [ ] T018 [P] Add observability and audit baseline tests for runtime timeline, structured logs, metrics, traces, and access-denial audit events in `tests/unit/runtime/orchestration/test_events.py`, `tests/unit/audit/test_runtime_audit.py`, and `tests/integration/runtime/test_runtime_api_flows.py`
- [ ] T019 Implement runtime timeline events, audit emission, metrics, logs, and trace attributes in `src/multi_agent_platform/runtime/orchestration/events.py`, `src/multi_agent_platform/audit/models.py`, `src/multi_agent_platform/audit/service.py`, `src/multi_agent_platform/observability/logging.py`, `src/multi_agent_platform/observability/metrics.py`, and `src/multi_agent_platform/observability/tracing.py`

**Checkpoint**: Shared durable runtime infrastructure is complete; user story
phases can begin.

---

## Phase 3: User Story 1 - Run Published Workflows Durably (Priority: P1) MVP

**Goal**: Operators can start published workflow runs, workers execute them
with pinned bundles and PostgreSQL checkpoints, and interrupted runs resume
from durable state without duplicating completed side effects.

**Independent Test**: Start a published workflow run, force interruption after
a checkpoint and after side-effect success, restart the worker, and verify the
run resumes from the latest checkpoint with the same bundle digest, same thread
id, and no duplicate externally visible action.

### Tests for User Story 1

> Write these tests first and ensure they fail before implementation.

- [ ] T020 [P] [US1] Add unit tests for run state transitions, terminal-state immutability, retry budget resolution, and idempotency-key generation in `tests/unit/runtime/orchestration/test_service.py`
- [ ] T021 [P] [US1] Add unit tests for worker lease claim exclusivity, renewal, expiry defaults, configured expiry overrides, and duplicate-claim backoff in `tests/unit/runtime/orchestration/test_leasing.py`
- [ ] T022 [P] [US1] Add unit tests for side-effect intent creation, applied-result reuse, compensation-hook selection, and idempotent retry handling in `tests/unit/runtime/orchestration/test_side_effects.py`
- [ ] T023 [P] [US1] Add contract tests for start, inspect, cancel, timeline, handoff list, side-effect list, and error responses in `tests/contract/test_runtime_orchestration_contract.py`
- [ ] T024 [P] [US1] Add PostgreSQL integration tests for LangGraph `AsyncPostgresSaver` setup, checkpoint persistence, checkpoint references, and resume with stable `thread_id` in `tests/integration/runtime/test_langgraph_checkpoint_resume.py`
- [ ] T025 [US1] Add crash-recovery tests for crash after lease claim, crash after checkpoint, crash after side-effect intent creation, crash after side-effect success before ack, stale queued work after terminal state, and resume-after-crash behavior in `tests/integration/runtime/test_orchestration_crash_resume.py`
- [ ] T026 [US1] Add runtime API flow tests for published-only start, missing bundle denial, incompatible bundle denial, tenant authorization denial, quota denial, run inspection, cancellation, and audit events in `tests/integration/runtime/test_runtime_api_flows.py`

### Implementation for User Story 1

- [ ] T027 [P] [US1] Implement runtime domain models, state enums, retry policies, and graph state schema in `src/multi_agent_platform/runtime/orchestration/models.py` and `src/multi_agent_platform/runtime/orchestration/state.py`
- [ ] T028 [P] [US1] Implement worker lease policy, claim renewal, expiry calculation, duplicate-claim backoff, and terminal-run guards in `src/multi_agent_platform/runtime/orchestration/leasing.py`
- [ ] T029 [P] [US1] Implement LangGraph checkpointer adapter, checkpoint compatibility checks, and semantic checkpoint reference recording in `src/multi_agent_platform/runtime/orchestration/checkpointing.py`
- [ ] T030 [P] [US1] Implement side-effect intent planning, applied-result reuse, deterministic idempotency keys, retry transitions, and compensation hook dispatch in `src/multi_agent_platform/runtime/orchestration/side_effects.py`
- [ ] T031 [US1] Implement run start, bundle pinning, initial state persistence, resume orchestration, inspect, cancel, and terminal transitions in `src/multi_agent_platform/runtime/orchestration/service.py`
- [ ] T032 [US1] Implement workflow bundle to LangGraph assembly and graph invocation boundaries in `src/multi_agent_platform/runtime/orchestration/compiler.py` and `src/multi_agent_platform/runtime/orchestration/checkpointing.py`
- [ ] T033 [US1] Implement orchestration worker claim, execute, checkpoint, renew, retry, resume, release, and completion loop in `src/multi_agent_platform/workers/orchestration.py` and `src/multi_agent_platform/workers/loops.py`
- [ ] T034 [US1] Implement runtime JSON API routes for start, inspect, cancel, timeline, side-effects, and handoffs in `src/multi_agent_platform/api/routers/runtime_runs.py` and route registration in `src/multi_agent_platform/api/main.py`
- [ ] T035 [US1] Add run-start, claim, checkpoint, resume, retry, side-effect, cancellation, terminal, and recoverable-failure audit and metrics in `src/multi_agent_platform/runtime/orchestration/events.py`, `src/multi_agent_platform/audit/service.py`, `src/multi_agent_platform/observability/metrics.py`, and `src/multi_agent_platform/observability/tracing.py`

**Checkpoint**: User Story 1 is functional and independently testable.

---

## Phase 4: User Story 2 - Enforce Agent Handoff Contracts (Priority: P2)

**Goal**: Every agent-to-agent handoff is persisted as a versioned envelope,
validated against the pinned contract digest, and routed through the workflow's
declared failure path before any receiver consumes invalid payloads.

**Independent Test**: Execute workflows with valid and invalid handoffs,
confirm valid envelopes are consumed by receivers, invalid envelopes are
blocked with diagnostics, and contract versions remain pinned to the selected
execution bundle.

### Tests for User Story 2

> Write these tests first and ensure they fail before implementation.

- [ ] T036 [P] [US2] Add unit tests for contract schema loading, pinned digest resolution, payload validation, unavailable contract versions, and operator-readable diagnostics in `tests/unit/runtime/orchestration/test_contracts.py`
- [ ] T037 [P] [US2] Add unit tests for handoff envelope lifecycle, valid consumption, invalid rejection, failure-route defaulting, and tenant-scoped payload references in `tests/unit/runtime/orchestration/test_handoffs.py`
- [ ] T038 [P] [US2] Add contract and integration tests proving invalid payloads are blocked before receiver consumption and valid payloads preserve context and lineage in `tests/contract/test_runtime_orchestration_contract.py` and `tests/integration/runtime/test_runtime_api_flows.py`
- [ ] T039 [US2] Add version-bundle pinning tests proving all handoffs use contract versions and digests from the selected run bundle even after registry definitions change in `tests/integration/runtime/test_orchestration_crash_resume.py`

### Implementation for User Story 2

- [ ] T040 [P] [US2] Implement pinned handoff contract validator, digest comparison, structured validation errors, and unavailable-contract handling in `src/multi_agent_platform/runtime/orchestration/contracts.py`
- [ ] T041 [P] [US2] Implement handoff envelope creation, validation, consumption guard, payload hashing, payload reference handling, and failure-route application in `src/multi_agent_platform/runtime/orchestration/handoffs.py`
- [ ] T042 [US2] Integrate contract-gated routing with graph execution and worker resume boundaries in `src/multi_agent_platform/runtime/orchestration/service.py`, `src/multi_agent_platform/runtime/orchestration/compiler.py`, and `src/multi_agent_platform/workers/orchestration.py`
- [ ] T043 [US2] Expose handoff envelope inspection and validation details in `src/multi_agent_platform/api/routers/runtime_runs.py` and `src/multi_agent_platform/api/schemas/runtime_runs.py`
- [ ] T044 [US2] Add handoff-created, handoff-valid, handoff-invalid, failure-route-applied, and receiver-consumed audit and metrics in `src/multi_agent_platform/runtime/orchestration/events.py`, `src/multi_agent_platform/audit/service.py`, and `src/multi_agent_platform/observability/metrics.py`

**Checkpoint**: User Stories 1 and 2 are both independently functional.

---

## Phase 5: User Story 3 - Pause And Resume Approval Gates (Priority: P3)

**Goal**: Workflows pause durably at approval gates, persist approver context,
survive worker restarts while paused, and resume or terminate only after the
first valid authorized decision.

**Independent Test**: Run a workflow that pauses for approval, restart workers
while paused, submit approve and reject decisions, and verify the runtime
continues or terminates from preserved state with the same pinned bundle and
lineage context.

### Tests for User Story 3

> Write these tests first and ensure they fail before implementation.

- [ ] T045 [P] [US3] Add unit tests for approval gate creation, approver policy checks, default no-timeout behavior, explicit timeout behavior, duplicate decisions, late decisions, unauthorized decisions, and first-valid-decision preservation in `tests/unit/runtime/orchestration/test_approvals.py`
- [ ] T046 [P] [US3] Add integration tests for approval pause persistence, worker restart while paused, approve resume, reject termination, and same-thread LangGraph `Command(resume=...)` behavior in `tests/integration/runtime/test_orchestration_crash_resume.py`
- [ ] T047 [P] [US3] Add runtime API tests for approval gate listing, decision submission, rejection conflicts, cancellation while paused, and audit evidence in `tests/integration/runtime/test_runtime_api_flows.py`
- [ ] T048 [US3] Add contract tests for approval-gate and approval-decision request and response shapes in `tests/contract/test_runtime_orchestration_contract.py`

### Implementation for User Story 3

- [ ] T049 [P] [US3] Implement approval gate domain rules, timeout policy resolution, decision acceptance, duplicate rejection, and resume command payload creation in `src/multi_agent_platform/runtime/orchestration/approvals.py`
- [ ] T050 [US3] Integrate LangGraph interrupt wait state and approval resume behavior with worker execution in `src/multi_agent_platform/runtime/orchestration/compiler.py`, `src/multi_agent_platform/runtime/orchestration/service.py`, and `src/multi_agent_platform/workers/orchestration.py`
- [ ] T051 [US3] Implement approval gate listing, approve, reject, cancel, conflict, and authorization route behavior in `src/multi_agent_platform/api/routers/runtime_runs.py` and `src/multi_agent_platform/api/schemas/runtime_runs.py`
- [ ] T052 [US3] Add approval-requested, viewed, approved, rejected, duplicate, denied, timeout, cancelled, and resumed audit and metrics in `src/multi_agent_platform/runtime/orchestration/events.py`, `src/multi_agent_platform/audit/service.py`, and `src/multi_agent_platform/observability/metrics.py`

**Checkpoint**: User Stories 1 through 3 are independently functional.

---

## Phase 6: User Story 4 - Trace Nested Subworkflows (Priority: P4)

**Goal**: Published subworkflows execute as child runs with their own pinned
bundle and LangGraph thread while preserving parent-child lineage, join policy,
status propagation, and cancellation policy.

**Independent Test**: Execute a workflow that starts nested subworkflows,
inspect the run tree from parent and child paths, fail and resume a child run,
and verify parent and child statuses remain consistent.

### Tests for User Story 4

> Write these tests first and ensure they fail before implementation.

- [ ] T053 [P] [US4] Add unit tests for lineage creation, parent-child tenant matching, join policy resolution, child cancellation policy defaulting to cascade-cancel, and lineage retention rules in `tests/unit/runtime/orchestration/test_lineage.py`
- [ ] T054 [P] [US4] Add integration tests for child run creation, child bundle pinning, parent step waiting, child completion, child failure propagation, child pause propagation, parent cancellation cascade, and child resume after crash in `tests/integration/runtime/test_orchestration_crash_resume.py`
- [ ] T055 [P] [US4] Add runtime API tests for lineage traversal from parent to child and child to parent, lineage visibility, cross-tenant denial, and child status inspection in `tests/integration/runtime/test_runtime_api_flows.py`
- [ ] T056 [US4] Add contract tests for lineage endpoint response shape, parent-child edge fields, child bundle digest fields, and run status fields in `tests/contract/test_runtime_orchestration_contract.py`

### Implementation for User Story 4

- [ ] T057 [P] [US4] Implement lineage creation, parent-child relationship rules, join policy handling, status propagation, and retention behavior in `src/multi_agent_platform/runtime/orchestration/lineage.py`
- [ ] T058 [US4] Integrate subworkflow start, child bundle pinning, child worker scheduling, parent waiting, child result envelope validation, and cancellation propagation in `src/multi_agent_platform/runtime/orchestration/service.py`, `src/multi_agent_platform/runtime/orchestration/compiler.py`, and `src/multi_agent_platform/workers/orchestration.py`
- [ ] T059 [US4] Expose lineage traversal and child run inspection through runtime API routes and schemas in `src/multi_agent_platform/api/routers/runtime_runs.py` and `src/multi_agent_platform/api/schemas/runtime_runs.py`
- [ ] T060 [US4] Add child-run-created, child-run-completed, child-run-failed, child-run-paused, parent-waiting, join-resolved, and cascade-cancel audit and metrics in `src/multi_agent_platform/runtime/orchestration/events.py`, `src/multi_agent_platform/audit/service.py`, and `src/multi_agent_platform/observability/metrics.py`

**Checkpoint**: All user stories are independently functional and reviewable.

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Finish documentation, review guidance, QA tooling, coverage,
security, and operational validation work that spans multiple stories.

- [ ] T061 [P] Add operator runtime documentation for worker startup, checkpoint health, crash recovery, lease expiry, contract failures, approval pauses, subworkflow lineage, side-effect intents, and retention behavior in `docs/durable-orchestration-runtime.md`
- [ ] T062 Update repository quickstart and durable runtime feature quickstart with runtime worker commands, run-start examples, crash/resume checks, approval resume examples, and quality gates in `docs/quickstart.md` and `specs/004-durable-orchestration-runtime/quickstart.md`
- [ ] T063 Update README with durable runtime setup, required dependency versions, API examples, worker commands, failure-recovery testing, approval pause-resume, and troubleshooting guidance in `README.md`
- [ ] T064 Update PR review notes and required evidence for durability, worker leases, idempotency, checkpoint compatibility, lineage, approval authorization, tenant isolation, and contract-version pinning in `.github/pull_request_template.md` and `docs/durable-orchestration-runtime.md`
- [ ] T065 [P] Update runtime QA guide, QA env files, and Postman collection with final implemented endpoint names, seed data, expected responses, and troubleshooting notes in `specs/004-durable-orchestration-runtime/qa004.md`, `specs/004-durable-orchestration-runtime/.env.qa004`, `specs/004-durable-orchestration-runtime/.env.qa003`, and `specs/004-durable-orchestration-runtime/qa004_collection.json`
- [ ] T066 [P] Add retention cleanup tests for tenant-specific retention, 90-day checkpoint and run payload defaults, indefinite audit and lineage retention, and safe payload reference cleanup in `tests/unit/runtime/orchestration/test_retention.py` and `tests/integration/runtime/test_runtime_repository.py`
- [ ] T067 Implement retention policy calculation and cleanup job hooks for runtime checkpoints, payload references, audit events, and lineage records in `src/multi_agent_platform/runtime/orchestration/repository.py`, `src/multi_agent_platform/runtime/orchestration/service.py`, and `src/multi_agent_platform/workers/orchestration.py`
- [ ] T068 [P] Add runtime latency/performance tests for the Performance Validation Profile covering run-start, worker-claim, run-inspection, and handoff-validation latency targets from `SC-002`, `SC-010`, `SC-011`, and `SC-012` in `tests/performance/runtime/test_runtime_latency.py`
- [ ] T069 Run and document targeted runtime evidence for checkpoint persistence, resume after crash, worker lease expiry, contract-gated routing, version-bundle pinning, subworkflow lineage, approval pause-resume, idempotent retry handling, and latency targets in `specs/004-durable-orchestration-runtime/quickstart.md` and `docs/durable-orchestration-runtime.md`
- [ ] T070 Run and document quality gates `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src`, and `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90` in `specs/004-durable-orchestration-runtime/quickstart.md` and `docs/durable-orchestration-runtime.md`
- [ ] T071 Complete security review notes for stale credentials on resume, cross-tenant inspection, worker claim scope, secret redaction, payload references, tool allowlists, egress policy, and approval authorization in `docs/durable-orchestration-runtime.md` and `.github/pull_request_template.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup**: No dependencies
- **Phase 2: Foundational**: Depends on Phase 1 and blocks all user stories
- **Phase 3: US1**: Depends on Phase 2 and is the MVP
- **Phase 4: US2**: Depends on US1 because handoff routing needs run state,
  worker execution, pinned bundles, and checkpoint semantics
- **Phase 5: US3**: Depends on US1 and can proceed after the durable run and
  worker foundations exist; it should integrate with US2 where approval routes
  depend on contract failures
- **Phase 6: US4**: Depends on US1 and US2 because child results are delivered
  through contract-compliant envelopes and child runs reuse durable execution
- **Final Phase**: Depends on all targeted user stories being complete

### Within Each User Story

- Tests MUST be written and failing before implementation where practical
- Persistence and schemas come before services
- Services come before API routes and worker integrations
- Checkpoint and idempotency boundaries come before crash-resume behavior
- Story-specific audit, metrics, and documentation evidence are required
  before story completion

### Parallel Opportunities

- **Setup**: `T002`, `T003`, `T004`, and `T005` can run in parallel after
  `T001`
- **Foundational**: `T008`, `T010`, `T012`, `T014`, `T016`, and `T018` can run
  in parallel after `T006`; `T007`, `T009`, `T011`, `T013`, `T015`, `T017`,
  and `T019` follow their corresponding tests
- **US1**: `T020` through `T024` can run in parallel before `T025` and `T026`;
  `T027`, `T028`, `T029`, and `T030` can run in parallel before `T031`
- **US2**: `T036`, `T037`, and `T038` can run in parallel before `T039`;
  `T040` and `T041` can run in parallel before `T042`
- **US3**: `T045`, `T046`, and `T047` can run in parallel before `T048`;
  `T049` can run before `T050`, while `T051` and `T052` follow the service
  behavior
- **US4**: `T053`, `T054`, and `T055` can run in parallel before `T056`;
  `T057` can run before `T058`, while `T059` and `T060` follow service
  behavior
- **Final Phase**: `T061`, `T065`, and `T066` can run in parallel; `T064`
  should follow `T061` because both update
  `docs/durable-orchestration-runtime.md`; `T068` can run once runtime
  performance surfaces exist, while `T069`, `T070`, and `T071` should run after
  implementation evidence exists

---

## Implementation Strategy

### MVP First

1. Complete Phase 1
2. Complete Phase 2
3. Complete User Story 1
4. Validate durable run start, checkpoint persistence, crash resume, worker
   lease expiry, version-bundle pinning, and idempotent retry handling
5. Stop and demo before expanding into handoff contracts, approvals, and
   subworkflow lineage

### Incremental Delivery

1. Finish Setup and Foundational work
2. Deliver User Story 1 and validate durability independently
3. Deliver User Story 2 and validate contract-gated routing independently
4. Deliver User Story 3 and validate approval pause-resume independently
5. Deliver User Story 4 and validate nested subworkflow lineage independently
6. Finish docs, QA collection, README, PR review notes, coverage, and security
   validation

## Notes

- `[P]` markers are used only where tasks touch different files or isolated
  modules and do not depend on incomplete work in the same files.
- User Story 1 is the suggested MVP because it delivers the durable execution
  promise required by every later story.
- The QA guide and Postman collection are part of the feature deliverables so
  reviewers can reproduce runtime behavior without reverse-engineering the
  implementation.
