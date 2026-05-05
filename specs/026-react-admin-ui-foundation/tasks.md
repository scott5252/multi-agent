# Tasks: React Admin UI Foundation

**Input**: Design documents from `specs/026-react-admin-ui-foundation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required. The feature specification mandates unit, contract,
backend route, dual-auth-mode, Playwright, QA document, and quickstart
validation.

**Organization**: Tasks are grouped by user story so each story remains
independently testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and has no
  dependency on an incomplete task
- **[Story]**: User story label from `spec.md`
- Every task includes an exact file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the frontend workspace, static/build placeholders, and
developer tooling required by every story.

- [x] T001 Create npm package metadata and scripts in `frontend/admin/package.json`
- [x] T002 Generate and commit npm lockfile for the React admin workspace in `frontend/admin/package-lock.json`
- [x] T003 [P] Add Node runtime guidance for the React admin workspace in `frontend/admin/.nvmrc`
- [x] T004 [P] Configure Vite app build, dev proxy, and FastAPI asset base in `frontend/admin/vite.config.ts`
- [x] T005 [P] Configure strict TypeScript app and node build settings in `frontend/admin/tsconfig.json` and `frontend/admin/tsconfig.node.json`
- [x] T006 [P] Configure Vitest, Testing Library, and jsdom setup in `frontend/admin/vitest.config.ts` and `frontend/admin/src/test/setup.ts`
- [x] T007 [P] Add the Vite HTML entry shell in `frontend/admin/index.html`
- [x] T008 [P] Create FastAPI static asset placeholder directory in `src/multi_agent_platform/web_admin/static/react/.gitkeep`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define backend-owned contracts, generated type workflow, feature
flags, and router inclusion before story work begins.

**CRITICAL**: No user story work can begin until this phase is complete.

- [x] T009 Define Pydantic React admin response schemas in `src/multi_agent_platform/api/schemas/admin_react.py`
- [x] T010 Add React admin feature flag and static asset settings in `src/multi_agent_platform/config/settings.py`
- [x] T011 Add the React admin Jinja host template in `src/multi_agent_platform/web_admin/templates/admin_react/app.html`
- [x] T012 Add the initial FastAPI React admin router skeleton in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T013 Register the React admin router in `src/multi_agent_platform/api/main.py`
- [x] T014 Create generated TypeScript contract workflow script in `scripts/frontend/generate_admin_react_types.py`
- [x] T015 Generate initial browser contract types in `frontend/admin/src/api/generated/reactAdminApi.ts`

**Checkpoint**: Foundation ready; user story implementation can now proceed.

---

## Phase 3: User Story 1 - Open Authenticated React Admin Entry (Priority: P1) MVP

**Goal**: Authorized Auth0-backed and local-principal administrators can open
`/admin/app`, see safe identity/scope metadata, and return to existing Jinja
admin pages.

**Independent Test**: Sign in as an authorized admin in both supported auth
modes, open `/admin/app`, verify safe principal/scope display and fallback
links, and verify unauthorized access fails closed.

### Tests for User Story 1

- [x] T016 [P] [US1] Add Pydantic schema unit tests for safe principal/scope payloads in `tests/unit/api/test_admin_react_schema.py`
- [x] T017 [P] [US1] Add FastAPI route tests for Auth0-backed principal resolution and denied access in `tests/integration/test_admin_react_routes.py`
- [x] T018 [P] [US1] Add FastAPI route tests for `AUTH_MODE=local_principal` admin entry and bootstrap behavior in `tests/integration/test_admin_react_routes.py`
- [x] T019 [P] [US1] Add React shell render and fallback-link tests in `frontend/admin/src/App.test.tsx`

### Implementation for User Story 1

- [x] T020 [US1] Implement schema helpers for safe principal, scope, version, and action-token payloads in `src/multi_agent_platform/api/schemas/admin_react.py`
- [x] T021 [US1] Implement `/admin/app` HTML shell and `/admin/app/bootstrap.json` bootstrap routes in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T022 [US1] Include the built React asset references and safe bootstrap URL in `src/multi_agent_platform/web_admin/templates/admin_react/app.html`
- [x] T023 [US1] Implement typed bootstrap fetch client in `frontend/admin/src/api/client.ts`
- [x] T024 [US1] Implement the React app entry and route skeleton in `frontend/admin/src/main.tsx`, `frontend/admin/src/App.tsx`, and `frontend/admin/src/routes.tsx`
- [x] T025 [US1] Implement minimal admin shell, scope summary, and safe state components in `frontend/admin/src/components/AdminShell.tsx`, `frontend/admin/src/components/ScopeSummary.tsx`, and `frontend/admin/src/components/StatePanel.tsx`
- [x] T026 [US1] Add responsive foundation styling in `frontend/admin/src/styles/admin.css`
- [x] T027 [US1] Update generated TypeScript contracts from backend schemas in `frontend/admin/src/api/generated/reactAdminApi.ts`

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Fetch Safe Bootstrap And Navigation Metadata (Priority: P2)

**Goal**: The browser receives only backend-authorized bootstrap, scope,
navigation, config, version, feature flag, and manifest data.

**Independent Test**: Request bootstrap/config/manifest endpoints as platform,
tenant, unauthorized, and cross-tenant principals and verify safe fields,
omissions, and fail-closed responses.

### Tests for User Story 2

- [x] T028 [P] [US2] Add contract tests for bootstrap, config, manifest, and generated TypeScript drift checks in `tests/contract/test_admin_react_contract.py`
- [x] T029 [P] [US2] Add tenant-scope, platform-only navigation, audit-failure, cross-tenant denial, and redaction route tests in `tests/integration/test_admin_react_routes.py`
- [x] T030 [P] [US2] Add frontend bootstrap contract rendering tests in `frontend/admin/src/bootstrapContract.test.ts`

### Implementation for User Story 2

- [x] T031 [US2] Convert existing admin shell navigation, audit visibility recording, and available scopes into React-safe navigation payloads in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T032 [US2] Implement `/admin/app/config.json` and `/admin/app/manifest.json` routes in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T033 [US2] Add safe asset manifest parsing and unavailable-state handling in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T034 [US2] Extend generated contract script checks for backend schema drift in `scripts/frontend/generate_admin_react_types.py`
- [x] T035 [US2] Render authorized navigation, feature flags, version, and unavailable states in `frontend/admin/src/components/AdminShell.tsx` and `frontend/admin/src/App.tsx`

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Use Reversible Migration Guardrails (Priority: P3)

**Goal**: Existing Jinja admin pages remain available, future React domain
routes stay disabled until flagged by later specs, and asset failures fail
safely.

**Independent Test**: Open existing Jinja admin routes, try disabled future
React routes, and simulate missing/malformed asset manifests without exposing
filesystem paths or raw configuration.

### Tests for User Story 3

- [x] T036 [P] [US3] Add fallback and existing Jinja route preservation tests in `tests/integration/test_admin_react_routes.py`
- [x] T037 [US3] Add local-principal Playwright smoke requirements for authenticated, fallback, and denied states in `specs/026-react-admin-ui-foundation/qa026_ui.md`
- [x] T038 [P] [US3] Add static asset missing-manifest safe-state tests in `tests/integration/test_admin_react_routes.py`

### Implementation for User Story 3

- [x] T039 [US3] Enforce backend-controlled React domain route flags and disabled-route fallback behavior in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T040 [US3] Add explicit Jinja fallback destinations and disabled-route labels to React navigation payloads in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T041 [US3] Render disabled future routes and Jinja fallback links safely in `frontend/admin/src/components/AdminShell.tsx`
- [x] T042 [US3] Reconcile the generated Playwright route hint and denied-access smoke steps in `specs/_autopilot/react-ui-roadmap/026-react-admin-ui-foundation/validation.yml`

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, reviewer guidance, QA documents, and final
validation across the completed foundation.

- [x] T043 [P] Update React admin foundation instructions in `README.md`
- [x] T044 [P] Update local validation instructions in `docs/quickstart.md`
- [x] T045 [P] Create implementation reviewer notes in `specs/026-react-admin-ui-foundation/pr_notes.md`
- [x] T046 Generate QA API/database guide in `specs/026-react-admin-ui-foundation/qa026.md`
- [x] T047 Generate QA UI walkthrough in `specs/026-react-admin-ui-foundation/qa026_ui.md`
- [x] T048 Generate QA environment file in `specs/026-react-admin-ui-foundation/.env.qa026`
- [x] T049 Generate detailed manual user guide in `specs/026-react-admin-ui-foundation/qa026_user_guide.md`
- [x] T050 Run frontend build/test commands and record outcomes in `specs/026-react-admin-ui-foundation/pr_notes.md`
- [x] T051 Run backend quality commands and record outcomes in `specs/026-react-admin-ui-foundation/pr_notes.md`
- [x] T052 Run QA docs, Spec QA, and Playwright validation commands and record evidence paths in `specs/026-react-admin-ui-foundation/pr_notes.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational; MVP scope.
- **User Story 2 (Phase 4)**: Depends on Foundational and integrates with US1 contracts, but remains independently testable through endpoint calls.
- **User Story 3 (Phase 5)**: Depends on Foundational and can be validated after US1 fallback links exist.
- **Polish (Phase 6)**: Depends on the implemented user stories.

