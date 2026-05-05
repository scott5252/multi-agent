# Tasks: React Channel, Telegram, And Briefing Preferences

**Input**: Design documents from `specs/036-react-channel-telegram-and-briefing-preferences/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`
**Tests**: Required by FR-020, FR-021, SC-001 through SC-008, and the React UI roadmap dual-auth validation policy.
**Organization**: Tasks are grouped by user story so each story remains independently testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches distinct files or does not depend on unfinished tasks.
- **[Story]**: User story label for story phases only.
- Every task names an exact file path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare Spec 036 artifacts and additive React channel workspace structure.

- [X] T001 Verify `.specify/feature.json` points to `specs/036-react-channel-telegram-and-briefing-preferences` and `AGENTS.md` references `specs/036-react-channel-telegram-and-briefing-preferences/plan.md`.
- [X] T002 [P] Create the channel/Telegram/briefing React component directory at `frontend/admin/src/components/channelTelegramBriefing/`.
- [X] T003 [P] Create the channel/Telegram/briefing frontend fixture file at `frontend/admin/src/test/channelTelegramBriefingTestData.ts`.
- [X] T004 [P] Create the backend schema module at `src/multi_agent_platform/api/schemas/admin_channel_telegram_briefing_react.py`.
- [X] T005 [P] Create the React adapter/service package at `src/multi_agent_platform/admin/channel_telegram_briefing/`.
- [X] T006 [P] Create the performance test directory at `tests/performance/channel_telegram_briefing/`.
- [X] T007 [P] Create QA036 documentation placeholders in `specs/036-react-channel-telegram-and-briefing-preferences/qa036.md`, `specs/036-react-channel-telegram-and-briefing-preferences/qa036_ui.md`, `specs/036-react-channel-telegram-and-briefing-preferences/.env.qa036`, `specs/036-react-channel-telegram-and-briefing-preferences/qa036_user_guide.md`, and `specs/036-react-channel-telegram-and-briefing-preferences/pr_notes.md`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish safe contracts, projections, generated types, protected routes, and shared fixtures before story work.

