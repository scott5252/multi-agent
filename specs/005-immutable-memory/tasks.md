# Tasks: Immutable Versioned Memory

**Input**: Design documents from `/specs/005-immutable-memory/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md
**Tests**: Required. The user explicitly requested TDD-friendly tasks and focused coverage for append-only writes, head resolution, lineage integrity, concurrent writes, retrieval filters, audit views, and tenant-scoped access behavior.
**Organization**: Tasks are grouped by user story so each story can be implemented and validated as an independent increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with other marked tasks in the same phase because it touches different files or test scopes.
- **[Story]**: Maps implementation work to the user stories in `specs/005-immutable-memory/spec.md`.
- Every task includes at least one concrete file path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the memory package, test locations, and delivery artifact placeholders used by every story.

- [ ] T001 Create memory package modules and package exports in src/multi_agent_platform/memory/__init__.py
- [ ] T002 [P] Create memory unit test package scaffolding in tests/unit/memory/__init__.py
- [ ] T003 [P] Create memory API contract test placeholder in tests/contract/test_memory_contract.py
- [ ] T004 [P] Create memory integration test placeholders in tests/integration/api/test_memory_api.py and tests/integration/runtime/test_runtime_memory_flows.py
- [ ] T005 [P] Create immutable memory documentation placeholders in docs/immutable-memory.md and specs/005-immutable-memory/pr-review-notes.md
- [ ] T006 [P] Create reviewer testing-instructions placeholder in specs/005-immutable-memory/testing-instructions.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish canonical JSON, domain types, database schema, and shared repository contracts that all memory stories depend on.

**Critical**: No user story work should begin until this phase is complete.

### Tests First

- [ ] T007 [P] Add canonical JSON unit tests for deterministic ordering, SHA-256 stability, explicit nulls, explicit removal markers, unsupported values, and byte-size calculation in tests/unit/memory/test_canonical.py
- [ ] T008 [P] Add domain model unit tests for scope normalization, write precondition validation, conflict errors, runtime source validation, and audit result enums in tests/unit/memory/test_models.py
- [ ] T009 [P] Add SQLAlchemy model unit tests for scope uniqueness, version sequence constraints, head uniqueness, idempotency uniqueness, and append-only archive event validation in tests/unit/db/test_memory_models.py
- [ ] T010 [P] Add migration integration tests for memory tables, indexes, foreign keys, and update/delete trigger rejection on memory_versions in tests/integration/db/test_memory_migration.py

### Implementation

- [ ] T011 Implement canonical JSON serialization, removal marker handling, content hashing, and size helpers in src/multi_agent_platform/memory/canonical.py
- [ ] T012 Implement memory domain dataclasses, request/result models, enums, and exceptions in src/multi_agent_platform/memory/models.py
- [ ] T013 Implement SQLAlchemy models for memory_scopes, memory_versions, memory_heads, and memory_audit_events in src/multi_agent_platform/db/models/memory.py
- [ ] T014 Register memory SQLAlchemy models in src/multi_agent_platform/db/models/__init__.py
- [ ] T015 Create Alembic migration for memory tables, tenant indexes, lineage indexes, idempotency constraint, append-only memory_archive_events table, and memory_versions immutability trigger in alembic/versions/0005_immutable_memory.py
- [ ] T016 Define the service-facing memory repository protocol in src/multi_agent_platform/memory/repository.py

**Checkpoint**: Canonical JSON, domain validation, and database schema are ready for story implementation.

---

## Phase 3: User Story 1 - Preserve Every Memory Change (Priority: P1) MVP

**Goal**: Every authorized memory write creates a new immutable version with preserved content and prior-version lineage.

**Independent Test**: Create an initial memory version, create a successor, retrieve both versions, and verify the first version content, metadata, hash, sequence, and lineage are unchanged.

### Tests for User Story 1

> Write these tests first and confirm they fail before implementation.

- [ ] T017 [P] [US1] Add contract tests for POST /memory/versions initial and non-initial writes with append-only version responses in tests/contract/test_memory_contract.py
- [ ] T018 [P] [US1] Add service tests for append-only initial writes, successor writes, immutable prior content, content hashes, and required preconditions in tests/unit/memory/test_service.py
- [ ] T019 [P] [US1] Add repository tests for transactional version insert, previous_memory_version_id linkage, monotonically increasing version_sequence, and idempotent retry behavior in tests/unit/memory/test_repository.py
- [ ] T020 [P] [US1] Add API integration tests that create two versions and retrieve both without prior-version mutation in tests/integration/api/test_memory_api.py

### Implementation for User Story 1

- [ ] T021 [US1] Implement transactional scope resolution, initial write, successor write, idempotency lookup, version retrieval, and append-only conflict errors in src/multi_agent_platform/db/repositories/memory.py
- [ ] T022 [US1] Implement MemoryService write_version and get_version behavior with canonical content, expected-head validation, lineage metadata, and immutable result objects in src/multi_agent_platform/memory/service.py
- [ ] T023 [US1] Implement MemoryWriteRequest, MemoryWriteResponse, MemoryVersionResponse, MemoryConflictResponse, and shared schema validators in src/multi_agent_platform/api/schemas/memory.py
- [ ] T024 [US1] Implement POST /memory/versions and GET /memory/versions/{memory_version_id} routes in src/multi_agent_platform/api/routers/memory.py
- [ ] T025 [US1] Wire the memory repository, memory service, and memory router into src/multi_agent_platform/bootstrap/container.py and src/multi_agent_platform/api/main.py
- [ ] T026 [US1] Add focused observability fields for memory write latency, conflict type, scope id, version id, and content hash without raw content in src/multi_agent_platform/observability/logging.py

**Checkpoint**: User Story 1 is functional and independently testable as the MVP.

---

## Phase 4: User Story 2 - Retrieve Current Memory for Execution (Priority: P2)

**Goal**: Workflow execution and API callers can retrieve the current head, receive explicit no-memory results, reject stale writes, and preserve tenant-scoped access.

**Independent Test**: Create several versions for one scope, request the current head, request a missing scope, attempt stale and racing writes, and verify tenant-mismatched callers cannot read or advance the head.

### Tests for User Story 2

> Write these tests first and confirm they fail before implementation.

- [ ] T027 [P] [US2] Add contract tests for GET /memory/head, GET /memory/scopes/{memory_scope_id}/versions, explicit no-memory responses, history pagination, and 409 stale-head responses in tests/contract/test_memory_contract.py
- [ ] T027a [P] [US2] Add runtime memory protocol version and compatibility tests for pinned in-flight runs in tests/contract/test_memory_contract.py
- [ ] T028 [P] [US2] Add policy unit tests for tenant-scoped memory content, history, write, runtime read, and runtime write access decisions in tests/unit/memory/test_policy.py
- [ ] T028a [P] [US2] Add tenant quota and concurrency-budget policy tests for memory read, write, replay, diff, and audit actions in tests/unit/memory/test_policy.py
- [ ] T029 [US2] Add service tests for current-head resolution, missing-head responses, stale expected_current_version_id rejection, history filters, and tenant fail-closed behavior in tests/unit/memory/test_service.py
- [ ] T030 [US2] Add repository tests for head projection updates, list-history cursor filters, include_content behavior, and tenant predicates on every query in tests/unit/memory/test_repository.py
- [ ] T031 [P] [US2] Add PostgreSQL-backed concurrent write tests for racing initial writes, racing successor writes, stale resumed writes, and head rollback safety in tests/integration/db/test_memory_concurrency.py
- [ ] T032 [P] [US2] Add runtime integration tests for get_current_head_for_runtime, no-memory runtime reads, pinned bundle validation, run_step_id links, and tenant-mismatched runtime denial in tests/integration/runtime/test_runtime_memory_flows.py
- [ ] T032a [P] [US2] Add runtime integration tests for child-run memory writes, run_lineage_id persistence, deterministic idempotency-key resume, already-created version return after crash resume, and idempotency conflicts in tests/integration/runtime/test_runtime_memory_flows.py

### Implementation for User Story 2

- [ ] T033 [US2] Implement memory access policy helpers for content, write, history, audit, replay, diff, and runtime context checks in src/multi_agent_platform/memory/policy.py
- [ ] T034 [US2] Extend the memory repository with current-head lookup, head row locking, stale-head conflict detection, history pagination, include_content gating, and tenant predicates in src/multi_agent_platform/db/repositories/memory.py
- [ ] T035 [US2] Extend MemoryService with get_current_head, list_history, get_current_head_for_runtime, write_version_for_runtime, runtime protocol version validation, pinned bundle validation, and runtime idempotency handling in src/multi_agent_platform/memory/service.py
- [ ] T036 [US2] Extend memory API schemas for MemoryHeadResponse, MemoryHistoryResponse, RuntimeSourceRef, cursor fields, and no-memory results in src/multi_agent_platform/api/schemas/memory.py
- [ ] T037 [US2] Implement GET /memory/head and GET /memory/scopes/{memory_scope_id}/versions routes with tenant-aware dependency usage in src/multi_agent_platform/api/routers/memory.py
- [ ] T038 [US2] Integrate the MemoryService runtime facade into orchestration-safe memory calls in src/multi_agent_platform/runtime/orchestration/service.py
- [ ] T039 [US2] Add memory conflict, head read, no-memory, and concurrency metrics without raw content labels in src/multi_agent_platform/observability/metrics.py
- [ ] T040 [US2] Add runtime memory tracing spans with tenant id, workflow lineage id, scope id, version id, run id, bundle digest, and action outcome only in src/multi_agent_platform/observability/tracing.py
- [ ] T040b [US2] Implement tenant memory operation budget checks and fail-closed limit errors in src/multi_agent_platform/memory/policy.py and src/multi_agent_platform/memory/service.py
- [ ] T040c [US2] Add quota, throttling, and noisy-neighbor metrics without raw content labels in src/multi_agent_platform/observability/metrics.py

**Checkpoint**: User Story 2 can be validated through API head retrieval, runtime head retrieval, stale-write rejection, concurrent write tests, and tenant isolation tests.

---

## Phase 5: User Story 3 - Replay and Compare Memory History (Priority: P3)

**Goal**: Reviewers can replay memory to a selected version and compare compatible versions while invalid cross-scope or unauthorized comparisons fail closed.

**Independent Test**: Create a known version chain, replay to version 1 and version 2, diff the two versions, diff identical versions, and reject unrelated or unauthorized version comparisons.

### Tests for User Story 3

> Write these tests first and confirm they fail before implementation.

- [ ] T041 [P] [US3] Add contract tests for GET /memory/versions/{memory_version_id}/replay and POST /memory/diffs success, identical-version, 400 incompatible-lineage, and 404 unauthorized cases in tests/contract/test_memory_contract.py
- [ ] T042 [P] [US3] Add diff unit tests for JSON Pointer additions, removals, changed values, explicit removal markers versus JSON null, arrays, nested objects, and identical snapshots in tests/unit/memory/test_diff.py
- [ ] T043 [P] [US3] Add replay unit tests for lineage reconstruction, target-snapshot return, missing target, unauthorized target, and scope assertion mismatch in tests/unit/memory/test_replay.py
- [ ] T044 [US3] Add service tests for replay authorization, diff authorization, incompatible scopes, audit outcome hooks, and retrieval filter interactions in tests/unit/memory/test_service.py
- [ ] T045 [US3] Add API integration tests for replay, diff, incompatible diff, tenant-mismatched diff denial, and no raw audit leakage from replay/diff responses in tests/integration/api/test_memory_api.py

### Implementation for User Story 3

- [ ] T046 [US3] Implement JSON Pointer diff generation for additions, removals, changes, identical snapshots, arrays, nested objects, and removal markers in src/multi_agent_platform/memory/diff.py
- [ ] T047 [US3] Implement replay result construction and ordered lineage metadata helpers in src/multi_agent_platform/memory/replay.py
- [ ] T048 [US3] Extend the memory repository with version pair loading, lineage window queries, replay target loading, and tenant-scoped incompatible-version detection in src/multi_agent_platform/db/repositories/memory.py
- [ ] T049 [US3] Extend MemoryService with replay_version and diff_versions methods that enforce policy checks and return invalid, not-found, or forbidden outcomes consistently in src/multi_agent_platform/memory/service.py
- [ ] T050 [US3] Extend memory API schemas for MemoryReplayResponse, MemoryDiffRequest, MemoryDiffEntry, and MemoryDiffResponse in src/multi_agent_platform/api/schemas/memory.py
- [ ] T051 [US3] Implement GET /memory/versions/{memory_version_id}/replay and POST /memory/diffs routes in src/multi_agent_platform/api/routers/memory.py

**Checkpoint**: User Story 3 can be validated through replay and diff tests without changing write or current-head behavior.

---

## Phase 6: User Story 4 - Audit and Review Delivery (Priority: P4)

**Goal**: Memory writes and read-oriented actions produce content-free audit evidence, and reviewers receive documentation, testing instructions, README guidance, and PR notes.

**Independent Test**: Create memory versions, retrieve head/history/version, replay, diff, and denied tenant accesses, then inspect audit output and delivery artifacts for required fields, redaction, and coverage evidence.

### Tests for User Story 4

> Write these tests first and confirm they fail before implementation.

- [ ] T052 [P] [US4] Add contract tests for GET /memory/audit filters by scope, version, workflow_run_id, action_type, outcome, limit, diff base/compare version ids, and content-free event shape in tests/contract/test_memory_contract.py
- [ ] T053 [P] [US4] Add service tests that every write, get_head, get_version, list_history, replay, diff, denied, not_found, conflict, and invalid outcome creates redacted audit metadata with no raw content, including both base and compare version ids for diff actions, in tests/unit/memory/test_service.py
- [ ] T054 [P] [US4] Add repository tests for audit event insertion, audit append-only behavior, tenant-scoped filters, action/outcome filters, run/bundle filters, and time ordering in tests/unit/memory/test_repository.py
- [ ] T055 [P] [US4] Add API integration tests for audit views, tenant-scoped audit access, audit-only user behavior, raw content exclusion, and denied access audit records in tests/integration/api/test_memory_api.py

### Implementation for User Story 4

- [ ] T056 [US4] Extend the memory repository with audit event insertion, filtered audit listing, append-only audit safeguards, and denied-scope audit best-effort handling in src/multi_agent_platform/db/repositories/memory.py
- [ ] T057 [US4] Extend MemoryService to record content-free audit events for write, get_head, get_version, list_history, replay, diff, conflict, denied, not_found, and invalid outcomes in src/multi_agent_platform/memory/service.py
- [ ] T058 [US4] Extend memory API schemas for MemoryAuditAction, MemoryAuditEvent, MemoryAuditResponse, diff base/compare version identifiers, and redaction-safe denial details in src/multi_agent_platform/api/schemas/memory.py
- [ ] T059 [US4] Implement GET /memory/audit with tenant-scoped filters and audit-only policy handling in src/multi_agent_platform/api/routers/memory.py
- [ ] T059a [US4] Add service tests that memory write, get_head, list_history, replay, diff, conflict, denied, and invalid outcomes emit content-free workflow timeline/debug events in tests/unit/memory/test_service.py
- [ ] T059b [US4] Implement content-free workflow timeline/debug event emission for memory actions in src/multi_agent_platform/memory/service.py and src/multi_agent_platform/runtime/orchestration/service.py
- [ ] T059c [US4] Document operator debugging paths for memory audit, logs, metrics, traces, and workflow timeline events in docs/immutable-memory.md
- [ ] T060 [US4] Add docs for immutable memory concepts, append-only guarantees, head resolution, replay, diff, audit redaction, tenant isolation, and operational review in docs/immutable-memory.md
- [ ] T061 [US4] Update repository quickstart with immutable memory validation commands, curl examples, and expected results in docs/quickstart.md
- [ ] T062 [US4] Update README current scope, quickstart, operations links, and validation evidence expectations for immutable memory in README.md
- [ ] T063 [US4] Write reviewer testing instructions covering version creation, current-head retrieval, stale-head handling, racing writes, replay, diffing, audit filters, and access behavior in specs/005-immutable-memory/testing-instructions.md
- [ ] T064 [US4] Write PR review notes covering immutability guarantees, lineage behavior, replay and diff behavior, audit coverage, tenant predicates, known risks, and coverage evidence in specs/005-immutable-memory/pr-review-notes.md

**Checkpoint**: User Story 4 provides audit evidence and maintainer-facing delivery artifacts.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validate performance, quality gates, documentation consistency, and final review evidence across all stories.

- [ ] T065 [P] Add performance tests for indexed current-head lookup, latest-100 history lookup, replay, and diff latency targets in tests/performance/memory/test_memory_latency.py
- [ ] T066 [P] Add archive event tests for archived_at, archive_reason, current-head archive protection, append-only archive records, and immutable archived version content in tests/unit/memory/test_archive.py
- [ ] T067 [P] Add security regression tests that assert raw memory content is absent from logs, metrics, traces, and audit responses in tests/unit/memory/test_security_redaction.py
- [ ] T068 Update architecture documentation with memory tables, service boundaries, runtime facade, and audit surfaces in docs/architecture.md
- [ ] T069 Run `uv run ruff check .` and record the result in specs/005-immutable-memory/pr-review-notes.md
- [ ] T070 Run `uv run ruff format --check .` and record the result in specs/005-immutable-memory/pr-review-notes.md
- [ ] T071 Run `uv run mypy src` and record the result in specs/005-immutable-memory/pr-review-notes.md
- [ ] T072 Run focused memory tests and record command output summary in specs/005-immutable-memory/pr-review-notes.md
- [ ] T073 Run `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90` and record coverage evidence in specs/005-immutable-memory/pr-review-notes.md
- [ ] T074 Validate specs/005-immutable-memory/quickstart.md against the implemented API and mirror any corrections into docs/quickstart.md
- [ ] T075 Review specs/005-immutable-memory/tasks.md for completed checkbox state, story traceability, and any implementation follow-up notes before PR handoff

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup and blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational. This is the MVP.
- **User Story 2 (Phase 4)**: Depends on User Story 1 because current-head retrieval and stale-write behavior require persisted versions.
- **User Story 3 (Phase 5)**: Depends on User Story 1 and can proceed alongside late User Story 2 work once version retrieval exists.
- **User Story 4 (Phase 6)**: Depends on the actions from User Stories 1 through 3 so audit evidence covers writes, reads, history, replay, diff, and failures.
- **Polish (Phase 7)**: Depends on all desired user stories.

### User Story Dependencies

- **US1 Preserve Every Memory Change**: Requires Phase 2 only.
- **US2 Retrieve Current Memory for Execution**: Requires US1 version creation and head projection.
- **US3 Replay and Compare Memory History**: Requires US1 version storage and retrieval.
- **US4 Audit and Review Delivery**: Requires US1 through US3 action surfaces for complete audit and reviewer evidence.

### Within Each User Story

- Tests must be written first and should fail before implementation.
- Domain and repository behavior should land before service orchestration.
- Service behavior should land before API route wiring.
- API contract and integration tests should pass before checkpoint completion.
- Audit, logging, metrics, and traces must never include raw memory content.

---

## Parallel Execution Examples

### User Story 1

```bash
# Tests can be prepared together after Phase 2:
Task: "T017 contract tests in tests/contract/test_memory_contract.py"
Task: "T018 service tests in tests/unit/memory/test_service.py"
Task: "T019 repository tests in tests/unit/memory/test_repository.py"
Task: "T020 API integration tests in tests/integration/api/test_memory_api.py"
```

### User Story 2

```bash
# Policy, database concurrency, and runtime tests can be prepared in parallel:
Task: "T028 policy tests in tests/unit/memory/test_policy.py"
Task: "T031 concurrent write tests in tests/integration/db/test_memory_concurrency.py"
Task: "T032 runtime memory flow tests in tests/integration/runtime/test_runtime_memory_flows.py"
```

### User Story 3

```bash
# Diff and replay unit tests are independent:
Task: "T042 diff tests in tests/unit/memory/test_diff.py"
Task: "T043 replay tests in tests/unit/memory/test_replay.py"
```

### User Story 4

```bash
# Audit tests and documentation can start together once audited actions exist:
Task: "T052 audit contract tests in tests/contract/test_memory_contract.py"
Task: "T055 audit integration tests in tests/integration/api/test_memory_api.py"
Task: "T060 docs in docs/immutable-memory.md"
Task: "T064 PR review notes in specs/005-immutable-memory/pr-review-notes.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 tests and implementation for append-only memory writes.
3. Validate with `uv run pytest tests/unit/memory/test_canonical.py tests/unit/memory/test_models.py tests/unit/memory/test_service.py tests/unit/memory/test_repository.py tests/integration/api/test_memory_api.py -q`.
4. Stop and review that prior versions are unchanged and lineage is intact.

### Incremental Delivery

1. Deliver US1 append-only versions and immutable lineage.
2. Add US2 current-head retrieval, stale-head rejection, concurrent-write handling, runtime facade, and tenant-scoped access.
3. Add US3 replay and diff endpoints.
4. Add US4 audit views, documentation, testing instructions, README updates, and PR review notes.
5. Finish Phase 7 quality gates and coverage evidence.

### TDD Focus Areas

- Append-only writes: T018, T019, T020.
- Head resolution: T027, T029, T030, T032.
- Lineage integrity: T018, T019, T043, T047.
- Concurrent writes: T031.
- Retrieval filters: T027, T030, T052, T054.
- Audit views: T052, T053, T054, T055.
- Tenant-scoped access behavior: T028, T029, T032, T045, T055.

---

## Notes

- [P] tasks are safe to run in parallel within their phase when the listed files do not conflict.
- Keep repository queries tenant-predicated, including negative and conflict paths.
- Keep raw memory content out of audit events, logs, metrics, traces, and PR evidence.
- Commit after each phase or after a coherent story checkpoint.
