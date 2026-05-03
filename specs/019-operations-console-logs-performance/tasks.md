# Tasks: Operations Console Logs And Performance

**Input**: Design documents from `/Users/scottcornell/src/my-projects/multi-agent/specs/019-operations-console-logs-performance/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/operations-console.openapi.yaml`, `contracts/admin-operations-ui.md`, `quickstart.md`
**Tests**: Required for authorization, platform-admin access, auditor read-only
access, tenant-admin denial, health aggregation, dependency mapping, worker and
queue metrics, DB pool pressure, object-storage status, model provider status,
Telegram/channel status, reliability state links, usage throughput, log
filtering by trace/run/tenant/component/severity/status/dependency/time,
redaction, exports, UI rendering, query performance, docs, and 90 percent
coverage.

## Phase 1: Setup

**Purpose**: Establish feature scaffolding, contracts, and docs-test expectations.

- [X] T001 Create `src/multi_agent_platform/operations/__init__.py`
- [X] T002 [P] Add contract coverage for `specs/019-operations-console-logs-performance/contracts/operations-console.openapi.yaml` in `tests/contract/test_operations_console_contract.py`
- [X] T003 [P] Add docs existence and README expectation tests in `tests/docs/test_operations_console_docs.py`
- [X] T004 [P] Add no-new-migration assertion in `tests/unit/operations/test_service.py`

---

## Phase 2: Foundational Models, Redaction, Export, Schemas, And Policy

**Purpose**: Blocking DTOs, redaction, export, schemas, and authorization used by every story.

- [X] T005 Implement operations domain DTOs in `src/multi_agent_platform/operations/models.py`
- [X] T006 Implement redaction helpers in `src/multi_agent_platform/operations/redaction.py`
- [X] T007 [P] Add redaction tests in `tests/unit/operations/test_redaction.py`
- [X] T008 Implement redacted CSV export helpers in `src/multi_agent_platform/operations/export.py`
- [X] T009 [P] Add export CSV tests in `tests/unit/operations/test_export.py`
- [X] T010 Add Pydantic schemas in `src/multi_agent_platform/api/schemas/operations.py`
- [X] T011 [P] Add schema tests in `tests/unit/api/test_operations_schemas.py`
- [X] T012 Add operations protected surfaces in `src/multi_agent_platform/auth/policy.py`
- [X] T013 Update local-principal permission helpers in `src/multi_agent_platform/auth/local_principals.py`
- [X] T014 [P] Add operations policy tests in `tests/unit/auth/test_operations_policy.py`

**Checkpoint**: DTOs, redaction, export, schemas, and authorization are ready.

---

## Phase 3: User Story 1 - Review Platform Health And Capacity (Priority: P1)

**Goal**: Platform admins can inspect health, dependencies, worker capacity, queue pressure, DB pool pressure, object storage, latency, error rate, and reliability pressure.

**Independent Test**: Platform admin opens `/admin/operations` and sees safe dashboard cards.

### Tests for User Story 1

- [X] T015 [P] [US1] Add service tests for health/dependency/capacity aggregation in `tests/unit/operations/test_service.py`
- [X] T016 [P] [US1] Add UI model tests in `tests/unit/api/test_operations_ui_models.py`

### Implementation for User Story 1

- [X] T017 [US1] Implement dashboard aggregation service in `src/multi_agent_platform/operations/service.py`
- [X] T018 [US1] Implement UI view models in `src/multi_agent_platform/api/ui/operations.py`

**Checkpoint**: User Story 1 dashboard aggregation is independently testable.

---

## Phase 4: User Story 2 - Inspect Dependency And Throughput Panels (Priority: P2)

**Goal**: Operators can inspect provider health, Telegram/channel readiness, usage throughput, model latency, run lifecycle throughput, and links.

**Independent Test**: Seed provider, usage, gateway, timeline, Telegram, and capacity records, then verify dashboard panels and links.

### Tests for User Story 2

- [X] T019 [P] [US2] Add service tests for provider, Telegram, usage, model latency, and run lifecycle summaries in `tests/unit/operations/test_service.py`
- [X] T020 [P] [US2] Add integration API tests for dashboard summaries in `tests/integration/api/test_admin_operations_api.py`

### Implementation for User Story 2

- [X] T021 [US2] Extend operations aggregation service for provider, Telegram, usage, gateway, and timeline summaries in `src/multi_agent_platform/operations/service.py`
- [X] T022 [US2] Implement admin operations router in `src/multi_agent_platform/api/routers/admin_operations.py`
- [X] T023 [US2] Register operations router in `src/multi_agent_platform/api/main.py`

**Checkpoint**: User Story 2 panels are independently testable through JSON API.

---

## Phase 5: User Story 3 - Filter Redacted Operational Logs (Priority: P3)

**Goal**: Operators and auditors can filter redacted logs by trace, tenant, run, component, severity, status, dependency, and time range.