- [X] T008 Define safe text helpers, unsafe marker validation, status enums, action enums, and formatted primitives in `src/multi_agent_platform/api/schemas/admin_channel_telegram_briefing_react.py`.
- [X] T009 Define `ChannelTelegramBriefingDashboard`, readiness, tenant config, alias, link token, linked identity, webhook diagnostic, delivery attempt, run status, preference profile, mutation result, and problem schemas in `src/multi_agent_platform/api/schemas/admin_channel_telegram_briefing_react.py`.
- [X] T010 Define dashboard query, alias create/update request, alias action request, webhook validation request, link-token create request, preference save/import/export requests, and safe result schemas in `src/multi_agent_platform/api/schemas/admin_channel_telegram_briefing_react.py`.
- [X] T011 Add schema validators that reject bot tokens, webhook secrets, full Telegram identifiers, link tokens after creation, private messages, raw preference values, raw prompts, run results, raw tool payloads, local paths, fake QA secrets, and unauthorized tenant labels in `src/multi_agent_platform/api/schemas/admin_channel_telegram_briefing_react.py`.
- [X] T012 [P] Add schema tests for safe readiness, masked identities, one-time token creation, hidden follow-up token state, bounded rows, preference summaries, and unsafe marker rejection in `tests/unit/api/test_admin_channel_telegram_briefing_react_schema.py`.
- [X] T013 Implement deterministic QA036 constants, Acme/Globex tenant labels, readiness fixtures, alias fixtures, linked identity fixtures, delivery attempt fixtures, run status fixtures, preference profile fixtures, and audit references in `src/multi_agent_platform/admin/channel_telegram_briefing/react_channel_telegram_briefing.py`.
- [X] T014 Implement backend-owned redaction, masking, safe summary, idempotency, revision, link-token, and timestamp formatting helpers in `src/multi_agent_platform/admin/channel_telegram_briefing/react_channel_telegram_briefing.py`.
- [X] T015 Implement dashboard scope, allowed scope options, readiness cards, empty/denied/stale/audit-unavailable states, and tenant-filtered projections in `src/multi_agent_platform/admin/channel_telegram_briefing/react_channel_telegram_briefing.py`.
- [X] T016 Implement alias, link-token, linked identity, webhook diagnostic, delivery attempt, run status, preference profile, import/export, and admin-summary builders in `src/multi_agent_platform/admin/channel_telegram_briefing/react_channel_telegram_briefing.py`.
- [X] T017 Implement safe mutation result builders for config save, webhook validate, alias create/update/action, link-token create, preference save, preference import, and preference export in `src/multi_agent_platform/admin/channel_telegram_briefing/react_channel_telegram_briefing.py`.
- [X] T018 Implement fail-closed cross-tenant, tenant-user, invalid revision, idempotency replay, token-hidden, audit-unavailable, and dependency-unavailable result builders in `src/multi_agent_platform/admin/channel_telegram_briefing/react_channel_telegram_briefing.py`.
- [X] T019 [P] Add service tests for platform dashboard, tenant dashboard, tenant-user dashboard, token hiding, alias mutation, webhook validation, delivery diagnostics, preference save/import/export, cross-tenant denial, and redaction safety in `tests/unit/admin/channel_telegram_briefing/test_react_channel_telegram_briefing_service.py`.
- [X] T020 [P] Add bounded query/performance tests for dashboard, aliases, identities, diagnostics, run status, and preference projections in `tests/performance/channel_telegram_briefing/test_react_channel_telegram_briefing_queries.py`.
- [X] T021 Extend `scripts/frontend/generate_admin_react_types.py` with generated TypeScript interfaces and assert helpers for all channel/Telegram/briefing React schemas and request bodies.
- [X] T022 Regenerate `frontend/admin/src/api/generated/reactAdminApi.ts` from `scripts/frontend/generate_admin_react_types.py`.
- [X] T023 Add API client helpers for dashboard, webhook validation, alias actions, link-token creation, delivery diagnostics, run status, preference save/import/export, and export detail in `frontend/admin/src/api/client.ts`.
- [X] T024 Add protected React routes and endpoints for `/admin/app/channels` and `/admin/app/channels/*` in `src/multi_agent_platform/api/routers/admin_react.py`.
- [X] T025 Register channel/Telegram/briefing React route surfaces as authenticated protected surfaces in `src/multi_agent_platform/auth/policy.py`.
- [X] T026 Wire `/admin/app/channels` and safe run status/detail routes into `frontend/admin/src/App.tsx`.
- [X] T027 Remove channels from disabled React route fallbacks while preserving existing Jinja fallback handling in `frontend/admin/src/routes.tsx`.
- [X] T028 Add channel/Telegram/briefing workspace styles, responsive layout rules, form/table dimensions, token result states, and stable diagnostic row dimensions in `frontend/admin/src/styles/admin.css`.
- [X] T029 [P] Add contract coverage for dashboard, webhook validation, alias actions, link tokens, deliveries, run status, preference save/import/export route shapes in `tests/contract/test_admin_react_contract.py`.
- [X] T030 [P] Add integration coverage for denied, Auth0-shaped, local-principal platform, tenant-admin, and tenant-user React route authorization in `tests/integration/test_admin_react_routes.py`.
- [X] T031 [P] Add frontend fixture data mirroring generated schemas in `frontend/admin/src/test/channelTelegramBriefingTestData.ts`.

**Checkpoint**: Backend contracts, generated browser types, protected routes, and shared fixtures are ready.

---

## Phase 3: User Story 1 - Review Channel And Telegram Readiness (Priority: P1)

**Goal**: Platform and tenant administrators can understand channel readiness, Telegram enablement, webhook status, secret-reference readiness, linked identity coverage, delivery health, and safe next steps.

