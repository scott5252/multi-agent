# Tasks: Agent And Workflow Test Bench

**Input**: Design documents from `/Users/scottcornell/src/my-projects/multi-agent/specs/015-agent-workflow-test-bench/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/agent-test-bench.openapi.yaml`, `contracts/admin-agent-test-bench-ui.md`, `quickstart.md`  
**Tests**: Required by the feature specification for suite/case CRUD, sandbox execution modes, side-effect blocking, skill policy enforcement, contract assertions, evaluator assertions, redaction, artifact metadata, usage capture, publish gate integration, unauthorized denial, UI rendering, docs, and 90 percent coverage.

**Organization**: Tasks are grouped by independently testable user stories after shared storage, policy, and sandbox foundations are in place.

## Phase 1: Setup

**Purpose**: Establish feature scaffolding, migration placeholder, and docs-test expectations.

- [x] T001 Create `src/multi_agent_platform/testing/agent_bench/__init__.py`
- [x] T002 [P] Add initial contract coverage for `specs/015-agent-workflow-test-bench/contracts/agent-test-bench.openapi.yaml` in `tests/contract/test_agent_test_bench_contract.py`
- [x] T003 [P] Add docs existence and README expectation tests in `tests/docs/test_agent_test_bench_docs.py`
- [x] T004 [P] Add migration smoke test placeholder for agent test tables in `tests/integration/db/test_agent_tests_migration.py`

---

## Phase 2: Foundational Storage, Schemas, Policy, And Sandbox

**Purpose**: Blocking database, schema, policy, redaction, assertion, and sandbox primitives used by every story.

**Critical**: No user story implementation should start until these tasks are complete.

- [x] T005 Add SQLAlchemy models for suites, cases, assertions, runs, run steps, artifacts, and publication requirements in `src/multi_agent_platform/db/models/agent_tests.py`
- [x] T006 Register agent test models in `src/multi_agent_platform/db/models/__init__.py`
- [x] T007 Add additive Alembic migration for agent test bench tables and indexes in `alembic/versions/0015_agent_workflow_test_bench.py`
- [x] T008 [P] Add unit tests for agent test SQLAlchemy models in `tests/unit/db/test_agent_tests_models.py`
- [x] T009 Implement async repository methods for suites, cases, assertions, runs, steps, artifacts, and publish requirements in `src/multi_agent_platform/db/repositories/agent_tests.py`
- [x] T010 [P] Add repository tests for tenant filtering, revision checks, run evidence lookup, and artifact metadata in `tests/unit/db/test_agent_tests_repository.py`
- [x] T011 Add Pydantic request/response schemas for suites, cases, assertions, runs, run steps, artifacts, and publish gate summaries in `src/multi_agent_platform/api/schemas/agent_tests.py`
- [x] T012 [P] Add schema validation tests for safe modes, target types, thresholds, assertions, fixture redaction fields, and run status values in `tests/unit/api/test_agent_test_schemas.py`
- [x] T013 Add admin policy actions for agent test CRUD, run launch, result read, artifact read, and publish gate management in `src/multi_agent_platform/auth/policy.py`
- [x] T014 Update local-principal QA admin permissions for agent test bench actions in `src/multi_agent_platform/auth/local_principals.py`
- [x] T015 [P] Add protected-surface policy tests for agent test bench actions in `tests/unit/auth/test_agent_test_policy.py`
- [x] T016 Implement domain models and enums for safe modes, targets, statuses, assertions, and result summaries in `src/multi_agent_platform/testing/agent_bench/models.py`
- [x] T017 Implement redaction helpers for fixtures, transcripts, provider metadata, tool payloads, and artifact summaries in `src/multi_agent_platform/testing/agent_bench/redaction.py`
- [x] T018 [P] Add redaction unit tests in `tests/unit/testing/agent_bench/test_redaction.py`
- [x] T019 Implement deterministic assertion evaluation for equals, contains, regex, JSON schema, status, latency, and token usage checks in `src/multi_agent_platform/testing/agent_bench/assertions.py`
- [x] T020 [P] Add deterministic and evaluator assertion unit tests in `tests/unit/testing/agent_bench/test_assertions.py`
- [x] T021 Implement sandbox execution service for mock model, mock tools, mocked real gateway, approved-probe blocking, side-effect decisions, usage summaries, and run-step diagnostics in `src/multi_agent_platform/testing/agent_bench/sandbox.py`
- [x] T022 [P] Add sandbox unit tests for mock model execution, mocked provider execution, side-effect blocking, unapproved real probe rejection, redacted transcripts, and usage capture in `tests/unit/testing/agent_bench/test_sandbox.py`
- [x] T023 Implement high-level agent test bench service orchestration in `src/multi_agent_platform/testing/agent_bench/service.py`
- [x] T024 [P] Add service tests for suite/case CRUD, run creation, idempotency, tenant isolation, artifact metadata, and publication evidence in `tests/unit/testing/agent_bench/test_service.py`

