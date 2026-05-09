# Tasks: Design Review Coordinator And Iteration Loop

**Input**: Design documents from `specs/062-design-review-coordinator-and-iteration-loop/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required. This feature touches design review persistence, runtime
run creation, coordinator decisions, API contracts, tenant scope, redaction, QA,
and curl coverage.

**Organization**: Tasks are grouped by independently testable user stories.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish feature scaffolding, contracts, QA placeholders, and tests.

- [x] T001 Create coordinator service module in `src/multi_agent_platform/admin/design_review/coordinator.py`
- [x] T002 Create focused tests in `tests/unit/admin/design_review/test_design_review_coordinator.py`, `tests/contract/test_design_review_coordinator_contracts.py`, `tests/integration/api/test_admin_design_review_coordinator_api.py`, and `tests/integration/runtime/test_design_review_coordinator_runtime.py`
- [x] T003 Create QA files `specs/062-design-review-coordinator-and-iteration-loop/qa062.md`, `qa062_ui.md`, `.env.qa062`, `qa062_user_guide.md`, and `pr_notes.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add repository/service primitives for coordinator-safe state updates.

- [x] T004 Add design review repository helpers for session status updates, round status updates, active revision lookup, next revision creation, and latest coordinator state in `src/multi_agent_platform/db/repositories/design_review.py`
- [x] T005 Add design review service wrappers that preserve tenant access checks and safe text/digest validation in `src/multi_agent_platform/admin/design_review/service.py`
- [x] T006 Add coordinator domain models and response result models in `src/multi_agent_platform/admin/design_review/models.py`
- [x] T007 [P] Add quorum policy unit tests for four-of-five, three-of-four, blockers, incomplete evidence, and unknown policy in `tests/unit/admin/design_review/test_design_review_coordinator.py`
- [x] T008 [P] Add redaction and unsafe evidence tests for coordinator inputs in `tests/unit/admin/design_review/test_design_review_coordinator.py`

**Checkpoint**: Coordinator support code can update existing durable state safely without launching runtime runs yet.

---

## Phase 3: User Story 1 - Launch A Review Round From A Session (Priority: P1)

**Goal**: Launch exactly one DB-backed runtime run and review round for the active revision.

**Independent Test**: Launch a round for a seeded session and assert one round, one runtime run, assignments, state transition, and idempotent replay.

### Tests for User Story 1

- [x] T009 [P] [US1] Add unit tests for launch success, idempotent replay, terminal-session denial, missing active revision, and max-round denial in `tests/unit/admin/design_review/test_design_review_coordinator.py`
- [x] T010 [P] [US1] Add contract tests for launch request/response schemas in `tests/contract/test_design_review_coordinator_contracts.py`
- [x] T011 [US1] Add API integration tests for launch, replay, and cross-tenant denial in `tests/integration/api/test_admin_design_review_coordinator_api.py`
- [x] T012 [US1] Add runtime integration tests proving launched runs are DB-backed and worker-visible in `tests/integration/runtime/test_design_review_coordinator_runtime.py`

### Implementation for User Story 1

- [x] T013 [US1] Implement `DesignReviewCoordinator.launch_round` with tenant-safe active revision lookup, workflow bundle validation, runtime bundle/run creation, round creation, assignment recording, session status update, and replay handling
- [x] T014 [US1] Add coordinator launch request/response schemas in `src/multi_agent_platform/api/schemas/design_review.py`
- [x] T015 [US1] Add `POST /admin/design-reviews/sessions/{session_id}/coordinator/launch-round` route in `src/multi_agent_platform/api/routers/admin_design_review.py`
- [x] T016 [US1] Add `GET /admin/design-reviews/sessions/{session_id}/coordinator` state projection route in `src/multi_agent_platform/api/routers/admin_design_review.py`

**Checkpoint**: User Story 1 is fully functional and independently testable.

---

## Phase 4: User Story 2 - Evaluate Round Completion And Iterate (Priority: P2)

**Goal**: Record safe verdicts, evaluate quorum, create handoff or next revision, and pause for manual resolution when needed.

**Independent Test**: Complete rounds with approval, revision-required, blockers, incomplete evidence, and max rounds.

### Tests for User Story 2

- [x] T017 [P] [US2] Add unit tests for approval handoff, revision-required next revision, blocker manual resolution, incomplete evidence manual resolution, and max-round manual resolution in `tests/unit/admin/design_review/test_design_review_coordinator.py`
- [x] T018 [P] [US2] Add contract tests for round completion request/response schemas in `tests/contract/test_design_review_coordinator_contracts.py`
- [x] T019 [US2] Add API integration tests for completion approval, revision-required, and replay behavior in `tests/integration/api/test_admin_design_review_coordinator_api.py`
- [x] T020 [US2] Add runtime integration tests that execute a deterministic DB-backed run and then complete coordinator state in `tests/integration/runtime/test_design_review_coordinator_runtime.py`

