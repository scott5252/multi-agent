# Tasks: Workflow Graph Execution And Parallel Sub-Agent Runtime

**Input**: Design documents from `/Users/scottcornell/src/my-projects/multi-agent/specs/020-workflow-graph-execution-parallel-sub-agent-runtime/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/workflow-graph-execution.md`, `quickstart.md`
**Tests**: Required for graph contracts, bundle loading, dependency scheduling,
parallel fan-out, role/sub-agent execution, join policies, partial failures,
checkpoint/resume idempotency, worker integration, tenant isolation, redaction,
Daily Intelligence Briefing, docs, and 90 percent coverage.

## Phase 1: Setup

**Purpose**: Establish graph execution contracts and docs-test expectations.

- [X] T001 Create graph execution module in `src/multi_agent_platform/runtime/orchestration/graph_execution.py`
- [X] T002 [P] Create role executor module in `src/multi_agent_platform/runtime/orchestration/graph_roles.py`
- [X] T003 [P] Create redaction helper module in `src/multi_agent_platform/runtime/orchestration/graph_redaction.py`
- [X] T004 [P] Add contract tests for `specs/020-workflow-graph-execution-parallel-sub-agent-runtime/contracts/workflow-graph-execution.md` in `tests/contract/test_workflow_graph_execution_contract.py`
- [X] T005 [P] Add docs expectation tests in `tests/docs/test_workflow_graph_execution_docs.py`
- [X] T006 [P] Add no-new-migration assertion in `tests/unit/runtime/orchestration/test_graph_execution.py`

---

## Phase 2: Foundational Graph Planning, Redaction, Roles, And Repository

**Purpose**: Blocking contracts and persistence helpers used by every story.

- [X] T007 Implement graph DTOs, validation, and plan builder in `src/multi_agent_platform/runtime/orchestration/graph_execution.py`
- [X] T008 [P] Add graph plan validation tests in `tests/unit/runtime/orchestration/test_graph_execution.py`
- [X] T009 Implement safe graph output redaction in `src/multi_agent_platform/runtime/orchestration/graph_redaction.py`
- [X] T010 [P] Add redaction tests in `tests/unit/runtime/orchestration/test_graph_redaction.py`
- [X] T011 Implement deterministic role executor in `src/multi_agent_platform/runtime/orchestration/graph_roles.py`
- [X] T012 [P] Add role executor tests in `tests/unit/runtime/orchestration/test_graph_roles.py`
- [X] T013 Add runtime repository methods for bundles, run steps, final status, and graph timeline events in `src/multi_agent_platform/db/repositories/runtime_orchestration.py`
- [X] T014 [P] Add repository integration tests in `tests/integration/runtime/test_workflow_graph_execution.py`

**Checkpoint**: Planner, redaction, role execution, and repository persistence are ready.

---

## Phase 3: User Story 1 - Execute Published Workflow Graphs (Priority: P1) MVP

**Goal**: Worker execution advances a published graph from entry node to terminal node with durable evidence.

**Independent Test**: Seed a simple published bundle and runnable run, execute the graph service, and verify run steps, timeline, checkpoints, handoffs, final output, and succeeded status.

### Tests for User Story 1

- [X] T015 [P] [US1] Add simple graph execution tests in `tests/unit/runtime/orchestration/test_graph_execution.py`
- [X] T016 [P] [US1] Add DB-backed simple graph integration test in `tests/integration/runtime/test_workflow_graph_execution.py`

### Implementation for User Story 1

- [X] T017 [US1] Implement graph scheduler and node state persistence in `src/multi_agent_platform/runtime/orchestration/graph_execution.py`
- [X] T018 [US1] Persist safe checkpoints, handoff summaries, and final output references in `src/multi_agent_platform/runtime/orchestration/graph_execution.py`

**Checkpoint**: User Story 1 is independently executable.

---

## Phase 4: User Story 2 - Fan Out Parallel Sub-Agent Branches (Priority: P2)

**Goal**: Independent scout branches execute in the same parallel wave and join before downstream nodes.

**Independent Test**: Execute the Daily Intelligence Briefing graph and verify four scout nodes appear in one wave before focus and synthesis nodes.

### Tests for User Story 2

- [X] T019 [P] [US2] Add Daily Intelligence Briefing graph fixture tests in `tests/unit/runtime/orchestration/test_graph_execution.py`
- [X] T020 [P] [US2] Add DB-backed Daily Intelligence Briefing integration test in `tests/integration/runtime/test_workflow_graph_execution.py`

### Implementation for User Story 2

- [X] T021 [US2] Implement parallel ready-wave execution with `asyncio.gather` in `src/multi_agent_platform/runtime/orchestration/graph_execution.py`
- [X] T022 [US2] Persist wave timeline evidence and branch summaries in `src/multi_agent_platform/runtime/orchestration/graph_execution.py`

**Checkpoint**: User Story 2 parallel fan-out is independently testable.

---

## Phase 5: User Story 3 - Apply Join Policies And Partial Failure Semantics (Priority: P3)

**Goal**: Joins support all_success, quorum, first_success, and manual_resolution with safe partial failure summaries.

**Independent Test**: Evaluate each join policy over branch outcomes and verify downstream scheduling or paused/failure state.

### Tests for User Story 3

