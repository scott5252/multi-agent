# Tasks: Workflow Registry Full React Parity And Jinja Removal

**Input**: Design artifacts from `specs/040-workflow-registry-full-react-parity-and-jinja-removal/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`

## Phase 1: Setup

- [x] T001 Verify `.specify/feature.json` points to `specs/040-workflow-registry-full-react-parity-and-jinja-removal`
- [x] T002 [P] Review workflow inventory items in `specs/038-jinja-surface-inventory-and-deletion-plan/jinja_inventory.json`
- [x] T003 [P] Confirm current workflow browser routes, TemplateResponse calls, and workflow static references in `src/multi_agent_platform/api/routers/admin_workflow_ui.py`, `src/multi_agent_platform/api/routers/admin_react.py`, `src/multi_agent_platform/web_admin/templates/workflows/`, and `src/multi_agent_platform/web_admin/static/workflow_studio.*`
- [x] T004 [P] Review existing React workflow builder contracts and components from Spec 030 in `src/multi_agent_platform/api/schemas/admin_workflow_builder.py`, `src/multi_agent_platform/admin/workflow_builder.py`, and `frontend/admin/src/components/workflows/`

## Phase 2: Tests First

- [x] T005 [P] [US1] Extend contract tests for workflow registry/create/detail/revision/publish React envelopes in `tests/contract/test_admin_react_contract.py`
- [x] T006 [P] [US1] Extend integration tests for React workflow JSON routes and Auth0-shaped authorization behavior in `tests/integration/test_admin_react_routes.py`
- [x] T007 [P] [US1] Extend frontend tests for workflow list, create, draft edit, validation, publish gate, revision, and version views in `frontend/admin/src/components/workflows/WorkflowBuilderPage.test.tsx` and `frontend/admin/src/App.test.tsx`
- [x] T008 [P] [US1] Add graph accessibility tests for visual graph and keyboard/list alternatives in `frontend/admin/src/components/workflows/WorkflowGraphPanel.test.tsx`
- [x] T009 [P] [US2] Add legacy workflow URL redirect and non-Jinja compatibility tests in `tests/integration/api/test_admin_workflow_ui.py`
- [x] T010 [P] [US2] Add direct-link preservation tests for tenant, filter, saved-filter, draft, revision, publish-gate, and stale-conflict parameters in `tests/unit/api/test_admin_workflow_ui_routes.py`
- [x] T011 [P] [US2] Add legacy workflow POST compatibility tests for create, save, validate, publish, restore, and copy in `tests/integration/api/test_admin_workflow_ui.py`
- [x] T012 [P] [US3] Add workflow template/static scanner coverage through QA docs, reviewer notes, and focused deletion checks in `specs/040-workflow-registry-full-react-parity-and-jinja-removal/qa040.md`
- [x] T013 [P] [US3] Add integration tests proving workflow browser routes no longer return TemplateResponse after deletion in `tests/integration/api/test_admin_workflow_ui.py`
- [x] T014 [P] [US3] Add redaction tests for workflow React envelopes, legacy responses, and reviewer evidence through focused route tests and `specs/040-workflow-registry-full-react-parity-and-jinja-removal/qa040.md`

## Phase 3: User Story 1 - Use Workflow Registry Only Through React (Priority: P1)

**Goal**: Full workflow list/create/draft/validation/publish/revision/version browser journeys are React-backed and backend-owned.

**Independent Test**: Run T005-T008 plus focused React workflow browser tests and verify platform-admin and tenant-admin flows reach workflow surfaces without Jinja rendering.

