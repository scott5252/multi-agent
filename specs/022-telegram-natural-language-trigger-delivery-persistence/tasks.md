# Tasks: Telegram Natural-Language Trigger Delivery Persistence

**Input**: Design documents from `/specs/022-telegram-natural-language-trigger-delivery-persistence/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/  
**Tests**: Required. Write tests before implementation for alias persistence, webhook routing, idempotency, mocked Bot API delivery, tenant isolation, revocation, UI, docs, and QA validation.

## Phase 1: Setup

- [X] T001 Create additive migration `alembic/versions/0019_telegram_alias_delivery.py`.
- [X] T002 Add Telegram alias and update receipt models in `src/multi_agent_platform/db/models/telegram_config.py` and register exports in `src/multi_agent_platform/db/models/__init__.py`.
- [X] T003 Add Telegram Bot API boundary module in `src/multi_agent_platform/channels/telegram_delivery.py`.

## Phase 2: Tests First - Contracts, Persistence, And Routing

- [X] T004 [P] [US1] Add alias API contract tests in `tests/contract/test_telegram_alias_delivery_contract.py`.
- [X] T005 [P] [US1] Extend repository tests for alias CRUD, normalized uniqueness, and update receipts in `tests/unit/db/test_telegram_config_repository.py`.
- [X] T006 [P] [US2] Extend channel repository tests for persistent Telegram identity lookup and delivery attempts in `tests/unit/db/test_channel_models.py`.
- [X] T007 [P] [US3] Add Bot API formatting and mock-delivery tests in `tests/unit/channels/test_telegram_delivery.py`.
- [X] T008 [US1] Extend admin Telegram API tests for alias create/list/stale conflict/cross-tenant denial in `tests/integration/api/test_admin_telegram_api.py`.
- [X] T009 [US1] Extend admin Telegram UI tests for the `Telegram Command Aliases` section in `tests/integration/api/test_admin_telegram_ui.py`.
- [X] T010 [US2] Extend Telegram webhook tests for persistent link consumption, `Morning briefing` alias routing, duplicate update replay, disabled tenant denial, and revoked identity denial in `tests/integration/api/test_telegram_webhook.py`.

## Phase 3: Alias Persistence And Admin Surface

- [X] T011 [US1] Implement alias normalization, response models, and stale revision handling in `src/multi_agent_platform/admin/telegram_config/models.py`, `src/multi_agent_platform/api/schemas/telegram_config.py`, and `src/multi_agent_platform/db/repositories/telegram_config.py`.
- [X] T012 [US1] Implement alias service methods and diagnostics in `src/multi_agent_platform/admin/telegram_config/service.py`.
- [X] T013 [US1] Add alias API and form handlers in `src/multi_agent_platform/api/routers/admin_telegram.py`.
- [X] T014 [US1] Render aliases in `src/multi_agent_platform/api/ui/telegram_config.py` and `src/multi_agent_platform/web_admin/templates/telegram/index.html`.

## Phase 4: Runtime Alias Routing And Delivery

- [X] T015 [US2] Implement persistent token consumption, identity lookup, update receipt replay, and delivery attempt repository helpers in `src/multi_agent_platform/db/repositories/channels.py` and `src/multi_agent_platform/db/repositories/telegram_config.py`.
- [X] T016 [US2] Extend `src/multi_agent_platform/channels/telegram.py` to route normalized aliases, enforce tenant config/readiness, reject revoked identities, and persist update receipts.
- [X] T017 [US3] Implement safe result formatting, mockable Bot API sendMessage client, and delivery attempt persistence in `src/multi_agent_platform/channels/telegram_delivery.py` and `src/multi_agent_platform/channels/telegram.py`.
- [X] T018 [US2] Wire webhook dependencies for session, config repository, channel repository, secret provider, and mock client injection in `src/multi_agent_platform/api/routers/telegram_webhook.py`.

## Phase 5: Documentation And QA Artifacts

- [X] T019 [P] Update `README.md` with QA022 Telegram alias trigger and delivery summary.
- [X] T020 [P] Update `docs/quickstart.md` with QA022 validation pointers.
- [X] T021 [P] Add QA environment file at `specs/022-telegram-natural-language-trigger-delivery-persistence/.env.qa022`.
- [X] T022 [P] Add generated QA validation guide at `specs/022-telegram-natural-language-trigger-delivery-persistence/qa022.md`.
- [X] T023 [P] Add generated Playwright QA guide at `specs/022-telegram-natural-language-trigger-delivery-persistence/qa022_ui.md`.
- [X] T024 [P] Add non-developer manual QA guide at `specs/022-telegram-natural-language-trigger-delivery-persistence/qa022_user_guide.md`.
- [X] T025 [P] Add PR review notes and testing instructions in `specs/022-telegram-natural-language-trigger-delivery-persistence/pr-review-notes.md` and `specs/022-telegram-natural-language-trigger-delivery-persistence/testing-instructions.md`.

## Phase 6: Validation

- [X] T026 Run targeted Telegram alias and delivery tests.
- [X] T027 Run `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/022-telegram-natural-language-trigger-delivery-persistence`.
- [X] T028 Run `uv run ruff check .`.
- [X] T029 Run `uv run ruff format --check .`.
- [X] T030 Run `uv run mypy src`.
- [X] T031 Run `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`.
- [X] T032 Run `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/022-telegram-natural-language-trigger-delivery-persistence/validation.yml`.
- [X] T033 Run `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/022-telegram-natural-language-trigger-delivery-persistence/validation.yml --start-processes`.

## Dependencies & Execution Order

- Phase 1 creates file anchors and migration shape.
- Phase 2 tests should fail before Phases 3 and 4 implementation.
- Phase 3 blocks browser/API alias management.
- Phase 4 blocks runtime delivery validation.
- Phase 5 can proceed after route names and file names stabilize.
- Phase 6 validates the completed feature.

## Parallel Opportunities

- T004 through T007 can be authored in parallel because they target disjoint test files.
- T019 through T025 can be authored in parallel after route names stabilize.
- Runtime delivery and admin UI work must remain sequential around shared Telegram modules.

## Implementation Strategy

1. Complete setup and tests.
2. Deliver P1 admin alias configuration and P1 runtime alias trigger.
3. Add P2 final Telegram delivery evidence through the mocked Bot API client.
4. Finish docs and validation gates.
