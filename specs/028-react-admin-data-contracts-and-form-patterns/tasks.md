# Tasks: React Admin Data Contracts And Form Patterns

**Input**: Design documents from `specs/028-react-admin-data-contracts-and-form-patterns/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required. The feature specification mandates backend schema/route
coverage, frontend helper/component coverage, dual-auth validation, stale
conflict and idempotency tests, redaction tests, Playwright evidence, QA docs,
and full quality gates.

**Organization**: Tasks are grouped by user story so each story remains
independently testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and has no
  dependency on an incomplete task
- **[Story]**: User story label from `spec.md`
- Every task includes an exact file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare contract, route, and frontend folders for reusable
data/form patterns.

- [x] T001 Add backend reusable pattern schema module in `src/multi_agent_platform/api/schemas/admin_patterns.py`
- [x] T002 [P] Add frontend data component directory in `frontend/admin/src/components/data/`
- [x] T003 [P] Add frontend form component directory in `frontend/admin/src/components/forms/`
- [x] T004 [P] Add frontend hook directory in `frontend/admin/src/hooks/`
- [x] T005 [P] Add sample patterns test fixture in `frontend/admin/src/test/patternsTestData.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define generated backend/frontend contracts before the sample page
and form helpers consume them.

**CRITICAL**: No story implementation can proceed until these tasks are done.

- [x] T006 Extend `src/multi_agent_platform/api/schemas/admin_patterns.py` with safe problem, field validation, action, mutation, filter, pagination, sorting, export, evidence, and page envelope models
- [x] T007 Extend `scripts/frontend/generate_admin_react_types.py` to emit the Spec 028 pattern contracts
- [x] T008 Regenerate `frontend/admin/src/api/generated/reactAdminApi.ts`
- [x] T009 Add generated contract drift and OpenAPI reference tests in `tests/contract/test_admin_react_contract.py`
- [x] T010 Add redaction and validation unit tests in `tests/unit/api/test_admin_patterns_schema.py`

---

## Phase 3: User Story 1 - Consume Safe Page Envelopes (Priority: P1) MVP

**Goal**: Future React admin pages can consume a backend-authorized page
envelope with safe records, filters, pagination, sorting, actions, evidence,
and state metadata.

**Independent Test**: Request `/admin/app/patterns.json` as local tenant,
Auth0-shaped platform, unauthorized, and cross-tenant principals and verify
safe, scoped envelope behavior.

### Tests for User Story 1

- [x] T011 [P] [US1] Add backend route tests for local-principal page envelope behavior in `tests/integration/test_admin_react_routes.py`
- [x] T012 [P] [US1] Add backend route tests for Auth0-shaped page envelope behavior in `tests/integration/test_admin_react_routes.py`
- [x] T013 [P] [US1] Add denied and cross-tenant page envelope tests in `tests/integration/test_admin_react_routes.py`
- [x] T014 [P] [US1] Add frontend envelope assertion tests in `frontend/admin/src/bootstrapContract.test.ts`
- [x] T015 [P] [US1] Add sample page render tests in `frontend/admin/src/components/patterns/PatternsPage.test.tsx`

### Implementation for User Story 1

- [x] T016 [US1] Implement backend sample page envelope helpers in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T017 [US1] Add `/admin/app/patterns.json` route in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T018 [US1] Add protected `/admin/app/patterns` route fallback support in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T019 [US1] Add React client support for fetching pattern envelopes in `frontend/admin/src/api/client.ts`
- [x] T020 [US1] Implement sample patterns page component in `frontend/admin/src/components/patterns/PatternsPage.tsx`
- [x] T021 [US1] Route `/admin/app/patterns` from `frontend/admin/src/App.tsx`
- [x] T022 [US1] Add page envelope and sample table styling in `frontend/admin/src/styles/admin.css`

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Submit Forms With Safe Feedback (Priority: P2)

**Goal**: Future React admin pages can use common form helpers for validation,
confirmation, idempotency, dirty-state protection, stale conflicts, safe toasts,
and audit-aware results.

**Independent Test**: Submit the harmless sample form with valid, invalid,
stale, replayed, and confirmation-required inputs.

### Tests for User Story 2

- [x] T023 [P] [US2] Add backend mutation result tests for validation, stale, replayed, confirmation, and accepted outcomes in `tests/integration/test_admin_react_routes.py`
- [x] T024 [P] [US2] Add frontend form helper tests in `frontend/admin/src/components/forms/AdminForm.test.tsx`
- [x] T025 [P] [US2] Add mutation hook tests in `frontend/admin/src/hooks/useAdminMutation.test.tsx`
- [x] T026 [P] [US2] Add stale conflict and dirty-state tests in `frontend/admin/src/components/patterns/PatternsPage.test.tsx`

### Implementation for User Story 2

