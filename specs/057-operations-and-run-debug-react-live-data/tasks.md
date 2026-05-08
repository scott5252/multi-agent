# Tasks: Operations And Run Debug React Live Data

**Input**: Design documents from `specs/057-operations-and-run-debug-react-live-data/`
**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: Required by FR-014, FR-015, and SC-006. Write or update tests before each implementation slice where practical.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently.

## Phase 1: Setup

**Purpose**: Establish Spec 057 artifacts, QA configuration, and current deterministic operations inventory.

- [X] T001 Record the Spec 057 deterministic workbench inventory for `src/multi_agent_platform/operations/workbench.py`, `src/multi_agent_platform/api/routers/admin_react.py`, `frontend/admin/src/components/workbench/WorkbenchPage.tsx`, `tests/integration/test_admin_react_routes.py`, and `tests/performance/operations/test_workbench_queries.py` in `specs/057-operations-and-run-debug-react-live-data/quickstart.md`
- [X] T002 [P] Create QA environment file `specs/057-operations-and-run-debug-react-live-data/.env.qa057` for database `multi_agent_platform_qa057`
- [X] T003 [P] Create PR reviewer notes scaffold `specs/057-operations-and-run-debug-react-live-data/pr_notes.md`
- [X] T004 [P] Inspect generated React contract coverage for operations routes in `frontend/admin/src/api/generated/reactAdminApi.ts`

---

## Phase 2: Foundational

**Purpose**: Shared live source, route, scanner, and QA foundations that block all user stories.

- [X] T005 Add live operations workbench query helpers or service methods for bounded summaries, logs, reliability, run-debug, and exports in `src/multi_agent_platform/operations/workbench.py`
- [X] T006 Use or add bounded run-debug timeline, lineage, and export evidence helpers in `src/multi_agent_platform/db/repositories/runtime_orchestration.py`
- [X] T007 Use or add bounded delivery, skill diagnostic, provider/gateway, usage, and reliability evidence helpers in `src/multi_agent_platform/db/repositories/channels.py`, `src/multi_agent_platform/db/repositories/skill_registry.py`, `src/multi_agent_platform/db/repositories/model_providers.py`, `src/multi_agent_platform/db/repositories/usage.py`, and `src/multi_agent_platform/db/repositories/reliability.py`
- [X] T008 [P] Add seeded and empty operations QA fixture helpers in `tests/fixtures/operations_workbench.py`
- [X] T009 [P] Add qa057 seed script `scripts/qa/seed_operations_qa057.py` with Acme operational evidence inside the 60-minute window and Globex empty state
- [X] T010 [P] Add qa057 verifier script `scripts/qa/verify_operations_qa057.py` for post-UI export persistence and redaction-safe database evidence
- [X] T011 Update live-data scanner mappings and blocked marker detection for QA029 operations fixtures in `src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py`
- [X] T012 [P] Update scanner tests for Spec 057 operations fixture removal in `tests/unit/admin/test_live_data_inventory_scanner.py`
- [X] T013 [P] Update workbench schemas for live empty, denied, unavailable, queued, validation, conflict, and not-found states in `src/multi_agent_platform/api/schemas/admin_workbench.py`

**Checkpoint**: Live operations source helpers, QA seed/verifier, schema states, and scanner expectations are ready.

---

## Phase 3: User Story 1 - Review Live Operational Health (Priority: P1)

**Goal**: Summary cards, health panels, likely causes, reliability items, logs, filters, and empty states come from live operational evidence for the authorized scope.

**Independent Test**: Empty and seeded workbench requests match persisted operations evidence for the default 60-minute window and do not render fixed QA029 cards or logs.

### Tests for User Story 1

- [X] T014 [P] [US1] Replace workbench service unit tests with live seeded and empty scope expectations in `tests/unit/operations/test_workbench_service.py`
- [X] T015 [P] [US1] Update Auth0-shaped route tests for `/admin/app/operations.json` seeded, empty, and cross-tenant behavior in `tests/integration/test_admin_react_routes.py`
- [X] T016 [P] [US1] Add bounded query performance coverage for operations workbench summaries in `tests/performance/operations/test_workbench_queries.py`
- [X] T017 [P] [US1] Add frontend workbench page tests for live summary cards, empty states, filters, and redaction in `frontend/admin/src/components/workbench/WorkbenchPage.test.tsx`

### Implementation for User Story 1