**Independent Test**: Sign in as platform-admin and tenant-admin-acme, open `/admin/app/channels`, and verify readiness cards, tenant config, webhook validation, safe references, identity summaries, states, and no unauthorized tenant or secret data.

### Tests for User Story 1

- [X] T032 [P] [US1] Add dashboard rendering, loading, denied, and stale-readiness tests in `frontend/admin/src/components/channelTelegramBriefing/ChannelTelegramBriefingPage.test.tsx`.
- [X] T033 [P] [US1] Add readiness card and tenant config panel tests in `frontend/admin/src/components/channelTelegramBriefing/ReadinessAndConfigPanel.test.tsx`.
- [X] T034 [P] [US1] Add webhook validation panel tests in `frontend/admin/src/components/channelTelegramBriefing/WebhookValidationPanel.test.tsx`.
- [X] T035 [P] [US1] Extend platform and tenant dashboard integration tests in `tests/integration/test_admin_react_routes.py`.

### Implementation for User Story 1

- [X] T036 [US1] Implement `ChannelTelegramBriefingPage` orchestration, bootstrap loading, scope-aware state, refresh handling, and mutation result toasts in `frontend/admin/src/components/channelTelegramBriefing/ChannelTelegramBriefingPage.tsx`.
- [X] T037 [P] [US1] Implement `ChannelReadinessHeader` with active scope, readiness status, validation freshness, and refresh action in `frontend/admin/src/components/channelTelegramBriefing/ChannelReadinessHeader.tsx`.
- [X] T038 [P] [US1] Implement `ReadinessCardGrid` for channel, Telegram, webhook, secret-reference, identity, delivery, and preference resolver readiness in `frontend/admin/src/components/channelTelegramBriefing/ReadinessCardGrid.tsx`.
- [X] T039 [P] [US1] Implement `TelegramConfigPanel` with enablement status, safe reference labels, validation action, revision, and audit evidence in `frontend/admin/src/components/channelTelegramBriefing/TelegramConfigPanel.tsx`.
- [X] T040 [P] [US1] Implement `WebhookValidationPanel` with explicit validation action, result status, timestamp, safe receipt summary, and audit evidence in `frontend/admin/src/components/channelTelegramBriefing/WebhookValidationPanel.tsx`.
- [X] T041 [P] [US1] Implement `ChannelStatePanel` for empty, stale, denied, dependency-unavailable, validation-error, conflict, and audit-unavailable states in `frontend/admin/src/components/channelTelegramBriefing/ChannelStatePanel.tsx`.
- [X] T042 [US1] Connect dashboard bootstrap, config save, webhook validation, platform scope, tenant scope, and safe problem rendering in `frontend/admin/src/components/channelTelegramBriefing/ChannelTelegramBriefingPage.tsx`.
- [X] T043 [US1] Update `src/multi_agent_platform/api/routers/admin_react.py` to return platform and tenant dashboard projections for `/admin/app/channels/bootstrap.json`.
- [X] T044 [US1] Update `tests/integration/test_admin_react_routes.py` to assert tenant admins cannot see Globex readiness while platform admins can intentionally review authorized tenant readiness.

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Manage Aliases, Identity Links, Delivery Diagnostics, And Run Links (Priority: P2)

**Goal**: Tenant administrators can manage aliases, create one-time link tokens, inspect masked linked identities, review delivery diagnostics, and open safe run status summaries.

**Independent Test**: In Acme tenant scope, create/update/disable an alias, refresh readiness, create a link token, verify token one-time visibility, inspect identities and delivery attempts, and open a safe run status link.

### Tests for User Story 2