**Independent Test**: Seed multi-source events and verify filters return only matching redacted rows.

### Tests for User Story 3

- [X] T024 [P] [US3] Add unit tests for log filtering in `tests/unit/operations/test_service.py`
- [X] T025 [P] [US3] Add API integration tests for log filters, tenant-admin denial, and auditor access in `tests/integration/api/test_admin_operations_api.py`
- [X] T026 [P] [US3] Add bounded query performance test in `tests/performance/operations/test_log_filtering.py`

### Implementation for User Story 3

- [X] T027 [US3] Implement bounded log query and redacted event conversion in `src/multi_agent_platform/operations/service.py`
- [X] T028 [US3] Implement log query API and filter parsing in `src/multi_agent_platform/api/routers/admin_operations.py`

**Checkpoint**: User Story 3 filters are independently testable.

---

## Phase 6: User Story 4 - Export Redacted Evidence (Priority: P4)

**Goal**: Platform admins and auditors can export redacted CSV logs, and exports or denials are audited.

**Independent Test**: Export as platform admin/auditor and deny tenant admin while verifying artifacts, redaction, and audit metadata.

### Tests for User Story 4

- [X] T029 [P] [US4] Add service tests for export artifact metadata and audit records in `tests/unit/operations/test_service.py`
- [X] T030 [P] [US4] Add API integration tests for export and denial in `tests/integration/api/test_admin_operations_api.py`

### Implementation for User Story 4

- [X] T031 [US4] Implement export service method with storage and inspection audit records in `src/multi_agent_platform/operations/service.py`
- [X] T032 [US4] Add export API and browser wrapper route in `src/multi_agent_platform/api/routers/admin_operations.py`

**Checkpoint**: User Story 4 exports are independently testable.

---

## Phase 7: Server-Rendered UI

**Goal**: The browser console is usable and screenshot-safe.

- [X] T033 [P] Add UI integration tests for `/admin/operations` rendering, filters, links, redaction notice, and tenant-admin denial in `tests/integration/api/test_admin_operations_ui.py`
- [X] T034 Add Operations Console navigation item and filter profile in `src/multi_agent_platform/api/ui/admin_console.py`
- [X] T035 Implement console template in `src/multi_agent_platform/web_admin/templates/operations/index.html`

---

## Final Phase: Polish And Cross-Cutting Verification

- [X] T036 [P] Generate QA environment file in `specs/019-operations-console-logs-performance/.env.qa019`
- [X] T037 [P] Generate manual QA guide in `specs/019-operations-console-logs-performance/qa019.md`
- [X] T038 [P] Generate browser UI QA walkthrough in `specs/019-operations-console-logs-performance/qa019_ui.md`
- [X] T039 [P] Generate non-developer manual QA user guide with at least 160 lines in `specs/019-operations-console-logs-performance/qa019_user_guide.md`
- [X] T040 [P] Add PR review notes in `specs/019-operations-console-logs-performance/pr-review-notes.md`
- [X] T041 [P] Add testing instructions in `specs/019-operations-console-logs-performance/testing-instructions.md`
- [X] T042 Update `README.md` with Operations Console admin/API/QA summary
- [X] T043 Update `docs/quickstart.md` with QA019 validation entry
- [X] T044 Run QA document validation with `.specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/019-operations-console-logs-performance`
- [X] T045 Run API validation with `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/019-operations-console-logs-performance/validation.yml`
- [X] T046 Run Playwright UI validation with `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/019-operations-console-logs-performance/validation.yml --start-processes`
- [X] T047 Run quality gates `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src`, and `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`
- [X] T048 Mark completed tasks in `specs/019-operations-console-logs-performance/tasks.md`

## Dependencies

- Phase 1 must complete before Phase 2.
- Phase 2 must complete before all user stories.
- User Story 1 is the MVP and blocks meaningful UI dashboard work.
- User Story 2 depends on dashboard aggregation foundations.
- User Story 3 depends on redaction and filter DTOs.
- User Story 4 depends on log filtering and export helpers.
- UI rendering depends on service, router, and view models.
- Final polish depends on all selected implementation stories.

## Parallel Execution Examples

- T002, T003, and T004 can run in parallel after T001.
- T007, T009, T011, and T014 can run in parallel while paired implementation tasks land.
- T015 and T016 can run in parallel once Phase 2 is complete.
- T019 and T020 can run in parallel once dashboard aggregation exists.
- T024, T025, and T026 can run in parallel once log filtering exists.
- T036 through T041 can run in parallel after behavior stabilizes.

## Implementation Strategy

1. Deliver MVP dashboard by completing Phases 1-3.
2. Add provider/channel/usage/reliability throughput panels.
3. Add redacted log filtering.
4. Add redacted export artifacts and audit evidence.
5. Complete browser UI, docs, QA artifacts, Playwright validation, and quality gates.
