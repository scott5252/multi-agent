# Tasks: React Admin Migration Hardening And Jinja Retirement

**Input**: Design documents from `specs/037-react-admin-migration-hardening-and-jinja-retirement/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`
**Tests**: Required by FR-011 through FR-018, SC-001 through SC-010, and the React UI roadmap dual-auth validation policy.
**Organization**: Tasks are grouped by user story so each story remains independently testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches distinct files or does not depend on unfinished tasks.
- **[Story]**: User story label for story phases only.
- Every task names an exact file path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare Spec 037 artifacts and additive migration-hardening structure.

- [X] T001 Verify `.specify/feature.json` points to `specs/037-react-admin-migration-hardening-and-jinja-retirement` and `AGENTS.md` references `specs/037-react-admin-migration-hardening-and-jinja-retirement/plan.md`.
- [X] T002 [P] Create migration-hardening React component directory at `frontend/admin/src/components/migrationHardening/`.
- [X] T003 [P] Create migration-hardening frontend fixture file at `frontend/admin/src/test/migrationHardeningTestData.ts`.
- [X] T004 [P] Create backend schema module at `src/multi_agent_platform/api/schemas/admin_migration_hardening_react.py`.
- [X] T005 [P] Create React-safe migration projection package at `src/multi_agent_platform/admin/migration_hardening/`.
- [X] T006 [P] Create performance test directory at `tests/performance/migration_hardening/`.
- [X] T007 [P] Create QA037 documentation placeholders in `specs/037-react-admin-migration-hardening-and-jinja-retirement/qa037.md`, `specs/037-react-admin-migration-hardening-and-jinja-retirement/qa037_ui.md`, `specs/037-react-admin-migration-hardening-and-jinja-retirement/.env.qa037`, `specs/037-react-admin-migration-hardening-and-jinja-retirement/qa037_user_guide.md`, and `specs/037-react-admin-migration-hardening-and-jinja-retirement/pr_notes.md`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish safe contracts, route inventory, generated types, protected routes, and shared fixtures before story work.

- [X] T008 Define safe text helpers, unsafe marker validation, status enums, route decision enums, scope enums, budget enums, and formatted primitives in `src/multi_agent_platform/api/schemas/admin_migration_hardening_react.py`.
- [X] T009 Define `AdminMigrationHardeningDashboard`, summary, route group, route entry, rollback plan, performance budget, performance measurement, accessibility audit, sweep summary, and migration problem schemas in `src/multi_agent_platform/api/schemas/admin_migration_hardening_react.py`.
- [X] T010 Add schema validators rejecting raw secrets, credential values, provider headers, raw prompts, raw completions, raw memory, private messages, raw run payloads, raw tool payloads, raw package payloads, raw test transcripts, private briefing preferences, full Telegram identifiers, link tokens after creation, stack traces, local filesystem paths, and unauthorized tenant labels in `src/multi_agent_platform/api/schemas/admin_migration_hardening_react.py`.
- [X] T011 [P] Add schema tests for safe dashboard payloads, retirement eligibility, bounded rows, rollback plans, sweep summaries, performance measurements, and unsafe marker rejection in `tests/unit/api/test_admin_migration_hardening_react_schema.py`.
- [X] T012 Implement deterministic QA037 constants, route inventory fixtures, parity evidence, migration decisions, rollback evidence, performance measurements, accessibility evidence, redaction sweep, tenant-isolation sweep, and safe state fixtures in `src/multi_agent_platform/admin/migration_hardening/react_migration_hardening.py`.
- [X] T013 Implement backend-owned route classification, actor scoping, tenant-safe filtering, retirement eligibility, redirect preservation, rollback, budget, accessibility, sweep, and problem builders in `src/multi_agent_platform/admin/migration_hardening/react_migration_hardening.py`.
- [X] T014 [P] Add service tests for platform dashboard, tenant-admin dashboard, tenant-user dashboard, retirement gating, blocked route evidence, rollback plan, performance budget, accessibility audit, redaction sweep, tenant isolation sweep, and unsafe marker safety in `tests/unit/admin/test_migration_hardening_service.py`.
- [X] T015 [P] Add bounded projection/performance tests for route groups, route entries, route lists, and dashboard projections in `tests/performance/migration_hardening/test_react_migration_hardening_queries.py`.
- [X] T016 Extend `scripts/frontend/generate_admin_react_types.py` with generated TypeScript interfaces and assert helpers for all migration hardening schemas.
- [X] T017 Regenerate `frontend/admin/src/api/generated/reactAdminApi.ts` from `scripts/frontend/generate_admin_react_types.py`.
- [X] T018 Add API client helpers for migration dashboard, route groups, and rollback plan in `frontend/admin/src/api/client.ts`.
- [X] T019 Add protected React routes and endpoints for `/admin/app`, `/admin/app/migration`, `/admin/app/migration/bootstrap.json`, `/admin/app/migration/routes.json`, and `/admin/app/migration/rollback.json` in `src/multi_agent_platform/api/routers/admin_react.py`.
- [X] T020 Register migration hardening React surfaces as authenticated protected surfaces in `src/multi_agent_platform/auth/policy.py`.
- [X] T021 Wire `/admin/app` and `/admin/app/migration` into `frontend/admin/src/App.tsx`.
- [X] T022 Add migration hardening route registration or disabled-route behavior in `frontend/admin/src/routes.tsx`.
- [X] T023 Add migration dashboard styles, parity matrix layout, status pills, budget rows, rollback panels, and responsive no-overlap rules in `frontend/admin/src/styles/admin.css`.
- [X] T024 [P] Add contract coverage for migration dashboard, routes, rollback, OpenAPI schemas, shell route, and protected-surface registration in `tests/contract/test_admin_react_contract.py`.
- [X] T025 [P] Add integration coverage for unauthenticated, Auth0-shaped, local-principal platform, tenant-admin, tenant-user, route list, rollback, and tenant-scope behavior in `tests/integration/test_admin_react_routes.py`.
- [X] T026 [P] Add frontend fixture data mirroring generated schemas in `frontend/admin/src/test/migrationHardeningTestData.ts`.

