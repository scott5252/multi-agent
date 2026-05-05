# Tasks: React Workflow Builder

**Input**: Design documents from `specs/030-react-workflow-builder/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required. The feature specification mandates backend schema/service
coverage, contract and generated TypeScript drift checks, Auth0-shaped and
local-principal route coverage, tenant isolation, redaction tests, graph
accessibility tests, performance tests, frontend component coverage,
Playwright evidence, QA docs, and full quality gates.

**Organization**: Tasks are grouped by user story so each story remains
independently testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and has no
  dependency on an incomplete task.
- **[Story]**: User story label from `spec.md`.
- Every task includes an exact file path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare backend, frontend, and test folders for the React workflow builder.

- [X] T001 Add backend workflow builder schema module in `src/multi_agent_platform/api/schemas/admin_workflow_builder.py`
- [X] T002 [P] Add workflow builder aggregation/service module in `src/multi_agent_platform/admin/workflow_builder.py`
- [X] T003 [P] Add React workflow builder component directory in `frontend/admin/src/components/workflows/`
- [X] T004 [P] Add React workflow builder fixture file in `frontend/admin/src/test/workflowBuilderTestData.ts`
- [X] T005 [P] Add performance test directory in `tests/performance/workflows/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define shared contracts, generated types, route protection, and deterministic fixtures.

**CRITICAL**: No user story implementation can proceed until these tasks are done.

- [X] T006 Extend `src/multi_agent_platform/api/schemas/admin_workflow_builder.py` with builder envelope, draft document, section, reference option, graph preview, validation, publish readiness, revision, JSON inspector, save request, publish request, and mutation result models
- [X] T007 Extend `scripts/frontend/generate_admin_react_types.py` to emit Spec 030 workflow builder contracts and assertion helpers
- [X] T008 Regenerate `frontend/admin/src/api/generated/reactAdminApi.ts`
- [X] T009 Add Spec 030 OpenAPI and generated-contract drift checks in `tests/contract/test_admin_react_contract.py`
- [X] T010 Add workflow builder schema redaction and validation tests in `tests/unit/api/test_admin_workflow_builder_schema.py`
- [X] T011 Add React client helpers for builder bootstrap, lookups, save, validate, and publish requests in `frontend/admin/src/api/client.ts`
- [X] T012 Register protected React workflow builder route/action surfaces in `src/multi_agent_platform/auth/policy.py`
- [X] T013 Add `/admin/app/workflows` route constants and fallback links in `src/multi_agent_platform/api/routers/admin_react.py`

---

## Phase 3: User Story 1 - Guided Draft Authoring (Priority: P1) MVP

**Goal**: Admins can load the builder, edit guided draft sections, save explicitly, and recover from stale revisions.

**Independent Test**: Open as tenant admin, edit deterministic draft metadata and references, save, verify revision/audit response, then submit stale revision and verify safe conflict.

### Tests for User Story 1

- [X] T014 [P] [US1] Add local-principal builder envelope route tests for tenant and platform scopes in `tests/integration/test_admin_react_routes.py`
- [X] T015 [P] [US1] Add Auth0-shaped builder route tests in `tests/integration/test_admin_react_routes.py`
- [X] T016 [P] [US1] Add unauthenticated, denied, and cross-tenant builder tests in `tests/integration/test_admin_react_routes.py`
- [X] T017 [P] [US1] Add draft bootstrap, reference catalog, explicit save, dirty state, and stale-conflict unit tests in `tests/unit/admin/test_workflow_builder_service.py`
- [X] T018 [P] [US1] Add React draft header and section navigation tests in `frontend/admin/src/components/workflows/WorkflowBuilderPage.test.tsx`
- [X] T019 [P] [US1] Add React guided form panel tests in `frontend/admin/src/components/workflows/WorkflowSectionForm.test.tsx`
- [X] T020 [P] [US1] Add React reference picker tests in `frontend/admin/src/components/workflows/WorkflowReferencePicker.test.tsx`

### Implementation for User Story 1