- [x] T015 [US1] Add workflow registry, create, detail, publish gate, revision, version, sharing, and legacy mapping schemas in `src/multi_agent_platform/api/schemas/admin_workflow_builder.py`
- [x] T016 [US1] Extend workflow builder service builders for registry/create/detail/publish/revision/version/sharing envelopes in `src/multi_agent_platform/admin/workflow_builder.py`
- [x] T017 [US1] Add React workflow registry/create/detail/publish/revision/version JSON routes in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T018 [US1] Add generated TypeScript workflow parity contracts via `scripts/frontend/generate_admin_react_types.py` and `frontend/admin/src/api/generated/reactAdminApi.ts`
- [x] T019 [US1] Verify workflow builder/lookups/mutation client helpers hydrate registry/create/detail/publish/revision/version state in `frontend/admin/src/api/client.ts`
- [x] T020 [US1] Implement React workflow registry list and filter surface in `frontend/admin/src/components/workflows/WorkflowRegistryPage.tsx`
- [x] T021 [US1] Implement React workflow create surface in `frontend/admin/src/components/workflows/WorkflowCreatePage.tsx`
- [x] T022 [US1] Extend React workflow draft/detail surface for direct-link entry states in `frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx`
- [x] T023 [US1] Extend React workflow publish gate and required evidence surface in `frontend/admin/src/components/workflows/WorkflowPublishPanel.tsx`
- [x] T024 [US1] Extend React workflow revision and published version detail surfaces in `frontend/admin/src/components/workflows/WorkflowRevisionPanel.tsx`
- [x] T025 [US1] Add workflow sharing summary and action state component in `frontend/admin/src/components/workflows/WorkflowSharingPanel.tsx`
- [x] T026 [US1] Wire workflow React routes in `frontend/admin/src/App.tsx` and `frontend/admin/src/routes.tsx`
- [x] T027 [US1] Update shell navigation/search workflow destinations to React routes in `src/multi_agent_platform/api/ui/admin_console.py`
- [x] T028 [US1] Ensure workflow graph preview exposes keyboard/list alternatives in `frontend/admin/src/components/workflows/WorkflowGraphPanel.tsx`

## Phase 4: User Story 2 - Preserve Workflow Direct Links And Compatibility (Priority: P2)

**Goal**: Old workflow URLs redirect to React or return non-Jinja safe compatibility/problem responses.

**Independent Test**: Run T009-T011 and direct requests to old workflow list/create/draft/revision/publish/version URLs with representative tenant/query/id state.

- [x] T029 [US2] Add legacy workflow route mapping helpers in `src/multi_agent_platform/api/routers/admin_workflow_ui.py`
- [x] T030 [US2] Convert `/admin/workflows/ui` and `/admin/workflows/new` browser routes to redirects or non-Jinja compatibility responses in `src/multi_agent_platform/api/routers/admin_workflow_ui.py`
- [x] T031 [US2] Convert old draft editor, revision history, publish gate, and version detail browser routes to redirects or non-Jinja compatibility responses in `src/multi_agent_platform/api/routers/admin_workflow_ui.py`
- [x] T032 [US2] Preserve tenant, filter, saved-filter, workflow, draft, revision, publish-gate, and stale-conflict intent in workflow redirect URLs in `src/multi_agent_platform/api/routers/admin_workflow_ui.py`
- [x] T033 [US2] Convert legacy workflow create/save/validate/publish/restore/copy form posts to JSON or redirect compatibility handlers in `src/multi_agent_platform/api/routers/admin_workflow_ui.py`
- [x] T034 [US2] Add non-Jinja workflow compatibility/problem response helpers in `src/multi_agent_platform/api/routers/admin_workflow_ui.py`
- [x] T035 [US2] Add workflow legacy mapping projection to React migration evidence in `src/multi_agent_platform/api/routers/admin_react.py` and `specs/040-workflow-registry-full-react-parity-and-jinja-removal/pr_notes.md`
- [x] T036 [US2] Update workflow direct-link guidance from old workflow URLs to React or compatibility paths in `docs/quickstart.md` and `specs/040-workflow-registry-full-react-parity-and-jinja-removal/quickstart.md`

## Phase 5: User Story 3 - Retire Workflow-Owned Jinja Assets With Evidence (Priority: P3)

**Goal**: Workflow-owned templates/static assets are deleted only after route parity and scanner evidence prove they are obsolete.

**Independent Test**: Run T012-T014, scanner checks, and route tests proving workflow routes no longer render Jinja templates.

