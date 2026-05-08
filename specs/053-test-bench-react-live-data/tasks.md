# Tasks: Test Bench React Live Data

**Input**: Design documents from `specs/053-test-bench-react-live-data/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Required for this live-data migration because the spec must prove empty and seeded live data, Auth0-shaped and local-principal behavior, scanner guardrails, frontend behavior, Playwright, post-UI persistence, and curl validation.

**Organization**: Tasks are grouped by user story to enable independently testable increments.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the Spec 053 validation envelope and baseline test bench work area.

- [x] T001 Reconcile `specs/_autopilot/remove-mock-data-roadmap/053-test-bench-react-live-data/validation.yml` with QA053 test bench route, screenshot, and post-UI persistence expectations
- [x] T002 [P] Create QA env skeleton `specs/053-test-bench-react-live-data/.env.qa053`
- [x] T003 [P] Add reviewer notes skeleton `specs/053-test-bench-react-live-data/pr_notes.md`
- [x] T004 [P] Add QA guide skeleton `specs/053-test-bench-react-live-data/qa053.md`
- [x] T005 [P] Add UI QA guide skeleton `specs/053-test-bench-react-live-data/qa053_ui.md`
- [x] T006 [P] Add manual QA user guide skeleton `specs/053-test-bench-react-live-data/qa053_user_guide.md`
- [x] T007 [P] Add QA seed helper skeleton `scripts/qa/seed_test_bench_qa053.py`
- [x] T008 [P] Add post-UI verification skeleton `scripts/qa/verify_test_bench_qa053.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define shared contracts, repository helpers, fixtures, and scanner boundaries before changing production behavior.

- [x] T009 [P] Add live test bench provenance and empty-state schema expectations in `tests/unit/api/test_admin_test_bench_schema.py`
- [x] T010 [P] Add empty and seeded test bench route contract expectations in `tests/contract/test_admin_react_contract.py`
- [x] T011 [P] Add live-data scanner expectations for QA033/QA043 test bench markers in `tests/unit/admin/test_live_data_inventory_scanner.py`
- [x] T012 [P] Add repository-backed test bench fixture helpers in `tests/fixtures/agent_tests.py`
- [x] T013 Add bounded list/detail helper methods for live projections in `src/multi_agent_platform/db/repositories/agent_tests.py`
- [x] T014 Update `src/multi_agent_platform/api/schemas/admin_test_bench.py` with provenance, empty-state, nullable selected-suite, safe detail, and safe mutation result fields
- [x] T015 Update `scripts/frontend/generate_admin_react_types.py` to emit and validate the new test bench contract fields
- [x] T016 Update `frontend/admin/src/test/testBenchTestData.ts` with test-only empty and seeded fixtures matching generated contracts
- [x] T017 Update `src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py` to classify Spec 053 test bench production routes and allowed test-only fixtures

**Checkpoint**: Test bench contracts and scanner expectations are ready before user-story implementation.

---

## Phase 3: User Story 1 - Review Live Test Bench State (Priority: P1) MVP

**Goal**: Authorized users see live test bench rows or truthful empty states for suites, cases, assertions, launcher metadata, runs, progress, artifacts, publish gates, diagnostics, and audit panels.

**Independent Test**: Empty QA database returns empty/unavailable test bench panels with no QA033/QA043 domain rows; seeded QA database returns only persisted records for the active scope.

### Tests for User Story 1

- [x] T018 [P] [US1] Add unit tests for empty and seeded dashboard projections in `tests/unit/admin/test_test_bench_react_service.py`
- [x] T019 [P] [US1] Add integration tests for tenant, Auth0-shaped, denied, empty, and seeded test bench bootstrap routes in `tests/integration/test_admin_react_routes.py`
- [x] T020 [P] [US1] Add bounded query test for live test bench dashboard projection in `tests/performance/test_bench/test_react_test_bench_queries.py`
- [x] T021 [P] [US1] Add frontend empty/seeded dashboard tests in `frontend/admin/src/components/testBench/TestBenchPage.test.tsx`

### Implementation for User Story 1