- [X] T021 [US1] Implement platform and tenant builder bootstrap builders in `src/multi_agent_platform/admin/workflow_builder.py`
- [X] T022 [US1] Implement deterministic draft document and reference catalog builders in `src/multi_agent_platform/admin/workflow_builder.py`
- [X] T023 [US1] Implement explicit save and stale-conflict mutation result builders in `src/multi_agent_platform/admin/workflow_builder.py`
- [X] T024 [US1] Add `/admin/app/workflows` and `/admin/app/workflows/builder.json` routes in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T025 [US1] Add `/admin/app/workflows/lookups.json` route in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T026 [US1] Add `/admin/app/workflows/drafts/{workflow_draft_id}/save` route in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T027 [US1] Add frontend workflow builder fetch/save helpers in `frontend/admin/src/api/client.ts`
- [X] T028 [US1] Implement `WorkflowBuilderPage` in `frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx`
- [X] T029 [US1] Implement `WorkflowSectionForm` in `frontend/admin/src/components/workflows/WorkflowSectionForm.tsx`
- [X] T030 [US1] Implement `WorkflowReferencePicker` in `frontend/admin/src/components/workflows/WorkflowReferencePicker.tsx`
- [X] T031 [US1] Route `/admin/app/workflows` from `frontend/admin/src/App.tsx` and remove it from disabled fallback in `frontend/admin/src/routes.tsx`
- [X] T032 [US1] Add draft header, section rail, dirty state, form, stale conflict, and reference picker styles in `frontend/admin/src/styles/admin.css`

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Graph, Validation, And Accessible Review (Priority: P2)

**Goal**: Admins can understand graph structure, edit graph semantics through safe controls, run validation, and use keyboard/list alternatives.

**Independent Test**: Load graph fixture, inspect graph and lists, edit join policy, validate, and verify backend-owned findings and publish blockers.

### Tests for User Story 2

- [X] T033 [P] [US2] Add graph preview, validation, join policy, and validation route tests in `tests/integration/test_admin_react_routes.py`
- [X] T034 [P] [US2] Add graph builder, join policy, validation finding, and large-workflow unit tests in `tests/unit/admin/test_workflow_builder_service.py`
- [X] T035 [P] [US2] Add graph redaction tests in `tests/unit/api/test_admin_workflow_builder_schema.py`
- [X] T036 [P] [US2] Add graph/list render and keyboard-accessible alternative tests in `frontend/admin/src/components/workflows/WorkflowGraphPanel.test.tsx`
- [X] T037 [P] [US2] Add validation panel component tests in `frontend/admin/src/components/workflows/WorkflowValidationPanel.test.tsx`
- [X] T038 [P] [US2] Add bounded large-workflow performance tests in `tests/performance/workflows/test_workflow_builder_queries.py`

### Implementation for User Story 2

- [X] T039 [US2] Add `@xyflow/react` dependency to `frontend/admin/package.json`
- [X] T040 [US2] Implement graph preview and large-workflow builders in `src/multi_agent_platform/admin/workflow_builder.py`
- [X] T041 [US2] Implement validation summary and finding builders in `src/multi_agent_platform/admin/workflow_builder.py`
- [X] T042 [US2] Add `/admin/app/workflows/drafts/{workflow_draft_id}/validate` route in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T043 [US2] Add validation request helper in `frontend/admin/src/api/client.ts`
- [X] T044 [US2] Implement `WorkflowGraphPanel` with graph canvas and list alternatives in `frontend/admin/src/components/workflows/WorkflowGraphPanel.tsx`
- [X] T045 [US2] Implement `WorkflowValidationPanel` in `frontend/admin/src/components/workflows/WorkflowValidationPanel.tsx`
- [X] T046 [US2] Wire graph and validation panels into `frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx`
- [X] T047 [US2] Add graph, node, edge, branch, join policy, validation, and keyboard-list styles in `frontend/admin/src/styles/admin.css`

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Publish Gate, Evidence, And Revision Review (Priority: P3)

**Goal**: Admins can inspect required evidence, revisions, read-only JSON, and publish decisions safely.

**Independent Test**: Review blocked and ready publish fixtures, inspect revision history and JSON inspector, confirm publish, and verify safe artifact/audit evidence.

### Tests for User Story 3

- [X] T048 [P] [US3] Add publish readiness, evidence, publish action, and revision route tests in `tests/integration/test_admin_react_routes.py`
- [X] T049 [P] [US3] Add publish denial, confirmation, ready fixture, and cross-tenant publish tests in `tests/integration/test_admin_react_routes.py`
- [X] T050 [P] [US3] Add publish readiness, evidence, revision, and JSON inspector unit tests in `tests/unit/admin/test_workflow_builder_service.py`
- [X] T051 [P] [US3] Add JSON inspector and publish redaction tests in `tests/unit/api/test_admin_workflow_builder_schema.py`
- [X] T052 [P] [US3] Add publish panel component tests in `frontend/admin/src/components/workflows/WorkflowPublishPanel.test.tsx`
- [X] T053 [P] [US3] Add revision history and JSON inspector component tests in `frontend/admin/src/components/workflows/WorkflowRevisionPanel.test.tsx`

### Implementation for User Story 3

