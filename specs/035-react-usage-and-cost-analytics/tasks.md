# Tasks: React Usage And Cost Analytics

**Input**: Design documents from `specs/035-react-usage-and-cost-analytics/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`
**Tests**: Required by FR-017, SC-001 through SC-008, and the React UI roadmap dual-auth validation policy.
**Organization**: Tasks are grouped by user story so each story remains independently testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches distinct files or does not depend on unfinished tasks.
- **[Story]**: User story label for story phases only.
- Every task names an exact file path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare Spec 035 artifacts and confirm usage analytics remains additive.

- [x] T001 Verify `.specify/feature.json` points to `specs/035-react-usage-and-cost-analytics` and `AGENTS.md` references `specs/035-react-usage-and-cost-analytics/plan.md`.
- [x] T002 [P] Create the usage React component directory at `frontend/admin/src/components/usage/`.
- [x] T003 [P] Create the usage frontend fixture file at `frontend/admin/src/test/usageTestData.ts`.
- [x] T004 [P] Create the usage backend schema module at `src/multi_agent_platform/api/schemas/admin_usage_react.py`.
- [x] T005 [P] Create the usage React adapter/service package at `src/multi_agent_platform/admin/usage/`.
- [x] T006 [P] Create the usage performance test directory at `tests/performance/usage/`.
- [x] T007 [P] Create the QA035 documentation placeholders in `specs/035-react-usage-and-cost-analytics/qa035.md`, `specs/035-react-usage-and-cost-analytics/qa035_ui.md`, `specs/035-react-usage-and-cost-analytics/.env.qa035`, `specs/035-react-usage-and-cost-analytics/qa035_user_guide.md`, and `specs/035-react-usage-and-cost-analytics/pr_notes.md`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish safe backend contracts, generated browser types, protected routes, and shared usage fixtures before story work.

- [x] T008 Define usage React enums, unsafe marker validation helpers, safe text helpers, and formatted value primitives in `src/multi_agent_platform/api/schemas/admin_usage_react.py`.
- [x] T009 Define `UsageReactDashboard`, `UsageReactScope`, `UsageReactFilterMetadata`, `UsageReactSummaryCard`, `UsageReactTrendPoint`, `UsageReactRollupSection`, `UsageReactRollupRow`, `UsageReactEventDrilldown`, `UsageReactEventRow`, `UsageReactExportSummary`, and `UsageReactProblem` schemas in `src/multi_agent_platform/api/schemas/admin_usage_react.py`.
- [x] T010 Define usage filter query, dashboard query, event query, export create request, export detail response, and mutation result schemas in `src/multi_agent_platform/api/schemas/admin_usage_react.py`.
- [x] T011 Add schema validators that reject raw prompts, completions, memory content, authorization headers, provider tokens, credential values, credential reference internals, raw tool payloads, private messages, local filesystem paths, and unauthorized tenant labels in `src/multi_agent_platform/api/schemas/admin_usage_react.py`.
- [x] T012 [P] Add schema tests for safe labels, confidence statuses, filter metadata, bounded rows, export summaries, and unsafe marker rejection in `tests/unit/api/test_admin_usage_react_schema.py`.
- [x] T013 Implement deterministic QA035 constants, Acme/Globex tenant labels, provider/model/workflow/agent/prompt labels, graph node labels, gateway/attempt/tool labels, and audit references in `src/multi_agent_platform/admin/usage/react_usage.py`.
- [x] T014 Implement backend-owned cost, token, latency, status, date-range, and safe attribution formatting helpers in `src/multi_agent_platform/admin/usage/react_usage.py`.
- [x] T015 Implement dashboard scope, default filter, filter metadata, summary-card, empty-state, partial-state, denied-state, and stale-pricing builders in `src/multi_agent_platform/admin/usage/react_usage.py`.
- [x] T016 Implement trend, rollup, event drilldown, all Spec 016 grouping dimensions, gateway operation, physical attempt, graph node, and governed tool attribution builders in `src/multi_agent_platform/admin/usage/react_usage.py`.
- [x] T017 Implement export create/detail projection builders with safe filter snapshots, artifact references, checksum prefixes, row counts, requester/scope labels, persisted audit references, and audit-unavailable failure behavior in `src/multi_agent_platform/admin/usage/react_usage.py`.
- [x] T018 Implement fail-closed cross-tenant, platform-only, invalid range, unsupported grouping, audit-unavailable, and export-unavailable result builders in `src/multi_agent_platform/admin/usage/react_usage.py`.
- [x] T019 [P] Add service tests for platform dashboard projections, tenant projections, confidence card totals, trend buckets, rollup bounds, event drilldown bounds, export summaries, cross-tenant denial, and redaction safety in `tests/unit/admin/usage/test_react_usage_service.py`.
- [x] T020 [P] Add bounded query/performance tests for dashboard, rollup, drilldown, and export projection builders in `tests/performance/usage/test_react_usage_queries.py`.
- [x] T021 Extend `scripts/frontend/generate_admin_react_types.py` with generated TypeScript interfaces and assert helpers for all usage React schemas and request bodies.
- [x] T022 Regenerate `frontend/admin/src/api/generated/reactAdminApi.ts` from `scripts/frontend/generate_admin_react_types.py`.
- [x] T023 Add usage API client helpers for bootstrap, events, export creation, and export detail in `frontend/admin/src/api/client.ts`.
- [x] T024 Add protected usage React routes and export endpoints to `src/multi_agent_platform/api/routers/admin_react.py`.
- [x] T025 Register usage React route surfaces as authenticated protected surfaces in `src/multi_agent_platform/auth/policy.py`.
- [x] T026 Wire `/admin/app/usage` into the React app router in `frontend/admin/src/App.tsx`.
- [x] T027 Remove `usage` from disabled React route fallbacks while preserving `/admin/usage` Jinja fallback handling in `frontend/admin/src/routes.tsx`.
- [x] T028 Add usage workspace styles, responsive layout rules, chart dimensions, and stable table/control dimensions in `frontend/admin/src/styles/admin.css`.
- [x] T029 [P] Add contract coverage for usage dashboard, events, export creation, and export detail route shapes in `tests/contract/test_admin_react_contract.py`.
- [x] T030 [P] Add integration coverage for denied, Auth0-shaped, and local-principal usage React route authorization in `tests/integration/test_admin_react_routes.py`.
- [x] T031 [P] Add usage fixture data mirroring generated schemas in `frontend/admin/src/test/usageTestData.ts`.

