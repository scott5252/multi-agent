# Tasks: Token Usage And Cost Analytics

**Input**: Design documents from `/Users/scottcornell/src/my-projects/multi-agent/specs/016-token-usage-cost-analytics/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/usage-analytics.openapi.yaml`, `contracts/admin-usage-ui.md`, `quickstart.md`  
**Tests**: Required by the feature specification for usage normalization, missing provider fields, estimated vs confirmed usage, attribution, tenant isolation, dashboard filters, rollups, pricing version calculation, CSV export authorization, redaction, late reconciliation, query performance, docs, and 90 percent coverage.

**Organization**: Tasks are grouped by independently testable user stories after shared storage, pricing, policy, and capture foundations are in place.

## Phase 1: Setup

**Purpose**: Establish feature scaffolding, contract checks, and docs-test expectations.

- [X] T001 Create `src/multi_agent_platform/usage/__init__.py`
- [X] T002 [P] Add contract coverage for `specs/016-token-usage-cost-analytics/contracts/usage-analytics.openapi.yaml` in `tests/contract/test_usage_analytics_contract.py`
- [X] T003 [P] Add docs existence and README expectation tests in `tests/docs/test_usage_analytics_docs.py`
- [X] T004 [P] Add migration smoke test placeholder for usage tables in `tests/integration/db/test_usage_migration.py`

---

## Phase 2: Foundational Storage, Pricing, Policy, And Redaction

**Purpose**: Blocking data, schema, pricing, repository, authorization, and redaction primitives used by every story.

**Critical**: No user story implementation should start until these tasks are complete.

- [X] T005 Add SQLAlchemy models for usage events, rollups, pricing versions, export requests, and reconciliation records in `src/multi_agent_platform/db/models/usage.py`
- [X] T006 Register usage models in `src/multi_agent_platform/db/models/__init__.py`
- [X] T007 Add additive Alembic migration for usage analytics tables and indexes in `alembic/versions/0016_token_usage_cost_analytics.py`
- [X] T008 [P] Add unit tests for usage SQLAlchemy models in `tests/unit/db/test_usage_models.py`
- [X] T009 Implement usage domain models and enums in `src/multi_agent_platform/usage/models.py`
- [X] T010 Implement provider usage normalization for cached tokens, reasoning tokens, billable units, and field status in `src/multi_agent_platform/model_providers/usage.py`
- [X] T011 [P] Add normalization tests in `tests/unit/model_providers/test_usage.py`
- [X] T012 Implement pricing estimator and default QA pricing in `src/multi_agent_platform/usage/pricing.py`
- [X] T013 [P] Add pricing tests in `tests/unit/usage/test_pricing.py`
- [X] T014 Implement async repository methods for capture, filters, rollups, exports, and reconciliation in `src/multi_agent_platform/db/repositories/usage.py`
- [X] T015 [P] Add repository tests for tenant filtering, rollups, exports, idempotency, and reconciliation in `tests/unit/db/test_usage_repository.py`
- [X] T016 Add Pydantic schemas for filters, summaries, events, pricing, and exports in `src/multi_agent_platform/api/schemas/usage.py`
- [X] T017 [P] Add schema validation tests for filters, statuses, CSV-safe fields, and export requests in `tests/unit/api/test_usage_schemas.py`
- [X] T018 Add usage analytics protected surfaces and permissions in `src/multi_agent_platform/auth/policy.py`
- [X] T019 Update local-principal QA admin permissions for usage analytics in `src/multi_agent_platform/auth/local_principals.py`
- [X] T020 [P] Add protected-surface policy tests for usage analytics actions in `tests/unit/auth/test_usage_policy.py`

**Checkpoint**: Storage, pricing, schemas, repository filters, and authorization are ready for capture and UI work.

---

## Phase 3: User Story 1 - Normalize Every Model Invocation (Priority: P1)

