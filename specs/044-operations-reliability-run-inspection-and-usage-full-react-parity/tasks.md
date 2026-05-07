# Tasks: Operations, Reliability, Run Inspection, And Usage Full React Parity

**Input**: Design documents from `specs/044-operations-reliability-run-inspection-and-usage-full-react-parity/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required by roadmap. Add or update tests before deleting templates.

**Organization**: Tasks are grouped by independently testable user story slices.

## Phase 1: Setup

**Purpose**: Confirm current React coverage and legacy Jinja inventory.

- [x] T001 Record current operations/reliability/run/usage template inventory in quickstart.md
- [x] T002 [P] Confirm operations React route coverage in tests/integration/test_admin_react_routes.py
- [x] T003 [P] Confirm usage React route coverage in tests/integration/test_admin_react_routes.py
- [x] T004 [P] Confirm old browser coverage in tests/integration/api/test_admin_operations_ui.py
- [x] T005 [P] Confirm old reliability browser coverage in tests/integration/api/test_reliability_controls_ui.py
- [x] T006 [P] Confirm old run inspection browser coverage in tests/integration/api/test_admin_run_inspection_ui.py
- [x] T007 [P] Confirm user-facing run browser coverage in tests/integration/api/test_web_run_ui.py
- [x] T008 [P] Confirm old usage browser coverage in tests/integration/api/test_admin_usage_ui.py

---

## Phase 2: Foundational Tests And Contracts

**Purpose**: Add route/scanner proof before conversion and deletion.

- [x] T009 [P] Add Spec 044 legacy route expectations in tests/contract/test_admin_react_contract.py
- [x] T010 [P] Add operations Jinja retirement scanner in tests/unit/admin/test_operations_jinja_retirement.py
- [x] T011 [P] Add legacy operations redirect assertions in tests/integration/api/test_admin_operations_ui.py
- [x] T012 [P] Add legacy reliability redirect assertions in tests/integration/api/test_reliability_controls_ui.py
- [x] T013 [P] Add legacy admin run inspection redirect assertions in tests/integration/api/test_admin_run_inspection_ui.py
- [x] T014 [P] Add legacy user-facing run redirect assertions in tests/integration/api/test_web_run_ui.py
- [x] T015 [P] Add legacy usage redirect assertions in tests/integration/api/test_admin_usage_ui.py
- [x] T016 Add safe legacy redirect helpers for operations/reliability/run/usage browser routers
- [x] T017 Regenerate React admin TypeScript contracts in frontend/admin/src/api/generated/reactAdminApi.ts

**Checkpoint**: Tests and contracts define the deletion-grade route behavior.

---

## Phase 3: User Story 1 - Triage Operations In React

**Goal**: Operations console old links redirect to React operations with filters and safe tenant scope.

### Tests

- [x] T018 [P] [US1] Add old `/admin/operations` redirect and query preservation tests
- [x] T019 [P] [US1] Add tenant denial tests for operations old URLs
- [x] T020 [P] [US1] Add frontend workbench query-state tests in frontend/admin/src/components/workbench

### Implementation

- [x] T021 [US1] Convert GET `/admin/operations` to a React redirect in src/multi_agent_platform/api/routers/admin_operations.py
- [x] T022 [US1] Update operations workbench links from old operations URLs to `/admin/app/operations`
- [x] T023 [US1] Update WorkbenchPage to honor panel, tenant, filter, export, and run query state
- [x] T024 [US1] Update operations docs and migration ledger entries for React-only operations console

**Checkpoint**: Operations triage is React-only for browser users.

---

## Phase 4: User Story 2 - Govern Reliability Actions In React

**Goal**: Reliability index, breaker, dead-letter, and safe action routes map to React operations.

### Tests

- [x] T025 [P] [US2] Add reliability index/breaker/dead-letter redirect tests
- [x] T026 [P] [US2] Add reliability action denial and mutation-result tests
- [x] T027 [P] [US2] Add frontend reliability panel tests in frontend/admin/src/components/workbench

### Implementation

- [x] T028 [US2] Convert reliability browser GET routes to React redirects in src/multi_agent_platform/api/routers/reliability_controls.py
- [x] T029 [US2] Preserve safe reliability query context for panel, tenant, breaker, dead-letter, and filters
- [x] T030 [US2] Update operations/reliability service links to React operations panels
- [x] T031 [US2] Update WorkbenchReliabilityPanel action and unavailable-state rendering

**Checkpoint**: Reliability browser templates are no longer needed.

---

## Phase 5: User Story 3 - Inspect Runs, Replay, And Lineage In React

**Goal**: Admin run search/detail/replay/lineage browser routes redirect to React run debug panels.

### Tests

- [x] T032 [P] [US3] Add old `/admin/runs` search redirect tests
- [x] T033 [P] [US3] Add old admin run detail/replay/lineage redirect tests
- [x] T034 [P] [US3] Add old user-facing `/runs` redirect tests
- [x] T035 [P] [US3] Add cross-tenant run denial tests
- [x] T036 [P] [US3] Add frontend run-debug detail tests in frontend/admin/src/components/workbench
- [x] T037 [P] [US3] Extend performance coverage for bounded run debug and timeline queries

### Implementation

- [x] T038 [US3] Convert admin run inspection browser routes to React redirects in src/multi_agent_platform/api/routers/admin_run_inspection.py
- [x] T039 [US3] Convert user-facing `/runs` browser routes to React channel redirects in src/multi_agent_platform/api/routers/web_run_ui.py
- [x] T040 [US3] Update operations run debug JSON links and old `/admin/runs` references to React destinations
- [x] T041 [US3] Update WorkbenchTimeline for replay, lineage, unavailable, and redaction states
- [x] T042 [US3] Delete old run inspection templates after admin and user-facing route tests pass

**Checkpoint**: Run inspection browser journeys are React-only.

---

## Phase 6: User Story 4 - Review Usage And Exports In React

**Goal**: Usage dashboard and export detail old links redirect to React usage.

### Tests

- [x] T043 [P] [US4] Add old `/admin/usage` redirect and filter preservation tests
- [x] T044 [P] [US4] Add old usage export detail redirect and cross-tenant denial tests
- [x] T045 [P] [US4] Add frontend usage export detail route tests
- [x] T046 [P] [US4] Extend usage export metadata/redaction schema tests

### Implementation

- [x] T047 [US4] Convert usage browser GET routes to React redirects in src/multi_agent_platform/api/routers/admin_usage.py
- [x] T048 [US4] Update usage React export detail handling for legacy query state
- [x] T049 [US4] Update usage docs and references to `/admin/app/usage`
- [x] T050 [US4] Delete old usage templates after redirect and export tests pass

**Checkpoint**: Usage browser journeys are React-only.

---

## Phase 7: Template Deletion And Scanners

**Purpose**: Delete only bounded templates with deletion-grade evidence.

- [x] T051 Delete operations template directory src/multi_agent_platform/web_admin/templates/operations
- [x] T052 Delete reliability template directory src/multi_agent_platform/web_admin/templates/reliability
- [x] T053 Delete run inspection/user-facing run template directory src/multi_agent_platform/web_admin/templates/runs
- [x] T054 Delete usage template directory src/multi_agent_platform/web_admin/templates/usage
- [x] T055 Remove unused TemplateResponse/Jinja imports from converted routers
- [x] T056 Run scanner tests proving no converted router references retired templates

---

## Phase 8: Polish And Validation

- [x] T057 [P] Create `.env.qa044`
- [x] T058 [P] Create `qa044.md`
- [x] T059 [P] Create `qa044_ui.md`
- [x] T060 [P] Create `qa044_user_guide.md`
- [x] T061 [P] Create `pr_notes.md`
- [x] T062 Update Spec 038 migration inventory notes for operations/reliability/run/usage
- [x] T063 Patch validation.yml to use local-principal login and `/admin/app/operations`
- [x] T064 Run generated TypeScript contract check
- [x] T065 Run focused backend tests from quickstart
- [x] T066 Run frontend tests for workbench, usage, and App
- [x] T067 Run QA document validation
- [x] T068 Run `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui2-roadmap/044-operations-reliability-run-inspection-and-usage-full-react-parity/validation.yml`
- [x] T069 Run `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui2-roadmap/044-operations-reliability-run-inspection-and-usage-full-react-parity/validation.yml --start-processes`
- [x] T070 Inspect Playwright screenshot under output/playwright/qa044_ui

## Dependencies & Execution Order

- Setup precedes all changes.
- Foundational tests precede route conversion.
- US1, US2, US3, and US4 can be implemented independently after foundational tests.
- Template deletion depends on all route conversions and scanner tests.
- Validation depends on docs, generated assets, backend tests, frontend tests, and Playwright.

## Implementation Strategy

1. Add route expectations and scanner tests.
2. Convert old browser routes to React redirects or safe problems.
3. Update React query-state and internal links.
4. Delete only bounded templates.
5. Refresh docs, QA env, generated assets, and validation manifest.
6. Run full Spec 044 validation before advancing to Spec 045.