**Checkpoint**: Backend contracts, generated browser types, protected routes, and shared usage fixtures are ready for user-story implementation.

---

## Phase 3: User Story 1 - Review Usage And Cost Health (Priority: P1)

**Goal**: Platform and tenant admins can open the React usage workspace and understand recent token usage, cost estimates, latency, unavailable usage, and confirmed-versus-estimated coverage.

**Independent Test**: Sign in as a platform administrator and as an Acme tenant administrator, open `/admin/app/usage`, and verify each scope shows safe summary cards, daily trend, confidence badges, latency, unavailable usage, empty/partial states, and no unauthorized tenant rows.

### Tests for User Story 1

- [x] T032 [P] [US1] Add dashboard rendering and loading-state tests in `frontend/admin/src/components/usage/UsagePage.test.tsx`.
- [x] T033 [P] [US1] Add summary card status, currency precision, latency, and unavailable usage tests in `frontend/admin/src/components/usage/UsageSummaryCards.test.tsx`.
- [x] T034 [P] [US1] Add daily trend chart and accessible fallback tests in `frontend/admin/src/components/usage/UsageTrendPanel.test.tsx`.
- [x] T035 [P] [US1] Add platform and tenant dashboard route integration tests in `tests/integration/test_admin_react_routes.py`.

### Implementation for User Story 1

- [x] T036 [US1] Implement `UsagePage` orchestration, bootstrap loading, filter state, local error states, refresh handling, and export result toasts in `frontend/admin/src/components/usage/UsagePage.tsx`.
- [x] T037 [P] [US1] Implement `UsageHeader` with active scope, selected range, freshness, confidence summary, and export action in `frontend/admin/src/components/usage/UsageHeader.tsx`.
- [x] T038 [P] [US1] Implement `UsageFilterBar` with backend-owned range, tenant, provider, model, confidence, and availability controls in `frontend/admin/src/components/usage/UsageFilterBar.tsx`.
- [x] T039 [P] [US1] Implement `UsageSummaryCards` with tokens, estimated cost, event count, latency, unavailable usage, and confirmed/estimated coverage cards in `frontend/admin/src/components/usage/UsageSummaryCards.tsx`.
- [x] T040 [P] [US1] Implement `UsageTrendPanel` with accessible SVG trend rendering and bucket summaries in `frontend/admin/src/components/usage/UsageTrendPanel.tsx`.
- [x] T041 [P] [US1] Implement `UsageStatePanel` for empty, partial, unavailable, denied, stale-pricing, export-pending, and audit-unavailable states in `frontend/admin/src/components/usage/UsageStatePanel.tsx`.
- [x] T042 [US1] Connect dashboard bootstrap, filter changes, platform scope, tenant scope, and safe problem rendering to `UsagePage` in `frontend/admin/src/components/usage/UsagePage.tsx`.
- [x] T043 [US1] Update `src/multi_agent_platform/api/routers/admin_react.py` to return platform and tenant dashboard projections for `/admin/app/usage/bootstrap.json`.
- [x] T044 [US1] Update `tests/integration/test_admin_react_routes.py` to assert tenant admins cannot see Globex labels and platform admins can intentionally review authorized tenant rollups.

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Compare Rollups And Attribution (Priority: P2)