- [x] T027 [US2] Add `/admin/app/patterns/actions/sample` route in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T028 [US2] Implement sample mutation outcome builder in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T029 [US2] Add React client mutation helper in `frontend/admin/src/api/client.ts`
- [x] T030 [US2] Implement `useAdminMutation` in `frontend/admin/src/hooks/useAdminMutation.ts`
- [x] T031 [US2] Implement validation mapping and dirty-state helpers in `frontend/admin/src/components/forms/AdminForm.tsx`
- [x] T032 [US2] Wire sample form outcomes into `frontend/admin/src/components/patterns/PatternsPage.tsx`
- [x] T033 [US2] Add form, confirmation, conflict, and toast styling in `frontend/admin/src/styles/admin.css`

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Browse, Filter, Export, And Recover Safely (Priority: P3)

**Goal**: Administrators can browse sample records, apply allowed filters,
change sorting, inspect details, and request safe export snapshots through
reusable components.

**Independent Test**: Use the sample patterns page to filter, sort, review
details, request an export snapshot, and verify no unsafe data appears.

### Tests for User Story 3

- [x] T034 [P] [US3] Add backend filter, sorting, pagination, and export snapshot tests in `tests/integration/test_admin_react_routes.py`
- [x] T035 [P] [US3] Add frontend table/filter/export tests in `frontend/admin/src/components/data/AdminDataTable.test.tsx`
- [x] T036 [P] [US3] Add redaction tests for export/evidence summaries in `tests/unit/api/test_admin_patterns_schema.py`

### Implementation for User Story 3

- [x] T037 [US3] Add filter, sorting, and pagination validation to sample envelope helpers in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T038 [US3] Add `/admin/app/patterns/export` sample route in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T039 [US3] Implement reusable table, filter chip, detail panel, and export status components in `frontend/admin/src/components/data/AdminDataTable.tsx`
- [x] T040 [US3] Wire filter/sort/export interactions into `frontend/admin/src/components/patterns/PatternsPage.tsx`
- [x] T041 [US3] Add data table, details, filter, and export styling in `frontend/admin/src/styles/admin.css`

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, QA artifacts, validation manifest reconciliation,
and full quality evidence.

- [x] T042 [P] Update React data/form pattern notes in `README.md`
- [x] T043 [P] Update local validation notes in `docs/quickstart.md`
- [x] T044 [P] Create implementation reviewer notes in `specs/028-react-admin-data-contracts-and-form-patterns/pr_notes.md`
- [x] T045 Generate QA API/database guide in `specs/028-react-admin-data-contracts-and-form-patterns/qa028.md`
- [x] T046 Generate QA UI walkthrough in `specs/028-react-admin-data-contracts-and-form-patterns/qa028_ui.md`
- [x] T047 Generate QA environment file in `specs/028-react-admin-data-contracts-and-form-patterns/.env.qa028`
- [x] T048 Generate detailed manual user guide in `specs/028-react-admin-data-contracts-and-form-patterns/qa028_user_guide.md`
- [x] T049 Reconcile QA028 validation commands and Playwright patterns flows in `specs/_autopilot/react-ui-roadmap/028-react-admin-data-contracts-and-form-patterns/validation.yml`
- [x] T050 Run frontend build/test commands and record outcomes in `specs/028-react-admin-data-contracts-and-form-patterns/pr_notes.md`
- [x] T051 Run backend quality commands and record outcomes in `specs/028-react-admin-data-contracts-and-form-patterns/pr_notes.md`
- [x] T052 Run QA docs, Spec QA, and Playwright validation commands and record evidence paths in `specs/028-react-admin-data-contracts-and-form-patterns/pr_notes.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational and provides the MVP contract surface.
- **User Story 2 (Phase 4)**: Depends on Foundational and integrates with US1 envelope/page.
- **User Story 3 (Phase 5)**: Depends on Foundational and uses US1/US2 patterns.
- **Polish (Phase 6)**: Depends on implemented stories.

### Parallel Opportunities

- T002-T005 can run in parallel after T001.
- T011-T015 can run in parallel after contracts are generated.
- T023-T026 can run in parallel after mutation contracts exist.
- T034-T036 can run in parallel after data contracts exist.
- T042-T044 can run in parallel with QA document drafting.

## Implementation Strategy

1. Complete schema and generated TypeScript contracts.
2. Deliver the safe sample page envelope for `/admin/app/patterns`.
3. Add reusable form and mutation helpers.
4. Add table/filter/sort/export components and sample interactions.
5. Finish QA docs and validation evidence.

## Notes

- Do not migrate major domain pages in Spec 028.
- Do not duplicate authorization, tenant scoping, filter validation, action acceptance, stale conflict checks, export authorization, or redaction in React.
- Stop if action token semantics, tenant isolation, audit evidence, exports, or redaction behavior becomes ambiguous.
