# Tasks: Channels, Telegram, Briefing React Live Data

**Input**: Design documents from `specs/055-channels-telegram-briefing-react-live-data/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required by the feature spec. Include backend route/service/repository tests, generated contract checks, frontend tests, scanner tests, QA document validation, Spec QA, Playwright, post-UI persistence verification, and curl regression validation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel when executed by separate workers because it touches different files and has no dependency on incomplete tasks.
- **[Story]**: Maps task to US1, US2, or US3 from spec.md.
- No task requires staging, committing, or a clean Git worktree; validated prior-spec changes remain in the dirty worktree until the user commits.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Align contracts, validation manifests, and QA targets before implementation.

- [X] T001 Review current channel/Telegram/briefing React builders, route wiring, schemas, repositories, services, and frontend panels in `src/multi_agent_platform/admin/channel_telegram_briefing/react_channel_telegram_briefing.py`, `src/multi_agent_platform/api/routers/admin_react.py`, `src/multi_agent_platform/api/schemas/admin_channel_telegram_briefing_react.py`, `src/multi_agent_platform/channels/`, `src/multi_agent_platform/admin/briefing_preferences.py`, and `frontend/admin/src/components/channelTelegramBriefing/`
- [X] T002 [P] Reconcile qa055 validation commands, route hints, Playwright flow target, and post-UI persistence command in `specs/_autopilot/remove-mock-data-roadmap/055-channels-telegram-briefing-react-live-data/validation.yml`
- [X] T003 [P] Add qa055 seed and verifier script placeholders in `scripts/qa/seed_channels_briefing_qa055.py` and `scripts/qa/verify_channels_briefing_qa055.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core live-data contracts and safe projection foundation that all user stories depend on.

- [X] T004 [P] Extend channel/Telegram/briefing React schemas with provenance, empty-state, source metadata, and safe mutation result contracts in `src/multi_agent_platform/api/schemas/admin_channel_telegram_briefing_react.py`
- [X] T005 [P] Add bounded repository/service helper methods for live config, aliases, identities, link-token audits, webhook receipts, deliveries, notifications, run links, preferences, imports, exports, and audits in `src/multi_agent_platform/channels/`, `src/multi_agent_platform/admin/briefing_preferences.py`, and related `src/multi_agent_platform/db/repositories/` modules
- [X] T006 [P] Add qa055 live channel and briefing fixtures for tests in `tests/fixtures/channel_telegram_briefing.py`
- [X] T007 Add shared channel/briefing projection helpers for scope resolution, safe labels, empty sections, mutation results, and redaction in `src/multi_agent_platform/admin/channel_telegram_briefing/react_channel_telegram_briefing.py`
- [X] T008 Regenerate frontend API contracts from Pydantic schemas into `frontend/admin/src/api/generated/reactAdminApi.ts`

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Review Live Channel And Briefing State (Priority: P1)

**Goal**: Authorized operators and tenant administrators see only live Telegram config, aliases, identities, deliveries, webhook receipts, notifications, run links, briefing preferences, imports, exports, and audit rows for the active scope, or truthful empty/denied/unavailable states.

**Independent Test**: Load `/admin/app/channels/bootstrap.json` and the browser workspace against an empty qa055 database and a seeded qa055 database, then compare rows to persisted channel/briefing records.

### Tests for User Story 1

- [X] T009 [P] [US1] Add live empty/seeded dashboard service tests in `tests/unit/admin/channel_telegram_briefing/test_react_channel_telegram_briefing_service.py`
- [X] T010 [P] [US1] Add repository tenant/platform filtering tests for config, aliases, identities, deliveries, notifications, and preferences in `tests/unit/db/test_channel_telegram_briefing_repositories.py`
- [X] T011 [P] [US1] Add Auth0-shaped and local-principal route tests for channel bootstrap, empty state, seeded state, and cross-tenant denial in `tests/integration/test_admin_react_routes.py`
- [X] T012 [P] [US1] Add bounded query performance coverage in `tests/performance/channel_telegram_briefing/test_react_channel_telegram_briefing_queries.py`

