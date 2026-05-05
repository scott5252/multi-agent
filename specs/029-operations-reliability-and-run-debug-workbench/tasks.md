# Tasks: Operations, Reliability, And Run Debug Workbench

**Input**: Design documents from `specs/029-operations-reliability-and-run-debug-workbench/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required. The feature specification mandates backend schema/service
coverage, contract and generated TypeScript drift checks, Auth0-shaped and
local-principal route coverage, tenant isolation, redaction tests, performance
tests, frontend component coverage, Playwright evidence, QA docs, and full
quality gates.

**Organization**: Tasks are grouped by user story so each story remains
independently testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and has no
  dependency on an incomplete task.
- **[Story]**: User story label from `spec.md`.
- Every task includes an exact file path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare backend, frontend, and test folders for the React
operations workbench.

- [x] T001 Add backend workbench schema module in `src/multi_agent_platform/api/schemas/admin_workbench.py`
- [x] T002 [P] Add operations workbench aggregation module in `src/multi_agent_platform/operations/workbench.py`
- [x] T003 [P] Add React workbench component directory in `frontend/admin/src/components/workbench/`
- [x] T004 [P] Add React workbench fixture file in `frontend/admin/src/test/workbenchTestData.ts`
- [x] T005 [P] Add performance test directory in `tests/performance/operations/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define shared contracts, generated types, and protected route
surface before any user story consumes the workbench.

**CRITICAL**: No user story implementation can proceed until these tasks are done.

- [x] T006 Extend `src/multi_agent_platform/api/schemas/admin_workbench.py` with workbench envelope, time range, refresh hint, summary card, likely-cause, health panel, run debug, timeline, branch, gateway, tool, channel, reliability, log, export, and request models
- [x] T007 Extend `scripts/frontend/generate_admin_react_types.py` to emit Spec 029 workbench contracts and assertion helpers
- [x] T008 Regenerate `frontend/admin/src/api/generated/reactAdminApi.ts`
- [x] T009 Add Spec 029 OpenAPI and generated-contract drift checks in `tests/contract/test_admin_react_contract.py`
- [x] T010 Add workbench schema redaction and validation tests in `tests/unit/api/test_admin_workbench_schema.py`
- [x] T011 Add React client helpers for workbench envelope, run debug, and export requests in `frontend/admin/src/api/client.ts`
- [x] T012 Register protected React workbench route/action surfaces in `src/multi_agent_platform/auth/policy.py`
- [x] T013 Add `/admin/app/operations` shell route constants and fallback links in `src/multi_agent_platform/api/routers/admin_react.py`

---

## Phase 3: User Story 1 - Triage Platform Health And Pressure (Priority: P1) MVP

**Goal**: Platform operators can open one React workbench that summarizes
health, dependencies, capacity, queue pressure, database pressure, provider and
channel status, connector readiness, reliability posture, trends, safe logs,
likely causes, and next destinations.

**Independent Test**: Open the workbench as platform admin/auditor and verify
safe platform summaries render; open it as unauthenticated and tenant-limited
principals and verify platform-only data is denied or hidden.

### Tests for User Story 1

- [x] T014 [P] [US1] Add platform-admin and auditor workbench envelope route tests with last-60-minutes default and Spec 019-style filter coverage in `tests/integration/test_admin_react_routes.py`
- [x] T015 [P] [US1] Add Auth0-shaped platform principal route tests in `tests/integration/test_admin_react_routes.py`
- [x] T016 [P] [US1] Add unauthenticated, denied, and tenant-limited platform data tests in `tests/integration/test_admin_react_routes.py`
- [x] T017 [P] [US1] Add aggregation, likely-cause, default-range, refresh-hint, and degraded-card unit tests in `tests/unit/operations/test_workbench_service.py`
- [x] T018 [P] [US1] Add bounded log and dashboard performance tests in `tests/performance/operations/test_workbench_queries.py`
- [x] T019 [P] [US1] Add React summary grid component tests in `frontend/admin/src/components/workbench/WorkbenchSummaryGrid.test.tsx`
- [x] T020 [P] [US1] Add React workbench page platform/tenant render tests in `frontend/admin/src/components/workbench/WorkbenchPage.test.tsx`

### Implementation for User Story 1