**Goal**: Administrators can switch rollup dimensions and compare provider, model, workflow, agent, prompt, graph node, gateway operation, physical attempt, and governed tool attribution safely.

**Independent Test**: Use the default dashboard filters, switch grouping dimensions, and verify each rollup table updates with safe labels, token/cost totals, latency, unavailable usage, attempt/tool summaries, confidence badges, and bounded row counts.

### Tests for User Story 2

- [x] T045 [P] [US2] Add group selector and rollup table tests in `frontend/admin/src/components/usage/UsageRollupPanel.test.tsx`.
- [x] T046 [P] [US2] Add graph, gateway, physical-attempt, and governed-tool attribution tests in `frontend/admin/src/components/usage/UsageAttributionBadges.test.tsx`.
- [x] T047 [P] [US2] Add backend rollup dimension and safe attribution tests in `tests/unit/admin/usage/test_react_usage_service.py`.
- [x] T048 [P] [US2] Extend integration tests for provider/model/workflow/agent/sub-agent/prompt/execution-mode/principal/tenant/gateway/tool group query parameters in `tests/integration/test_admin_react_routes.py`.

### Implementation for User Story 2

- [x] T049 [P] [US2] Implement `UsageGroupSelector` with backend-provided group choices and disabled reasons in `frontend/admin/src/components/usage/UsageGroupSelector.tsx`.
- [x] T050 [P] [US2] Implement `UsageRollupPanel` with bounded rows, safe labels, metric columns, confidence badges, and drilldown actions in `frontend/admin/src/components/usage/UsageRollupPanel.tsx`.
- [x] T051 [P] [US2] Implement `UsageAttributionBadges` for graph node, gateway operation, physical attempt, governed tool, archived reference, and pricing confidence summaries in `frontend/admin/src/components/usage/UsageAttributionBadges.tsx`.
- [x] T052 [US2] Update `UsagePage` to reload rollups when group, provider, model, tenant, confidence, or availability filters change in `frontend/admin/src/components/usage/UsagePage.tsx`.
- [x] T053 [US2] Update `src/multi_agent_platform/admin/usage/react_usage.py` to project Spec 016 dimensions plus graph node, gateway operation, physical attempt, governed tool, archived reference, and unavailable-pricing summaries from normalized fields and safe attribution.
- [x] T054 [US2] Update `src/multi_agent_platform/api/routers/admin_react.py` to validate unsupported grouping values and return safe problem responses for usage rollups.
- [x] T055 [US2] Update `tests/unit/admin/usage/test_react_usage_service.py` to prove rollups stay capped at 25 rows and never expose unsafe attribution markers.

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Drill Down And Export Evidence (Priority: P3)

**Goal**: Administrators can inspect bounded safe event rows and create audited CSV exports for the active safe filter snapshot.

**Independent Test**: Open a drilldown from a rollup row, verify safe event details, create an export, open export detail, and confirm status, artifact reference, audit evidence, and tenant scope are safe.

### Tests for User Story 3

- [x] T056 [P] [US3] Add event drilldown rendering, bounded-row, and unsafe marker tests in `frontend/admin/src/components/usage/UsageEventDrilldown.test.tsx`.
- [x] T057 [P] [US3] Add export creation, pending/completed/denied status, and audit reference tests in `frontend/admin/src/components/usage/UsageExportPanel.test.tsx`.
- [x] T058 [P] [US3] Add export detail route and delayed artifact tests in `frontend/admin/src/components/usage/UsageExportDetailPage.test.tsx`.
- [x] T059 [P] [US3] Extend export creation, export detail, cross-tenant denial, Auth0-shaped, and local-principal route tests in `tests/integration/test_admin_react_routes.py`.

