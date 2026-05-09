# Tasks: Durable Agent Interaction Evidence And Replay Graph

**Input**: Design documents from `specs/068-durable-agent-interaction-evidence-and-replay-graph/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/interaction-replay-graph.md, quickstart.md

**Tests**: Tests are required because this spec adds durable runtime persistence, worker instrumentation, graph replay projection, generated TypeScript surface, UI replay evidence, QA seed data, Playwright screenshots, and curl regression coverage.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish durable interaction contracts and schema before runtime instrumentation.

- [X] T001 Add `RuntimeInteractionKind`, `RuntimeInteractionStatus`, and `RuntimeInteractionEvidenceRecord` to `src/multi_agent_platform/db/models/runtime_orchestration.py`
- [X] T002 Export the new runtime interaction model/enums from `src/multi_agent_platform/db/models/__init__.py`
- [X] T003 Add Alembic migration `alembic/versions/0022_runtime_interaction_evidence.py`
- [X] T004 Extend generated graph schemas with `interaction_evidence` reference type in `src/multi_agent_platform/api/schemas/admin_agent_graph.py`
- [X] T005 Refresh generated React graph types via `scripts/frontend/generate_admin_react_types.py` and `frontend/admin/src/api/generated/reactAdminApi.ts`
- [X] T006 Create runtime interaction evidence helper module in `src/multi_agent_platform/runtime/orchestration/interaction_evidence.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build safe persistence, idempotency, and redaction behavior used by every story.

- [X] T007 Add repository methods to record/list interaction evidence in `src/multi_agent_platform/db/repositories/runtime_orchestration.py`
- [X] T008 Implement deterministic idempotency and per-run sequence assignment in the repository
- [X] T009 Implement safe summary, redacted metadata, classification, artifact ref, and digest helpers in `src/multi_agent_platform/runtime/orchestration/interaction_evidence.py`
- [X] T010 Add persistence/idempotency/redaction tests in `tests/unit/db/test_runtime_interaction_evidence_repository.py`
- [X] T011 Add shared QA/runtime replay fixtures in `tests/fixtures/runtime_agent_graph.py`

**Checkpoint**: Interaction evidence can be safely recorded and listed without duplicates.

---

## Phase 3: User Story 1 - Record Safe Interactions (Priority: P1)

**Goal**: Runtime graph execution records safe interaction evidence for handoffs, result returns, joins, approvals, and completion.

**Independent Test**: Execute deterministic graph paths and verify persisted interactions are safe, ordered, tenant-scoped, and idempotent.

### Tests for User Story 1

- [X] T012 [P] [US1] Add graph execution interaction instrumentation tests in `tests/unit/runtime/test_graph_execution_interaction_evidence.py`
- [X] T013 [P] [US1] Add sensitive metadata redaction assertions in `tests/unit/runtime/test_interaction_evidence.py`

### Implementation for User Story 1

- [X] T014 [US1] Record context transfer and handoff evidence in `_persist_success_evidence` in `src/multi_agent_platform/runtime/orchestration/graph_execution.py`
- [X] T015 [US1] Record result return and run completion evidence in role/terminal finalization paths in `src/multi_agent_platform/runtime/orchestration/graph_execution.py`
- [X] T016 [US1] Record join contribution and manual-resolution evidence in `_execute_join_node`
- [X] T017 [US1] Record approval pause evidence in `_execute_decision_node`
- [X] T018 [US1] Ensure worker retry/resume uses stable idempotency keys in graph execution instrumentation

**Checkpoint**: Deterministic runtime execution produces durable replay interactions.

---

## Phase 4: User Story 2 - Inspect Replay Path (Priority: P2)

**Goal**: Authorized admins see replay evidence in the existing runtime graph.

**Independent Test**: Seed replay evidence, request the graph route, and verify mapped edge references, provenance counts, and safe selected details.

### Tests for User Story 2

- [X] T019 [P] [US2] Add replay projection tests in `tests/unit/operations/test_runtime_agent_graph.py`
- [X] T020 [P] [US2] Add API replay evidence tests in `tests/integration/api/test_admin_runtime_agent_graph_api.py`
- [X] T021 [P] [US2] Add replay detail Vitest coverage in `frontend/admin/src/components/workbench/RuntimeAgentGraphPanel.test.tsx`

### Implementation for User Story 2

- [X] T022 [US2] Load interaction evidence in `src/multi_agent_platform/operations/runtime_agent_graph.py`
- [X] T023 [US2] Map source/target interaction evidence to existing runtime graph edges
- [X] T024 [US2] Add graph-level partial replay evidence counts for unmapped interactions
- [X] T025 [US2] Render interaction evidence reference labels and statuses in `frontend/admin/src/components/workflows/AgentGraphPanel.tsx`
- [X] T026 [US2] Update reusable workbench fixture data in `frontend/admin/src/test/workbenchTestData.ts`

