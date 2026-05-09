# Tasks: React Workflow Graph And Agent Role Builder

**Input**: Design documents from `/specs/070-react-workflow-graph-and-agent-role-builder/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/workflow-graph-role-builder.md, quickstart.md  
**Tests**: Required by spec for frontend controls, backend persistence smoke, validation findings, accessibility alternatives, desktop/mobile Playwright, QA docs, and curl regression review.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Capture current component behavior, QA routes, and reviewer notes before implementation.

- [x] T001 Audit existing workflow builder, graph preview, generated API client, validation panel, and test fixtures in specs/070-react-workflow-graph-and-agent-role-builder/implementation_notes.md
- [x] T002 [P] Add reviewer notes scaffold for graph accessibility, redaction, dirty state, responsive UI, and curl coverage in specs/070-react-workflow-graph-and-agent-role-builder/pr_notes.md
- [x] T003 [P] Reconcile Spec 070 validation route hints and browser journey requirements in specs/_autopilot/workflow-setup-roadmap/070-react-workflow-graph-and-agent-role-builder/validation.yml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared document editor helpers and tests required by all user stories.

- [x] T004 Add frontend workflow document helper utilities for keyed collections, safe cloning, stable key generation, dependency checks, and local graph projection in frontend/admin/src/components/workflows/workflowDocumentEditor.ts
- [x] T005 [P] Add unit tests for workflow document helpers, duplicate key detection, dependency warnings, graph projection, and unknown-field preservation in frontend/admin/src/components/workflows/workflowDocumentEditor.test.ts
- [x] T006 Add shared editor UI primitives for collection headers, compact item rows, dependency warnings, section dirty badges, and icon buttons in frontend/admin/src/components/workflows/WorkflowEditorControls.tsx
- [x] T007 [P] Add CSS for workflow editor grids, controls, graph/list responsive framing, and no-overlap mobile behavior in frontend/admin/src/styles/admin.css
- [x] T008 Update workflow builder fixture documents with roles, contracts, nodes, edges, joins, approvals, subworkflows, and annotations in frontend/admin/src/test/workflowBuilderTestData.ts
- [x] T009 [P] Add backend smoke test helpers for full graph documents and invalid graph variants in tests/integration/test_admin_react_routes.py

**Checkpoint**: Shared editor utilities, fixtures, and smoke helpers are ready for story work.

---

## Phase 3: User Story 1 - Build Agent Roles And Contracts (Priority: P1) MVP

**Goal**: Authorized admins can add, edit, duplicate, reorder, delete, save, and reload agent roles and contracts through browser controls.

**Independent Test**: Create or open a workflow draft, add at least three roles and two contracts through visible controls, save, reload, and verify the durable document renders the same roles and contracts without raw JSON editing.

### Tests for User Story 1

- [x] T010 [P] [US1] Add frontend role and contract editor tests for add, edit, duplicate, reorder, delete warnings, dirty state, save payload, and reload fixture rendering in frontend/admin/src/components/workflows/WorkflowBuilderPage.test.tsx
- [x] T011 [P] [US1] Add backend route smoke test proving roles and contracts saved by the React route persist and reload in tests/integration/test_admin_react_routes.py
- [x] T012 [P] [US1] Add validation mapping tests for duplicate role keys, duplicate contract keys, missing contract references, and referenced contract deletion in tests/unit/admin/test_workflow_builder_service.py

### Implementation for User Story 1

- [x] T013 [US1] Add role authoring component with role kind, purpose, responsibilities, contract selectors, prompt/profile placeholders, skill binding summaries, duplicate, reorder, and delete warning controls in frontend/admin/src/components/workflows/WorkflowRoleEditor.tsx
- [x] T014 [US1] Add contract authoring component with contract type, summary, example summary, duplicate, reorder, and dependency warning controls in frontend/admin/src/components/workflows/WorkflowContractEditor.tsx
- [x] T015 [US1] Integrate role and contract local document state, cancel/revert section actions, and Spec 069 full-document save payload assembly in frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx
- [x] T016 [US1] Update metadata section to show section dirty state, save/revert status, and backend mutation summaries without raw payloads in frontend/admin/src/components/workflows/WorkflowSectionForm.tsx
- [x] T017 [US1] Ensure backend section summaries and validation anchors include roles and contracts for the expanded editor in src/multi_agent_platform/admin/workflow_builder.py

**Checkpoint**: User Story 1 can save and reload role and contract edits independently.

---

## Phase 4: User Story 2 - Author Graph Topology And Joins (Priority: P2)

**Goal**: Authorized admins can build role, join, approval, subworkflow, and terminal topology with graph preview and equivalent keyboard-readable lists.

**Independent Test**: Starting from saved roles, add role nodes, a join node, terminal node, converging edges, a join policy, an approval gate, and a subworkflow reference, then save and reload; graph canvas and lists show matching durable state.

### Tests for User Story 2

- [x] T018 [P] [US2] Add frontend topology editor tests for node, edge, join, approval, subworkflow, layout, graph preview, list alternative, save, and reload behavior in frontend/admin/src/components/workflows/WorkflowBuilderPage.test.tsx
- [x] T019 [P] [US2] Add backend route smoke test for persisting nodes, edges, joins, approval gates, subworkflows, and layout annotations in tests/integration/test_admin_react_routes.py
- [x] T020 [P] [US2] Add frontend graph projection helper tests for desktop/mobile node positions and canvas/list count consistency in frontend/admin/src/components/workflows/workflowDocumentEditor.test.ts

### Implementation for User Story 2

- [x] T021 [US2] Add topology editor component for node and edge collection editing, source/target selectors, branch labels, contract selectors, failure behavior, and layout controls in frontend/admin/src/components/workflows/WorkflowTopologyEditor.tsx
- [x] T022 [US2] Add join, approval, and subworkflow editor component with inbound edge selectors, quorum/timeout fields, approval scope, resume behavior, and safe reference summaries in frontend/admin/src/components/workflows/WorkflowJoinApprovalEditor.tsx
- [x] T023 [US2] Update graph preview to render the current dirty document projection plus keyboard-readable node, edge, join, approval, and subworkflow lists in frontend/admin/src/components/workflows/WorkflowGraphPanel.tsx
- [x] T024 [US2] Wire topology, join, approval, subworkflow, and layout state into the builder save/revert flow in frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx
- [x] T025 [US2] Extend backend graph/editor projection helpers for dirty graph section anchors and layout annotation summaries in src/multi_agent_platform/admin/workflow_builder.py

**Checkpoint**: User Story 2 can build and reload a multi-agent graph with a join through UI controls.

---

## Phase 5: User Story 3 - Recover From Invalid Or Stale Graph Edits (Priority: P3)

**Goal**: Invalid, stale, unsafe, unauthorized, and dependency-sensitive edits produce backend-owned findings and safe recovery states.

**Independent Test**: Submit invalid node, edge, join, role, contract, approval, subworkflow, stale revision, and unsafe text changes through the browser and verify the UI renders safe section-specific recovery without persisting invalid changes.

### Tests for User Story 3

- [x] T026 [P] [US3] Add frontend validation rendering tests for duplicate keys, missing nodes, missing roles, invalid quorum, unsupported failure behavior, stale conflicts, and safe reload recovery in frontend/admin/src/components/workflows/WorkflowBuilderPage.test.tsx
- [x] T027 [P] [US3] Add backend route tests for deleting referenced nodes/contracts, invalid quorum, invalid entry node, duplicate keys, cycle rejection if enabled, unsupported branch/failure combinations, unsafe strings, and cross-tenant denial in tests/integration/test_admin_react_routes.py
- [x] T028 [P] [US3] Add validation section mapping tests for nodes, edges, joins, approvals, subworkflows, and layout annotations in tests/unit/admin/test_workflow_builder_service.py

### Implementation for User Story 3

- [x] T029 [US3] Add section-level validation anchors and dependency warning rendering for role, contract, graph, join, approval, and subworkflow editors in frontend/admin/src/components/workflows/WorkflowValidationPanel.tsx
- [x] T030 [US3] Add stale conflict, idempotent replay, validation error, and authorization-denied recovery states to the expanded save flow in frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx
- [x] T031 [US3] Extend backend validation finding section mapping for joins, approvals, subworkflows, layout annotations, and unsupported graph combinations in src/multi_agent_platform/admin/workflow_registry/validation.py
- [x] T032 [US3] Verify safe problem detail and audit summaries for invalid graph save attempts in src/multi_agent_platform/api/routers/admin_react.py

**Checkpoint**: User Story 3 gives safe, actionable validation feedback without browser-owned publish decisions.

---

## Phase 6: Documentation, Curl Coverage, And QA

**Purpose**: Complete required Spec 070 QA artifacts and route coverage review.

- [x] T033 [P] Add Spec 070 QA environment file in specs/070-react-workflow-graph-and-agent-role-builder/.env.qa070
- [x] T034 [P] Add deterministic QA seed script for graph and role builder data in scripts/qa/seed_workflow_graph_role_builder_qa070.py
- [x] T035 [P] Add detailed API/database QA guide in specs/070-react-workflow-graph-and-agent-role-builder/qa070.md
- [x] T036 [P] Add browser-first desktop/mobile UI walkthrough in specs/070-react-workflow-graph-and-agent-role-builder/qa070_ui.md
- [x] T037 [P] Add reviewer user guide with visible-navigation workflow setup steps in specs/070-react-workflow-graph-and-agent-role-builder/qa070_user_guide.md
- [x] T038 [P] Update reviewer notes with redaction, accessibility, responsive, performance, validation, and curl coverage evidence in specs/070-react-workflow-graph-and-agent-role-builder/pr_notes.md
- [x] T039 Review README.md and docs/quickstart.md impact, updating those files if graph/role builder onboarding commands or UI route guidance changed, and record the decision in specs/070-react-workflow-graph-and-agent-role-builder/pr_notes.md
- [x] T040 Update curl_testing.md if Spec 070 changes route behavior; otherwise record unchanged route-family coverage in specs/070-react-workflow-graph-and-agent-role-builder/pr_notes.md
- [x] T041 Update specs/_autopilot/workflow-setup-roadmap/070-react-workflow-graph-and-agent-role-builder/validation.yml with desktop and mobile Playwright journeys for graph/role builder controls
- [x] T042 Update specs/_autopilot/workflow-setup-roadmap/070-react-workflow-graph-and-agent-role-builder/status.json with implementation artifact summary and curl coverage decision

---

## Phase 7: Spec Validation

**Purpose**: Required validation before starting Spec 071.

- [x] T043 Run generated TypeScript freshness check with uv run python scripts/frontend/generate_admin_react_types.py --check
- [x] T044 Run focused backend tests with uv run pytest tests/contract/test_admin_react_contract.py tests/contract/test_workflow_builder_contract.py tests/integration/test_admin_react_routes.py tests/unit/admin/test_workflow_builder_service.py -q --no-cov
- [x] T045 Run frontend workflow tests with cd frontend/admin && npm test -- Workflow
- [x] T046 Run frontend typecheck with cd frontend/admin && npm run typecheck
- [x] T047 Run frontend build with cd frontend/admin && npm run build
- [x] T048 Run repository quality checks with uv run ruff check ., uv run ruff format --check ., and uv run mypy src
- [x] T049 Run QA document validation with bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/070-react-workflow-graph-and-agent-role-builder
- [x] T050 Run uv run python scripts/qa/run_spec_qa.py specs/_autopilot/workflow-setup-roadmap/070-react-workflow-graph-and-agent-role-builder/validation.yml
- [x] T051 Run uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/workflow-setup-roadmap/070-react-workflow-graph-and-agent-role-builder/validation.yml --start-processes
- [x] T052 Run uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa070-after-spec
- [x] T053 Update specs/_autopilot/workflow-setup-roadmap/070-react-workflow-graph-and-agent-role-builder/status.json and specs/_autopilot/workflow-setup-roadmap/queue.json after all validation passes

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 has no dependencies.
- Phase 2 depends on Phase 1 and blocks user-story implementation.
- User Story 1 depends on Phase 2 and is the MVP.
- User Story 2 depends on User Story 1 roles/contracts.
- User Story 3 depends on User Story 1 and User Story 2 save/validation flows.
- Phase 6 depends on all user stories.
- Phase 7 depends on Phase 6.

### User Story Dependencies

- **US1**: Provides durable role and contract authoring.
- **US2**: Builds on US1 by using roles/contracts in graph topology and joins.
- **US3**: Builds on US1 and US2 to exercise invalid combinations and recovery.

### Parallel Opportunities

- T002 and T003 can run after T001 starts.
- T005, T007, and T009 can run in parallel after helper design is clear.
- T010 through T012 can be drafted in parallel for US1.
- T018 through T020 can be drafted in parallel for US2.
- T026 through T028 can be drafted in parallel for US3.
- T033 through T039 can be prepared in parallel once UI routes and seed data are stable.

## Parallel Example: User Story 2

```bash
Task: "Add frontend topology editor tests in frontend/admin/src/components/workflows/WorkflowBuilderPage.test.tsx"
Task: "Add backend route smoke test in tests/integration/test_admin_react_routes.py"
Task: "Add graph projection helper tests in frontend/admin/src/components/workflows/workflowDocumentEditor.test.ts"
```

## Implementation Strategy

1. Complete setup and shared editor helper work.
2. Deliver US1 roles/contracts first and verify save/reload independently.
3. Deliver US2 graph topology, joins, approvals, subworkflows, and graph/list previews.
4. Deliver US3 validation, dependency warnings, stale conflict, and denied states.
5. Finish QA docs, Playwright desktop/mobile journeys, curl coverage review, and required validation.

## Notes

- Do not create commits, stage files, or push branches during the autopilot run.
- Persist all durable changes through Spec 069 full-document save behavior.
- Keep authorization, tenant scoping, validation, publish readiness, redaction, and audit decisions backend-owned.
- Do not expose raw prompts, completions, secrets, credentials, provider payloads, raw tool payloads, raw test transcripts, stack traces, local filesystem paths, or unauthorized tenant labels in UI, tests, docs, screenshots, curl outputs, or audit summaries.
