# Tasks: Automatic Test Bench Evidence Integration In Workflow Publish Gates

**Input**: Design documents from `/specs/024-automatic-test-bench-evidence-integration-workflow-publish-gates/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Tests**: Required for repository evidence classification, workflow validation, publish gates, tenant isolation, UI rendering, docs, and 90 percent coverage.

## Phase 1: Setup (Shared Infrastructure)

- [x] T001 Update active Spec Kit feature pointer in `.specify/feature.json`
- [x] T002 [P] Create feature spec, plan, research, data model, contract, quickstart, and task artifacts under `specs/024-automatic-test-bench-evidence-integration-workflow-publish-gates/`

## Phase 2: Foundational (Blocking Prerequisites)

- [x] T003 [P] Add required-suite evidence projection models in `src/multi_agent_platform/testing/agent_bench/models.py`
- [x] T004 [P] Add latest-run repository helpers for suite, tenant, target, and target-version matching in `src/multi_agent_platform/db/repositories/agent_tests.py`
- [x] T005 Add required-suite evidence classification service logic in `src/multi_agent_platform/testing/agent_bench/service.py`
- [x] T006 Add DB-backed required-test snapshot support to `src/multi_agent_platform/admin/workflow_registry/reference_validation.py`

## Phase 3: User Story 1 - Block Publish Without Current Evidence (Priority: P1)

**Goal**: Validation and publication block when required suites lack current passing evidence.

**Independent Test**: A workflow draft with manual `latest_result_status="passed"` but no current run fails validation and publish gate evaluation.

### Tests for User Story 1

- [x] T007 [P] Add publish-gate unit tests for missing, failing, stale, and manual-status bypass behavior in `tests/unit/admin/test_publish_gate.py`
- [x] T008 [P] Add workflow service tests for required evidence blocking validation and publication in `tests/unit/admin/test_workflow_registry_service.py`

### Implementation for User Story 1

- [x] T009 Integrate required-test evidence lookups into workflow validation in `src/multi_agent_platform/admin/workflow_registry/service.py`
- [x] T010 Integrate required-test evidence lookups into publish gate evaluation and final publication in `src/multi_agent_platform/admin/workflow_registry/service.py`
- [x] T011 Persist safe required-test evidence pins in published version summaries via `src/multi_agent_platform/admin/workflow_registry/publish_gate.py`

## Phase 4: User Story 2 - Accept Only Tenant-Scoped Current Passing Evidence (Priority: P1)

**Goal**: Same-tenant, current-revision evidence is accepted; cross-tenant, wrong-target, and old-revision evidence fails closed.

**Independent Test**: A tenant workflow referencing another tenant's suite blocks without disclosing that tenant's suite details.

### Tests for User Story 2

- [x] T012 [P] Add same-tenant current passing evidence service tests in `tests/unit/admin/test_workflow_registry_service.py`
- [x] T013 [P] Add cross-tenant and wrong-target denial tests in `tests/unit/admin/test_workflow_registry_service.py`

### Implementation for User Story 2

- [x] T014 Enforce tenant, target type, target ID, and current revision target-version matching in `src/multi_agent_platform/testing/agent_bench/service.py`
- [x] T015 Add safe unavailable/mismatched diagnostics for denied evidence in `src/multi_agent_platform/admin/workflow_registry/reference_validation.py`
- [x] T016 Ensure platform-scope required tenant tests fail closed in `src/multi_agent_platform/admin/workflow_registry/service.py`

## Phase 5: User Story 3 - Show Safe Evidence Summaries In Admin UI (Priority: P2)

**Goal**: Admins can see evidence counts and safe remediation text in the workflow publish gate UI.

**Independent Test**: Publish gate UI renders required, passing, missing, failing, and stale counts and disables confirmation when evidence is blocked.

### Tests for User Story 3

- [x] T017 [P] Add UI model/template tests for required-test evidence summary rendering in `tests/integration/api/test_admin_workflow_ui.py`

### Implementation for User Story 3

- [x] T018 Update publish gate page model or template to render required-test evidence summary in `src/multi_agent_platform/api/ui/admin_workflows.py` and `src/multi_agent_platform/web_admin/templates/workflows/publish_gate.html`
- [x] T019 Update workflow reference lookup display for required tests when safe evidence summaries are available in `src/multi_agent_platform/web_admin/templates/workflows/components/reference_picker.html`

## Phase 6: Documentation And QA

- [x] T020 [P] Add testing instructions in `specs/024-automatic-test-bench-evidence-integration-workflow-publish-gates/testing-instructions.md`
- [x] T021 [P] Add PR review notes in `specs/024-automatic-test-bench-evidence-integration-workflow-publish-gates/pr-review-notes.md`
- [x] T022 [P] Update `README.md` and `docs/quickstart.md` with repository-backed workflow publish evidence notes
- [x] T023 Generate QA024 docs and environment files in `specs/024-automatic-test-bench-evidence-integration-workflow-publish-gates/`
- [x] T024 Create non-developer QA024 user guide in `specs/024-automatic-test-bench-evidence-integration-workflow-publish-gates/qa024_user_guide.md`

## Phase 7: Validation

- [x] T025 Run focused pytest command for workflow publish evidence integration
- [x] T026 Run `uv run ruff check .`
- [x] T027 Run `uv run ruff format --check .`
- [x] T028 Run `uv run mypy src`
- [x] T029 Run `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`
- [x] T030 Run QA validation scripts from `specs/_autopilot/024-automatic-test-bench-evidence-integration-workflow-publish-gates/validation.yml`

## Dependencies & Execution Order

- Phase 1 must complete before analysis.
- Phase 2 blocks all user-story implementation.
- User Stories 1 and 2 are both P1 and share service files, so implement them sequentially after foundational tests land.
- User Story 3 depends on publish gate response data from User Stories 1 and 2.
- Documentation and QA can proceed after implementation behavior is stable.

## Parallel Opportunities

- T003 and T004 can run in parallel.
- T007, T008, T012, T013, and T017 are test tasks in different files or isolated sections.
- T020, T021, and T022 can run in parallel once implementation terminology settles.