- [X] T018 [US1] Replace deterministic platform and tenant summary cards in `src/multi_agent_platform/operations/workbench.py` with live dependency, operations, reliability, usage, provider, channel, skill, and audit evidence
- [X] T019 [US1] Implement authorized scope and bounded 60-minute filter conversion in `src/multi_agent_platform/operations/workbench.py`
- [X] T020 [US1] Implement live health panels, likely-cause summaries, reliability summaries, logs, empty states, and safe fallback links in `src/multi_agent_platform/operations/workbench.py`
- [X] T021 [US1] Convert `/admin/app/operations.json` to an async live builder with injected session/container dependencies in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T022 [US1] Update React workbench components for truthful empty/unavailable states in `frontend/admin/src/components/workbench/WorkbenchSummaryGrid.tsx`, `frontend/admin/src/components/workbench/WorkbenchReliabilityPanel.tsx`, and `frontend/admin/src/components/workbench/WorkbenchTimeline.tsx`
- [X] T023 [US1] Refresh generated TypeScript contracts after backend schema/route changes using `frontend/admin/src/api/generated/reactAdminApi.ts`

**Checkpoint**: User Story 1 works independently for live seeded and empty workbench dashboards.

---

## Phase 4: User Story 2 - Inspect Live Run Debug Evidence (Priority: P2)

**Goal**: Run-debug projections show authorized live runtime, timeline, branch, gateway, tool, delivery, lineage, replay, and bundle evidence without fake rows.

**Independent Test**: A seeded run-debug request returns persisted live run evidence; missing and cross-tenant runs return truthful not-found or denied states without deterministic fallback data.

### Tests for User Story 2

- [X] T024 [P] [US2] Add run-debug unit tests for seeded, missing, and cross-tenant evidence in `tests/unit/operations/test_workbench_service.py`
- [X] T025 [P] [US2] Add route tests for `/admin/app/operations/runs/{workflow_run_id}.json` seeded, missing, and cross-tenant behavior in `tests/integration/test_admin_react_routes.py`
- [X] T026 [P] [US2] Add frontend run-debug tests for live timeline, branch, gateway, tool, delivery, and unavailable states in `frontend/admin/src/components/workbench/WorkbenchTimeline.test.tsx`
- [X] T027 [P] [US2] Add performance coverage for bounded run-debug timeline and evidence queries in `tests/performance/operations/test_workbench_queries.py`

### Implementation for User Story 2