**Checkpoint**: Backend contracts, generated browser types, protected routes, and shared fixtures are ready.

---

## Phase 3: User Story 1 - Verify Admin Route Parity And Safe Navigation (Priority: P1)

**Goal**: Platform and tenant administrators can inspect route parity, React paths, fallback decisions, direct-link behavior, and safe navigation status.

**Independent Test**: Open `/admin/app` as platform-admin and tenant-admin-acme, verify the parity matrix, route decisions, React paths, fallback notices, and denied unauthenticated/cross-tenant behavior.

### Tests for User Story 1

- [X] T027 [P] [US1] Add migration dashboard rendering, loading, denied, and route matrix tests in `frontend/admin/src/components/migrationHardening/MigrationHardeningPage.test.tsx`.
- [X] T028 [P] [US1] Add summary and parity matrix component tests in `frontend/admin/src/components/migrationHardening/MigrationSummaryAndMatrix.test.tsx`.
- [X] T029 [P] [US1] Extend platform and tenant route parity integration tests in `tests/integration/test_admin_react_routes.py`.

### Implementation for User Story 1

- [X] T030 [US1] Implement `MigrationHardeningPage` orchestration, bootstrap loading, scope-aware state, refresh handling, and safe error rendering in `frontend/admin/src/components/migrationHardening/MigrationHardeningPage.tsx`.
- [X] T031 [P] [US1] Implement `MigrationSummaryHeader` with overall status, route counts, update timestamp, and refresh action in `frontend/admin/src/components/migrationHardening/MigrationSummaryHeader.tsx`.
- [X] T032 [P] [US1] Implement `MigrationParityMatrix` with grouped route entries, React paths, legacy paths, decisions, auth modes, scope requirements, preserved redirect state, evidence, fallback notices, and audit references in `frontend/admin/src/components/migrationHardening/MigrationParityMatrix.tsx`.
- [X] T033 [P] [US1] Implement `MigrationStatePanel` for retained fallback, blocked retirement, rollback, stale evidence, denied, and audit-unavailable states in `frontend/admin/src/components/migrationHardening/MigrationStatePanel.tsx`.
- [X] T034 [US1] Update `src/multi_agent_platform/admin/migration_hardening/react_migration_hardening.py` to project platform and tenant-safe route groups for Specs 026 through 036.
- [X] T035 [US1] Update `src/multi_agent_platform/api/routers/admin_react.py` to return dashboard and route projections for `/admin/app/migration/bootstrap.json` and `/admin/app/migration/routes.json`.

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Retire Or Redirect Legacy UI Cautiously (Priority: P2)

**Goal**: Operators can see which legacy routes redirect, alias, remain fallback, or qualify for future retirement, and can follow rollback instructions.

**Independent Test**: Open migration hardening as platform-admin, inspect retirement candidates and retained fallbacks, fetch rollback JSON, and confirm no route is marked retirement-allowed without evidence.

### Tests for User Story 2

- [X] T036 [P] [US2] Add rollback plan and route decision tests in `frontend/admin/src/components/migrationHardening/RollbackAndRouteDecisionPanel.test.tsx`.
- [X] T037 [P] [US2] Add backend route decision, retirement gating, and rollback service tests in `tests/unit/admin/test_migration_hardening_service.py`.
- [X] T038 [P] [US2] Extend integration tests for rollback JSON, retirement candidates, retained fallback notices, and direct-link metadata in `tests/integration/test_admin_react_routes.py`.

