# Tasks: Runtime Agent Communication Graph For Runs

**Input**: Design documents from `specs/067-runtime-agent-communication-graph-for-runs/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/runtime-agent-graph.md, quickstart.md

**Tests**: Tests are required because this spec adds a new runtime graph contract, tenant-scoped route behavior, generated TypeScript surface, React workbench behavior, QA seed data, Playwright screenshots, and curl regression coverage.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish runtime graph contracts, type generation, and deterministic QA seed ownership before feature work.

- [X] T001 Extend `src/multi_agent_platform/api/schemas/admin_agent_graph.py` with runtime graph source/status/evidence/provenance fields
- [X] T002 Add runtime graph type generation entries in `scripts/frontend/generate_admin_react_types.py`
- [X] T003 Refresh generated runtime graph types in `frontend/admin/src/api/generated/reactAdminApi.ts`
- [X] T004 Add `fetchRunAgentGraph` client helper in `frontend/admin/src/api/client.ts`
- [X] T005 Create runtime graph projection module in `src/multi_agent_platform/operations/runtime_agent_graph.py`
- [X] T006 Create deterministic QA067 seed script in `scripts/qa/seed_runtime_agent_graph_qa067.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build runtime evidence mapping and safe status rules used by every story.

- [X] T007 Implement topology loading from runtime execution bundle and published workflow version evidence in `src/multi_agent_platform/operations/runtime_agent_graph.py`
- [X] T008 Implement run-step-to-node mapping and status precedence in `src/multi_agent_platform/operations/runtime_agent_graph.py`
- [X] T009 Implement runtime timeline evidence mapping in `src/multi_agent_platform/operations/runtime_agent_graph.py`
- [X] T010 Implement handoff, approval, gateway, tool, delivery, lineage, and artifact evidence reference mapping in `src/multi_agent_platform/operations/runtime_agent_graph.py`
- [X] T011 Implement partial and unmapped evidence handling in `src/multi_agent_platform/operations/runtime_agent_graph.py`
- [X] T012 Add shared runtime graph fixtures in `tests/fixtures/runtime_agent_graph.py`
- [X] T013 Add reusable runtime graph UI fixture data in `frontend/admin/src/test/workbenchTestData.ts`
- [X] T014 Add runtime status/badge rendering support in `frontend/admin/src/components/workflows/AgentGraphPanel.tsx`
- [X] T015 Add runtime graph CSS refinements in `frontend/admin/src/styles/admin.css`

**Checkpoint**: Runtime graph projection can produce a safe graph payload and the existing graph panel can render runtime statuses.

---

## Phase 3: User Story 1 - Inspect Completed Run Communication (Priority: P1)

**Goal**: Authorized admins can inspect a completed run communication graph with safe evidence references.

**Independent Test**: Seed a completed run and verify the runtime graph route and workbench panel show completed node/edge statuses, safe evidence references, and accessible list summaries.

### Tests for User Story 1

- [X] T016 [P] [US1] Add completed runtime graph projection tests in `tests/unit/operations/test_runtime_agent_graph.py`
- [X] T017 [P] [US1] Add completed runtime graph route tests in `tests/integration/api/test_admin_runtime_agent_graph_api.py`
- [X] T018 [P] [US1] Add runtime graph workbench rendering tests in `frontend/admin/src/components/workbench/RuntimeAgentGraphPanel.test.tsx`

### Implementation for User Story 1

- [X] T019 [US1] Wire `GET /admin/runs/{workflow_run_id}/agent-graph` in `src/multi_agent_platform/api/routers/admin_run_inspection.py`
- [X] T020 [US1] Add runtime graph fetch/render integration to `frontend/admin/src/components/workbench/WorkbenchPage.tsx`
- [X] T021 [US1] Render completed runtime graph evidence without replacing timeline panels in `frontend/admin/src/components/workbench/WorkbenchTimeline.tsx`
- [X] T022 [US1] Add safe completed-run evidence output to `scripts/qa/seed_runtime_agent_graph_qa067.py`

**Checkpoint**: Completed run graph is independently functional and tested.

---

## Phase 4: User Story 2 - Diagnose Failed Branch (Priority: P2)

**Goal**: Authorized operators can identify failed or retrying runtime nodes and edges.

**Independent Test**: Seed a failed/retrying branch and verify failed and retry-scheduled statuses plus safe evidence detail appear on the correct graph items.

### Tests for User Story 2

- [X] T023 [P] [US2] Add failed and retry-scheduled projection tests in `tests/unit/operations/test_runtime_agent_graph.py`
- [X] T024 [P] [US2] Add visible-copy redaction assertions for failed evidence in `tests/integration/api/test_admin_runtime_agent_graph_api.py`
- [X] T025 [P] [US2] Add selected failed-node UI tests in `frontend/admin/src/components/workbench/RuntimeAgentGraphPanel.test.tsx`

### Implementation for User Story 2

- [X] T026 [US2] Map failed and retry-scheduled run evidence to action-first node/edge statuses in `src/multi_agent_platform/operations/runtime_agent_graph.py`
- [X] T027 [US2] Add failed/retry safe evidence summaries to the QA067 seed in `scripts/qa/seed_runtime_agent_graph_qa067.py`
- [X] T028 [US2] Ensure selected failed-node detail renders safe evidence in `frontend/admin/src/components/workflows/AgentGraphPanel.tsx`

**Checkpoint**: Failed and retrying branch diagnostics are independently functional and tested.

---

## Phase 5: User Story 3 - Inspect Paused Or Manual-Resolution Run (Priority: P3)

**Goal**: Authorized admins can see where a run is waiting, paused, or manual-resolution required.

**Independent Test**: Seed paused approval, handoff, and manual-resolution evidence and verify graph status, details, and list alternatives identify the blocked node or edge.