- [x] T021 [US1] Implement platform and tenant access scope builders in `src/multi_agent_platform/operations/workbench.py`
- [x] T022 [US1] Implement deterministic workbench summary aggregation, default last-60-minutes range, and backend-owned filter mapping in `src/multi_agent_platform/operations/workbench.py`
- [x] T023 [US1] Implement likely-cause and degraded-card builders in `src/multi_agent_platform/operations/workbench.py`
- [x] T024 [US1] Add `/admin/app/operations` and `/admin/app/operations.json` routes in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T025 [US1] Add frontend workbench envelope fetch integration in `frontend/admin/src/api/client.ts`
- [x] T026 [US1] Implement `WorkbenchSummaryGrid` in `frontend/admin/src/components/workbench/WorkbenchSummaryGrid.tsx`
- [x] T027 [US1] Implement `WorkbenchPage` platform and tenant triage layout with manual refresh and safe health polling hints in `frontend/admin/src/components/workbench/WorkbenchPage.tsx`
- [x] T028 [US1] Route `/admin/app/operations` from `frontend/admin/src/App.tsx`
- [x] T029 [US1] Add workbench summary, health card, likely-cause, refresh, filter, and partial-data styles in `frontend/admin/src/styles/admin.css`

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Debug Runs, Graphs, Tools, And Deliveries (Priority: P2)

**Goal**: Authorized administrators can inspect one safe run-centric view that
connects timeline events, graph branches, join decisions, run steps, tool
calls, gateway attempts, credential diagnostic categories, Telegram/channel
deliveries, lineage, replay links, and audit references.

**Independent Test**: Load a deterministic run debug fixture as a platform
operator and authorized tenant admin, then verify timeline, branch, join, tool,
gateway, delivery, lineage, and replay summaries are safe and scoped.

### Tests for User Story 2

- [x] T030 [P] [US2] Add run debug envelope route tests for platform and tenant scopes in `tests/integration/test_admin_react_routes.py`
- [x] T031 [P] [US2] Add cross-tenant run debug denial tests in `tests/integration/test_admin_react_routes.py`
- [x] T032 [P] [US2] Add run timeline, branch, gateway, tool, and delivery aggregation tests in `tests/unit/operations/test_workbench_service.py`
- [x] T033 [P] [US2] Add run debug redaction tests in `tests/unit/api/test_admin_workbench_schema.py`
- [x] T034 [P] [US2] Add React timeline component tests in `frontend/admin/src/components/workbench/WorkbenchTimeline.test.tsx`

### Implementation for User Story 2

- [x] T035 [US2] Implement run debug envelope builders in `src/multi_agent_platform/operations/workbench.py`
- [x] T036 [US2] Implement graph branch and join summary builders in `src/multi_agent_platform/operations/workbench.py`
- [x] T037 [US2] Implement gateway, tool, and channel delivery summary builders in `src/multi_agent_platform/operations/workbench.py`
- [x] T038 [US2] Add `/admin/app/operations/runs/{workflow_run_id}.json` route in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T039 [US2] Add run debug fetch helper in `frontend/admin/src/api/client.ts`
- [x] T040 [US2] Implement `WorkbenchTimeline` in `frontend/admin/src/components/workbench/WorkbenchTimeline.tsx`
- [x] T041 [US2] Wire run debug panel into `frontend/admin/src/components/workbench/WorkbenchPage.tsx`
- [x] T042 [US2] Add timeline, branch, gateway, tool, delivery, and lineage styles in `frontend/admin/src/styles/admin.css`

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Recover, Export, And Hand Off Safely (Priority: P3)

**Goal**: Operators can inspect reliability controls, retries, dead letters,
compensation, quotas, leases, replay/remediation links, confirmation prompts,
and safe export snapshots from the workbench.

**Independent Test**: Use deterministic reliability fixtures to review breaker,
retry, dead-letter, replay confirmation, partial-data, and export snapshot
states, then verify artifact references and redaction behavior.

### Tests for User Story 3

- [x] T043 [P] [US3] Add reliability recovery route and export snapshot tests in `tests/integration/test_admin_react_routes.py`
- [x] T044 [P] [US3] Add export denial and cross-tenant export tests in `tests/integration/test_admin_react_routes.py`
- [x] T045 [P] [US3] Add reliability recovery and confirmation unit tests in `tests/unit/operations/test_workbench_service.py`
- [x] T046 [P] [US3] Add export snapshot and local-path redaction tests in `tests/unit/api/test_admin_workbench_schema.py`
- [x] T047 [P] [US3] Add React reliability panel tests in `frontend/admin/src/components/workbench/WorkbenchReliabilityPanel.test.tsx`
- [x] T048 [P] [US3] Add React export panel tests in `frontend/admin/src/components/workbench/WorkbenchExportPanel.test.tsx`

### Implementation for User Story 3