### Implementation for User Story 3

- [x] T060 [P] [US3] Implement `UsageEventDrilldown` with safe event rows, trace/audit references, confidence labels, provider/model/workflow/agent/prompt labels, attempt summaries, and bounded result copy in `frontend/admin/src/components/usage/UsageEventDrilldown.tsx`.
- [x] T061 [P] [US3] Implement `UsageExportPanel` with active safe filter snapshot preview, create-export action, status summary, row count, artifact reference, checksum prefix, and audit reference in `frontend/admin/src/components/usage/UsageExportPanel.tsx`.
- [x] T062 [P] [US3] Implement `UsageExportDetailPage` with export detail loading, pending/completed/failed/denied states, artifact metadata, filter snapshot, and safe next steps in `frontend/admin/src/components/usage/UsageExportDetailPage.tsx`.
- [x] T063 [US3] Connect drilldown loading, row selection, export creation, export detail navigation, and mutation toasts to `UsagePage` in `frontend/admin/src/components/usage/UsagePage.tsx`.
- [x] T064 [US3] Add event drilldown and export detail API client calls to `frontend/admin/src/api/client.ts`.
- [x] T065 [US3] Add event drilldown, export create, export detail, and export audit persistence endpoints to `src/multi_agent_platform/api/routers/admin_react.py`.
- [x] T066 [US3] Update `src/multi_agent_platform/admin/usage/react_usage.py` to create safe export summaries for completed, pending, failed, denied, and delayed artifact cases.
- [x] T067 [US3] Update `tests/unit/admin/usage/test_react_usage_service.py` to prove export summaries hide local paths and unsafe storage internals.
- [x] T068 [US3] Update `tests/contract/test_admin_react_contract.py` to include event drilldown and export detail contract assertions.

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation manifest, generated checks, redaction scans, and final task completion.

- [x] T069 [P] Update Spec 035 QA API/database guide in `specs/035-react-usage-and-cost-analytics/qa035.md`.
- [x] T070 [P] Update Spec 035 UI walkthrough in `specs/035-react-usage-and-cost-analytics/qa035_ui.md`.
- [x] T071 [P] Update Spec 035 local QA environment in `specs/035-react-usage-and-cost-analytics/.env.qa035`.
- [x] T072 [P] Update Spec 035 manual user guide in `specs/035-react-usage-and-cost-analytics/qa035_user_guide.md`.
- [x] T073 [P] Update Spec 035 reviewer notes in `specs/035-react-usage-and-cost-analytics/pr_notes.md`.
- [x] T074 Update React roadmap validation manifest for QA035 routes, curl commands, quality commands, Playwright flows, screenshots, and redaction scans in `specs/_autopilot/react-ui-roadmap/035-react-usage-and-cost-analytics/validation.yml`.
- [x] T075 [P] Update usage React feature notes in `README.md`.
- [x] T076 [P] Update local validation quickstart notes in `docs/quickstart.md`.
- [x] T077 Run `uv run python scripts/frontend/generate_admin_react_types.py --check` and fix drift in `scripts/frontend/generate_admin_react_types.py` or `frontend/admin/src/api/generated/reactAdminApi.ts`.
- [x] T078 Run focused backend tests with `uv run pytest --no-cov tests/unit/api/test_admin_usage_react_schema.py tests/unit/admin/usage/test_react_usage_service.py tests/performance/usage/test_react_usage_queries.py tests/contract/test_admin_react_contract.py tests/integration/test_admin_react_routes.py` and fix failures in touched files.
- [x] T079 Run frontend checks with `npm run typecheck`, `npm run test`, and `npm run build` in `frontend/admin` and fix failures in `frontend/admin/src/`.
- [x] T080 Run QA document validation with `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/035-react-usage-and-cost-analytics` and fix Spec 035 docs.
- [x] T081 Run full Spec QA with `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/035-react-usage-and-cost-analytics/validation.yml` and fix active-spec failures only.
- [x] T082 Run Playwright UI validation with `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/035-react-usage-and-cost-analytics/validation.yml --start-processes` and fix active-spec failures only.
- [x] T083 Run redaction scan `rg -n "qa035-secret-value|raw prompt|raw completion|memory content|authorization header|provider token|credential value|credential reference|raw tool payload|/Users/|unauthorized tenant label|private message" /tmp/qa035-* output/playwright/qa035_ui || true` and remove unsafe QA035 evidence if any appears.
- [x] T084 Mark completed tasks in `specs/035-react-usage-and-cost-analytics/tasks.md` after implementation and validation pass.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational; MVP scope.
- **User Story 2 (Phase 4)**: Depends on Foundational and can be implemented after US1 once dashboard and filter orchestration exist.
- **User Story 3 (Phase 5)**: Depends on Foundational and can be implemented after US1/US2 drilldown targets are available.
- **Polish (Phase 6)**: Depends on the desired user stories and validation artifacts.