- [X] T054 [US3] Implement publish readiness, required evidence, revision history, and JSON inspector builders in `src/multi_agent_platform/admin/workflow_builder.py`
- [X] T055 [US3] Implement publish mutation result builders in `src/multi_agent_platform/admin/workflow_builder.py`
- [X] T056 [US3] Add `/admin/app/workflows/drafts/{workflow_draft_id}/publish` route in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T057 [US3] Add publish request helper in `frontend/admin/src/api/client.ts`
- [X] T058 [US3] Implement `WorkflowPublishPanel` in `frontend/admin/src/components/workflows/WorkflowPublishPanel.tsx`
- [X] T059 [US3] Implement `WorkflowRevisionPanel` in `frontend/admin/src/components/workflows/WorkflowRevisionPanel.tsx`
- [X] T060 [US3] Implement `WorkflowJsonInspector` in `frontend/admin/src/components/workflows/WorkflowJsonInspector.tsx`
- [X] T061 [US3] Wire publish, evidence, revision, and JSON inspector panels into `frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx`
- [X] T062 [US3] Add publish gate, evidence, revision, JSON inspector, confirmation, and handoff styles in `frontend/admin/src/styles/admin.css`

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation manifest reconciliation, QA evidence, and final quality gates.

- [X] T063 [P] Update React workflow builder notes in `README.md`
- [X] T064 [P] Update local validation notes in `docs/quickstart.md`
- [X] T065 [P] Create implementation reviewer notes in `specs/030-react-workflow-builder/pr_notes.md`
- [X] T066 Generate QA API/database guide in `specs/030-react-workflow-builder/qa030.md`
- [X] T067 Generate QA UI walkthrough in `specs/030-react-workflow-builder/qa030_ui.md`
- [X] T068 Generate QA environment file in `specs/030-react-workflow-builder/.env.qa030`
- [X] T069 Generate detailed manual user guide in `specs/030-react-workflow-builder/qa030_user_guide.md`
- [X] T070 Reconcile QA030 validation commands and Playwright builder flows in `specs/_autopilot/react-ui-roadmap/030-react-workflow-builder/validation.yml`
- [X] T071 Run frontend build/test commands and record outcomes in `specs/030-react-workflow-builder/pr_notes.md`
- [X] T072 Run backend quality commands and record outcomes in `specs/030-react-workflow-builder/pr_notes.md`
- [X] T073 Run QA docs, Spec QA, and Playwright validation commands and record evidence paths in `specs/030-react-workflow-builder/pr_notes.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup and blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational and provides the MVP builder.
- **User Story 2 (Phase 4)**: Depends on Foundational and integrates with US1 while remaining testable through graph/validation endpoints.
- **User Story 3 (Phase 5)**: Depends on Foundational and integrates with US1/US2 while remaining testable through publish/revision fixtures.
- **Polish (Phase 6)**: Depends on implemented stories.

### Parallel Opportunities

- T002-T005 can run in parallel after T001 is planned.
- T009-T010 and T012 can run in parallel after T006.
- T014-T020 can run in parallel after foundational contracts exist.
- T033-T038 can run in parallel after graph/validation contracts exist.
- T048-T053 can run in parallel after publish/revision contracts exist.
- T063-T065 can run in parallel with QA document drafting.

## Parallel Example: User Story 1

```bash
Task: "Add local-principal builder envelope route tests in tests/integration/test_admin_react_routes.py"
Task: "Add draft bootstrap and explicit save unit tests in tests/unit/admin/test_workflow_builder_service.py"
Task: "Add React guided form panel tests in frontend/admin/src/components/workflows/WorkflowSectionForm.test.tsx"
Task: "Add React reference picker tests in frontend/admin/src/components/workflows/WorkflowReferencePicker.test.tsx"
```

## Implementation Strategy

1. Complete schemas, generated contracts, route protection, and client helpers.
2. Deliver User Story 1 as the MVP guided draft authoring route.
3. Add User Story 2 graph review, validation, and accessible list alternatives.
4. Add User Story 3 publish gate, evidence, revision, and read-only JSON review.
5. Finish QA docs, validation manifest, screenshots, and full quality evidence.

## Notes

- Do not retire or weaken existing Jinja workflow routes.
- Do not call live providers, Telegram, credential stores, or external tools in QA.
- Do not render raw prompts, completions, memory, private messages, provider responses, Telegram updates, tool payloads, stack traces, local paths, or unauthorized tenant labels.
- Stop if tenant scope, publish safety, evidence freshness, graph semantics, revision handling, credential diagnostics, or redaction behavior becomes ambiguous.