- [X] T023 [P] [US3] Add join policy unit tests in `tests/unit/runtime/orchestration/test_graph_execution.py`
- [X] T024 [P] [US3] Add manual-resolution pause integration test in `tests/integration/runtime/test_workflow_graph_execution.py`

### Implementation for User Story 3

- [X] T025 [US3] Implement join policy evaluator in `src/multi_agent_platform/runtime/orchestration/graph_execution.py`
- [X] T026 [US3] Persist partial failure and manual-resolution evidence in `src/multi_agent_platform/runtime/orchestration/graph_execution.py`

**Checkpoint**: User Story 3 join policies are independently testable.

---

## Phase 6: User Story 4 - Preserve Tenant Isolation, Resume Safety, And Redaction (Priority: P4)

**Goal**: Cross-tenant bundle execution fails closed, resume is idempotent, and safe records contain no raw sensitive payloads.

**Independent Test**: Run cross-tenant denial, double-resume, and redaction scans over DB-backed execution records.

### Tests for User Story 4

- [X] T027 [P] [US4] Add tenant-isolation and resume tests in `tests/integration/runtime/test_workflow_graph_execution.py`
- [X] T028 [P] [US4] Add redaction scan tests for step and timeline payloads in `tests/integration/runtime/test_workflow_graph_execution.py`

### Implementation for User Story 4

- [X] T029 [US4] Enforce tenant-compatible bundle loading in `src/multi_agent_platform/runtime/orchestration/graph_execution.py`
- [X] T030 [US4] Reconstruct completed nodes from persisted steps before scheduling in `src/multi_agent_platform/runtime/orchestration/graph_execution.py`

**Checkpoint**: User Story 4 safety behavior is independently testable.

---

## Phase 7: Worker Integration

**Goal**: Claimed DB-backed runs execute through the graph executor.

- [X] T031 [P] Add worker integration tests for claim, success, pause, and safe failure in `tests/integration/workers/test_orchestration_worker.py`
- [X] T032 Integrate `GraphExecutionService` into `src/multi_agent_platform/workers/orchestration.py`
- [X] T033 Add worker result fields for graph execution outcome in `src/multi_agent_platform/workers/orchestration.py`

---

## Final Phase: Polish And Cross-Cutting Verification

- [X] T034 [P] Add performance test for graph scheduling in `tests/performance/runtime/test_workflow_graph_execution_performance.py`
- [X] T035 [P] Generate QA environment file in `specs/020-workflow-graph-execution-parallel-sub-agent-runtime/.env.qa020`
- [X] T036 [P] Generate manual QA guide in `specs/020-workflow-graph-execution-parallel-sub-agent-runtime/qa020.md`
- [X] T037 [P] Generate browser UI QA walkthrough in `specs/020-workflow-graph-execution-parallel-sub-agent-runtime/qa020_ui.md`
- [X] T038 [P] Generate non-developer manual QA user guide with at least 160 lines in `specs/020-workflow-graph-execution-parallel-sub-agent-runtime/qa020_user_guide.md`
- [X] T039 [P] Add PR review notes in `specs/020-workflow-graph-execution-parallel-sub-agent-runtime/pr-review-notes.md`
- [X] T040 [P] Add testing instructions in `specs/020-workflow-graph-execution-parallel-sub-agent-runtime/testing-instructions.md`
- [X] T041 Update `README.md` with Workflow Graph Execution worker/runtime summary
- [X] T042 Update `docs/quickstart.md` with QA020 validation entry
- [X] T043 Run QA document validation with `.specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/020-workflow-graph-execution-parallel-sub-agent-runtime`
- [X] T044 Run API validation with `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/020-workflow-graph-execution-parallel-sub-agent-runtime/validation.yml`
- [X] T045 Run Playwright UI validation with `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/020-workflow-graph-execution-parallel-sub-agent-runtime/validation.yml --start-processes`
- [X] T046 Run quality gates `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src`, and `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`
- [X] T047 Mark completed tasks in `specs/020-workflow-graph-execution-parallel-sub-agent-runtime/tasks.md`

## Dependencies

- Phase 1 must complete before Phase 2.
- Phase 2 blocks all user stories.
- User Story 1 is the MVP and precedes Daily Intelligence Briefing fan-out.
- User Story 2 depends on graph scheduling foundations.
- User Story 3 depends on branch result summaries from User Story 2.
- User Story 4 depends on persisted step reconstruction and bundle loading.
- Worker integration depends on graph service and repository methods.
- Final polish depends on all selected implementation stories.

## Parallel Execution Examples

- T002, T003, T004, T005, and T006 can run in parallel after T001.
- T008, T010, T012, and T014 can run in parallel with their paired implementation tasks.
- T015 and T016 can run in parallel once Phase 2 completes.
- T019 and T020 can run in parallel once the scheduler exists.
- T023 and T024 can run in parallel once branch summaries exist.
- T035 through T040 can run in parallel after behavior stabilizes.

## Implementation Strategy

1. Deliver MVP graph execution by completing Phases 1-3.
2. Add Daily Intelligence Briefing parallel fan-out.
3. Add join policy and partial failure semantics.
4. Add tenant isolation, resume, and redaction hardening.
5. Wire worker integration.
6. Complete docs, QA artifacts, validation, Playwright smoke, and quality gates.