### User Story Dependencies

- **US1**: No story dependency after Foundational; delivers the dashboard health MVP.
- **US2**: Uses shared filters and summary shell from US1 but must remain independently testable with rollup fixtures.
- **US3**: Uses rollup row context from US2 for drilldown entry points but must also support direct event/export routes.

### Parallel Opportunities

- Setup tasks T002 through T007 are parallelizable.
- Schema/service/performance/frontend fixture tests T012, T019, T020, T029, T030, and T031 can be prepared in parallel once schemas are sketched.
- US1 component tests T032 through T034 can be developed in parallel with backend integration test T035.
- US1 component implementations T037 through T041 can be implemented in parallel after `UsagePage` contracts are stable.
- US2 tests T045 through T048 and US2 components T049 through T051 can be split by frontend/backend ownership.
- US3 tests T056 through T059 and components T060 through T062 can be split safely by file.
- Documentation tasks T069 through T076 can be drafted in parallel after implementation behavior is stable.

## Parallel Example: User Story 1

```bash
Task: "Add summary card status, currency precision, latency, and unavailable usage tests in frontend/admin/src/components/usage/UsageSummaryCards.test.tsx"
Task: "Add daily trend chart and accessible fallback tests in frontend/admin/src/components/usage/UsageTrendPanel.test.tsx"
Task: "Implement UsageHeader with active scope, selected range, freshness, confidence summary, and export action in frontend/admin/src/components/usage/UsageHeader.tsx"
Task: "Implement UsageSummaryCards with tokens, estimated cost, event count, latency, unavailable usage, and confirmed/estimated coverage cards in frontend/admin/src/components/usage/UsageSummaryCards.tsx"
```

## Parallel Example: User Story 2

```bash
Task: "Implement UsageGroupSelector with backend-provided group choices and disabled reasons in frontend/admin/src/components/usage/UsageGroupSelector.tsx"
Task: "Implement UsageAttributionBadges for graph node, gateway operation, physical attempt, governed tool, archived reference, and pricing confidence summaries in frontend/admin/src/components/usage/UsageAttributionBadges.tsx"
Task: "Add backend rollup dimension and safe attribution tests in tests/unit/admin/usage/test_react_usage_service.py"
```

## Parallel Example: User Story 3

```bash
Task: "Implement UsageEventDrilldown with safe event rows, trace/audit references, confidence labels, provider/model/workflow/agent/prompt labels, attempt summaries, and bounded result copy in frontend/admin/src/components/usage/UsageEventDrilldown.tsx"
Task: "Implement UsageExportPanel with active safe filter snapshot preview, create-export action, status summary, row count, artifact reference, checksum prefix, and audit reference in frontend/admin/src/components/usage/UsageExportPanel.tsx"
Task: "Extend export creation, export detail, cross-tenant denial, Auth0-shaped, and local-principal route tests in tests/integration/test_admin_react_routes.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup and Foundational phases.
2. Implement US1 platform and tenant dashboard health views.
3. Validate US1 with focused backend, frontend, and route tests before adding advanced attribution.

### Incremental Delivery

1. Deliver US1 for safe dashboard health.
2. Add US2 for backend-owned attribution rollups and grouping.
3. Add US3 for bounded drilldowns and audited export evidence.
4. Complete docs, generated type drift checks, Spec QA, Playwright, and redaction scans.

### Parallel Team Strategy

1. Complete backend schemas, projections, route wiring, generated types, and shared fixtures together.
2. Split components by file: dashboard/cards/trend, rollup/attribution, and drilldown/export.
3. Split tests by layer: unit schema/service, integration/contract, component, and Playwright QA.

## Notes

- `[P]` tasks touch distinct files or can proceed once shared contracts are stable.
- Existing `/admin/usage` Jinja pages remain available until Spec 037 explicitly proves parity retirement.
- Browser code must not own tenant authorization, confidence calculation, redaction, or export filtering.
- Stop if usage scope, audit persistence, export storage, or redaction behavior becomes ambiguous.