**Checkpoint**: Storage, schemas, auth policy, redaction, assertion evaluation, and sandbox execution are ready for user-story API/UI work.

---

## Phase 3: User Story 1 - Define Reusable Test Suites (Priority: P1)

**Goal**: Admins can create, edit, list, inspect, archive, and restore suites and cases with fixtures, contract shapes, deterministic assertions, evaluator prompts, model/tool mode, and thresholds.

**Independent Test**: A tenant admin creates a suite with two cases and assertions, sees it in API and UI, and a cross-tenant admin cannot access it.

### Tests for User Story 1

- [x] T025 [P] [US1] Add API integration tests for suite CRUD, case CRUD, fixture validation, assertion validation, and tenant isolation in `tests/integration/api/test_admin_agent_tests_api.py`
- [x] T026 [P] [US1] Add UI integration tests for suite index, suite create form, suite detail, case form, validation errors, and tenant isolation in `tests/integration/api/test_admin_agent_tests_api.py`
- [ ] T027 [P] [US1] Add UI view model tests for suite lists, form errors, assertion summaries, and redaction notices in `tests/unit/api/test_agent_test_ui_models.py`

### Implementation for User Story 1

- [x] T028 [US1] Implement suite/case CRUD API routes in `src/multi_agent_platform/api/routers/admin_agent_tests.py`
- [x] T029 [US1] Register the agent test router in `src/multi_agent_platform/api/main.py`
- [x] T030 [US1] Implement UI view models for suite index/detail/forms in `src/multi_agent_platform/api/ui/agent_tests.py`
- [x] T031 [US1] Implement suite index template in `src/multi_agent_platform/web_admin/templates/agent_tests/index.html`
- [x] T032 [US1] Implement suite detail template in `src/multi_agent_platform/web_admin/templates/agent_tests/suite_detail.html`
- [x] T033 [US1] Implement suite form template in `src/multi_agent_platform/web_admin/templates/agent_tests/suite_form.html`
- [x] T034 [US1] Implement case form template in `src/multi_agent_platform/web_admin/templates/agent_tests/case_form.html`
- [x] T035 [US1] Add Agent Tests navigation item to admin shell navigation in `src/multi_agent_platform/api/ui/admin_console.py`

**Checkpoint**: User Story 1 is independently testable through API and browser UI.

---

## Phase 4: User Story 2 - Run Tests In Safe Execution Modes (Priority: P1)

**Goal**: Admins can start runs for suites and targets in mock model, mock tools, real model side-effects-disabled, and approved-probe modes with safe behavior.

**Independent Test**: A tenant admin starts mock and mocked-provider runs, sees durable run state, side-effect blocks, usage capture, and pass/fail status.

### Tests for User Story 2

- [x] T036 [P] [US2] Add API integration tests for run creation, mock model execution, mocked provider execution, unapproved real probe rejection, idempotency, and run listing in `tests/integration/api/test_admin_agent_tests_api.py`
- [x] T037 [P] [US2] Add runtime integration test for model gateway test-bench metadata in `tests/integration/runtime/test_agent_workflow_test_bench_gateway.py`

