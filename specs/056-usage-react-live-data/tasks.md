# Tasks: Usage React Live Data

**Input**: Design documents from `specs/056-usage-react-live-data/`
**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: Required by FR-015 and SC-006. Write or update tests before each implementation slice where practical.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently.

## Phase 1: Setup

**Purpose**: Establish Spec 056 artifacts, QA configuration, and current route inventory.

- [X] T001 Record the Spec 056 fixture-removal inventory for `src/multi_agent_platform/admin/usage/react_usage.py`, `src/multi_agent_platform/api/routers/admin_react.py`, `frontend/admin/src/components/usage/UsagePage.tsx`, `tests/unit/admin/usage/test_react_usage_service.py`, and `tests/integration/test_admin_react_routes.py` in `specs/056-usage-react-live-data/quickstart.md`
- [X] T002 [P] Create QA environment file `specs/056-usage-react-live-data/.env.qa056` for database `multi_agent_platform_qa056`
- [X] T003 [P] Create PR reviewer notes scaffold `specs/056-usage-react-live-data/pr_notes.md`
- [X] T004 [P] Inspect generated React contract coverage for usage routes in `frontend/admin/src/api/generated/reactAdminApi.ts`

---

## Phase 2: Foundational

**Purpose**: Shared backend, route, scanner, and QA foundations that block the user stories.

- [X] T005 Add live export listing and bounded source-metadata helpers to `src/multi_agent_platform/db/repositories/usage.py`
- [X] T006 [P] Add seeded and empty usage QA fixture helpers in `tests/fixtures/usage_react.py`
- [X] T007 [P] Add qa056 seed script `scripts/qa/seed_usage_qa056.py` with Acme usage/pricing/reconciliation/export rows and Globex empty state
- [X] T008 [P] Add qa056 verifier script `scripts/qa/verify_usage_qa056.py` for post-UI export persistence and redaction-safe database evidence
- [X] T009 Update scanner inventory and blocked marker detection for qa035 usage fixtures in `src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py`
- [X] T010 [P] Update scanner tests for Spec 056 usage fixture removal in `tests/unit/admin/test_live_data_inventory_scanner.py`
- [X] T011 [P] Update React usage schema enums and validators for missing, reconciliation-pending, queued, validation, conflict, and unavailable outcomes in `src/multi_agent_platform/api/schemas/admin_usage_react.py`

**Checkpoint**: Live usage source helpers, QA seed/verifier, and scanner expectations are ready.

---

## Phase 3: User Story 1 - Review Live Usage Totals (Priority: P1)

**Goal**: Dashboard totals, trends, rollups, filter metadata, and empty states come from live usage evidence for the authorized scope.

**Independent Test**: Empty and seeded dashboard requests match persisted usage rows for the default last-30-days window and do not render fixed qa035 events.

### Tests for User Story 1

- [X] T012 [P] [US1] Replace dashboard unit tests with live seeded/empty scope expectations in `tests/unit/admin/usage/test_react_usage_service.py`
- [X] T013 [P] [US1] Add usage repository tests for bounded event, export, and filter helpers in `tests/unit/db/repositories/test_usage_repository.py`
- [X] T014 [P] [US1] Update Auth0-shaped route tests for `/admin/app/usage/bootstrap.json` seeded, empty, and cross-tenant behavior in `tests/integration/test_admin_react_routes.py`
- [X] T015 [P] [US1] Add performance coverage for bounded date-range usage dashboard queries in `tests/performance/usage/test_react_usage_queries.py`

### Implementation for User Story 1