- [x] T022 [US1] Replace fixed dashboard aggregation in `src/multi_agent_platform/testing/agent_bench/react_test_bench.py` with async live projection entry points that accept repository/service dependencies, active scope, and principal context
- [x] T023 [US1] Implement suite, case, assertion, target binding, and launcher metadata live projections from `AgentTestRepository` in `src/multi_agent_platform/testing/agent_bench/react_test_bench.py`
- [x] T024 [US1] Implement run list, run detail, progress, and diagnostic live projections from persisted run and run-step records in `src/multi_agent_platform/testing/agent_bench/react_test_bench.py`
- [x] T025 [US1] Implement artifact, publish-gate evidence, and audit empty/unavailable projections in `src/multi_agent_platform/testing/agent_bench/react_test_bench.py`
- [x] T026 [US1] Wire test bench bootstrap, suites, runs, gates, artifacts, and audit endpoints to live async projections in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T027 [US1] Preserve test bench route authorization surfaces in `src/multi_agent_platform/auth/policy.py`
- [x] T028 [US1] Update `frontend/admin/src/components/testBench/TestBenchPage.tsx` to render empty, unavailable, denied, and live provenance states without assuming fixed suites or runs
- [x] T029 [US1] Update test bench panels in `frontend/admin/src/components/testBench/TestBenchDashboardPanel.tsx`, `frontend/admin/src/components/testBench/SuiteListPanel.tsx`, `frontend/admin/src/components/testBench/SuiteAuthoringPanel.tsx`, `frontend/admin/src/components/testBench/RunListPanel.tsx`, `frontend/admin/src/components/testBench/RunProgressPanel.tsx`, `frontend/admin/src/components/testBench/RunDetailPanel.tsx`, `frontend/admin/src/components/testBench/TraceAndArtifactPanel.tsx`, `frontend/admin/src/components/testBench/PublishGateEvidencePanel.tsx`, and `frontend/admin/src/components/testBench/TestBenchAuditPanel.tsx`

**Checkpoint**: User Story 1 can be validated independently through backend route tests and frontend empty/seeded rendering tests.

---

## Phase 4: User Story 2 - Inspect Redaction-Safe Test Evidence (Priority: P2)

**Goal**: Test bench detail panels show redaction-safe suite, case, assertion, run, diagnostic, artifact, publish-gate, and audit evidence without raw protected content.

**Independent Test**: Seeded records containing sensitive-adjacent values render safe summaries only; unsafe markers are rejected or summarized before reaching React.

### Tests for User Story 2

- [x] T030 [P] [US2] Add schema safety tests for unsafe test bench text and route paths in `tests/unit/api/test_admin_test_bench_schema.py`
- [x] T031 [P] [US2] Add service tests for safe suite/case summaries, run diagnostics, trace summaries, artifact metadata, publish-gate evidence, and audit safety in `tests/unit/admin/test_test_bench_react_service.py`
- [x] T032 [P] [US2] Add route tests for safe detail endpoints and redaction behavior in `tests/integration/test_admin_react_routes.py`
- [x] T033 [P] [US2] Add frontend panel safety tests in `frontend/admin/src/components/testBench/AssertionAndTargetPanel.test.tsx`, `frontend/admin/src/components/testBench/RunDetailPanel.test.tsx`, `frontend/admin/src/components/testBench/TraceAndArtifactPanel.test.tsx`, `frontend/admin/src/components/testBench/PublishGateEvidencePanel.test.tsx`, and `frontend/admin/src/components/testBench/TestBenchAuditPanel.test.tsx`

### Implementation for User Story 2

- [x] T034 [US2] Implement safe suite, case, assertion, fixture, and expected-contract detail projections in `src/multi_agent_platform/testing/agent_bench/react_test_bench.py`
- [x] T035 [US2] Implement run diagnostic, trace, assertion-result, blocked-side-effect, and redaction summary projections in `src/multi_agent_platform/testing/agent_bench/react_test_bench.py`
- [x] T036 [US2] Implement artifact reference projection from persisted safe metadata in `src/multi_agent_platform/testing/agent_bench/react_test_bench.py`
- [x] T037 [US2] Implement current-revision publish-gate evidence projection from persisted publication requirements and latest qualifying runs in `src/multi_agent_platform/testing/agent_bench/react_test_bench.py`
- [x] T038 [US2] Implement test bench audit timeline projection with bounded safe audit summaries in `src/multi_agent_platform/testing/agent_bench/react_test_bench.py`
- [x] T039 [US2] Regenerate generated TypeScript test bench contracts in `frontend/admin/src/api/generated/reactAdminApi.ts`

**Checkpoint**: User Story 2 can be validated independently by seeded safe-detail API tests and frontend panel tests.

---

## Phase 5: User Story 3 - Exercise Durable Test Bench Actions (Priority: P3)

**Goal**: At least one safe user-visible test bench action persists through backend services and is verified after UI execution.

**Independent Test**: The UI saves suite/case metadata, launches a mocked-safe run, or refreshes gate evidence; the backend returns persisted evidence and the saved state is visible through API/database evidence after refresh.

### Tests for User Story 3

- [x] T040 [P] [US3] Add service tests for suite save, case save, run launch, gate refresh, stale conflict, unavailable, and denied action behavior in `tests/unit/admin/test_test_bench_react_service.py`
- [x] T041 [P] [US3] Add integration route tests for safe test bench mutations, tenant-scoped actions, stale conflicts, and cross-tenant denial in `tests/integration/test_admin_react_routes.py`
- [x] T042 [P] [US3] Add frontend mutation tests in `frontend/admin/src/components/testBench/TestBenchPage.test.tsx`, `frontend/admin/src/components/testBench/SuiteAuthoringPanel.test.tsx`, `frontend/admin/src/components/testBench/RunLauncherPanel.test.tsx`, and `frontend/admin/src/components/testBench/PublishGateEvidencePanel.test.tsx`

### Implementation for User Story 3

