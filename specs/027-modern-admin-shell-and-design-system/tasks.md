# Tasks: Modern Admin Shell And Design System

**Input**: Design documents from `specs/027-modern-admin-shell-and-design-system/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required. The feature specification mandates backend contract/route
coverage, frontend component coverage, keyboard/responsive checks, dual-auth
validation, Playwright evidence, QA documents, and full quality gates.

**Organization**: Tasks are grouped by user story so each story remains
independently testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and has no
  dependency on an incomplete task
- **[Story]**: User story label from `spec.md`
- Every task includes an exact file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Extend the existing React admin workspace with shell design-system
dependencies and token structure.

- [x] T001 Add `lucide-react` dependency and update the lockfile in `frontend/admin/package.json` and `frontend/admin/package-lock.json`
- [x] T002 [P] Add shared design tokens in `frontend/admin/src/styles/tokens.css`
- [x] T003 Import shared tokens from `frontend/admin/src/styles/admin.css`
- [x] T004 [P] Add shell component test utilities in `frontend/admin/src/test/shellTestData.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define backend-owned shell contracts and generated TypeScript
types before the React shell consumes them.

**CRITICAL**: No story implementation can proceed until these tasks are done.

- [x] T005 Extend React admin Pydantic schemas for shell chrome, common states, command/search results, saved-filter chips, page actions, and notifications in `src/multi_agent_platform/api/schemas/admin_react.py`
- [x] T006 Extend generated TypeScript contract workflow for the new shell schemas in `scripts/frontend/generate_admin_react_types.py`
- [x] T007 Regenerate TypeScript contracts in `frontend/admin/src/api/generated/reactAdminApi.ts`
- [x] T008 Add contract tests for shell schema exposure and generated type drift in `tests/contract/test_admin_react_contract.py`

---

## Phase 3: User Story 1 - Navigate The Platform Confidently (Priority: P1) MVP

**Goal**: Platform and tenant administrators can use a clear modern shell with
scope, navigation groups, breadcrumbs, page header, and fallback links.

**Independent Test**: Sign in as platform and tenant admins, open `/admin/app`,
and verify shell navigation, active scope, breadcrumbs, and existing-page links.

### Tests for User Story 1

- [x] T009 [P] [US1] Add backend route tests for Auth0-shaped and local-principal shell chrome metadata in `tests/integration/test_admin_react_routes.py`
- [x] T010 [P] [US1] Add React shell render tests for navigation groups, breadcrumbs, and scope display in `frontend/admin/src/App.test.tsx`
- [x] T011 [P] [US1] Add responsive shell snapshot/behavior tests in `frontend/admin/src/components/shell/AdminShell.test.tsx`

### Implementation for User Story 1

- [x] T012 [US1] Build shell chrome metadata from existing admin shell context in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T013 [US1] Implement React shell layout components in `frontend/admin/src/components/shell/AdminShell.tsx`, `ShellSidebar.tsx`, `ShellTopbar.tsx`, `Breadcrumbs.tsx`, and `ScopeSwitcher.tsx`
- [x] T014 [US1] Update `frontend/admin/src/App.tsx` to render the modern shell and preserve disabled-route fallback behavior
- [x] T015 [US1] Replace legacy shell imports with the new shell component path in `frontend/admin/src/main.tsx` and related files
- [x] T016 [US1] Add responsive shell styling in `frontend/admin/src/styles/admin.css`

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Use Shared UI Components And States (Priority: P2)

**Goal**: The shell provides reusable accessible primitives and common state
surfaces for future domain pages.

**Independent Test**: Render component and state examples, verify accessible
labels, keyboard focus behavior, safe state copy, and desktop/mobile layout.

### Tests for User Story 2

- [x] T017 [P] [US2] Add primitive component tests in `frontend/admin/src/components/primitives/primitives.test.tsx`
- [x] T018 [P] [US2] Add common-state rendering tests in `frontend/admin/src/components/states/CommonState.test.tsx`
- [x] T019 [P] [US2] Add keyboard/drawer behavior tests in `frontend/admin/src/components/shell/KeyboardNavigation.test.tsx`

### Implementation for User Story 2

- [x] T020 [US2] Implement Button, IconButton, Badge, Tabs, Panel, TextInput, and VisuallyHidden primitives in `frontend/admin/src/components/primitives/`
- [x] T021 [US2] Implement Modal, Drawer, ToastRegion, and focus helpers in `frontend/admin/src/components/primitives/`
- [x] T022 [US2] Implement common state components in `frontend/admin/src/components/states/CommonState.tsx`
- [x] T023 [US2] Wire loading, empty, filtered-empty, denied, not-found, validation-error, dependency-unavailable, partial-data, and unexpected-error state descriptors into `frontend/admin/src/App.tsx`
- [x] T024 [US2] Add accessible status, focus, drawer, modal, toast, and density styling in `frontend/admin/src/styles/admin.css`

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Find Authorized Destinations Safely (Priority: P3)