- [X] T016 [US1] Replace fixed `USAGE_EVENTS`, `QA_NOW`, tenant labels, and fake export ids in `src/multi_agent_platform/admin/usage/react_usage.py` with live `UsageAnalyticsService` and `UsageRepository` inputs
- [X] T017 [US1] Implement React scope to `UsageAccessScope` and `UsageFilters` conversion with last-30-days defaults in `src/multi_agent_platform/admin/usage/react_usage.py`
- [X] T018 [US1] Implement live dashboard summary cards, trend points, rollup rows, filter options, and common empty/partial states in `src/multi_agent_platform/admin/usage/react_usage.py`
- [X] T019 [US1] Convert usage bootstrap and events routes to async live builders with injected repository/service dependencies in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T020 [US1] Refresh generated TypeScript contracts after backend schema/route changes using `frontend/admin/src/api/generated/reactAdminApi.ts`

**Checkpoint**: User Story 1 works independently for live seeded and empty usage dashboards.

---

## Phase 4: User Story 2 - Inspect Redaction-Safe Attribution And Drilldowns (Priority: P2)

**Goal**: Drilldowns and rollups show safe provider/model/workflow/prompt/profile/run/step/agent/skill attribution and confidence states without raw sensitive payloads.

**Independent Test**: Seeded usage drilldowns include safe attribution and confidence states while redaction scans find no raw prompts, completions, secrets, payloads, or unauthorized tenant labels.

### Tests for User Story 2

- [X] T021 [P] [US2] Add drilldown attribution and confidence tests in `tests/unit/admin/usage/test_react_usage_service.py`
- [X] T022 [P] [US2] Add usage API schema redaction tests in `tests/unit/api/test_admin_usage_react_schema.py`
- [X] T023 [P] [US2] Add React component tests for confidence badges, rollup drilldown loading, and empty attribution labels in `frontend/admin/src/components/usage/UsagePage.test.tsx`
- [X] T024 [P] [US2] Update frontend usage test data to use test-only live-like fixtures in `frontend/admin/src/test/usageTestData.ts`

### Implementation for User Story 2

- [X] T025 [US2] Implement `UsageReactEventRow` mapping from live usage event views and sanitized safe attribution in `src/multi_agent_platform/admin/usage/react_usage.py`
- [X] T026 [US2] Implement confidence mapping for confirmed, estimated, partial, missing, reconciliation-pending, and unavailable usage in `src/multi_agent_platform/admin/usage/react_usage.py`
- [X] T027 [US2] Implement drilldown rollup-key filtering and capped row counts in `src/multi_agent_platform/admin/usage/react_usage.py`
- [X] T028 [US2] Update usage UI copy and badges for truthful unavailable/missing states in `frontend/admin/src/components/usage/UsageEventDrilldown.tsx`, `frontend/admin/src/components/usage/UsageRollupPanel.tsx`, and `frontend/admin/src/components/usage/UsageSummaryCards.tsx`

**Checkpoint**: User Story 2 works independently for safe drilldowns and confidence states.

---

## Phase 5: User Story 3 - Create Durable Usage Exports (Priority: P3)

**Goal**: Browser export creation persists usage export requests and returns safe artifact metadata or truthful denied/failed/unavailable states.

**Independent Test**: Creating an export from the UI persists a `usage_export_requests` row and post-UI verification confirms row count, filters, artifact metadata, and redaction-safe status.

### Tests for User Story 3

- [X] T029 [P] [US3] Add backend export creation/detail tests in `tests/unit/admin/usage/test_react_usage_service.py`
- [X] T030 [P] [US3] Add route tests for `/admin/app/usage/exports` and `/admin/app/usage/exports/{usage_export_request_id}.json` in `tests/integration/test_admin_react_routes.py`
- [X] T031 [P] [US3] Add frontend export interaction tests in `frontend/admin/src/components/usage/UsagePage.test.tsx`
- [X] T032 [P] [US3] Add storage-backed export service regression coverage in `tests/unit/usage/test_export.py`

### Implementation for User Story 3

