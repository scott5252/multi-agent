# Tasks: User Briefing Preferences And Context

**Input**: Design documents from `/specs/023-user-briefing-preferences-and-context/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Phase 1: Setup And Contracts

- [X] T001 [P] [US1] Add contract coverage in `tests/contract/test_briefing_preferences_contract.py`.
- [X] T002 [P] [US1] Add documentation presence/redaction tests in `tests/docs/test_briefing_preferences_docs.py`.
- [X] T003 [P] [US1] Add auth surface/local permission tests in `tests/unit/auth/test_briefing_preferences_policy.py`.

## Phase 2: Data Model And Validation

- [X] T004 [US1] Add SQLAlchemy models in `src/multi_agent_platform/db/models/briefing_preferences.py`.
- [X] T005 [US1] Register briefing preference models in `src/multi_agent_platform/db/models/__init__.py`.
- [X] T006 [US1] Add additive Alembic migration in `alembic/versions/0020_briefing_preferences.py`.
- [X] T007 [P] [US1] Add domain models and validation helpers in `src/multi_agent_platform/admin/briefing_preferences/models.py`.
- [X] T008 [P] [US2] Add redaction helpers in `src/multi_agent_platform/admin/briefing_preferences/redaction.py`.
- [X] T009 [US1] Add repository in `src/multi_agent_platform/db/repositories/briefing_preferences.py`.

## Phase 3: User Profile Lifecycle (P1)

- [X] T010 [P] [US1] Add repository tests in `tests/unit/db/test_briefing_preferences_repository.py`.
- [X] T011 [P] [US1] Add service tests in `tests/unit/admin/briefing_preferences/test_briefing_preference_service.py`.
- [X] T012 [US1] Implement service lifecycle in `src/multi_agent_platform/admin/briefing_preferences/service.py`.
- [X] T013 [US1] Add API schemas in `src/multi_agent_platform/api/schemas/briefing_preferences.py`.
- [X] T014 [US1] Add API profile/import/export endpoints in `src/multi_agent_platform/api/routers/admin_briefing_preferences.py`.

## Phase 4: Admin Safe Summary UI (P2)

- [X] T015 [P] [US2] Add UI model in `src/multi_agent_platform/api/ui/briefing_preferences.py`.
- [X] T016 [P] [US2] Add Jinja template in `src/multi_agent_platform/web_admin/templates/briefing_preferences/index.html`.
- [X] T017 [US2] Register router, navigation, auth policies, and local principal permissions.
- [X] T018 [US2] Add integration API/UI tests in `tests/integration/api/test_admin_briefing_preferences_api.py` and `tests/integration/api/test_admin_briefing_preferences_ui.py`.

## Phase 5: Runtime Resolver (P3)

- [X] T019 [P] [US3] Add runtime resolver facade in `src/multi_agent_platform/runtime/briefing_preferences.py`.
- [X] T020 [US3] Integrate resolver into Telegram alias run inputs in `src/multi_agent_platform/channels/telegram.py` and `src/multi_agent_platform/api/routers/telegram_webhook.py`.
- [X] T021 [US3] Add runtime resolver tests in `tests/integration/runtime/test_briefing_preference_resolution.py`.

## Phase 6: Documentation And QA

- [X] T022 [P] Add QA docs `qa023.md`, `qa023_ui.md`, `qa023_user_guide.md`, `testing-instructions.md`, and `pr-review-notes.md`.
- [X] T023 [P] Update `README.md` and `docs/quickstart.md` with QA023 entry points.
- [X] T024 Run QA scripts, Playwright UI validation, Ruff, mypy, and pytest coverage gates.

## Dependencies & Execution Order

Phase 1 and Phase 2 establish contracts, schema, migration, and validation.
P1 profile lifecycle depends on the repository and domain validation. P2 UI
depends on P1 service/schemas. P3 runtime resolver depends on P1 service and
repository. Documentation and full validation happen after implementation.

## Parallel Opportunities

Tasks marked `[P]` touch independent files and can run in parallel when staffed.
This autopilot run will execute them sequentially in dependency order because
no sub-agent delegation was requested.
