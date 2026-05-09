# Tasks: Model-Backed Graph Role Executor

**Input**: Design documents from `specs/061-model-backed-graph-role-executor/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required. This runtime feature touches graph execution, provider
governance, tenant scope, redaction, usage/provenance, and worker wiring.

**Organization**: Tasks are grouped by independently testable user stories.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish feature scaffolding, QA placeholders, and test files.

- [x] T001 Create model-backed role execution modules in `src/multi_agent_platform/runtime/orchestration/model_backed_roles.py` and `src/multi_agent_platform/runtime/orchestration/role_output_contracts.py`
- [x] T002 Create focused test files in `tests/unit/runtime/orchestration/test_model_backed_roles.py`, `tests/contract/test_model_backed_role_executor_contracts.py`, and `tests/integration/runtime/test_model_backed_graph_execution.py`
- [x] T003 Create QA placeholder files `specs/061-model-backed-graph-role-executor/qa061.md`, `specs/061-model-backed-graph-role-executor/qa061_ui.md`, `specs/061-model-backed-graph-role-executor/.env.qa061`, `specs/061-model-backed-graph-role-executor/qa061_user_guide.md`, and `specs/061-model-backed-graph-role-executor/pr_notes.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Extend role context/result metadata and contract validation without changing deterministic behavior.

- [x] T004 Add model-backed-safe context fields to `RoleExecutionContext` in `src/multi_agent_platform/runtime/orchestration/graph_roles.py`
- [x] T005 Add optional usage/provenance/artifact metadata to `RoleExecutionResult` in `src/multi_agent_platform/runtime/orchestration/graph_roles.py`
- [x] T006 Update graph result serialization helpers in `src/multi_agent_platform/runtime/orchestration/graph_execution.py` so new role result metadata is preserved safely
- [x] T007 [P] Add role output contract validation helpers and failure models in `src/multi_agent_platform/runtime/orchestration/role_output_contracts.py`
- [x] T008 [P] Add contract tests for success, missing required fields, unsafe markers, and oversized inline output in `tests/contract/test_model_backed_role_executor_contracts.py`
- [x] T009 [P] Expand deterministic executor regression tests in `tests/unit/runtime/orchestration/test_graph_roles.py`

**Checkpoint**: Existing deterministic role execution remains compatible while model-backed result metadata can be represented.

---

## Phase 3: User Story 1 - Select Governed Role Execution (Priority: P1) MVP

**Goal**: Graph execution selects deterministic or model-backed execution safely based on explicit execution mode and tenant-scoped prerequisites.

**Independent Test**: Unit and integration tests prove deterministic mode remains default, model-backed mode selects the new executor only with valid context, and missing mode/pins/tenant scope fails closed before provider invocation.

### Tests for User Story 1

- [x] T010 [P] [US1] Add unit tests for executor selection and deterministic fallback in `tests/unit/runtime/orchestration/test_model_backed_roles.py`
- [x] T011 [P] [US1] Add unit tests for missing tenant, missing run step, missing output contract, disabled execution mode, and denied pin resolution in `tests/unit/runtime/orchestration/test_model_backed_roles.py`
- [x] T012 [US1] Add integration tests proving deterministic graph execution remains unchanged in `tests/integration/runtime/test_model_backed_graph_execution.py`

### Implementation for User Story 1

- [x] T013 [US1] Implement model-backed execution mode parsing and safe failure builders in `src/multi_agent_platform/runtime/orchestration/model_backed_roles.py`
- [x] T014 [US1] Implement a composite role executor that delegates deterministic contexts to `DeterministicRoleNodeExecutor` in `src/multi_agent_platform/runtime/orchestration/model_backed_roles.py`
- [x] T015 [US1] Pass run step, run bundle, workflow version bundle, and output contract metadata into `RoleExecutionContext` from `src/multi_agent_platform/runtime/orchestration/graph_execution.py`
- [x] T016 [US1] Wire model-backed executor dependencies into worker bootstrap readiness in `src/multi_agent_platform/bootstrap/worker.py`

**Checkpoint**: User Story 1 is fully functional and independently testable.

---

## Phase 4: User Story 2 - Execute Role Nodes Through Governed Model Gateway (Priority: P2)

**Goal**: Valid model-backed role nodes resolve governed pins, build safe input, call `ModelGateway`, validate output, and return safe graph-compatible results.

**Independent Test**: Mocked gateway integration tests execute one model-backed role node with valid pins and verify gateway context, safe messages, output contract validation, provenance, and failure behavior.

### Tests for User Story 2

- [x] T017 [P] [US2] Add unit tests for safe model input construction and redaction rejection in `tests/unit/runtime/orchestration/test_model_backed_roles.py`
- [x] T018 [P] [US2] Add unit tests for mocked gateway success, gateway failure, malformed response, and contract-invalid response in `tests/unit/runtime/orchestration/test_model_backed_roles.py`
- [x] T019 [P] [US2] Add integration tests proving graph execution calls mocked `ModelGateway` with workflow, step, prompt, profile, model, trace, and idempotency context in `tests/integration/runtime/test_model_backed_graph_execution.py`
- [x] T020 [P] [US2] Expand ModelGateway guardrail tests if new runtime files need allowlisting in `tests/unit/guardrails/test_model_gateway_only_provider_calls.py`

### Implementation for User Story 2