- [X] T028 [US2] Implement live run-debug projection from runtime, audit-debug, gateway, skill, delivery, usage, lineage, and bundle evidence in `src/multi_agent_platform/operations/workbench.py`
- [X] T029 [US2] Implement missing-run and unauthorized-run handling with not-found or denied responses in `src/multi_agent_platform/operations/workbench.py` and `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T030 [US2] Replace deterministic branches, gateway attempts, tool calls, deliveries, lineage, replay links, and bundle summaries in `src/multi_agent_platform/operations/workbench.py`
- [X] T031 [US2] Update React run-debug rendering for live partial, empty, denied, and not-found states in `frontend/admin/src/components/workbench/WorkbenchTimeline.tsx`

**Checkpoint**: User Story 2 works independently for safe run-debug inspection.

---

## Phase 5: User Story 3 - Export Durable Operations Evidence (Priority: P3)

**Goal**: Browser export creation persists workbench export evidence and returns safe artifact metadata or truthful denied/failed/unavailable states.

**Independent Test**: Creating an export from the UI persists an export row or audit-debug export record and post-UI verification confirms scope, filters, included sections, artifact metadata, redaction summary, and row/section count.

### Tests for User Story 3

- [X] T032 [P] [US3] Add backend export creation/detail tests in `tests/unit/operations/test_workbench_service.py`
- [X] T033 [P] [US3] Add route tests for `/admin/app/operations/export` persisted, denied, and unavailable outcomes in `tests/integration/test_admin_react_routes.py`
- [X] T034 [P] [US3] Add frontend export interaction tests in `frontend/admin/src/components/workbench/WorkbenchExportPanel.test.tsx`
- [X] T035 [P] [US3] Add storage-backed export regression coverage for operations evidence exports in `tests/unit/operations/test_workbench_export.py`

### Implementation for User Story 3

- [X] T036 [US3] Implement live workbench export creation through existing audit-debug/export storage providers in `src/multi_agent_platform/operations/workbench.py`
- [X] T037 [US3] Implement safe export summaries from persisted metadata without storage URLs or local paths in `src/multi_agent_platform/operations/workbench.py`
- [X] T038 [US3] Wire export route dependencies for storage provider and async live export builder in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T039 [US3] Update `frontend/admin/src/components/workbench/WorkbenchExportPanel.tsx` to render persisted queued/completed/failed/denied/unavailable states without fake artifact ids

**Checkpoint**: User Story 3 works independently for durable workbench export creation.

---

## Phase 6: Polish And Validation

**Purpose**: Documentation, QA manifests, generated assets, and required post-spec validation.

- [X] T040 [P] Generate QA guide `specs/057-operations-and-run-debug-react-live-data/qa057.md`
- [X] T041 [P] Generate UI QA guide `specs/057-operations-and-run-debug-react-live-data/qa057_ui.md`
- [X] T042 [P] Generate user guide `specs/057-operations-and-run-debug-react-live-data/qa057_user_guide.md`
- [X] T043 Review `README.md` and `docs/quickstart.md` for operations workbench QA or command impact, then update them if shared guidance changed or record the no-update rationale in `specs/057-operations-and-run-debug-react-live-data/pr_notes.md`
- [X] T044 Update validation manifest `specs/_autopilot/remove-mock-data-roadmap/057-operations-and-run-debug-react-live-data/validation.yml` for qa057 seed, Playwright export action, screenshot, and post-UI verifier
- [X] T045 Update Playwright QA flow or inline script references for operations export validation in `specs/_autopilot/remove-mock-data-roadmap/057-operations-and-run-debug-react-live-data/validation.yml`
- [X] T046 Run `uv run ruff check src/multi_agent_platform/operations/workbench.py src/multi_agent_platform/api/routers/admin_react.py src/multi_agent_platform/api/schemas/admin_workbench.py tests/unit/operations/test_workbench_service.py tests/integration/test_admin_react_routes.py tests/unit/admin/test_live_data_inventory_scanner.py scripts/qa/seed_operations_qa057.py scripts/qa/verify_operations_qa057.py`
- [X] T047 Run `uv run mypy src/multi_agent_platform/operations/workbench.py src/multi_agent_platform/api/routers/admin_react.py`
- [X] T048 Run focused pytest coverage for operations workbench service, route, scanner, performance, repository, and export tests
- [X] T049 Run `npm run --prefix frontend/admin test -- --run Workbench` and `npm run --prefix frontend/admin typecheck`
- [X] T050 Run `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/057-operations-and-run-debug-react-live-data`
- [X] T051 Run `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/057-operations-and-run-debug-react-live-data/validation.yml`
- [X] T052 Run `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/057-operations-and-run-debug-react-live-data/validation.yml --start-processes`
- [X] T053 Run `uv run python scripts/qa/verify_operations_qa057.py` and record row-count/artifact evidence in `specs/_autopilot/remove-mock-data-roadmap/057-operations-and-run-debug-react-live-data/status.json`
- [X] T054 Run `uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa057-after-spec`
- [X] T055 Update `specs/_autopilot/remove-mock-data-roadmap/057-operations-and-run-debug-react-live-data/status.json` and `specs/_autopilot/remove-mock-data-roadmap/queue.json` with completed implement, validation, and spec completion history before moving to Spec 058

---

## Dependencies And Execution Order

### Phase Dependencies

- Phase 1 has no dependencies.
- Phase 2 depends on Phase 1 and blocks all user stories.
- User Story 1 depends on Phase 2 and is the MVP.
- User Story 2 depends on the live workbench source helpers from User Story 1.
- User Story 3 depends on the live filter/scope conversion and storage boundaries from User Story 1.
- Phase 6 depends on all implemented user stories.

### Parallel Opportunities

- T002, T003, and T004 can run in parallel.
- T008, T009, T010, T012, and T013 can run in parallel after T005-T007 source decisions are clear.
- Test tasks within each user story can run in parallel with each other.
- Frontend test updates can run in parallel with backend unit tests after contracts are stable.

## Implementation Strategy

1. Complete setup and foundational repository/QA/scanner/schema work.
2. Deliver User Story 1 as the MVP and validate seeded plus empty workbench behavior.
3. Add User Story 2 live run-debug projection and missing/cross-tenant behavior.
4. Add User Story 3 durable export creation/detail.
5. Run focused tests, full Spec QA, Playwright, post-UI verifier, and curl regression before queue advancement.