**Goal**: Every successful ModelGateway invocation records one safe normalized usage event with attribution, pricing, status flags, and idempotency.

**Independent Test**: A mocked gateway invocation persists a usage event with tenant, run, step, agent, provider, model, prompt, tokens, latency, pricing, and no raw content.

### Tests for User Story 1

- [X] T021 [P] [US1] Add service tests for capture payloads, idempotency, safe attribution, missing fields, malformed usage, and no raw content in `tests/unit/usage/test_usage_service.py`
- [X] T022 [P] [US1] Add ModelGateway capture integration tests in `tests/integration/model_providers/test_gateway_usage_capture.py`

### Implementation for User Story 1

- [X] T023 [US1] Implement usage capture service in `src/multi_agent_platform/usage/service.py`
- [X] T024 [US1] Extend `GatewayUsage` and `GatewayInvocationContext` attribution fields in `src/multi_agent_platform/model_providers/models.py`
- [X] T025 [US1] Integrate optional usage recorder into `src/multi_agent_platform/model_providers/gateway.py`
- [X] T026 [US1] Wire usage recorder into container ModelGateway factory in `src/multi_agent_platform/bootstrap/container.py`

**Checkpoint**: User Story 1 capture is independently testable.

---

## Phase 4: User Story 2 - Review Tenant-Scoped Usage Dashboards (Priority: P2)

**Goal**: Admins can review tenant-authorized usage summaries, rollups, filters, and drilldown rows.

**Independent Test**: Seed two tenants of usage and verify platform admin sees both while tenant admin sees only their tenant.

### Tests for User Story 2

- [X] T027 [P] [US2] Add API integration tests for summaries, event drilldowns, filters, rollups, tenant isolation, and denied access in `tests/integration/api/test_admin_usage_api.py`
- [X] T028 [P] [US2] Add UI integration tests for dashboard render, empty state, filter state, rollup table, event table, and tenant isolation in `tests/integration/api/test_admin_usage_ui.py`
- [X] T029 [P] [US2] Add UI view model tests in `tests/unit/api/test_usage_ui_models.py`
- [X] T030 [P] [US2] Add performance test for 10,000 event time-range queries in `tests/integration/db/test_usage_query_performance.py`

### Implementation for User Story 2

- [X] T031 [US2] Implement usage UI view models in `src/multi_agent_platform/api/ui/usage.py`
- [X] T032 [US2] Implement admin usage API/UI router in `src/multi_agent_platform/api/routers/admin_usage.py`
- [X] T033 [US2] Register usage router in `src/multi_agent_platform/api/main.py`
- [X] T034 [US2] Add Usage Analytics navigation item in `src/multi_agent_platform/api/ui/admin_console.py`
- [X] T035 [US2] Implement dashboard template in `src/multi_agent_platform/web_admin/templates/usage/index.html`

**Checkpoint**: User Story 2 dashboard is independently testable through API and browser UI.

---

## Phase 5: User Story 3 - Export Audited CSV Reports (Priority: P3)

**Goal**: Authorized admins can export filtered safe usage rows and every export or denial is auditable.

**Independent Test**: Platform admin, tenant admin, and unauthorized export attempts produce correct CSV metadata and audit-safe records.

### Tests for User Story 3

- [X] T036 [P] [US3] Add export unit tests for CSV columns, storage metadata, redaction, and denial summaries in `tests/unit/usage/test_export.py`
- [X] T037 [P] [US3] Add API integration tests for export authorization, artifact metadata, denied access, and audit records in `tests/integration/api/test_admin_usage_api.py`

### Implementation for User Story 3

- [X] T038 [US3] Implement CSV export helpers in `src/multi_agent_platform/usage/export.py`
- [X] T039 [US3] Add export route handlers to `src/multi_agent_platform/api/routers/admin_usage.py`
- [X] T040 [US3] Implement export detail template in `src/multi_agent_platform/web_admin/templates/usage/export_detail.html`
- [X] T041 [US3] Emit audit-safe export and denial records through the usage service in `src/multi_agent_platform/usage/service.py`