### Tests for User Story 3

- [X] T029 [P] [US3] Add paused/waiting/manual-resolution projection tests in `tests/unit/operations/test_runtime_agent_graph.py`
- [X] T030 [P] [US3] Add paused/manual-resolution route tests in `tests/integration/api/test_admin_runtime_agent_graph_api.py`
- [X] T031 [P] [US3] Add waiting-state accessible list UI tests in `frontend/admin/src/components/workbench/RuntimeAgentGraphPanel.test.tsx`

### Implementation for User Story 3

- [X] T032 [US3] Map approval, handoff, waiting-child, and manual-resolution evidence in `src/multi_agent_platform/operations/runtime_agent_graph.py`
- [X] T033 [US3] Add paused/manual-resolution QA seed records in `scripts/qa/seed_runtime_agent_graph_qa067.py`
- [X] T034 [US3] Render waiting/manual-resolution selected details and badges in `frontend/admin/src/components/workflows/AgentGraphPanel.tsx`

**Checkpoint**: Paused and manual-resolution runtime graph states are independently functional and tested.

---

## Phase 6: User Story 4 - Handle Partial Or Denied Runtime Evidence (Priority: P4)

**Goal**: Runtime graph requests show truthful partial, empty, and denied states without leaking protected content.

**Independent Test**: Exercise partial evidence, missing run evidence, not-found runs, and cross-tenant denial through API and UI tests.

### Tests for User Story 4

- [X] T035 [P] [US4] Add partial and unmapped evidence projection tests in `tests/unit/operations/test_runtime_agent_graph.py`
- [X] T036 [P] [US4] Add denied/not-found/cross-tenant route tests in `tests/integration/api/test_admin_runtime_agent_graph_api.py`
- [X] T037 [P] [US4] Add partial/error runtime graph UI tests in `frontend/admin/src/components/workbench/RuntimeAgentGraphPanel.test.tsx`

### Implementation for User Story 4

- [X] T038 [US4] Enforce tenant fail-closed behavior and safe problem details in `src/multi_agent_platform/api/routers/admin_run_inspection.py`
- [X] T039 [US4] Render partial, empty, denied, and error runtime graph states in `frontend/admin/src/components/workbench/WorkbenchPage.tsx`
- [X] T040 [US4] Add partial and denied QA seed/API coverage in `scripts/qa/seed_runtime_agent_graph_qa067.py`

**Checkpoint**: Partial and denied states are independently functional and tested.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, QA, curl coverage, and validation required before moving to Spec 068.

- [X] T041 Update `curl_testing.md` with `/admin/runs/{workflow_run_id}/agent-graph` success and cross-tenant denied commands
- [X] T042 Reconcile `specs/_autopilot/graphical-ui-roadmap/067-runtime-agent-communication-graph-for-runs/validation.yml` with QA067 seed, routes, browser flows, and screenshots
- [X] T043 Create `specs/067-runtime-agent-communication-graph-for-runs/qa067.md` with setup, runtime graph checks, state checks, redaction scans, and troubleshooting
- [X] T044 Create `specs/067-runtime-agent-communication-graph-for-runs/qa067_ui.md` with desktop/mobile run graph walkthrough, selected detail steps, screenshots, and reviewer evidence
- [X] T045 Create `specs/067-runtime-agent-communication-graph-for-runs/.env.qa067` with dedicated QA database, local-principal auth, static secret references, and QA artifact storage
- [X] T046 Create `specs/067-runtime-agent-communication-graph-for-runs/qa067_user_guide.md` with detailed manual QA workflow
- [X] T047 Add reviewer notes in `specs/067-runtime-agent-communication-graph-for-runs/pr_notes.md`
- [X] T048 Run generated TypeScript check, frontend typecheck/test/build, Ruff, mypy, focused backend tests, and QA document validation
- [X] T049 Run Spec 067 `run_spec_qa.py`, Playwright runtime graph validation, curl coverage review, and multi-agent curl regression

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 setup must complete before projection, route, and UI work.
- Phase 2 foundational runtime evidence mapping blocks all user stories.
- User Story 1 is the MVP and should be completed before failed/paused specialization.
- User Story 2 and User Story 3 can build on the same projection and UI primitives after User Story 1.
- User Story 4 depends on route and projection foundations but can be tested independently once fail-closed behavior exists.
- Polish and validation run after all user stories are implemented.

### Parallel Opportunities

- T016, T017, and T018 can run in parallel after foundational projection helpers exist.
- T023, T024, and T025 can run in parallel after failed/retry mapping is introduced.
- T029, T030, and T031 can run in parallel after paused/manual-resolution mapping is introduced.
- T035, T036, and T037 can run in parallel after partial/denied behavior is introduced.
- QA docs can be drafted while final validation manifest and curl coverage are reconciled.

## Implementation Strategy

### MVP First

1. Add runtime graph contract extensions and generated types.
2. Build runtime projection from published topology, run steps, and timeline events.
3. Add Admin run inspection route.
4. Integrate runtime graph into operations workbench without replacing timeline panels.
5. Validate completed run graph API and UI.

### Incremental Delivery

1. Completed runtime graph.
2. Failed/retrying branch diagnostics.
3. Paused/manual-resolution state diagnostics.
4. Partial/denied/empty state handling.
5. QA docs, Playwright evidence, and curl regression.

## Notes

- Do not add message-level interaction persistence in Spec 067.
- Do not create fake production run records.
- Do not display raw prompts, completions, credentials, provider payloads, private channel messages, memory contents, stack traces, or raw tool outputs.
- Preserve existing operations workbench timeline, branch, gateway, tool, delivery, lineage, replay, and export panels.
- Mark each task complete in this file when implemented.