**Checkpoint**: Runtime graph replay evidence is visible and safe.

---

## Phase 5: User Story 3 - Survive Retry And Resume (Priority: P3)

**Goal**: Retry/resume paths do not duplicate interaction evidence and preserve ordering.

**Independent Test**: Record repeated interactions and run resumed graph execution; verify counts and sequences.

### Tests for User Story 3

- [X] T027 [P] [US3] Add duplicate idempotency replay tests in `tests/unit/db/test_runtime_interaction_evidence_repository.py`
- [X] T028 [P] [US3] Add resumed graph execution evidence tests in `tests/unit/runtime/test_graph_execution_interaction_evidence.py`

### Implementation for User Story 3

- [X] T029 [US3] Ensure repository returns existing evidence on repeated idempotency keys
- [X] T030 [US3] Add stable idempotency key helpers for source/target/kind/step evidence
- [X] T031 [US3] Preserve interaction sequence ordering in graph projection references

**Checkpoint**: Replay path is stable under repeated instrumentation.

---

## Phase 6: User Story 4 - Exclude Sensitive Payloads (Priority: P4)

**Goal**: Durable evidence and UI/API replay responses exclude protected raw content.

**Independent Test**: Seed sensitive-looking metadata and verify persisted records, API responses, UI screenshots, and QA artifacts contain only safe redactions/digests.

### Tests for User Story 4

- [X] T032 [P] [US4] Add persistence redaction tests for sensitive key names and long strings
- [X] T033 [P] [US4] Add cross-tenant replay graph denial tests in `tests/integration/api/test_admin_runtime_agent_graph_api.py`
- [X] T034 [P] [US4] Add visible-copy sensitive marker assertions in frontend tests

### Implementation for User Story 4

- [X] T035 [US4] Enforce fail-closed tenant filtering for interaction evidence repository reads
- [X] T036 [US4] Ensure graph projection never exposes redacted structured metadata values
- [X] T037 [US4] Add QA068 seed records with protected marker source payloads and safe persisted summaries only

**Checkpoint**: Sensitive payloads remain absent from durable records and visible replay surfaces.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, QA, curl coverage, and final roadmap validation.

- [X] T038 Update `curl_testing.md` runtime graph success assertion for interaction replay evidence
- [X] T039 Reconcile `specs/_autopilot/graphical-ui-roadmap/068-durable-agent-interaction-evidence-and-replay-graph/validation.yml` with QA068 seed and desktop/mobile replay flows
- [X] T040 Create `scripts/qa/seed_runtime_interaction_evidence_qa068.py`
- [X] T041 Create `specs/068-durable-agent-interaction-evidence-and-replay-graph/.env.qa068`
- [X] T042 Create `specs/068-durable-agent-interaction-evidence-and-replay-graph/qa068.md`
- [X] T043 Create `specs/068-durable-agent-interaction-evidence-and-replay-graph/qa068_ui.md`
- [X] T044 Create `specs/068-durable-agent-interaction-evidence-and-replay-graph/qa068_user_guide.md`
- [X] T045 Add reviewer notes in `specs/068-durable-agent-interaction-evidence-and-replay-graph/pr_notes.md`
- [X] T046 Run Alembic upgrade, generated TypeScript freshness, focused backend tests, frontend typecheck/tests/build, Ruff, format, mypy, and QA document validation
- [X] T047 Run Spec 068 `run_spec_qa.py`, Playwright replay validation, curl coverage review, and multi-agent curl regression
- [X] T048 Run final whole-roadmap stability gate and update durable status files

---

## Dependencies & Execution Order

- Phase 1 setup blocks repository and runtime instrumentation.
- Phase 2 persistence/redaction blocks every user story.
- User Story 1 produces durable interaction evidence.
- User Story 2 projects that evidence into the graph UI/API.
- User Story 3 validates retry/resume stability after instrumentation exists.
- User Story 4 validates fail-closed redaction and tenant isolation throughout.
- Phase 7 validates docs, APIs, UI, curl coverage, and final stability.

## Parallel Opportunities

- T010, T012, and T013 can run in parallel after the model and helper signatures exist.
- T019, T020, and T021 can run in parallel after projection fields are implemented.
- T027 and T028 can run in parallel after repository idempotency is implemented.
- QA docs can be drafted while validation manifests and curl coverage are reconciled.

## Notes

- Do not persist message-level transcripts.
- Do not expose raw prompts, completions, memory contents, provider responses, credentials, private channel payloads, raw tool outputs, or stack traces.
- Do not synthesize production graph nodes for unmapped evidence.
- Preserve the existing operations workbench and runtime graph route.
- Mark each task complete in this file when implemented.