- [x] T037 [US3] Delete workflow templates proven obsolete in `src/multi_agent_platform/web_admin/templates/workflows/index.html`, `src/multi_agent_platform/web_admin/templates/workflows/create.html`, `src/multi_agent_platform/web_admin/templates/workflows/draft_editor.html`, `src/multi_agent_platform/web_admin/templates/workflows/publish_gate.html`, `src/multi_agent_platform/web_admin/templates/workflows/revision_history.html`, and `src/multi_agent_platform/web_admin/templates/workflows/version_detail.html`
- [x] T038 [US3] Delete workflow component templates proven obsolete in `src/multi_agent_platform/web_admin/templates/workflows/components/field_help_modal.html`, `src/multi_agent_platform/web_admin/templates/workflows/components/graph_preview.html`, `src/multi_agent_platform/web_admin/templates/workflows/components/reference_picker.html`, and `src/multi_agent_platform/web_admin/templates/workflows/components/validation_panel.html`
- [x] T039 [US3] Delete `src/multi_agent_platform/web_admin/static/workflow_studio.js` and retain `src/multi_agent_platform/web_admin/static/workflow_studio.css` with blocker evidence
- [x] T040 [US3] Retain workflow template view-model helpers in `src/multi_agent_platform/api/ui/admin_workflows.py` because exported model tests and legacy API shape documentation still import them
- [x] T041 [US3] Update workflow Jinja inventory outcomes and migration ledger evidence in `specs/040-workflow-registry-full-react-parity-and-jinja-removal/pr_notes.md`
- [x] T042 [US3] Add rollback notes for workflow template/static restoration in `specs/040-workflow-registry-full-react-parity-and-jinja-removal/pr_notes.md`

## Phase 6: Polish And Validation

- [x] T043 [P] Create QA guide in `specs/040-workflow-registry-full-react-parity-and-jinja-removal/qa040.md`
- [x] T044 [P] Create UI walkthrough in `specs/040-workflow-registry-full-react-parity-and-jinja-removal/qa040_ui.md`
- [x] T045 [P] Create QA environment file in `specs/040-workflow-registry-full-react-parity-and-jinja-removal/.env.qa040`
- [x] T046 [P] Create user guide in `specs/040-workflow-registry-full-react-parity-and-jinja-removal/qa040_user_guide.md`
- [x] T047 Update Spec 040 Playwright route/login steps in `specs/_autopilot/react-ui2-roadmap/040-workflow-registry-full-react-parity-and-jinja-removal/validation.yml`
- [x] T048 Run `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/040-workflow-registry-full-react-parity-and-jinja-removal`
- [x] T049 Run targeted backend tests for workflow React parity, legacy redirects, no-Jinja routes, redaction, and scanner coverage
- [x] T050 Run `cd frontend/admin && npm test -- --run src/components/workflows`
- [x] T051 Run `cd frontend/admin && npm run build`
- [x] T052 Run `uv run ruff check .`, `uv run ruff format --check .`, and `uv run mypy src`
- [x] T053 Run `uv run python scripts/frontend/generate_admin_react_types.py --check`
- [x] T054 Run Spec 040 validation and Playwright through `scripts/qa/run_spec_qa.py` and `scripts/qa/run_playwright_ui.py`

## Dependencies

- Setup T001-T004 must complete before tests and implementation.
- Tests T005-T014 should be added before corresponding implementation tasks.
- US1 T015-T028 establishes React workflow parity required by US2 redirect targets and US3 deletion.
- US2 T029-T036 depends on canonical React workflow routes from US1.
- US3 T037-T042 depends on passing route/scanner tests from US1 and US2.
- Validation T048-T054 depends on QA artifacts T043-T047 and reviewer notes T041-T042.

## Parallel Execution Examples

- T002, T003, and T004 can run in parallel because they inspect distinct source areas.
- T005-T014 can be drafted in parallel because each targets a distinct test file.
- After T015-T019 define contract shape, T020-T025 can proceed across distinct React components.
- T043-T046 can be prepared in parallel after implementation behavior stabilizes.

## Implementation Strategy

1. Establish tests and backend contract extensions for workflow React parity.
2. Make `/admin/app/workflows` cover list, create, draft, validation, publish, revision, version, sharing, graph accessibility, and denied/unavailable states.
3. Convert old workflow browser URLs and form posts to redirects, JSON, or non-Jinja compatibility responses.
4. Delete only workflow-owned templates/static assets proven unused by route tests and scanner evidence.
5. Finish QA docs, Spec QA, Playwright, and queue/status reconciliation before advancing to Spec 041.