- [X] T045 [P] [US2] Add alias list/form/action tests in `frontend/admin/src/components/channelTelegramBriefing/AliasManagementPanel.test.tsx`.
- [X] T046 [P] [US2] Add link-token and linked identity tests in `frontend/admin/src/components/channelTelegramBriefing/IdentityLinkPanel.test.tsx`.
- [X] T047 [P] [US2] Add delivery diagnostics and run status tests in `frontend/admin/src/components/channelTelegramBriefing/DeliveryDiagnosticsPanel.test.tsx`.
- [X] T048 [P] [US2] Add backend alias/link-token/diagnostics/run status tests in `tests/unit/admin/channel_telegram_briefing/test_react_channel_telegram_briefing_service.py`.
- [X] T049 [P] [US2] Extend integration tests for alias CRUD, idempotency replay, link-token creation, token hiding, delivery diagnostics, and safe run status in `tests/integration/test_admin_react_routes.py`.

### Implementation for User Story 2

- [X] T050 [P] [US2] Implement `AliasManagementPanel` with bounded rows, create/edit form, disable/delete/refresh actions, protected readiness badges, revision/conflict hints, and audit evidence in `frontend/admin/src/components/channelTelegramBriefing/AliasManagementPanel.tsx`.
- [X] T051 [P] [US2] Implement `IdentityLinkPanel` with one-time token result, token-hidden follow-up state, expiration guidance, masked linked identities, and audit evidence in `frontend/admin/src/components/channelTelegramBriefing/IdentityLinkPanel.tsx`.
- [X] T052 [P] [US2] Implement `DeliveryDiagnosticsPanel` with bounded attempts, webhook receipt summaries, retry categories, Bot API boundary status, safe run status link actions, and trace/audit evidence in `frontend/admin/src/components/channelTelegramBriefing/DeliveryDiagnosticsPanel.tsx`.
- [X] T053 [P] [US2] Implement `RunStatusSummaryPage` for safe user-facing run status summaries in `frontend/admin/src/components/channelTelegramBriefing/RunStatusSummaryPage.tsx`.
- [X] T054 [US2] Connect alias mutation, alias action, link-token creation, delivery reload, and run status navigation to `ChannelTelegramBriefingPage` in `frontend/admin/src/components/channelTelegramBriefing/ChannelTelegramBriefingPage.tsx`.
- [X] T055 [US2] Update `src/multi_agent_platform/admin/channel_telegram_briefing/react_channel_telegram_briefing.py` to project alias CRUD, protected readiness, link-token result, linked identity, delivery diagnostic, and run status summaries safely.
- [X] T056 [US2] Update `src/multi_agent_platform/api/routers/admin_react.py` with alias, link-token, delivery diagnostic, and run status endpoints.
- [X] T057 [US2] Update `tests/unit/admin/channel_telegram_briefing/test_react_channel_telegram_briefing_service.py` to prove one-time token visibility and follow-up token hiding.

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Manage Daily Briefing Preference Profiles (Priority: P3)

**Goal**: Authorized tenant users can manage their Daily Briefing preference profile, and tenant administrators can review safe preference summaries plus import/export evidence.

**Independent Test**: Sign in as tenant-user-acme, save a complete preference profile, then sign in as tenant-admin-acme and verify raw private values are redacted from summaries, import/export evidence, and screenshots.

### Tests for User Story 3

- [X] T058 [P] [US3] Add preference form validation and save tests in `frontend/admin/src/components/channelTelegramBriefing/BriefingPreferencePanel.test.tsx`.
- [X] T059 [P] [US3] Add admin summary and import/export tests in `frontend/admin/src/components/channelTelegramBriefing/BriefingPreferenceAdminPanel.test.tsx`.
- [X] T060 [P] [US3] Add backend preference save/import/export/redaction tests in `tests/unit/admin/channel_telegram_briefing/test_react_channel_telegram_briefing_service.py`.
- [X] T061 [P] [US3] Extend integration tests for tenant-user preference save, tenant-admin safe summaries, import/export, Auth0-shaped principal, and cross-user denial in `tests/integration/test_admin_react_routes.py`.

### Implementation for User Story 3