- [x] T049 [US3] Implement reliability recovery builders in `src/multi_agent_platform/operations/workbench.py`
- [x] T050 [US3] Implement safe workbench export snapshot builder in `src/multi_agent_platform/operations/workbench.py`
- [x] T051 [US3] Add `/admin/app/operations/export` route in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T052 [US3] Add workbench export request helper in `frontend/admin/src/api/client.ts`
- [x] T053 [US3] Implement `WorkbenchReliabilityPanel` in `frontend/admin/src/components/workbench/WorkbenchReliabilityPanel.tsx`
- [x] T054 [US3] Implement `WorkbenchExportPanel` in `frontend/admin/src/components/workbench/WorkbenchExportPanel.tsx`
- [x] T055 [US3] Wire reliability recovery and export flow into `frontend/admin/src/components/workbench/WorkbenchPage.tsx`
- [x] T056 [US3] Add reliability, confirmation, export, and handoff styles in `frontend/admin/src/styles/admin.css`

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation manifest reconciliation, QA evidence,
and final quality gates.

- [x] T057 [P] Update React operations workbench notes in `README.md`
- [x] T058 [P] Update local validation notes in `docs/quickstart.md`
- [x] T059 [P] Create implementation reviewer notes in `specs/029-operations-reliability-and-run-debug-workbench/pr_notes.md`
- [x] T060 Generate QA API/database guide in `specs/029-operations-reliability-and-run-debug-workbench/qa029.md`
- [x] T061 Generate QA UI walkthrough in `specs/029-operations-reliability-and-run-debug-workbench/qa029_ui.md`
- [x] T062 Generate QA environment file in `specs/029-operations-reliability-and-run-debug-workbench/.env.qa029`
- [x] T063 Generate detailed manual user guide in `specs/029-operations-reliability-and-run-debug-workbench/qa029_user_guide.md`
- [x] T064 Reconcile QA029 validation commands and Playwright workbench flows in `specs/_autopilot/react-ui-roadmap/029-operations-reliability-and-run-debug-workbench/validation.yml`
- [x] T065 Run frontend build/test commands and record outcomes in `specs/029-operations-reliability-and-run-debug-workbench/pr_notes.md`
- [x] T066 Run backend quality commands and record outcomes in `specs/029-operations-reliability-and-run-debug-workbench/pr_notes.md`
- [x] T067 Run QA docs, Spec QA, and Playwright validation commands and record evidence paths in `specs/029-operations-reliability-and-run-debug-workbench/pr_notes.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational and provides the MVP workbench route.
- **User Story 2 (Phase 4)**: Depends on Foundational and integrates with US1 page layout, but remains independently testable through the run debug endpoint.
- **User Story 3 (Phase 5)**: Depends on Foundational and integrates with US1 page layout, but remains independently testable through the export endpoint and reliability panel.
- **Polish (Phase 6)**: Depends on implemented stories.

### Parallel Opportunities

- T002-T005 can run in parallel after T001 is planned.
- T009-T010 and T012 can run in parallel after T006.
- T014-T020 can run in parallel after foundational contracts exist.
- T030-T034 can run in parallel after run debug contracts exist.
- T043-T048 can run in parallel after reliability/export contracts exist.
- T057-T059 can run in parallel with QA document drafting.

## Parallel Example: User Story 1

```bash
Task: "Add platform-admin and auditor workbench envelope route tests in tests/integration/test_admin_react_routes.py"
Task: "Add aggregation and likely-cause unit tests in tests/unit/operations/test_workbench_service.py"
Task: "Add React summary grid component tests in frontend/admin/src/components/workbench/WorkbenchSummaryGrid.test.tsx"
Task: "Add React workbench page platform/tenant render tests in frontend/admin/src/components/workbench/WorkbenchPage.test.tsx"
```

## Implementation Strategy

1. Complete schemas, generated contracts, route protection, and client helpers.
2. Deliver User Story 1 as the MVP platform/tenant triage route.
3. Add User Story 2 run debug panels and endpoint.
4. Add User Story 3 reliability recovery and export flow.
5. Finish QA docs, validation manifest, screenshots, and full quality evidence.

## Notes

- Do not retire or weaken existing Jinja admin routes.
- Do not call live providers, Telegram, credential stores, or external tools in QA.
- Do not render raw prompts, completions, memory, private messages, provider responses, Telegram updates, tool payloads, stack traces, local paths, or unauthorized tenant labels.
- Stop if tenant scope, export safety, replay/remediation actions, credential diagnostics, or redaction behavior becomes ambiguous.
