# Tasks: Agent Communication Graph Contracts And Projections

**Input**: Design documents from `specs/065-agent-communication-graph-contracts-and-projections/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/agent-graph-api.md, quickstart.md

**Tests**: Tests are required because this spec adds Admin JSON contracts, tenant authorization behavior, generated TypeScript contracts, and safe rendering guarantees.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish schema and projection files without changing existing workflow preview behavior.

- [x] T001 Create Agent Communication Graph schema module in `src/multi_agent_platform/api/schemas/admin_agent_graph.py`
- [x] T002 Create workflow registry projection module in `src/multi_agent_platform/admin/workflow_registry/agent_graph.py`
- [x] T003 Add test module shells in `tests/unit/admin/test_agent_graph.py`, `tests/unit/api/test_admin_agent_graph_schemas.py`, and `tests/integration/api/test_admin_agent_graph_api.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core contracts and helpers required by every graph endpoint.

- [x] T004 Define graph enums, provenance, layout, badge, reference, accessibility, node, edge, and response schemas in `src/multi_agent_platform/api/schemas/admin_agent_graph.py`
- [x] T005 Implement safe graph text validation and unsafe marker tests in `src/multi_agent_platform/api/schemas/admin_agent_graph.py` and `tests/unit/api/test_admin_agent_graph_schemas.py`
- [x] T006 Implement node and edge category mapping helpers in `src/multi_agent_platform/admin/workflow_registry/agent_graph.py`
- [x] T007 Implement validation badge and reference summary projection helpers in `src/multi_agent_platform/admin/workflow_registry/agent_graph.py`
- [x] T008 Implement accessibility summary and deterministic layout helper functions in `src/multi_agent_platform/admin/workflow_registry/agent_graph.py`

**Checkpoint**: Foundational graph contracts are ready for draft and published projections.

---

## Phase 3: User Story 1 - Inspect Draft Communication Graph (Priority: P1)

**Goal**: Authorized admins can retrieve a safe graph projection for workflow drafts.

**Independent Test**: Create a draft fixture with coordinator, sub-agent, tool, join, approval, handoff, and terminal nodes, then verify draft graph JSON shape, labels, categories, badges, references, and accessibility summaries.

### Tests for User Story 1

- [x] T009 [P] [US1] Add draft projection unit tests in `tests/unit/admin/test_agent_graph.py`
- [x] T010 [P] [US1] Add draft route integration tests in `tests/integration/api/test_admin_agent_graph_api.py`

### Implementation for User Story 1

- [x] T011 [US1] Implement draft graph projection entry point in `src/multi_agent_platform/admin/workflow_registry/agent_graph.py`
- [x] T012 [US1] Add `get_agent_communication_graph_for_draft` service method in `src/multi_agent_platform/admin/workflow_registry/service.py`
- [x] T013 [US1] Add draft graph route `GET /admin/workflows/drafts/{workflow_draft_id}/agent-graph` in `src/multi_agent_platform/api/routers/admin_workflows.py`

**Checkpoint**: Draft graph endpoint is independently functional and tested.

---

## Phase 4: User Story 2 - Inspect Published Bundle Graph (Priority: P2)

**Goal**: Authorized admins can retrieve a safe graph projection for published workflow versions.

**Independent Test**: Publish a workflow bundle, retrieve its agent graph, and verify published provenance, topology, and partial-state handling.

### Tests for User Story 2

- [x] T014 [P] [US2] Add published bundle projection unit tests in `tests/unit/admin/test_agent_graph.py`
- [x] T015 [P] [US2] Add published version route integration tests in `tests/integration/api/test_admin_agent_graph_api.py`

### Implementation for User Story 2

- [x] T016 [US2] Implement published bundle graph projection entry point in `src/multi_agent_platform/admin/workflow_registry/agent_graph.py`
- [x] T017 [US2] Add `get_agent_communication_graph_for_version` service method in `src/multi_agent_platform/admin/workflow_registry/service.py`
- [x] T018 [US2] Add version graph route `GET /admin/workflows/versions/{workflow_version_bundle_id}/agent-graph` in `src/multi_agent_platform/api/routers/admin_workflows.py`

**Checkpoint**: Published version graph endpoint is independently functional and tested.

---

## Phase 5: User Story 3 - Handle Denied, Missing, And Empty States (Priority: P3)

**Goal**: Empty, denied, missing, and cross-tenant cases are truthful, safe, and consistent with workflow Admin APIs.

**Independent Test**: Exercise empty draft graphs, not-found IDs, cross-tenant scope, tenant user denial, and missing auth against both route families.