### Implementation for User Story 2

- [X] T039 [P] [US2] Implement `RollbackPlanPanel` with feature flag, asset version, owner, steps, verification steps, reviewed timestamp, and audit evidence in `frontend/admin/src/components/migrationHardening/RollbackPlanPanel.tsx`.
- [X] T040 [P] [US2] Implement `RouteDecisionBadges` for redirect, alias, retained fallback, retirement candidate, blocked, and React primary decisions in `frontend/admin/src/components/migrationHardening/RouteDecisionBadges.tsx`.
- [X] T041 [US2] Connect rollback plan loading and route-decision evidence to `MigrationHardeningPage` in `frontend/admin/src/components/migrationHardening/MigrationHardeningPage.tsx`.
- [X] T042 [US2] Update `src/multi_agent_platform/admin/migration_hardening/react_migration_hardening.py` to project rollback plan, feature flag defaults, asset version labels, direct-link preservation notes, and retirement-allowed rules.
- [X] T043 [US2] Update `src/multi_agent_platform/api/routers/admin_react.py` with `/admin/app/migration/rollback.json`.

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Validate Performance, Accessibility, Visual Stability, And Guidance (Priority: P3)

**Goal**: Reviewers can inspect performance budget, accessibility audit, redaction sweep, tenant-isolation sweep, screenshots, and final migration guidance.

**Independent Test**: Open migration hardening, verify budget and audit panels, run Playwright screenshots, run redaction and tenant sweeps, and confirm reviewer/operator guidance identifies rollback steps.

### Tests for User Story 3

- [X] T044 [P] [US3] Add performance, accessibility, and sweep component tests in `frontend/admin/src/components/migrationHardening/EvidencePanels.test.tsx`.
- [X] T045 [P] [US3] Add backend performance budget, accessibility audit, redaction sweep, and tenant-isolation sweep tests in `tests/unit/admin/test_migration_hardening_service.py`.
- [X] T046 [P] [US3] Extend performance tests for dashboard build limits and bounded route groups in `tests/performance/migration_hardening/test_react_migration_hardening_queries.py`.

### Implementation for User Story 3

- [X] T047 [P] [US3] Implement `PerformanceBudgetPanel` with route bootstrap, interactivity, compressed asset, status, evidence, and mitigation rows in `frontend/admin/src/components/migrationHardening/PerformanceBudgetPanel.tsx`.
- [X] T048 [P] [US3] Implement `AccessibilityAuditPanel` with viewport coverage, keyboard, focus, landmark, label, contrast-sensitive state, text-overlap, and evidence references in `frontend/admin/src/components/migrationHardening/AccessibilityAuditPanel.tsx`.
- [X] T049 [P] [US3] Implement `MigrationSweepPanel` for redaction and tenant-isolation sweep status, checked artifacts, unsafe match counts, safe summaries, and evidence references in `frontend/admin/src/components/migrationHardening/MigrationSweepPanel.tsx`.
- [X] T050 [US3] Connect performance, accessibility, redaction, and tenant-isolation panels to `MigrationHardeningPage` in `frontend/admin/src/components/migrationHardening/MigrationHardeningPage.tsx`.
- [X] T051 [US3] Update `src/multi_agent_platform/admin/migration_hardening/react_migration_hardening.py` to project deterministic QA037 performance, accessibility, redaction, tenant-isolation, and visual evidence.

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation manifest, generated checks, redaction scans, task closure, and final migration evidence.