- [x] T043 [US3] Implement durable suite save mutation through `AgentTestBenchService` in `src/multi_agent_platform/testing/agent_bench/react_test_bench.py`
- [x] T044 [US3] Implement durable case save mutation through `AgentTestBenchService` in `src/multi_agent_platform/testing/agent_bench/react_test_bench.py`
- [x] T045 [US3] Implement mocked-safe run launch mutation through `AgentTestBenchService` and persisted run/step projection in `src/multi_agent_platform/testing/agent_bench/react_test_bench.py`
- [x] T046 [US3] Implement publish-gate refresh mutation result from repository-backed evidence in `src/multi_agent_platform/testing/agent_bench/react_test_bench.py`
- [x] T047 [US3] Wire suite, case, run, and gate mutation routes to live async service-backed results in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T048 [US3] Update test bench API client helpers in `frontend/admin/src/api/client.ts`
- [x] T049 [US3] Wire mutation result, stale conflict, refresh, and field-error handling in `frontend/admin/src/components/testBench/TestBenchPage.tsx`, `frontend/admin/src/components/testBench/SuiteAuthoringPanel.tsx`, `frontend/admin/src/components/testBench/RunLauncherPanel.tsx`, and `frontend/admin/src/components/testBench/PublishGateEvidencePanel.tsx`
- [x] T050 [US3] Run `npm run --prefix frontend/admin build` to rebuild `src/multi_agent_platform/web_admin/static/react/manifest.json` and asset files under `src/multi_agent_platform/web_admin/static/react/assets/`

**Checkpoint**: User Story 3 can be validated independently by a safe UI action, API/database persistence proof, and frontend mutation tests.

---

## Phase 6: Polish & Cross-Cutting Validation

**Purpose**: Documentation, scanners, generated contracts, and mandatory post-spec validation.

- [x] T051 [P] Finalize `specs/053-test-bench-react-live-data/qa053.md`
- [x] T052 [P] Finalize `specs/053-test-bench-react-live-data/qa053_ui.md`
- [x] T053 [P] Finalize `specs/053-test-bench-react-live-data/qa053_user_guide.md`
- [x] T054 [P] Finalize `specs/053-test-bench-react-live-data/pr_notes.md`
- [x] T055 Finalize QA seed and verification scripts in `scripts/qa/seed_test_bench_qa053.py` and `scripts/qa/verify_test_bench_qa053.py`
- [x] T056 Run `uv run python scripts/frontend/generate_admin_react_types.py --check`
- [x] T057 Run focused backend tests for `tests/unit/api/test_admin_test_bench_schema.py`, `tests/unit/admin/test_test_bench_react_service.py`, `tests/integration/test_admin_react_routes.py`, `tests/contract/test_admin_react_contract.py`, `tests/performance/test_bench/test_react_test_bench_queries.py`, and `tests/unit/admin/test_live_data_inventory_scanner.py`
- [x] T058 Run frontend test bench tests for `frontend/admin/src/components/testBench/*.test.tsx`, `npm run --prefix frontend/admin typecheck`, and `npm run --prefix frontend/admin build`
- [x] T059 Run QA document validation for `specs/053-test-bench-react-live-data`
- [x] T060 Run `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/053-test-bench-react-live-data/validation.yml`
- [x] T061 Run `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/053-test-bench-react-live-data/validation.yml --start-processes`
- [x] T062 Run post-UI API/database verification for test bench mutation persistence and record evidence in `specs/_autopilot/remove-mock-data-roadmap/053-test-bench-react-live-data/status.json`
- [x] T063 Run `uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa053-after-spec`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on setup; blocks all user stories.
- **US1 (Phase 3)**: Depends on foundational tasks; MVP for truthful live/empty test bench state.
- **US2 (Phase 4)**: Depends on foundational tasks and can run after US1 projection shapes are stable.
- **US3 (Phase 5)**: Depends on foundational tasks and the relevant live detail projection helpers from US1/US2.
- **Polish (Phase 6)**: Depends on all selected user stories.

### Parallel Opportunities

- T002-T008 can run in parallel.
- T009-T012 can run in parallel before shared schema/repository implementation.
- T018-T021, T030-T033, and T040-T042 can run in parallel by test file.
- Frontend panel work can run in parallel with backend projection work after generated contract shapes are known.
- Documentation tasks T051-T054 can run in parallel after implementation behavior is settled.

### Implementation Strategy

1. Complete setup and foundational contract/scanner tasks.
2. Deliver US1 first so every test bench page can truthfully render empty and seeded live states.
3. Add US2 safe details without expanding mutation behavior.
4. Add US3 durable safe actions and Playwright persistence proof.
5. Run all validation gates and update status/queue only after every gate passes.

## Notes

- Production code must not return fixed QA033/QA043 test bench rows.
- Test fixtures may keep QA033/QA043 markers only under test-only or historical spec paths.
- Do not commit between tasks or specs during this autopilot run; keep validated changes in the dirty worktree until the user commits at the end.