- [X] T062 [P] [US3] Implement `BriefingPreferencePanel` with location, timezone, topics, VIP sender hints, workday hours, commute mode, account references, output style, scheduled time, validation, and revision evidence in `frontend/admin/src/components/channelTelegramBriefing/BriefingPreferencePanel.tsx`.
- [X] T063 [P] [US3] Implement `BriefingPreferenceAdminPanel` with redacted summaries, runtime readiness, revision metadata, import/export actions, artifact references, and audit evidence in `frontend/admin/src/components/channelTelegramBriefing/BriefingPreferenceAdminPanel.tsx`.
- [X] T064 [P] [US3] Implement `BriefingPreferenceMutationResultPanel` for save/import/export accepted, replayed, validation-error, conflict, denied, and audit-unavailable states in `frontend/admin/src/components/channelTelegramBriefing/BriefingPreferenceMutationResultPanel.tsx`.
- [X] T065 [US3] Connect preference save/import/export and safe admin summaries to `ChannelTelegramBriefingPage` in `frontend/admin/src/components/channelTelegramBriefing/ChannelTelegramBriefingPage.tsx`.
- [X] T066 [US3] Update `src/multi_agent_platform/admin/channel_telegram_briefing/react_channel_telegram_briefing.py` to project preference profile, admin summaries, runtime readiness, save/import/export results, and profile-only scheduled time safely.
- [X] T067 [US3] Update `src/multi_agent_platform/api/routers/admin_react.py` with preference read, save, import, and export endpoints.
- [X] T068 [US3] Update `tests/unit/admin/channel_telegram_briefing/test_react_channel_telegram_briefing_service.py` to prove admin summaries hide raw private preference values.

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation manifest, generated checks, redaction scans, and final task completion.

- [X] T069 [P] Update Spec 036 QA API/database guide in `specs/036-react-channel-telegram-and-briefing-preferences/qa036.md`.
- [X] T070 [P] Update Spec 036 UI walkthrough in `specs/036-react-channel-telegram-and-briefing-preferences/qa036_ui.md`.
- [X] T071 [P] Update Spec 036 local QA environment in `specs/036-react-channel-telegram-and-briefing-preferences/.env.qa036`.
- [X] T072 [P] Update Spec 036 manual user guide in `specs/036-react-channel-telegram-and-briefing-preferences/qa036_user_guide.md`.
- [X] T073 [P] Update Spec 036 reviewer notes in `specs/036-react-channel-telegram-and-briefing-preferences/pr_notes.md`.
- [X] T074 Update React roadmap validation manifest for QA036 routes, curl commands, quality commands, Playwright flows, screenshots, and redaction scans in `specs/_autopilot/react-ui-roadmap/036-react-channel-telegram-and-briefing-preferences/validation.yml`.
- [X] T075 [P] Update React channel/Telegram/briefing feature notes in `README.md`.
- [X] T076 [P] Update local validation quickstart notes in `docs/quickstart.md`.
- [X] T077 Run `uv run python scripts/frontend/generate_admin_react_types.py --check` and fix drift in `scripts/frontend/generate_admin_react_types.py` or `frontend/admin/src/api/generated/reactAdminApi.ts`.
- [X] T078 Run focused backend tests with `uv run pytest --no-cov tests/unit/api/test_admin_channel_telegram_briefing_react_schema.py tests/unit/admin/channel_telegram_briefing/test_react_channel_telegram_briefing_service.py tests/performance/channel_telegram_briefing/test_react_channel_telegram_briefing_queries.py tests/contract/test_admin_react_contract.py tests/integration/test_admin_react_routes.py` and fix failures in touched files.
- [X] T079 Run frontend checks with `npm run typecheck`, `npm run test`, and `npm run build` in `frontend/admin` and fix failures in `frontend/admin/src/`.
- [X] T080 Run QA document validation with `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/036-react-channel-telegram-and-briefing-preferences` and fix Spec 036 docs.
- [X] T081 Run full Spec QA with `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/036-react-channel-telegram-and-briefing-preferences/validation.yml` and fix active-spec failures only.
- [X] T082 Run Playwright UI validation with `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/036-react-channel-telegram-and-briefing-preferences/validation.yml --start-processes` and fix active-spec failures only.
- [X] T083 Run redaction scan `rg -n "qa036-secret-value|bot token|webhook secret|full telegram|link token after creation|private message|raw preference|raw prompt|run result|raw tool payload|/Users/|unauthorized tenant label" /tmp/qa036-* output/playwright/qa036_ui || true` and remove unsafe QA036 evidence if any appears.
- [X] T084 Mark completed tasks in `specs/036-react-channel-telegram-and-briefing-preferences/tasks.md` after implementation and validation pass.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational; MVP scope.
- **User Story 2 (Phase 4)**: Depends on Foundational and can be implemented after US1 while remaining independently testable.
- **User Story 3 (Phase 5)**: Depends on Foundational and can be implemented after US1 while remaining independently testable.
- **Polish (Phase 6)**: Depends on all desired user stories and validation artifacts.