### Implementation for User Story 1

- [X] T013 [US1] Replace fixed channel/Telegram/briefing dashboard rows with async service-backed live snapshot projections in `src/multi_agent_platform/admin/channel_telegram_briefing/react_channel_telegram_briefing.py`
- [X] T014 [US1] Wire `/admin/app/channels/bootstrap.json` to live Telegram config, delivery, notification, audit, and briefing preference dependencies in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T015 [US1] Update frontend empty/live provenance rendering in `frontend/admin/src/components/channelTelegramBriefing/ChannelTelegramBriefingPage.tsx` and related panel components
- [X] T016 [US1] Update frontend channel/briefing test fixtures and component tests for live empty and seeded states in `frontend/admin/src/test/channelTelegramBriefingTestData.ts` and `frontend/admin/src/components/channelTelegramBriefing/*.test.tsx`

**Checkpoint**: User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Inspect Redaction-Safe Delivery And Telegram Evidence (Priority: P2)

**Goal**: Telegram readiness, alias, linked identity, link-token audit, webhook receipt, delivery diagnostic, run link, notification, briefing preference, import/export, and audit details show useful safe evidence without leaking raw identifiers or payloads.

**Independent Test**: Seed sensitive-adjacent records, then assert JSON, browser text, screenshots, QA docs, and artifacts expose only masked labels, safe summaries, and authorized references.

### Tests for User Story 2

- [X] T017 [P] [US2] Add schema redaction and unsafe-text rejection tests in `tests/unit/api/test_admin_channel_telegram_briefing_react_schema.py`
- [X] T018 [P] [US2] Add delivery diagnostics, webhook receipt, run link, preference, import/export, and audit route tests in `tests/integration/test_admin_react_routes.py`
- [X] T019 [P] [US2] Add scanner guardrail tests for QA036 channel/Telegram/briefing markers in `tests/unit/admin/test_live_data_inventory_scanner.py`
- [X] T020 [P] [US2] Add frontend redaction tests for Telegram identifiers, token/link-token visibility, private messages, run payloads, and briefing content in `frontend/admin/src/components/channelTelegramBriefing/*.test.tsx`

### Implementation for User Story 2

- [X] T021 [US2] Replace fixed delivery diagnostics, webhook receipt, run link, notification, preference, import/export, and audit builders with live bounded projections in `src/multi_agent_platform/admin/channel_telegram_briefing/react_channel_telegram_briefing.py`
- [X] T022 [US2] Wire channel diagnostics, audit, preference, import/export, and run-link endpoints to live repositories/services in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T023 [US2] Update scanner production-surface rules to fail QA036 channel/Telegram/briefing markers in `src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py`
- [X] T024 [US2] Update frontend panels to render safe live evidence, empty states, and no raw identifiers in `frontend/admin/src/components/channelTelegramBriefing/`

**Checkpoint**: User Stories 1 and 2 should both work independently.

---

## Phase 5: User Story 3 - Exercise Durable Channel And Briefing Actions (Priority: P3)

**Goal**: At least one visible channel, Telegram, or briefing action persists through backend services, and mutation surfaces return persisted, replayed, stale, denied, validation, one-time-token, artifact, or unavailable evidence without browser-only success.

**Independent Test**: Use Playwright to save an alias or briefing preference, then verify persisted action and audit evidence through backend API or a redaction-safe qa055 database query.

### Tests for User Story 3

- [X] T025 [P] [US3] Add service mutation tests for alias save/enable/disable/delete, link-token creation/revocation, webhook validation, briefing preference save/import/export, replay, denial, and stale branches in `tests/unit/admin/channel_telegram_briefing/test_react_channel_telegram_briefing_service.py`
- [X] T026 [P] [US3] Add React route mutation tests for accepted, replayed, denied, stale, one-time-token, artifact, and invalid actions in `tests/integration/test_admin_react_routes.py`
- [X] T027 [P] [US3] Add frontend mutation result tests in `frontend/admin/src/components/channelTelegramBriefing/*.test.tsx`

