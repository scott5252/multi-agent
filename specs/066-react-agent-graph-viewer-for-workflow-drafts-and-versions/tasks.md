# Tasks: React Agent Graph Viewer For Workflow Drafts And Versions

**Input**: Design documents from `specs/066-react-agent-graph-viewer-for-workflow-drafts-and-versions/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/agent-graph-viewer.md, quickstart.md

**Tests**: Tests are required because this spec adds visible React behavior, generated TypeScript graph contracts, client fetch helpers, accessibility behavior, and browser-first QA evidence.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish typed graph contracts and reusable frontend data access before UI work.

- [X] T001 Add `AgentCommunicationGraph` and related schema imports to `scripts/frontend/generate_admin_react_types.py`
- [X] T002 Refresh generated graph types and assertion helpers in `frontend/admin/src/api/generated/reactAdminApi.ts`
- [X] T003 Add draft and version graph client helpers in `frontend/admin/src/api/client.ts`
- [X] T004 Add Agent Graph fixture data in `frontend/admin/src/test/workflowBuilderTestData.ts`
- [X] T005 Create `frontend/admin/src/components/workflows/AgentGraphPanel.tsx`
- [X] T006 Create `frontend/admin/src/components/workflows/AgentGraphPanel.test.tsx`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core graph transformation, safe display helpers, and state modeling required by every story.

- [X] T007 Define AgentGraphPanel props, selection state, loading/error state helpers, and category label helpers in `frontend/admin/src/components/workflows/AgentGraphPanel.tsx`
- [X] T008 Implement safe node and edge conversion to React Flow nodes/edges in `frontend/admin/src/components/workflows/AgentGraphPanel.tsx`
- [X] T009 Implement badge tone, category tone, and status label helpers in `frontend/admin/src/components/workflows/AgentGraphPanel.tsx`
- [X] T010 Implement selected item derivation for graph, node, and edge details in `frontend/admin/src/components/workflows/AgentGraphPanel.tsx`
- [X] T011 Add base Agent Graph CSS for responsive layout, fixed canvas sizing, node categories, edge labels, lists, and detail panel in `frontend/admin/src/styles/admin.css`
- [X] T012 Add visible-copy redaction test helper in `frontend/admin/src/components/workflows/AgentGraphPanel.test.tsx`

**Checkpoint**: The reusable panel can render typed graph data without page integration.

---

## Phase 3: User Story 1 - Inspect Draft Communication Graph (Priority: P1)

**Goal**: Authorized admins can inspect a workflow draft communication graph on the existing draft detail page.

**Independent Test**: Seed a draft graph fixture with all supported node categories, render the draft page, and verify canvas labels, list labels, edge labels, badges, and safe detail content.

### Tests for User Story 1

- [X] T013 [P] [US1] Add AgentGraphPanel draft rendering tests in `frontend/admin/src/components/workflows/AgentGraphPanel.test.tsx`
- [X] T014 [P] [US1] Add WorkflowBuilderPage draft graph fetch/render tests in `frontend/admin/src/components/workflows/WorkflowBuilderPage.test.tsx`

### Implementation for User Story 1

- [X] T015 [US1] Render draft graph nodes, categories, graph badges, and edge labels in `frontend/admin/src/components/workflows/AgentGraphPanel.tsx`
- [X] T016 [US1] Fetch draft agent graph data from `WorkflowBuilderPage` using `fetchDraftAgentGraph` in `frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx`
- [X] T017 [US1] Place the draft AgentGraphPanel after the existing workflow graph preview without removing JSON or validation panels in `frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx`
- [X] T018 [US1] Add draft loading, empty, partial, and error rendering paths in `frontend/admin/src/components/workflows/AgentGraphPanel.tsx`

**Checkpoint**: Draft graph viewer is independently functional and tested.

---

## Phase 4: User Story 2 - Inspect Published Version Communication Graph (Priority: P2)

**Goal**: Authorized admins can inspect a published workflow version communication graph and provenance on the existing version detail state.

**Independent Test**: Render a workflow version detail fixture, fetch its graph, and verify published provenance, partial-state copy, and safe graph content.

### Tests for User Story 2

- [X] T019 [P] [US2] Add published graph rendering and partial-state tests in `frontend/admin/src/components/workflows/AgentGraphPanel.test.tsx`
- [X] T020 [P] [US2] Add WorkflowBuilderPage version graph fetch/render tests in `frontend/admin/src/components/workflows/WorkflowBuilderPage.test.tsx`

### Implementation for User Story 2

- [X] T021 [US2] Fetch published version graph data from `WorkflowBuilderPage` using `fetchVersionAgentGraph` in `frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx`
- [X] T022 [US2] Render published graph provenance and partial-state messaging in `frontend/admin/src/components/workflows/AgentGraphPanel.tsx`
- [X] T023 [US2] Place the published AgentGraphPanel near the version detail panel in `frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx`
- [X] T024 [US2] Add denied and not-found safe state coverage for version graph fetches in `frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx`

**Checkpoint**: Published version graph viewer is independently functional and tested.

---

## Phase 5: User Story 3 - Select Graph Details (Priority: P3)

**Goal**: Admins can select graph nodes and edges and inspect safe backend-provided details.

**Independent Test**: Select representative nodes and edges from the canvas and list controls, then verify detail panel content and redaction scan results.

### Tests for User Story 3

- [X] T025 [P] [US3] Add selected node and edge detail tests in `frontend/admin/src/components/workflows/AgentGraphPanel.test.tsx`
- [X] T026 [P] [US3] Add visible-copy redaction assertions for detail rendering in `frontend/admin/src/components/workflows/AgentGraphPanel.test.tsx`

### Implementation for User Story 3

- [X] T027 [US3] Add selectable canvas node and edge interactions in `frontend/admin/src/components/workflows/AgentGraphPanel.tsx`
- [X] T028 [US3] Add selected item detail panel with badges, references, summaries, statuses, and safe links in `frontend/admin/src/components/workflows/AgentGraphPanel.tsx`
- [X] T029 [US3] Ensure selected item detail layout stays stable for long labels in `frontend/admin/src/styles/admin.css`

**Checkpoint**: Selection and safe details are independently functional and tested.

---

## Phase 6: User Story 4 - Use Accessible List Alternative (Priority: P4)

**Goal**: Admins can understand and select graph nodes and edges through keyboard-readable lists.

**Independent Test**: Navigate node and edge lists with keyboard controls, select items, and verify detail parity with canvas selection.

### Tests for User Story 4

- [X] T030 [P] [US4] Add keyboard list selection tests in `frontend/admin/src/components/workflows/AgentGraphPanel.test.tsx`
- [X] T031 [P] [US4] Add Testing Library accessibility assertions for graph, node list, edge list, and detail regions in `frontend/admin/src/components/workflows/AgentGraphPanel.test.tsx`

### Implementation for User Story 4

- [X] T032 [US4] Add keyboard-selectable node and edge list controls in `frontend/admin/src/components/workflows/AgentGraphPanel.tsx`
- [X] T033 [US4] Add accessible labels and region naming for graph canvas, list alternative, and detail panel in `frontend/admin/src/components/workflows/AgentGraphPanel.tsx`
- [X] T034 [US4] Ensure mobile layout keeps lists and detail panel visible without overlap in `frontend/admin/src/styles/admin.css`

**Checkpoint**: Accessible list alternative is independently functional and tested.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, QA, and validation required before moving to Spec 067.

- [X] T035 Create `specs/066-react-agent-graph-viewer-for-workflow-drafts-and-versions/qa066.md` with setup, seeded graph checks, state checks, redaction scans, and troubleshooting
- [X] T036 Create `specs/066-react-agent-graph-viewer-for-workflow-drafts-and-versions/qa066_ui.md` with desktop/mobile browser walkthrough, selected detail steps, screenshots, and reviewer evidence
- [X] T037 Create `specs/066-react-agent-graph-viewer-for-workflow-drafts-and-versions/.env.qa066` with dedicated QA database, local-principal auth, static secret references, and QA artifact storage
- [X] T038 Create `specs/066-react-agent-graph-viewer-for-workflow-drafts-and-versions/qa066_user_guide.md` with detailed manual QA workflow
- [X] T039 Add reviewer notes in `specs/066-react-agent-graph-viewer-for-workflow-drafts-and-versions/pr_notes.md`
- [X] T040 Reconcile `specs/_autopilot/graphical-ui-roadmap/066-react-agent-graph-viewer-for-workflow-drafts-and-versions/validation.yml` with implemented browser routes and screenshots
- [X] T041 Run focused frontend tests for AgentGraphPanel and WorkflowBuilderPage
- [X] T042 Run generated TypeScript check, frontend typecheck/test/build, Ruff, mypy, and QA document validation
- [X] T043 Run Spec 066 `run_spec_qa.py`, Playwright desktop/mobile validation, curl coverage review, and multi-agent curl regression

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 setup must complete before component implementation.
- Phase 2 foundational helpers block all user story rendering.
- User Story 1 is the MVP and must complete before full page integration is considered stable.
- User Story 2 depends on shared fetch and panel helpers from User Story 1.
- User Story 3 depends on rendered graph nodes and edges.
- User Story 4 depends on selection and list rendering.
- Polish and validation run after all user stories are implemented.

### Parallel Opportunities

- T013 and T014 can be written in parallel after foundational helpers exist.
- T019 and T020 can be written in parallel after version fixture data exists.
- T025 and T026 can be written in parallel with selected detail implementation.
- T030 and T031 can be written in parallel after list controls exist.
- QA docs can be drafted in parallel with final validation preparation.

## Implementation Strategy

### MVP First

1. Add generated graph types and client helpers.
2. Build the reusable AgentGraphPanel.
3. Integrate draft graph rendering into WorkflowBuilderPage.
4. Validate draft graph UI tests before version integration.

### Incremental Delivery

1. Draft graph viewer.
2. Published version graph viewer.
3. Node and edge selection details.
4. Accessible list selection parity.
5. Desktop/mobile Playwright evidence and full validation.

## Notes

- Do not add a new backend graph route unless implementation proves the Spec 065 routes are insufficient.
- Do not remove the existing workflow graph preview, JSON inspector, validation, publish, revision, or sharing panels.
- Do not add editable graph behavior.
- Do not create fake production graph records.
- Mark each task complete in this file when implemented.