**Goal**: Administrators can use safe command/search, saved-filter chips,
notifications, and contextual actions without exposing unauthorized data.

**Independent Test**: Request command/search metadata as platform, tenant,
unauthorized, and cross-tenant principals and verify only authorized safe
destinations render in React.

### Tests for User Story 3

- [x] T025 [P] [US3] Add backend search metadata route tests for Auth0-shaped, platform, tenant, denied, and cross-tenant behavior in `tests/integration/test_admin_react_routes.py`
- [x] T026 [P] [US3] Add frontend command/search and saved-filter rendering tests in `frontend/admin/src/components/shell/CommandMenu.test.tsx`
- [x] T027 [P] [US3] Add redaction tests for command/search and notification summaries in `tests/unit/api/test_admin_react_schema.py`

### Implementation for User Story 3

- [x] T028 [US3] Implement `/admin/app/search.json` using authorized navigation metadata in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T029 [US3] Add typed frontend API client support for command/search metadata in `frontend/admin/src/api/client.ts`
- [x] T030 [US3] Implement command/search UI in `frontend/admin/src/components/shell/CommandMenu.tsx`
- [x] T031 [US3] Implement saved-filter chips and empty management panel in `frontend/admin/src/components/savedFilters/SavedFilterChips.tsx`
- [x] T032 [US3] Implement notification and page-action rendering in `frontend/admin/src/components/shell/ShellTopbar.tsx`
- [x] T033 [US3] Add command/search, saved-filter, notification, and page-action styling in `frontend/admin/src/styles/admin.css`

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, QA artifacts, validation manifest reconciliation,
and full quality evidence.

- [x] T034 [P] Update React shell/design-system notes in `README.md`
- [x] T035 [P] Update local validation notes in `docs/quickstart.md`
- [x] T036 [P] Create implementation reviewer notes in `specs/027-modern-admin-shell-and-design-system/pr_notes.md`
- [x] T037 Generate QA API/database guide in `specs/027-modern-admin-shell-and-design-system/qa027.md`
- [x] T038 Generate QA UI walkthrough in `specs/027-modern-admin-shell-and-design-system/qa027_ui.md`
- [x] T039 Generate QA environment file in `specs/027-modern-admin-shell-and-design-system/.env.qa027`
- [x] T040 Generate detailed manual user guide in `specs/027-modern-admin-shell-and-design-system/qa027_user_guide.md`
- [x] T041 Reconcile QA027 validation commands and Playwright shell flows in `specs/_autopilot/react-ui-roadmap/027-modern-admin-shell-and-design-system/validation.yml`
- [x] T042 Run frontend build/test commands and record outcomes in `specs/027-modern-admin-shell-and-design-system/pr_notes.md`
- [x] T043 Run backend quality commands and record outcomes in `specs/027-modern-admin-shell-and-design-system/pr_notes.md`
- [x] T044 Run QA docs, Spec QA, and Playwright validation commands and record evidence paths in `specs/027-modern-admin-shell-and-design-system/pr_notes.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational and provides MVP shell value.
- **User Story 2 (Phase 4)**: Depends on Foundational and integrates with US1 layout.
- **User Story 3 (Phase 5)**: Depends on Foundational and uses US1 navigation metadata.
- **Polish (Phase 6)**: Depends on implemented stories.

### Parallel Opportunities

- T002 and T004 touch distinct frontend files after dependency setup.
- T009-T011 can run in parallel after contracts are generated.
- T017-T019 can run in parallel because they cover different component groups.
- T025-T027 can run in parallel after search contract schemas exist.
- T034-T036 can run in parallel with QA document drafting.

## Implementation Strategy

1. Complete setup and backend contract extensions.
2. Deliver the modern shell MVP for navigation, scope, breadcrumbs, and fallback links.
3. Add reusable primitives and common states.
4. Add safe command/search, saved-filter chips, notifications, and page actions.
5. Finish QA docs and validation evidence.

## Notes

- Do not migrate domain pages in Spec 027.
- Do not duplicate backend authorization, saved-filter, or search policy in React.
- Stop if search, saved-filter, notification, tenant isolation, audit, or redaction behavior becomes ambiguous.