### Implementation for User Story 2

- [x] T038 [US2] Extend `src/multi_agent_platform/agents/test_bench.py` with workflow test bench gateway invocation metadata helpers
- [x] T039 [US2] Implement run creation and listing API routes in `src/multi_agent_platform/api/routers/admin_agent_tests.py`
- [x] T040 [US2] Add run launch form to `src/multi_agent_platform/web_admin/templates/agent_tests/suite_detail.html`
- [x] T041 [US2] Implement run summary UI component in `src/multi_agent_platform/web_admin/templates/agent_tests/components/result_summary.html`

**Checkpoint**: User Story 2 safe execution modes are independently testable.

---

## Phase 5: User Story 3 - Inspect Results And Diagnostics (Priority: P2)

**Goal**: Admins can inspect step traces, model/provider choices, prompt/profile versions, skill versions, token usage, latency, contract validation, redacted transcripts, artifacts, and pass/fail diagnostics.

**Independent Test**: A failing run shows assertion and contract diagnostics with redacted transcript and artifact metadata.

### Tests for User Story 3

- [x] T042 [P] [US3] Add API integration tests for run detail diagnostics, assertion pass/fail, evaluator pass/fail, contract failures, redacted transcript metadata, and artifact references in `tests/integration/api/test_admin_agent_tests_api.py`
- [x] T043 [P] [US3] Add UI integration tests for run detail page, trace steps, result summary, artifact metadata, and redaction scans in `tests/integration/api/test_admin_agent_tests_api.py`

### Implementation for User Story 3

- [x] T044 [US3] Implement run detail API route in `src/multi_agent_platform/api/routers/admin_agent_tests.py`
- [x] T045 [US3] Implement run detail view model in `src/multi_agent_platform/api/ui/agent_tests.py`
- [x] T046 [US3] Implement run detail template in `src/multi_agent_platform/web_admin/templates/agent_tests/run_detail.html`
- [x] T047 [US3] Implement assertion diagnostics component in `src/multi_agent_platform/web_admin/templates/agent_tests/components/assertions.html`
- [x] T048 [US3] Implement trace steps component in `src/multi_agent_platform/web_admin/templates/agent_tests/components/trace_steps.html`

**Checkpoint**: User Story 3 result diagnostics are independently testable.

---

## Phase 6: User Story 4 - Gate Workflow Publication (Priority: P2)

**Goal**: Workflow publication can require selected suites to pass for the current candidate target version.

**Independent Test**: Publication gate blocks missing/stale/failing evidence and allows current passing evidence.

### Tests for User Story 4

- [x] T049 [P] [US4] Add publish gate unit tests for missing, stale, failing, and current passing test evidence in `tests/unit/admin/test_publish_gate.py`
- [ ] T050 [P] [US4] Add API integration tests for publish requirement CRUD and gate evaluation in `tests/integration/api/test_admin_agent_tests_api.py`
- [ ] T051 [P] [US4] Add workflow publish integration test for required suite evidence in `tests/integration/api/test_admin_workflow_publish_agent_tests.py`

### Implementation for User Story 4

- [x] T052 [US4] Extend publish gate helpers with agent test bench evidence summaries in `src/multi_agent_platform/admin/workflow_registry/publish_gate.py`
- [ ] T053 [US4] Implement publish requirement and gate evaluation routes in `src/multi_agent_platform/api/routers/admin_agent_tests.py`
- [x] T054 [US4] Implement publish gate status component in `src/multi_agent_platform/web_admin/templates/agent_tests/components/gate_status.html`
- [x] T055 [US4] Add gate status to suite detail in `src/multi_agent_platform/web_admin/templates/agent_tests/suite_detail.html`

**Checkpoint**: User Story 4 publish gating is independently testable.

---

## Phase 7: User Story 5 - Review Governance Evidence (Priority: P3)

**Goal**: Admins and auditors can review audit-safe governance evidence, redaction outcomes, usage summaries, tenant isolation, and artifact retention.