### Tests for User Story 3

- [x] T019 [P] [US3] Add empty and partial graph tests in `tests/unit/admin/test_agent_graph.py`
- [x] T020 [P] [US3] Add denied, cross-tenant, missing-auth, and not-found route tests in `tests/integration/api/test_admin_agent_graph_api.py`

### Implementation for User Story 3

- [x] T021 [US3] Ensure graph projection state and graph-level badges represent empty and partial data in `src/multi_agent_platform/admin/workflow_registry/agent_graph.py`
- [x] T022 [US3] Ensure workflow service route methods reuse existing fail-closed visibility checks in `src/multi_agent_platform/admin/workflow_registry/service.py`

**Checkpoint**: Non-happy paths are independently functional and tested.

---

## Phase 6: User Story 4 - Verify Safe Rendering Contracts (Priority: P4)

**Goal**: Generated contracts, schema validators, and docs prove the response is safe for the React viewer in Spec 066.

**Independent Test**: Generate/check React Admin API types, inspect OpenAPI for both endpoints, run safe-text tests, and verify no unsafe strings appear in QA/curl artifacts.

### Tests for User Story 4

- [x] T023 [P] [US4] Add schema safe-rendering tests in `tests/unit/api/test_admin_agent_graph_schemas.py`
- [x] T024 [P] [US4] Add OpenAPI route contract assertions in `tests/contract/test_workflow_registry_contract.py`

### Implementation for User Story 4

- [x] T025 [US4] Refresh generated React Admin API contracts in `frontend/admin/src/api/generated/reactAdminApi.ts`
- [x] T026 [US4] Update `curl_testing.md` with draft and published agent graph setup and success-path commands
- [x] T027 [US4] Add contract notes and reviewer notes in `specs/065-agent-communication-graph-contracts-and-projections/contracts/agent-graph-api.md` and `specs/065-agent-communication-graph-contracts-and-projections/pr_notes.md`

**Checkpoint**: Contract consumers and API regression coverage are ready for Spec 066.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, QA, and validation required before moving to Spec 066.

- [x] T028 Create `specs/065-agent-communication-graph-contracts-and-projections/qa065.md` with deterministic setup, seed data, API checks, redaction checks, and troubleshooting
- [x] T029 Create `specs/065-agent-communication-graph-contracts-and-projections/qa065_ui.md` with browser/OpenAPI smoke validation and reviewer evidence steps
- [x] T030 Create `specs/065-agent-communication-graph-contracts-and-projections/.env.qa065` with dedicated QA database, local-principal auth, and QA artifact storage
- [x] T031 Create `specs/065-agent-communication-graph-contracts-and-projections/qa065_user_guide.md` with detailed manual QA workflow
- [x] T032 Reconcile `specs/_autopilot/graphical-ui-roadmap/065-agent-communication-graph-contracts-and-projections/validation.yml` with implemented routes and QA evidence
- [x] T033 Run focused backend tests for agent graph schemas, projections, routes, and workflow registry contracts
- [x] T034 Run generated TypeScript check, Ruff, mypy for touched modules, and QA document validation
- [x] T035 Run Spec 065 `run_spec_qa.py`, Playwright validation, curl coverage review, and multi-agent curl regression

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 setup must complete before schema and projection helpers.
- Phase 2 foundational tasks block all user story implementation.
- User Story 1 is the MVP and must complete before published graph reuse.
- User Story 2 depends on shared projection helpers and version visibility checks.
- User Story 3 can run after the two route families exist.
- User Story 4 depends on route schemas and generated OpenAPI availability.
- Polish and validation run after all user stories are implemented.

### Parallel Opportunities

- T009 and T010 can be written in parallel after foundational helpers exist.
- T014 and T015 can be written in parallel after draft projection patterns land.
- T019 and T020 can be written in parallel once both endpoints exist.
- T023 and T024 can be written in parallel with docs updates.
- QA docs can be drafted in parallel with final validation command preparation.

## Implementation Strategy

### MVP First

1. Complete schema contracts and helpers.
2. Implement draft graph projection and route.
3. Validate draft graph tests before implementing published graph support.

### Incremental Delivery

1. Draft graph endpoint.
2. Published graph endpoint.
3. Empty/denied/partial state handling.
4. Generated contracts, curl coverage, QA docs, and validation.

## Notes

- Do not add a React graph canvas in Spec 065.
- Do not add new database tables or migrations unless implementation proves existing draft and published bundle records are insufficient.
- Do not create, render, log, or document production sample graph records.
- Mark each task complete in this file when implemented.