### Implementation for User Story 2

- [x] T021 [US2] Implement `DesignReviewCoordinator.complete_round` verdict recording, quorum evaluation, handoff creation, next revision creation, manual-resolution pause, and replay handling
- [x] T022 [US2] Add round completion schemas in `src/multi_agent_platform/api/schemas/design_review.py`
- [x] T023 [US2] Add `POST /admin/design-reviews/rounds/{round_id}/coordinator/complete` route in `src/multi_agent_platform/api/routers/admin_design_review.py`
- [x] T024 [US2] Add safe audit records for coordinator launch and completion actions in `src/multi_agent_platform/api/routers/admin_design_review.py`

**Checkpoint**: User Stories 1 and 2 are functional and tenant-safe.

---

## Phase 5: User Story 3 - Apply Durable Manual Decisions (Priority: P3)

**Goal**: Apply revise, approve-exception, retry, and cancel manual decisions to coordinator state.

**Independent Test**: Record each manual decision and verify state side effects and idempotency.

### Tests for User Story 3

- [x] T025 [P] [US3] Add unit tests for manual revise, approve-exception, retry, cancel, and replay behavior in `tests/unit/admin/design_review/test_design_review_coordinator.py`
- [x] T026 [P] [US3] Add contract tests for manual coordinator decision schemas in `tests/contract/test_design_review_coordinator_contracts.py`
- [x] T027 [US3] Add API integration tests for manual decisions and cross-tenant denial in `tests/integration/api/test_admin_design_review_coordinator_api.py`

### Implementation for User Story 3

- [x] T028 [US3] Implement `DesignReviewCoordinator.apply_manual_decision` with durable manual-decision creation and session side effects
- [x] T029 [US3] Add manual coordinator decision schemas in `src/multi_agent_platform/api/schemas/design_review.py`
- [x] T030 [US3] Add `POST /admin/design-reviews/sessions/{session_id}/coordinator/manual-decisions` route in `src/multi_agent_platform/api/routers/admin_design_review.py`
- [x] T031 [US3] Ensure existing manual-decision routes remain compatible and deterministic

**Checkpoint**: All coordinator user stories are functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: QA, curl coverage, generated evidence, docs, and validation readiness.

- [x] T032 Add QA seed and verifier scripts in `scripts/qa/seed_design_review_coordinator_qa062.py` and `scripts/qa/verify_design_review_coordinator_qa062.py`
- [x] T033 Update `specs/_autopilot/scenario-enhancement-roadmap/062-design-review-coordinator-and-iteration-loop/validation.yml` with QA seed/verifier commands
- [x] T034 Update `curl_testing.md` with coordinator launch, state, completion, manual-decision, and denial commands
- [x] T035 Complete QA docs in `qa062.md`, `qa062_ui.md`, `.env.qa062`, `qa062_user_guide.md`, and `pr_notes.md`
- [x] T036 Run focused backend validation for coordinator modules and tests, then fix failures in touched files
- [x] T037 Run QA document validation for `specs/062-design-review-coordinator-and-iteration-loop`
- [x] T038 Run `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/scenario-enhancement-roadmap/062-design-review-coordinator-and-iteration-loop/validation.yml`
- [x] T039 Run `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/scenario-enhancement-roadmap/062-design-review-coordinator-and-iteration-loop/validation.yml --start-processes`
- [x] T040 Run `uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa062-after-spec`

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 has no dependencies.
- Phase 2 depends on Phase 1 and blocks all user stories.
- User Story 1 depends on Phase 2 and is the MVP.
- User Story 2 depends on User Story 1.
- User Story 3 depends on User Story 2.
- Phase 6 depends on all selected user stories.

### Parallel Opportunities

- T007 and T008 can run in parallel after scaffolding.
- T009-T012 can run in parallel before T013-T016.
- T017-T020 can run in parallel before T021-T024.
- T025-T027 can run in parallel before T028-T031.
- QA docs can proceed after route contracts stabilize.

## Implementation Strategy

1. Extend repository/service primitives for safe coordinator state updates.
2. Implement coordinator launch with DB-backed runtime run creation and idempotency.
3. Implement quorum evaluation, handoff creation, and revision loop semantics.
4. Implement manual-resolution actions.
5. Add API routes, schemas, QA scripts/docs, curl coverage, and required validation.