**Independent Test**: Auditor-visible summaries contain safe metadata and cross-tenant attempts reveal no protected details.

### Tests for User Story 5

- [ ] T056 [P] [US5] Add governance and auditor read tests for safe summaries, denied cross-tenant access, audit metadata, and retention state in `tests/integration/api/test_admin_agent_tests_api.py`
- [ ] T057 [P] [US5] Add template redaction tests covering raw fixtures, raw prompts, raw provider messages, raw credential values, raw tool payloads, and cross-tenant target names in `tests/integration/api/test_admin_agent_tests_ui.py`

### Implementation for User Story 5

- [ ] T058 [US5] Emit audit-safe events for suite/case changes, run creation, safe-mode decisions, side-effect blocks, run finalization, redaction outcomes, artifacts, and gate decisions in `src/multi_agent_platform/testing/agent_bench/service.py`
- [ ] T059 [US5] Add retention and governance summaries to API responses in `src/multi_agent_platform/api/schemas/agent_tests.py`
- [x] T060 [US5] Render governance and retention summaries in run detail in `src/multi_agent_platform/web_admin/templates/agent_tests/run_detail.html`

**Checkpoint**: User Story 5 governance evidence and redaction behavior are independently testable.

---

## Final Phase: Polish And Cross-Cutting Verification

**Purpose**: Complete docs, QA artifacts, README updates, task tracking, and quality gates.

- [x] T061 [P] Generate QA environment file in `specs/015-agent-workflow-test-bench/.env.qa015`
- [x] T062 [P] Generate manual QA guide in `specs/015-agent-workflow-test-bench/qa015.md`
- [x] T063 [P] Generate browser UI QA walkthrough in `specs/015-agent-workflow-test-bench/qa015_ui.md`
- [x] T064 [P] Generate non-developer manual QA user guide with at least 160 lines in `specs/015-agent-workflow-test-bench/qa015_user_guide.md`
- [x] T065 [P] Add PR review notes in `specs/015-agent-workflow-test-bench/pr-review-notes.md`
- [x] T066 [P] Add testing instructions in `specs/015-agent-workflow-test-bench/testing-instructions.md`
- [x] T067 Update `README.md` with Agent Test Bench admin/API/QA summary
- [x] T068 Update `docs/quickstart.md` with QA015 validation entry
- [x] T069 Run QA document validation with `.specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/015-agent-workflow-test-bench`
- [x] T070 Run API validation with `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/015-agent-workflow-test-bench/validation.yml`
- [x] T071 Run Playwright UI validation with `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/015-agent-workflow-test-bench/validation.yml --start-processes`
- [x] T072 Run quality gates `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src`, and `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`
- [x] T073 Mark completed tasks in `specs/015-agent-workflow-test-bench/tasks.md`

## Dependencies

- Phase 1 must complete before Phase 2.
- Phase 2 must complete before all user stories.
- User Stories 1 and 2 are the MVP and block meaningful result inspection.
- User Story 3 depends on User Story 2 run data.
- User Story 4 depends on User Story 2 current run evidence.
- User Story 5 depends on all prior visible surfaces.
- Final polish depends on all selected implementation stories.

## Parallel Execution Examples

- T002, T003, and T004 can run in parallel after T001.
- T008, T010, T012, T015, T018, T020, T022, and T024 can run in parallel while their paired implementation tasks are developed.
- T025, T026, and T027 can run in parallel once Phase 2 is complete.
- T036 and T037 can run in parallel once User Story 1 API foundations exist.
- T042 and T043 can run in parallel once run creation exists.
- T049, T050, and T051 can run in parallel once run evidence lookup exists.
- T061 through T066 can run in parallel after implementation behavior stabilizes.

## Implementation Strategy

1. Deliver the MVP by completing Phases 1-4: storage, policy, schemas, suite/case CRUD, and safe run creation.
2. Add diagnostics with User Story 3 so failures become actionable.
3. Add publication gates with User Story 4.
4. Complete governance evidence, docs, QA artifacts, and full validation.