- [X] T033 [US3] Implement live export creation via `UsageAnalyticsService.create_csv_export()` and configured storage in `src/multi_agent_platform/admin/usage/react_usage.py`
- [X] T034 [US3] Implement live export detail and recent export summaries from persisted `UsageExportRequest` rows in `src/multi_agent_platform/admin/usage/react_usage.py`
- [X] T035 [US3] Wire export route dependencies for storage provider and async live export builders in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T036 [US3] Update `frontend/admin/src/components/usage/UsageExportPanel.tsx` to render persisted queued/completed/failed/denied/unavailable states without fake artifact ids

**Checkpoint**: User Story 3 works independently for durable export creation and detail retrieval.

---

## Phase 6: Polish And Validation

**Purpose**: Documentation, QA manifests, generated assets, and required post-spec validation.

- [X] T037 [P] Generate QA guide `specs/056-usage-react-live-data/qa056.md`
- [X] T038 [P] Generate UI QA guide `specs/056-usage-react-live-data/qa056_ui.md`
- [X] T039 [P] Generate user guide `specs/056-usage-react-live-data/qa056_user_guide.md`
- [X] T040 Update validation manifest `specs/_autopilot/remove-mock-data-roadmap/056-usage-react-live-data/validation.yml` for qa056 seed, Playwright export action, screenshot, and post-UI verifier
- [X] T041 Update Playwright QA flow or inline script references for usage export validation in `specs/_autopilot/remove-mock-data-roadmap/056-usage-react-live-data/validation.yml`
- [X] T042 Run `uv run ruff check src/multi_agent_platform/admin/usage/react_usage.py src/multi_agent_platform/api/routers/admin_react.py src/multi_agent_platform/db/repositories/usage.py tests/unit/admin/usage/test_react_usage_service.py tests/integration/test_admin_react_routes.py tests/unit/admin/test_live_data_inventory_scanner.py scripts/qa/seed_usage_qa056.py scripts/qa/verify_usage_qa056.py`
- [X] T043 Run `uv run mypy src/multi_agent_platform/admin/usage/react_usage.py src/multi_agent_platform/api/routers/admin_react.py`
- [X] T044 Run focused pytest coverage for usage service, route, scanner, repository, performance, and export tests
- [X] T045 Run `npm run --prefix frontend/admin test -- --run Usage` and `npm run --prefix frontend/admin typecheck`
- [X] T046 Run `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/056-usage-react-live-data`
- [X] T047 Run `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/056-usage-react-live-data/validation.yml`
- [X] T048 Run `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/056-usage-react-live-data/validation.yml --start-processes`
- [X] T049 Run `uv run python scripts/qa/verify_usage_qa056.py` and record row-count/artifact evidence in `specs/_autopilot/remove-mock-data-roadmap/056-usage-react-live-data/status.json`
- [X] T050 Run `uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa056-after-spec`
- [X] T051 Update `specs/_autopilot/remove-mock-data-roadmap/056-usage-react-live-data/status.json` and `specs/_autopilot/remove-mock-data-roadmap/queue.json` with completed implement, validation, and spec completion history before moving to Spec 057

---

## Dependencies And Execution Order

### Phase Dependencies

- Phase 1 has no dependencies.
- Phase 2 depends on Phase 1 and blocks all user stories.
- User Story 1 depends on Phase 2 and is the MVP.
- User Story 2 depends on the live event/query foundation from User Story 1.
- User Story 3 depends on the live filter/scope conversion from User Story 1.
- Phase 6 depends on all implemented user stories.

### Parallel Opportunities

- T002, T003, and T004 can run in parallel.
- T006, T007, T008, T010, and T011 can run in parallel after T005 decisions are clear.
- Test tasks within each story can run in parallel with each other.
- Frontend test updates can run in parallel with backend unit tests after contracts are stable.

## Implementation Strategy

1. Complete setup and foundational repository/QA/scanner work.
2. Deliver User Story 1 as the MVP and validate seeded plus empty dashboard behavior.
3. Add User Story 2 drilldown attribution and confidence states.
4. Add User Story 3 durable export creation/detail.
5. Run focused tests, full Spec QA, Playwright, post-UI verifier, and curl regression before queue advancement.