**Checkpoint**: User Story 3 exports are independently testable.

---

## Phase 6: User Story 4 - Reconcile Pricing And Late Usage (Priority: P4)

**Goal**: Estimated usage can be reconciled to confirmed usage while preserving audit-safe history and pricing-version explainability.

**Independent Test**: An estimated event receives confirmed values and dashboard totals reflect confirmed values with a reconciliation record.

### Tests for User Story 4

- [X] T042 [P] [US4] Add reconciliation tests for estimate-to-confirmed updates, pricing version preservation, rollup corrections, and redaction in `tests/unit/usage/test_usage_service.py`

### Implementation for User Story 4

- [X] T043 [US4] Implement reconciliation service method in `src/multi_agent_platform/usage/service.py`
- [X] T044 [US4] Add repository support for reconciliation records in `src/multi_agent_platform/db/repositories/usage.py`

**Checkpoint**: User Story 4 reconciliation is independently testable.

---

## Final Phase: Polish And Cross-Cutting Verification

**Purpose**: Complete docs, QA artifacts, README updates, task tracking, and quality gates.

- [X] T045 [P] Generate QA environment file in `specs/016-token-usage-cost-analytics/.env.qa016`
- [X] T046 [P] Generate manual QA guide in `specs/016-token-usage-cost-analytics/qa016.md`
- [X] T047 [P] Generate browser UI QA walkthrough in `specs/016-token-usage-cost-analytics/qa016_ui.md`
- [X] T048 [P] Generate non-developer manual QA user guide with at least 160 lines in `specs/016-token-usage-cost-analytics/qa016_user_guide.md`
- [X] T049 [P] Add PR review notes in `specs/016-token-usage-cost-analytics/pr-review-notes.md`
- [X] T050 [P] Add testing instructions in `specs/016-token-usage-cost-analytics/testing-instructions.md`
- [X] T051 Update `README.md` with Usage Analytics admin/API/QA summary
- [X] T052 Update `docs/quickstart.md` with QA016 validation entry
- [X] T053 Run QA document validation with `.specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/016-token-usage-cost-analytics`
- [X] T054 Run API validation with `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/016-token-usage-cost-analytics/validation.yml`
- [X] T055 Run Playwright UI validation with `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/016-token-usage-cost-analytics/validation.yml --start-processes`
- [X] T056 Run quality gates `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src`, and `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`
- [X] T057 Mark completed tasks in `specs/016-token-usage-cost-analytics/tasks.md`

## Dependencies

- Phase 1 must complete before Phase 2.
- Phase 2 must complete before all user stories.
- User Story 1 is the MVP and blocks meaningful dashboard/export data.
- User Story 2 depends on User Story 1 usage events.
- User Story 3 depends on User Story 2 filters and event query semantics.
- User Story 4 depends on User Story 1 event idempotency and pricing versions.
- Final polish depends on all selected implementation stories.

## Parallel Execution Examples

- T002, T003, and T004 can run in parallel after T001.
- T008, T011, T013, T015, T017, and T020 can run in parallel while their paired implementation tasks are developed.
- T021 and T022 can run in parallel once Phase 2 is complete.
- T027, T028, T029, and T030 can run in parallel once capture exists.
- T036 and T037 can run in parallel once dashboard filters exist.
- T045 through T050 can run in parallel after implementation behavior stabilizes.

## Implementation Strategy

1. Deliver MVP capture by completing Phases 1-3: storage, pricing, policy,
   schemas, repository, normalization, service, and ModelGateway integration.
2. Add dashboard summaries and drilldowns with User Story 2.
3. Add CSV exports and audit evidence with User Story 3.
4. Add reconciliation support with User Story 4.
5. Complete docs, QA artifacts, Playwright validation, and quality gates.
