# Tasks: Live Model Credential Resolution For Gateway Calls

**Input**: Design documents from `/specs/025-live-model-credential-resolution-for-gateway-calls/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Tests**: Required for probe credential use, gateway credential use, secret-resolution failures, safe summaries, adapter headers, local no-auth behavior, docs, and 90 percent coverage.

## Phase 1: Setup (Shared Infrastructure)

- [x] T001 Update active Spec Kit feature pointer in `.specify/feature.json`
- [x] T002 [P] Create feature spec, plan, research, data model, contract, quickstart, and task artifacts under `specs/025-live-model-credential-resolution-for-gateway-calls/`
- [x] T003 [P] Add QA025 environment file in `specs/025-live-model-credential-resolution-for-gateway-calls/.env.qa025`

## Phase 2: Foundational (Blocking Prerequisites)

- [x] T004 Add provider credential selection and optional local no-auth behavior in `src/multi_agent_platform/model_providers/secrets.py`
- [x] T005 Add credential reference validation hardening in `src/multi_agent_platform/model_providers/validation.py` and `src/multi_agent_platform/api/schemas/model_providers.py`
- [x] T006 Wire `ProviderSecretResolver` into `ProviderProbeRunner`, `ModelProviderService`, and container factories in `src/multi_agent_platform/model_providers/probes.py`, `src/multi_agent_platform/model_providers/service.py`, and `src/multi_agent_platform/bootstrap/container.py`
- [x] T007 Wire `ProviderSecretResolver` into `ModelGateway` in `src/multi_agent_platform/model_providers/gateway.py`

## Phase 3: User Story 1 - Probe Uses Configured Secret References (Priority: P1)

**Goal**: Provider probes resolve configured references at call time and fail safely when OpenAI credentials are missing or unresolved.

**Independent Test**: A provider probe with a mocked secret provider passes the resolved value into a mocked adapter, while missing/unresolved credentials fail before adapter invocation.

### Tests for User Story 1

- [x] T008 [P] Add resolver and validation tests in `tests/unit/model_providers/test_secret_references.py`, `tests/unit/model_providers/test_validation.py`, and `tests/unit/api/test_model_provider_schemas.py`
- [x] T009 [P] Add provider probe credential success/failure tests in `tests/unit/model_providers/test_probes.py` and `tests/unit/model_providers/test_model_provider_service.py`

### Implementation for User Story 1

- [x] T010 Implement probe credential resolution and safe failure summaries in `src/multi_agent_platform/model_providers/probes.py` and `src/multi_agent_platform/model_providers/service.py`
- [x] T011 Ensure probe failure persists `ConnectionTestResult` and health evidence with `secret_reference_invalid` in `src/multi_agent_platform/model_providers/service.py`

## Phase 4: User Story 2 - Runtime Gateway Resolves Credentials Live (Priority: P1)

**Goal**: Runtime gateway calls resolve provider credentials at call time and persist safe failure evidence without raw values.

**Independent Test**: `ModelGateway.invoke` with a mocked secret provider and adapter passes resolved credentials on success and avoids adapter calls on secret failures.

### Tests for User Story 2

- [x] T012 [P] Add gateway credential resolution tests in `tests/unit/model_providers/test_gateway.py`
- [x] T013 [P] Add gateway operation and attempt evidence redaction tests in `tests/integration/runtime/test_gateway_operation_recovery.py` and `tests/integration/model_providers/test_gateway_attempt_evidence.py`

### Implementation for User Story 2

- [x] T014 Implement gateway credential resolution and safe failure recording in `src/multi_agent_platform/model_providers/gateway.py`
- [x] T015 Preserve operation duplicate recovery and usage capture behavior after credential resolution changes in `src/multi_agent_platform/model_providers/gateway.py`

## Phase 5: User Story 3 - Diagnostics Stay Redaction-Safe (Priority: P2)

**Goal**: Adapter calls receive credentials while all persisted and rendered evidence excludes raw resolved values.

**Independent Test**: Adapter tests inspect authorization headers, and redaction tests verify raw fake values never appear in safe summaries.

### Tests for User Story 3

- [x] T016 [P] Add OpenAI and local adapter header tests in `tests/unit/model_providers/test_adapters.py`
- [x] T017 [P] Add docs/redaction tests for QA025 in `tests/docs/`

### Implementation for User Story 3

- [x] T018 Pass resolved local credentials through `LocalOpenAICompatibleAdapter` and keep no-auth local behavior in `src/multi_agent_platform/model_providers/local_adapter.py`
- [x] T019 Ensure OpenAI and local adapter code does not log or persist authorization headers in `src/multi_agent_platform/model_providers/openai_adapter.py`, `src/multi_agent_platform/model_providers/local_adapter.py`, and `src/multi_agent_platform/model_providers/adapters.py`

## Phase 6: Documentation And QA

- [x] T020 [P] Add QA025 testing instructions in `specs/025-live-model-credential-resolution-for-gateway-calls/testing-instructions.md`
- [x] T021 [P] Add QA025 PR review notes in `specs/025-live-model-credential-resolution-for-gateway-calls/pr-review-notes.md`
- [x] T022 [P] Update `README.md` and `docs/quickstart.md` with live model credential resolution notes
- [x] T023 Generate QA025 docs in `specs/025-live-model-credential-resolution-for-gateway-calls/qa025.md` and `specs/025-live-model-credential-resolution-for-gateway-calls/qa025_ui.md`
- [x] T024 Create non-developer QA025 user guide in `specs/025-live-model-credential-resolution-for-gateway-calls/qa025_user_guide.md`

## Phase 7: Validation

- [x] T025 Run focused pytest command for provider credential resolution
- [x] T026 Run `uv run ruff check .`
- [x] T027 Run `uv run ruff format --check .`
- [x] T028 Run `uv run mypy src`
- [x] T029 Run `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`
- [x] T030 Run QA validation scripts from `specs/_autopilot/025-live-model-credential-resolution-for-gateway-calls/validation.yml`

## Dependencies & Execution Order

- Phase 1 must complete before analysis.
- Phase 2 blocks all user-story implementation.
- User Stories 1 and 2 are both P1; implement probe path first, then gateway path.
- User Story 3 depends on adapter credential flow from User Stories 1 and 2.
- Documentation and QA can proceed after implementation terminology is stable.

## Parallel Opportunities

- T002 and T003 can run in parallel.
- T008, T009, T012, T013, T016, and T017 are test tasks in different files.
- T020, T021, T022, T023, and T024 can proceed in parallel after implementation wording is stable.
