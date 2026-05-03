# Tasks: Telegram Configuration Console

**Input**: Design documents from `/Users/scottcornell/src/my-projects/multi-agent/specs/017-telegram-configuration-console/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/telegram-configuration.openapi.yaml`, `contracts/admin-telegram-ui.md`, `quickstart.md`  
**Tests**: Required for authorization, platform vs tenant scope behavior, tenant isolation, safe secret-reference validation, production guardrails, local fake-token QA behavior, webhook readiness without real Telegram side effects, tenant enable/disable forms, linked identity list redaction, link-token issue/revoke flows, delivery diagnostic summaries, stale revision conflict handling, audit-safe diagnostics, metrics where available, admin navigation, browser UI forms, screenshot-safe redaction, docs, PR notes, testing instructions, and 90 percent coverage.

**Organization**: Tasks are grouped by independently testable user stories after shared storage, policy, schema, and redaction foundations are in place.

## Phase 1: Setup

**Purpose**: Establish feature scaffolding, contract checks, and docs-test expectations.

- [X] T001 Create `src/multi_agent_platform/admin/telegram_config/__init__.py`
- [X] T002 [P] Add contract coverage for `specs/017-telegram-configuration-console/contracts/telegram-configuration.openapi.yaml` in `tests/contract/test_telegram_configuration_contract.py`
- [X] T003 [P] Add docs existence and README expectation tests in `tests/docs/test_telegram_configuration_docs.py`
- [X] T004 [P] Add migration smoke test for Telegram console tables in `tests/integration/db/test_telegram_config_migration.py`

---

## Phase 2: Foundational Storage, Policy, Redaction, And Schemas

**Purpose**: Blocking data, schema, repository, authorization, and redaction primitives used by every story.

**Critical**: No user story implementation should start until these tasks are complete.

- [X] T005 Add SQLAlchemy models for tenant config, token audit, identity summaries, and diagnostics in `src/multi_agent_platform/db/models/telegram_config.py`
- [X] T006 Register Telegram config models in `src/multi_agent_platform/db/models/__init__.py`
- [X] T007 Add additive Alembic migration in `alembic/versions/0017_telegram_configuration_console.py`
- [X] T008 [P] Add repository tests in `tests/unit/db/test_telegram_config_repository.py`
- [X] T009 Implement domain models in `src/multi_agent_platform/admin/telegram_config/models.py`
- [X] T010 Implement redaction helpers in `src/multi_agent_platform/admin/telegram_config/redaction.py`
- [X] T011 [P] Add redaction tests in `tests/unit/admin/telegram_config/test_telegram_redaction.py`
- [X] T012 Implement async repository in `src/multi_agent_platform/db/repositories/telegram_config.py`
- [X] T013 Add Pydantic schemas in `src/multi_agent_platform/api/schemas/telegram_config.py`
- [X] T014 [P] Add schema tests in `tests/unit/api/test_telegram_config_schemas.py`
- [X] T015 Add Telegram console protected surfaces in `src/multi_agent_platform/auth/policy.py`
- [X] T016 Update local-principal QA permission helpers in `src/multi_agent_platform/auth/local_principals.py`
- [X] T017 [P] Add policy tests in `tests/unit/auth/test_telegram_config_policy.py`

**Checkpoint**: Storage, schemas, repository filters, redaction, and authorization are ready for readiness and UI work.

---

## Phase 3: User Story 1 - Verify Platform Telegram Readiness (Priority: P1)

**Goal**: Platform admins can inspect safe provider readiness and run local-only webhook validation without secret exposure or external calls.

**Independent Test**: Platform admin opens `/admin/telegram`, sees secret-reference readiness, runs webhook validation, and receives a safe diagnostic.

### Tests for User Story 1

- [X] T018 [P] [US1] Add service tests for readiness, production guardrails, local fake references, and safe diagnostics in `tests/unit/admin/telegram_config/test_telegram_service.py`
- [X] T019 [P] [US1] Add API tests for readiness and webhook validation in `tests/integration/api/test_admin_telegram_api.py`

### Implementation for User Story 1

- [X] T020 [US1] Implement readiness and webhook validation service in `src/multi_agent_platform/admin/telegram_config/service.py`
- [X] T021 [US1] Implement admin Telegram API/UI router in `src/multi_agent_platform/api/routers/admin_telegram.py`
- [X] T022 [US1] Register Telegram router in `src/multi_agent_platform/api/main.py`

**Checkpoint**: User Story 1 readiness is independently testable.

---

## Phase 4: User Story 2 - Manage Tenant Telegram Enablement (Priority: P2)

**Goal**: Admins can safely enable/disable Telegram per tenant with revision-token stale conflict protection.

**Independent Test**: Update Acme enablement as platform and tenant admins, submit stale revision, and verify Globex isolation.

### Tests for User Story 2

- [X] T023 [P] [US2] Add API integration tests for config update, stale conflict, and tenant isolation in `tests/integration/api/test_admin_telegram_api.py`
- [X] T024 [P] [US2] Add UI integration tests for tenant form, conflict state, and navigation in `tests/integration/api/test_admin_telegram_ui.py`
- [X] T025 [P] [US2] Add UI view model tests in `tests/unit/api/test_telegram_config_ui_models.py`

### Implementation for User Story 2