- [X] T052 [P] Update Spec 037 QA API/database guide in `specs/037-react-admin-migration-hardening-and-jinja-retirement/qa037.md`.
- [X] T053 [P] Update Spec 037 UI walkthrough in `specs/037-react-admin-migration-hardening-and-jinja-retirement/qa037_ui.md`.
- [X] T054 [P] Update Spec 037 local QA environment in `specs/037-react-admin-migration-hardening-and-jinja-retirement/.env.qa037`.
- [X] T055 [P] Update Spec 037 manual user guide in `specs/037-react-admin-migration-hardening-and-jinja-retirement/qa037_user_guide.md`.
- [X] T056 [P] Update Spec 037 reviewer notes in `specs/037-react-admin-migration-hardening-and-jinja-retirement/pr_notes.md`.
- [X] T057 Update React roadmap validation manifest for QA037 route curls, quality commands, Playwright flows, screenshots, accessibility/performance checks, and redaction scans in `specs/_autopilot/react-ui-roadmap/037-react-admin-migration-hardening-and-jinja-retirement/validation.yml`.
- [X] T058 [P] Update final React migration notes in `README.md`.
- [X] T059 [P] Update local validation quickstart notes in `docs/quickstart.md`.
- [X] T060 Run `uv run python scripts/frontend/generate_admin_react_types.py --check` and fix drift in `scripts/frontend/generate_admin_react_types.py` or `frontend/admin/src/api/generated/reactAdminApi.ts`.
- [X] T061 Run focused backend tests with `uv run pytest --no-cov tests/unit/api/test_admin_migration_hardening_react_schema.py tests/unit/admin/test_migration_hardening_service.py tests/performance/migration_hardening/test_react_migration_hardening_queries.py tests/contract/test_admin_react_contract.py tests/integration/test_admin_react_routes.py` and fix failures in touched files.
- [X] T062 Run frontend checks with `npm run typecheck`, `npm run test`, and `npm run build` in `frontend/admin` and fix failures in `frontend/admin/src/`.
- [X] T063 Run QA document validation with `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/037-react-admin-migration-hardening-and-jinja-retirement` and fix Spec 037 docs.
- [X] T064 Run full Spec QA with `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/037-react-admin-migration-hardening-and-jinja-retirement/validation.yml` and fix active-spec failures only.
- [X] T065 Run Playwright UI validation with `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/037-react-admin-migration-hardening-and-jinja-retirement/validation.yml --start-processes` and fix active-spec failures only.
- [X] T066 Run redaction scan `rg -n "qa037-secret-value|bot token|webhook secret|credential value|authorization header|raw prompt|raw completion|memory content|private message|raw run|run result|raw tool payload|full telegram|link token|stack trace|/Users/|unauthorized tenant label" /tmp/qa037-* output/playwright/qa037_ui || true` and remove unsafe QA037 evidence if any appears.
- [X] T067 Mark completed tasks in `specs/037-react-admin-migration-hardening-and-jinja-retirement/tasks.md` after implementation and validation pass.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational and is the MVP route parity matrix.
- **User Story 2 (Phase 4)**: Depends on Foundational and can be validated after US1.
- **User Story 3 (Phase 5)**: Depends on Foundational and can be validated after US1 and US2.
- **Polish (Phase 6)**: Depends on all desired user stories and validation artifacts.

### User Story Dependencies

- **US1**: No story dependency after Foundational.
- **US2**: Uses route decision data from US1 but remains independently testable through rollback JSON and retirement evidence.
- **US3**: Uses dashboard shell from US1 but remains independently testable through evidence panels and sweeps.

### Parallel Opportunities

- Setup tasks T002 through T007 are parallelizable.
- Schema, service, performance, contract, integration, and fixture tests T011, T014, T015, T024, T025, and T026 can be prepared in parallel after schema sketching.
- US1 components T031 through T033 can be developed in parallel with service/router wiring.
- US2 rollback and badge components T039 and T040 can be developed in parallel.
- US3 evidence panels T047 through T049 can be developed in parallel.
- Documentation tasks T052 through T059 can be drafted in parallel after behavior stabilizes.

## Parallel Example: User Story 1

```bash
Task: "Implement MigrationSummaryHeader with overall status, route counts, update timestamp, and refresh action in frontend/admin/src/components/migrationHardening/MigrationSummaryHeader.tsx"
Task: "Implement MigrationParityMatrix with grouped route entries, React paths, legacy paths, decisions, auth modes, scope requirements, preserved redirect state, evidence, fallback notices, and audit references in frontend/admin/src/components/migrationHardening/MigrationParityMatrix.tsx"
```

## Parallel Example: User Story 2

```bash
Task: "Implement RollbackPlanPanel with feature flag, asset version, owner, steps, verification steps, reviewed timestamp, and audit evidence in frontend/admin/src/components/migrationHardening/RollbackPlanPanel.tsx"
Task: "Implement RouteDecisionBadges for redirect, alias, retained fallback, retirement candidate, blocked, and React primary decisions in frontend/admin/src/components/migrationHardening/RouteDecisionBadges.tsx"
```

## Parallel Example: User Story 3

```bash
Task: "Implement PerformanceBudgetPanel with route bootstrap, interactivity, compressed asset, status, evidence, and mitigation rows in frontend/admin/src/components/migrationHardening/PerformanceBudgetPanel.tsx"
Task: "Implement AccessibilityAuditPanel with viewport coverage, keyboard, focus, landmark, label, contrast-sensitive state, text-overlap, and evidence references in frontend/admin/src/components/migrationHardening/AccessibilityAuditPanel.tsx"
```

## Implementation Strategy

1. Complete setup and foundational contracts.
2. Deliver US1 first as the MVP route parity and safe navigation dashboard.
3. Add US2 rollback, retirement, redirect, and fallback decision evidence.
4. Add US3 performance, accessibility, redaction, tenant-isolation, and visual evidence.
5. Complete docs, QA validation, redaction scans, and task closure to finish the React UI roadmap.