- [x] T021 [US2] Implement governed model/prompt/profile pin resolution through `ModelSkillConfigService` or a narrow resolver protocol in `src/multi_agent_platform/runtime/orchestration/model_backed_roles.py`
- [x] T022 [US2] Implement redaction-safe gateway message construction in `src/multi_agent_platform/runtime/orchestration/model_backed_roles.py`
- [x] T023 [US2] Implement mocked/governed `ModelGateway` invocation and gateway result mapping in `src/multi_agent_platform/runtime/orchestration/model_backed_roles.py`
- [x] T024 [US2] Implement role output parsing, validation, redaction, and digest calculation in `src/multi_agent_platform/runtime/orchestration/role_output_contracts.py`
- [x] T025 [US2] Ensure graph node failure handling records safe error categories and never treats contract-invalid model output as success in `src/multi_agent_platform/runtime/orchestration/graph_execution.py`

**Checkpoint**: User Stories 1 and 2 are functional and tenant-safe.

---

## Phase 5: User Story 3 - Preserve Evidence And Deterministic QA (Priority: P3)

**Goal**: Model-backed role execution records safe usage/provenance/artifact evidence while deterministic QA and test bench behavior remain unchanged.

**Independent Test**: Tests and QA scripts prove safe usage/provenance output, artifact reference behavior, idempotent gateway operations, deterministic test-bench compatibility, and redaction guardrails.

### Tests for User Story 3

- [x] T026 [P] [US3] Add unit tests for usage/provenance metadata and artifact reference output in `tests/unit/runtime/orchestration/test_model_backed_roles.py`
- [x] T027 [P] [US3] Add integration tests proving repeated model-backed execution uses gateway operation idempotency and does not duplicate authoritative evidence in `tests/integration/runtime/test_model_backed_graph_execution.py`
- [x] T028 [P] [US3] Add worker factory selection tests in `tests/unit/bootstrap/test_worker_gateway_bootstrap.py`
- [x] T029 [P] [US3] Add redaction assertions for QA-visible output in `tests/unit/runtime/orchestration/test_model_backed_roles.py`

### Implementation for User Story 3

- [x] T030 [US3] Add bounded inline output and artifact-reference persistence support in `src/multi_agent_platform/runtime/orchestration/model_backed_roles.py`
- [x] T031 [US3] Return usage, provenance, artifact references, and policy decision summaries through safe `RoleExecutionResult` metadata in `src/multi_agent_platform/runtime/orchestration/model_backed_roles.py`
- [x] T032 [US3] Update `OrchestrationWorker` to construct graph execution with deterministic or model-backed executor factories in `src/multi_agent_platform/workers/orchestration.py`
- [x] T033 [US3] Pass worker bootstrap gateway dependencies into orchestration polling in `src/multi_agent_platform/workers/loops.py`
- [x] T034 [US3] Keep test-bench deterministic mode behavior unchanged in affected runtime/test-bench code paths

**Checkpoint**: All model-backed role executor stories are functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: QA, docs, curl coverage review, generated evidence, and validation readiness.

- [x] T035 Add QA seed and verifier scripts in `scripts/qa/seed_model_backed_roles_qa061.py` and `scripts/qa/verify_model_backed_roles_qa061.py`
- [x] T036 Review `curl_testing.md`; update it only if Spec 061 adds or changes public/admin/runtime JSON APIs
- [x] T037 Update `specs/_autopilot/scenario-enhancement-roadmap/061-model-backed-graph-role-executor/validation.yml` with actual QA commands if implementation routes or QA scripts differ from the generated smoke manifest
- [x] T038 Complete QA docs in `specs/061-model-backed-graph-role-executor/qa061.md`, `specs/061-model-backed-graph-role-executor/qa061_ui.md`, `specs/061-model-backed-graph-role-executor/.env.qa061`, `specs/061-model-backed-graph-role-executor/qa061_user_guide.md`, and `specs/061-model-backed-graph-role-executor/pr_notes.md`
- [x] T039 Run focused backend validation for model-backed role execution modules and tests, then fix failures in touched files
- [x] T040 Run QA document validation for `specs/061-model-backed-graph-role-executor`
- [x] T041 Run `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/scenario-enhancement-roadmap/061-model-backed-graph-role-executor/validation.yml`
- [x] T042 Run `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/scenario-enhancement-roadmap/061-model-backed-graph-role-executor/validation.yml --start-processes`
- [x] T043 Run `uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa061-after-spec`

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 has no dependencies.
- Phase 2 depends on Phase 1 and blocks all user stories.
- User Story 1 depends on Phase 2 and is the MVP.
- User Story 2 depends on User Story 1 for executor selection and context.
- User Story 3 depends on User Story 2 for gateway and output metadata.
- Phase 6 depends on all selected user stories.

### Parallel Opportunities

- T007, T008, and T009 can run in parallel after scaffolding.
- T010, T011, and T012 can run in parallel before T013-T016.
- T017, T018, T019, and T020 can run in parallel before T021-T025.
- T026, T027, T028, and T029 can run in parallel before T030-T034.
- QA docs can proceed after executor contracts stabilize.

## Implementation Strategy

1. Preserve deterministic role execution behavior while extending safe result/context metadata.
2. Add contract validation and composite executor selection with fail-closed defaults.
3. Implement mocked model-backed gateway execution and safe output mapping.
4. Add usage/provenance/artifact evidence and worker factory wiring.
5. Complete QA docs/scripts, curl coverage review, and required validation before Spec 062.