### Implementation for User Story 3

- [X] T028 [US3] Migrate alias, link-token, webhook validation, briefing preference save/import/export, and diagnostic mutation builders to existing durable services in `src/multi_agent_platform/admin/channel_telegram_briefing/react_channel_telegram_briefing.py`
- [X] T029 [US3] Wire channel/briefing mutation endpoints to live dependencies and safe error mapping in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T030 [US3] Ensure frontend channel/briefing forms submit backend-owned actions and refresh persisted results in `frontend/admin/src/components/channelTelegramBriefing/`
- [X] T031 [US3] Implement qa055 Playwright seed and post-UI persistence verification in `scripts/qa/seed_channels_briefing_qa055.py`, `scripts/qa/verify_channels_briefing_qa055.py`, and `specs/_autopilot/remove-mock-data-roadmap/055-channels-telegram-briefing-react-live-data/validation.yml`

**Checkpoint**: All user stories should now be independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, QA artifacts, contract generation, and required validation.

- [X] T032 [P] Generate qa055 QA guide, UI walkthrough, environment file, manual user guide, and reviewer notes in `specs/055-channels-telegram-briefing-react-live-data/qa055.md`, `specs/055-channels-telegram-briefing-react-live-data/qa055_ui.md`, `specs/055-channels-telegram-briefing-react-live-data/.env.qa055`, `specs/055-channels-telegram-briefing-react-live-data/qa055_user_guide.md`, and `specs/055-channels-telegram-briefing-react-live-data/pr_notes.md`
- [X] T033 [P] Update channel/briefing live-data contracts and quickstart after implementation in `specs/055-channels-telegram-briefing-react-live-data/contracts/` and `specs/055-channels-telegram-briefing-react-live-data/quickstart.md`
- [X] T034 Run Ruff, mypy-targeted checks where applicable, focused pytest, frontend tests, and build commands from `specs/055-channels-telegram-briefing-react-live-data/quickstart.md`
- [X] T035 Run QA document validation with `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/055-channels-telegram-briefing-react-live-data`
- [X] T036 Run Spec QA with `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/055-channels-telegram-briefing-react-live-data/validation.yml`
- [X] T037 Run Playwright UI validation with `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/055-channels-telegram-briefing-react-live-data/validation.yml --start-processes`
- [X] T038 Run post-UI persistence verification with `uv run python scripts/qa/verify_channels_briefing_qa055.py`
- [X] T039 Run multi-agent curl regression with `uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa055-after-spec`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories.
- **User Stories (Phase 3-5)**: Depend on Foundational completion. Execute sequentially for the autopilot, but each story remains independently testable.
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational; no dependency on US2 or US3.
- **User Story 2 (P2)**: Can start after Foundational; uses the same live snapshot foundation as US1.
- **User Story 3 (P3)**: Can start after Foundational; mutation UI benefits from US1 refresh behavior and US2 redaction checks.

### Parallel Opportunities

- T002 and T003 can run in parallel after T001 review.
- T004, T005, and T006 can run in parallel before T007 integration.
- US1 tests T009-T012 can be drafted in parallel.
- US2 tests T017-T020 can be drafted in parallel.
- US3 tests T025-T027 can be drafted in parallel.
- Documentation T032 and contract/quickstart update T033 can proceed once implementation behavior is stable.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup and Foundational tasks.
2. Replace bootstrap/dashboard fixed data with live repository-backed projections.
3. Validate empty database, seeded database, and cross-tenant denial for `/admin/app/channels/bootstrap.json`.

### Incremental Delivery

1. Add US1 live dashboard and truthful empty state.
2. Add US2 redaction-safe diagnostics, run links, preferences, imports, exports, and audit evidence.
3. Add US3 durable channel/briefing actions and post-UI persistence verification.
4. Run full qa055 validation and curl regression before advancing to Spec 056.