### User Story Dependencies

- **US1**: Required MVP; no dependency on US2 or US3.
- **US2**: Uses US1 bootstrap shell but can be validated through JSON routes and frontend contract rendering.
- **US3**: Uses US1/US2 navigation payloads to prove reversible migration guardrails.

### Parallel Opportunities

- T003-T008 can run in parallel after T001/T002 are clear.
- T009-T015 touch distinct backend/script/frontend generated files and can be split after setup.
- Test tasks within each story are parallel where they touch different files.
- Documentation tasks T043-T045 can run in parallel with QA document drafting after implementation is stable.

## Parallel Example: User Story 1

```text
Task: "Add Pydantic schema unit tests in tests/unit/api/test_admin_react_schema.py"
Task: "Add React shell render tests in frontend/admin/src/App.test.tsx"
```

After those fail for the expected missing implementation, complete T020-T027
in order and rerun the story tests.

## Implementation Strategy

### MVP First

1. Complete Setup and Foundational phases.
2. Complete User Story 1 tests and implementation.
3. Validate `/admin/app` with Auth0-style route tests and local-principal
   browser smoke before adding richer metadata.

### Incremental Delivery

1. Add User Story 2 bootstrap/navigation/config/manifest contracts.
2. Add User Story 3 fallback and disabled-route guardrails.
3. Finish QA docs and reviewer notes.
4. Run mandatory QA docs, Spec QA, and Playwright validation before starting
   Spec 027.

## Notes

- [P] tasks must stay in disjoint files when executed in parallel.
- Do not add domain page migrations in Spec 026.
- Stop if auth, tenant isolation, audit, secret handling, production provider
  calls, external side effects, or irreversible Jinja retirement becomes
  ambiguous.