- [X] T026 [US2] Implement tenant configuration service methods in `src/multi_agent_platform/admin/telegram_config/service.py`
- [X] T027 [US2] Implement Telegram UI view models in `src/multi_agent_platform/api/ui/telegram_config.py`
- [X] T028 [US2] Add Telegram Configuration navigation item in `src/multi_agent_platform/api/ui/admin_console.py`
- [X] T029 [US2] Implement console template in `src/multi_agent_platform/web_admin/templates/telegram/index.html`

**Checkpoint**: User Story 2 tenant enablement is independently testable through API and browser UI.

---

## Phase 5: User Story 3 - Inspect Linked Identities And Link Tokens (Priority: P3)

**Goal**: Authorized admins can issue and revoke link tokens, inspect masked linked identities, and revoke identities.

**Independent Test**: Issue a token, simulate link summary creation, inspect masked identity, revoke token and identity.

### Tests for User Story 3

- [X] T030 [P] [US3] Add service tests for token issue/revoke, identity recording, revocation, masking, and command readiness in `tests/unit/admin/telegram_config/test_telegram_service.py`
- [X] T031 [P] [US3] Add API integration tests for token and identity flows in `tests/integration/api/test_admin_telegram_api.py`

### Implementation for User Story 3

- [X] T032 [US3] Implement link-token and identity service methods in `src/multi_agent_platform/admin/telegram_config/service.py`
- [X] T033 [US3] Add token and identity route handlers to `src/multi_agent_platform/api/routers/admin_telegram.py`
- [X] T034 [US3] Extend `ChannelService` with safe Telegram admin snapshots and revocation hooks in `src/multi_agent_platform/channels/service.py`

**Checkpoint**: User Story 3 token and identity operations are independently testable.

---

## Phase 6: User Story 4 - Review Safe Diagnostics (Priority: P4)

**Goal**: Admins can review recent webhook and delivery diagnostics without sensitive content.

**Independent Test**: Generate simulated diagnostics and verify category, status, trace, and redacted metadata rendering.

### Tests for User Story 4

- [X] T035 [P] [US4] Add service and repository tests for diagnostic list filtering and redaction in `tests/unit/admin/telegram_config/test_telegram_service.py`
- [X] T036 [P] [US4] Add API/UI integration tests for diagnostic summaries in `tests/integration/api/test_admin_telegram_api.py` and `tests/integration/api/test_admin_telegram_ui.py`

### Implementation for User Story 4

- [X] T037 [US4] Implement diagnostic list and creation methods in `src/multi_agent_platform/admin/telegram_config/service.py`
- [X] T038 [US4] Render diagnostics in `src/multi_agent_platform/web_admin/templates/telegram/index.html`

**Checkpoint**: User Story 4 diagnostics are independently testable.

---

## Final Phase: Polish And Cross-Cutting Verification

**Purpose**: Complete docs, QA artifacts, README updates, task tracking, and quality gates.

- [X] T039 [P] Generate QA environment file in `specs/017-telegram-configuration-console/.env.qa017`
- [X] T040 [P] Generate manual QA guide in `specs/017-telegram-configuration-console/qa017.md`
- [X] T041 [P] Generate browser UI QA walkthrough in `specs/017-telegram-configuration-console/qa017_ui.md`
- [X] T042 [P] Generate non-developer manual QA user guide with at least 160 lines in `specs/017-telegram-configuration-console/qa017_user_guide.md`
- [X] T043 [P] Add PR review notes in `specs/017-telegram-configuration-console/pr-review-notes.md`
- [X] T044 [P] Add testing instructions in `specs/017-telegram-configuration-console/testing-instructions.md`
- [X] T045 Update `README.md` with Telegram Configuration admin/API/QA summary
- [X] T046 Update `docs/quickstart.md` with QA017 validation entry
- [X] T047 Run QA document validation with `.specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/017-telegram-configuration-console`
- [X] T048 Run API validation with `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/017-telegram-configuration-console/validation.yml`
- [X] T049 Run Playwright UI validation with `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/017-telegram-configuration-console/validation.yml --start-processes`
- [X] T050 Run quality gates `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src`, and `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`
- [X] T051 Mark completed tasks in `specs/017-telegram-configuration-console/tasks.md`

## Dependencies

- Phase 1 must complete before Phase 2.
- Phase 2 must complete before all user stories.
- User Story 1 is the MVP and blocks meaningful UI readiness.
- User Story 2 depends on foundational tenant config storage.
- User Story 3 depends on User Story 2 tenant scope semantics.
- User Story 4 depends on diagnostic event storage.
- Final polish depends on all selected implementation stories.

## Parallel Execution Examples

- T002, T003, and T004 can run in parallel after T001.
- T008, T011, T014, and T017 can run in parallel while paired implementation tasks are developed.
- T018 and T019 can run in parallel once Phase 2 is complete.
- T023, T024, and T025 can run in parallel once readiness exists.
- T030 and T031 can run in parallel once tenant config exists.
- T039 through T044 can run in parallel after behavior stabilizes.

## Implementation Strategy

1. Deliver MVP readiness by completing Phases 1-3: storage, redaction, policy,
   schemas, repository, service, router, and admin shell registration.
2. Add tenant enablement and stale conflict handling with User Story 2.
3. Add link-token and linked identity controls with User Story 3.
4. Add diagnostics views with User Story 4.
5. Complete docs, QA artifacts, Playwright validation, and quality gates.
