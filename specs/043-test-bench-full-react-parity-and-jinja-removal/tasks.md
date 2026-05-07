# Tasks: Test Bench Full React Parity And Jinja Removal

**Input**: Design documents from `specs/043-test-bench-full-react-parity-and-jinja-removal/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required by the roadmap and feature spec. Add failing or updated tests before each implementation group where practical.

**Organization**: Tasks are grouped by user story so each slice is independently testable while preserving the sequential autopilot run.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the active Spec 043 evidence and route inventory before editing browser handlers.

- [x] T001 Record the active test-bench legacy route/template inventory in specs/043-test-bench-full-react-parity-and-jinja-removal/quickstart.md
- [x] T002 [P] Confirm current React test bench component coverage in frontend/admin/src/components/testBench/TestBenchPage.test.tsx
- [x] T003 [P] Confirm current backend React route coverage in tests/integration/test_admin_react_routes.py
- [x] T004 [P] Confirm current legacy API/browser coverage in tests/integration/api/test_admin_agent_tests_api.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared contracts, redirect helpers, and scanner tests that every story depends on.

- [x] T005 [P] Add legacy-route compatibility contract expectations in tests/contract/test_admin_react_contract.py
- [x] T006 [P] Add test-bench Jinja retirement scanner coverage in tests/unit/admin/test_test_bench_jinja_retirement.py
- [x] T007 [P] Add legacy browser redirect integration tests in tests/integration/api/test_admin_agent_tests_legacy_redirects.py
- [x] T008 Extend safe React test-bench route metadata in src/multi_agent_platform/api/schemas/admin_test_bench.py
- [x] T009 Add reusable safe redirect helpers for /admin/agent-tests/ui routes in src/multi_agent_platform/api/routers/admin_agent_tests.py
- [x] T010 Generate updated React admin TypeScript contracts in frontend/admin/src/api/generated/reactAdminApi.ts
- [x] T011 Update frontend client helpers for legacy-aware test bench URLs in frontend/admin/src/api/client.ts

**Checkpoint**: Redirect contract tests and scanner tests exist before browser route conversion begins.

---

## Phase 3: User Story 1 - Manage Suites And Cases In React (Priority: P1)

**Goal**: Suite list/detail/create/edit, case forms, assertions, and target selection work in React and all old suite/case links redirect safely.

**Independent Test**: Open old suite list, create, suite detail, and case form URLs as an Acme admin and verify React preserves tenant scope, ids, filters, safe summaries, and stale conflict state.

### Tests for User Story 1

- [x] T012 [P] [US1] Add suite list/create/detail redirect assertions in tests/integration/api/test_admin_agent_tests_legacy_redirects.py
- [x] T013 [P] [US1] Add legacy suite and case POST redirect assertions in tests/integration/api/test_admin_agent_tests_legacy_redirects.py
- [x] T014 [P] [US1] Add cross-tenant suite/case direct-link denial assertions in tests/integration/api/test_admin_agent_tests_legacy_redirects.py
- [x] T015 [P] [US1] Add React suite/case query-state tests in frontend/admin/src/components/testBench/TestBenchPage.test.tsx

### Implementation for User Story 1

- [x] T016 [US1] Convert GET /admin/agent-tests/ui to a React redirect in src/multi_agent_platform/api/routers/admin_agent_tests.py
- [x] T017 [US1] Convert GET /admin/agent-tests/ui/suites/new to a React create-suite redirect in src/multi_agent_platform/api/routers/admin_agent_tests.py
- [x] T018 [US1] Convert GET /admin/agent-tests/ui/suites/{suite_id} to a tenant-checked React suite redirect in src/multi_agent_platform/api/routers/admin_agent_tests.py
- [x] T019 [US1] Convert POST /admin/agent-tests/ui/suites to preserve create behavior and redirect to React in src/multi_agent_platform/api/routers/admin_agent_tests.py
- [x] T020 [US1] Convert POST /admin/agent-tests/ui/suites/{suite_id}/cases to preserve create behavior and redirect to React in src/multi_agent_platform/api/routers/admin_agent_tests.py
- [x] T021 [US1] Teach TestBenchPage to honor suite_id, mode, case_id, mutation, and conflict query state in frontend/admin/src/components/testBench/TestBenchPage.tsx
- [x] T022 [US1] Update suite, case, assertion, and target panels for legacy redirect state in frontend/admin/src/components/testBench/SuiteAuthoringPanel.tsx
- [x] T023 [US1] Update responsive wrapping and fixed control sizing for test-bench forms in frontend/admin/src/styles/admin.css

**Checkpoint**: Suite and case management is usable in React from old and new URLs.

---

## Phase 4: User Story 2 - Launch And Monitor Runs In React (Priority: P1)

**Goal**: Run launch, run list, run detail, and progress monitoring work through React and old run links/form posts redirect safely.

**Independent Test**: Launch a mock-mode run from an old suite form POST, follow the old run detail URL, and verify React shows backend-owned progress, target revision, safe mode, idempotency, and blocked side-effect evidence.

### Tests for User Story 2

- [x] T024 [P] [US2] Add legacy run launch POST redirect tests in tests/integration/api/test_admin_agent_tests_legacy_redirects.py
- [x] T025 [P] [US2] Add old run detail redirect and denied run tests in tests/integration/api/test_admin_agent_tests_legacy_redirects.py
- [x] T026 [P] [US2] Extend mutation fail-closed tests for approved probe denial in tests/integration/test_admin_react_routes.py
- [x] T027 [P] [US2] Add frontend run query/progress behavior tests in frontend/admin/src/components/testBench/TestBenchPage.test.tsx

### Implementation for User Story 2

- [x] T028 [US2] Convert POST /admin/agent-tests/ui/suites/{suite_id}/runs to preserve launch behavior and redirect to React in src/multi_agent_platform/api/routers/admin_agent_tests.py
- [x] T029 [US2] Convert GET /admin/agent-tests/ui/runs/{run_id} to a tenant-checked React run redirect in src/multi_agent_platform/api/routers/admin_agent_tests.py
- [x] T030 [US2] Extend run launch mutation summaries and safe-mode labels in src/multi_agent_platform/testing/agent_bench/react_test_bench.py
- [x] T031 [US2] Update RunLauncherPanel safe-mode messaging in frontend/admin/src/components/testBench/RunLauncherPanel.tsx
- [x] T032 [US2] Update RunProgressPanel for backend-owned polling/manual refresh language and states in frontend/admin/src/components/testBench/RunProgressPanel.tsx
- [x] T033 [US2] Update RunListPanel legacy-open behavior and active run selection in frontend/admin/src/components/testBench/RunListPanel.tsx

**Checkpoint**: Run launch and progress are React-only for browser users.

---

## Phase 5: User Story 3 - Inspect Results, Traces, And Artifacts In React (Priority: P2)

**Goal**: Result summaries, diagnostics, trace steps, artifact metadata, usage, latency, redaction status, and audit references are complete and safe in React.

**Independent Test**: Open passing and failing run details in React, inspect diagnostics and artifact metadata, and verify unsafe raw content is absent.

### Tests for User Story 3

- [x] T034 [P] [US3] Add schema tests for legacy metadata and artifact-only links in tests/unit/api/test_admin_test_bench_schema.py
- [x] T035 [P] [US3] Add service tests for result, trace, artifact, and redaction summaries in tests/unit/admin/test_test_bench_react_service.py
- [x] T036 [P] [US3] Add frontend trace/artifact detail tests in frontend/admin/src/components/testBench/TestBenchPage.test.tsx
- [x] T037 [P] [US3] Extend performance coverage for bounded run/artifact/audit lists in tests/performance/test_bench/test_react_test_bench_queries.py

### Implementation for User Story 3

- [x] T038 [US3] Extend TestRunDetail and ArtifactReferenceSummary contracts in src/multi_agent_platform/api/schemas/admin_test_bench.py
- [x] T039 [US3] Extend safe result and artifact builders in src/multi_agent_platform/testing/agent_bench/react_test_bench.py
- [x] T040 [US3] Update RunDetailPanel result diagnostics in frontend/admin/src/components/testBench/RunDetailPanel.tsx
- [x] T041 [US3] Update TraceAndArtifactPanel metadata-only rendering in frontend/admin/src/components/testBench/TraceAndArtifactPanel.tsx
- [x] T042 [US3] Update TestBenchAuditPanel redaction and audit-unavailable states in frontend/admin/src/components/testBench/TestBenchAuditPanel.tsx

**Checkpoint**: Results, traces, artifacts, and audit evidence render safely without Jinja.

---

## Phase 6: User Story 4 - Prove Publish-Gate And Direct-Link Parity (Priority: P2)

**Goal**: Publish-gate evidence is target-revision-bound, stale evidence is rejected, direct links are safe, and test-bench templates are deleted with evidence.

**Independent Test**: Open gate evidence from React and old links, verify stale/current states, delete templates, and rerun route/scanner tests proving no browser route references `agent_tests` templates.

### Tests for User Story 4

- [x] T043 [P] [US4] Add stale/current publish-gate link assertions in tests/integration/test_admin_react_routes.py
- [x] T044 [P] [US4] Add workflow gate link contract expectations in tests/contract/test_admin_react_contract.py
- [x] T045 [P] [US4] Add no-agent-tests-template assertions in tests/unit/admin/test_test_bench_jinja_retirement.py
- [x] T046 [P] [US4] Update docs tests for React-only test bench links in tests/docs/test_agent_test_bench_docs.py

### Implementation for User Story 4

- [x] T047 [US4] Extend publish-gate evidence links in src/multi_agent_platform/testing/agent_bench/react_test_bench.py
- [x] T048 [US4] Update PublishGateEvidencePanel stale/current evidence display in frontend/admin/src/components/testBench/PublishGateEvidencePanel.tsx
- [x] T049 [US4] Update workflow test-bench link destinations in src/multi_agent_platform/admin/workflow_builder.py
- [x] T050 [US4] Delete test-bench Jinja templates under src/multi_agent_platform/web_admin/templates/agent_tests
- [x] T051 [US4] Remove unused agent test UI view-model imports from src/multi_agent_platform/api/routers/admin_agent_tests.py
- [x] T052 [US4] Update Spec 038 migration inventory references for test bench in specs/038-jinja-surface-inventory-and-deletion-plan/pr_notes.md

**Checkpoint**: Test-bench browser surface is React-only and deletion evidence is present.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, generated assets, QA evidence, and final validation for Spec 043.

- [x] T053 [P] Update test bench docs for React-only browser routes in docs/quickstart.md
- [x] T054 [P] Update agent test bench docs for safe legacy redirects in specs/015-agent-workflow-test-bench/testing-instructions.md
- [x] T055 [P] Create QA env file in specs/043-test-bench-full-react-parity-and-jinja-removal/.env.qa043
- [x] T056 [P] Create backend QA guide in specs/043-test-bench-full-react-parity-and-jinja-removal/qa043.md
- [x] T057 [P] Create UI QA guide in specs/043-test-bench-full-react-parity-and-jinja-removal/qa043_ui.md
- [x] T058 [P] Create user guide in specs/043-test-bench-full-react-parity-and-jinja-removal/qa043_user_guide.md
- [x] T059 [P] Create reviewer PR notes in specs/043-test-bench-full-react-parity-and-jinja-removal/pr_notes.md
- [x] T060 Update validation manifest route hints in specs/_autopilot/react-ui2-roadmap/043-test-bench-full-react-parity-and-jinja-removal/validation.yml
- [x] T061 Run generated TypeScript contract update and check frontend/admin/src/api/generated/reactAdminApi.ts
- [x] T062 Build React assets and update src/multi_agent_platform/web_admin/static/react/manifest.json
- [x] T063 Run focused backend tests listed in specs/043-test-bench-full-react-parity-and-jinja-removal/quickstart.md
- [x] T064 Run frontend tests for src/components/testBench and src/App.test.tsx
- [x] T065 Run QA document validation for specs/043-test-bench-full-react-parity-and-jinja-removal
- [x] T066 Run uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui2-roadmap/043-test-bench-full-react-parity-and-jinja-removal/validation.yml
- [x] T067 Run uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui2-roadmap/043-test-bench-full-react-parity-and-jinja-removal/validation.yml --start-processes
- [x] T068 Inspect the Playwright screenshot under output/playwright/qa043_ui and fix any blank, overlapping, or unsafe UI evidence

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup and blocks all user stories.
- **US1 and US2 (P1)**: Depend on Foundational; can be implemented in either order but must both pass before deletion.
- **US3 and US4 (P2)**: Depend on Foundational; US4 deletion depends on US1 through US3 route and React evidence.
- **Polish**: Depends on all desired user stories and template deletion.

### User Story Dependencies

- **US1**: Can start after Foundational and proves suite/case React parity.
- **US2**: Can start after Foundational and proves run launch/progress React parity.
- **US3**: Can start after US2 data contracts are stable and proves diagnostics/artifact safety.
- **US4**: Depends on US1, US2, and US3 evidence before template deletion.

### Parallel Opportunities

- T002 through T004 can run independently.
- T005 through T007 can be drafted independently before implementation.
- Frontend panel tests can be updated while backend redirect tests are being written.
- QA docs can be drafted after implementation details stabilize, before final validation.

## Implementation Strategy

1. Build the tests and redirect helpers first.
2. Convert legacy browser GET routes to React redirects.
3. Preserve legacy form POST behavior with React redirects or safe problems.
4. Tighten React query-state handling and evidence rendering.
5. Delete only `agent_tests` templates after scanner and route tests prove safety.
6. Generate docs/assets and run full Spec 043 validation before advancing to Spec 044.