### User Story Dependencies

- **US1**: No story dependency after Foundational.
- **US2**: Uses shared dashboard scope and mutation result patterns from US1, but alias/diagnostic flows must remain independently testable.
- **US3**: Uses shared dashboard scope and mutation result patterns from US1, but preference profile flows must remain independently testable.

### Parallel Opportunities

- Setup tasks T002 through T007 are parallelizable.
- Schema/service/performance/frontend fixture tests T012, T019, T020, T029, T030, and T031 can be prepared in parallel once schemas are sketched.
- US1 component tests T032 through T034 can be developed in parallel with integration test T035.
- US2 tests T045 through T049 and components T050 through T053 can be split safely by file.
- US3 tests T058 through T061 and components T062 through T064 can be split safely by file.
- Documentation tasks T069 through T076 can be drafted in parallel after implementation behavior is stable.

## Parallel Example: User Story 1

```bash
Task: "Implement ReadinessCardGrid for channel, Telegram, webhook, secret-reference, identity, delivery, and preference resolver readiness in frontend/admin/src/components/channelTelegramBriefing/ReadinessCardGrid.tsx"
Task: "Implement WebhookValidationPanel with explicit validation action, result status, timestamp, safe receipt summary, and audit evidence in frontend/admin/src/components/channelTelegramBriefing/WebhookValidationPanel.tsx"
```

## Parallel Example: User Story 2

```bash
Task: "Implement AliasManagementPanel with bounded rows, create/edit form, disable/delete/refresh actions, protected readiness badges, revision/conflict hints, and audit evidence in frontend/admin/src/components/channelTelegramBriefing/AliasManagementPanel.tsx"
Task: "Implement DeliveryDiagnosticsPanel with bounded attempts, webhook receipt summaries, retry categories, Bot API boundary status, safe run status link actions, and trace/audit evidence in frontend/admin/src/components/channelTelegramBriefing/DeliveryDiagnosticsPanel.tsx"
```

## Parallel Example: User Story 3

```bash
Task: "Implement BriefingPreferencePanel with location, timezone, topics, VIP sender hints, workday hours, commute mode, account references, output style, scheduled time, validation, and revision evidence in frontend/admin/src/components/channelTelegramBriefing/BriefingPreferencePanel.tsx"
Task: "Implement BriefingPreferenceAdminPanel with redacted summaries, runtime readiness, revision metadata, import/export actions, artifact references, and audit evidence in frontend/admin/src/components/channelTelegramBriefing/BriefingPreferenceAdminPanel.tsx"
```

## Implementation Strategy

1. Complete setup and foundational contracts.
2. Deliver US1 first as the MVP readiness dashboard.
3. Add US2 alias, identity, delivery, and run status workflows.
4. Add US3 preference profile and safe admin summary workflows.
5. Complete docs, QA validation, redaction scans, and task closure before Spec 037.
