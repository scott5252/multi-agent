# Tasks: Channels, Memberships, Access, Telegram, And Briefing Full React Parity

**Input**: Design documents from `specs/045-channels-memberships-access-telegram-and-briefing-full-react-parity/`

## Phase 1: Setup And Existing Surface Verification

- [x] T001 Record remaining memberships/Telegram/briefing template inventory in quickstart.md
- [x] T002 [P] Confirm React membership route coverage in tests/integration/test_admin_react_routes.py
- [x] T003 [P] Confirm React channel route coverage in tests/integration/test_admin_react_routes.py
- [x] T004 [P] Confirm old membership browser coverage in tests/integration/api/test_admin_memberships_ui.py
- [x] T005 [P] Confirm old Telegram browser coverage in tests/integration/api/test_admin_telegram_ui.py
- [x] T006 [P] Confirm old briefing browser coverage in tests/integration/api/test_admin_briefing_preferences_ui.py

## Phase 2: Tests First

- [x] T007 [P] Add Spec 045 legacy route expectations in tests/contract/test_admin_react_contract.py
- [x] T008 [P] Add channels/people Jinja retirement scanner in tests/unit/admin/test_channels_people_jinja_retirement.py
- [x] T009 [P] Add membership GET redirect assertions in tests/integration/api/test_admin_memberships_ui.py
- [x] T010 [P] Add membership form-post redirect assertions in tests/integration/api/test_admin_memberships_ui.py
- [x] T011 [P] Add Telegram GET redirect assertions in tests/integration/api/test_admin_telegram_ui.py
- [x] T012 [P] Add Telegram form-post redirect assertions and token visibility checks in tests/integration/api/test_admin_telegram_ui.py
- [x] T013 [P] Add briefing GET redirect assertions in tests/integration/api/test_admin_briefing_preferences_ui.py
- [x] T014 [P] Add briefing save/import/export redirect assertions in tests/integration/api/test_admin_briefing_preferences_ui.py
- [x] T015 [P] Add cross-tenant denial coverage for old membership, Telegram, and briefing routes
- [x] T016 Add safe legacy redirect helpers for memberships, Telegram, and briefing routers

## Phase 3: Memberships React Parity And Jinja Removal

- [x] T017 [US1] Convert GET `/admin/memberships` to a React redirect in src/multi_agent_platform/api/routers/admin_memberships.py
- [x] T018 [US1] Convert old membership invitation, role-grant, revoke, principal-status, and membership-status form routes to redirect after retained service behavior
- [x] T019 [US1] Preserve safe membership query context for tenant, q, status, principal, membership, role grant, and saved filters
- [x] T020 [US1] Update admin shell membership navigation and filter profiles to `/admin/app/memberships`
- [x] T021 [US1] Update membership tests for platform, tenant admin, tenant user, unauthorized, and cross-tenant principals
- [x] T022 [US1] Delete `src/multi_agent_platform/web_admin/templates/memberships/index.html`

## Phase 4: Telegram And Channel React Parity And Jinja Removal

- [x] T023 [US2] Convert GET `/admin/telegram` and old Telegram browser GET variants to React channel redirects
- [x] T024 [US2] Convert old Telegram config, alias, webhook validation, and link-token form routes to redirect after retained service behavior
- [x] T025 [US2] Preserve safe Telegram query context for tenant, alias, identity, diagnostic, status, and saved filters
- [x] T026 [US2] Keep raw link token visibility creation-only in tests and docs
- [x] T027 [US2] Update admin shell Telegram navigation and filter profiles to `/admin/app/channels?panel=telegram`
- [x] T028 [US2] Delete `src/multi_agent_platform/web_admin/templates/telegram/index.html`

## Phase 5: Briefing Preferences React Parity And Jinja Removal

- [x] T029 [US3] Convert GET `/admin/briefing-preferences` to a React channel briefing redirect
- [x] T030 [US3] Convert old briefing save, import, and export browser routes to redirect after retained service behavior or safe metadata response
- [x] T031 [US3] Preserve safe briefing query context for tenant, panel, saved filters, import/export, and revision references
- [x] T032 [US3] Update admin shell briefing navigation and filter profiles to `/admin/app/channels?panel=briefing`
- [x] T033 [US3] Update briefing tests for tenant user, tenant admin, platform admin, Auth0-shaped, and cross-tenant paths
- [x] T034 [US3] Delete `src/multi_agent_platform/web_admin/templates/briefing_preferences/index.html`

## Phase 6: Cross-Cutting Cleanup

- [x] T035 Remove unused TemplateResponse/Jinja imports from converted routers
- [x] T036 Update migration inventory notes for Spec 045 in specs/038-jinja-surface-inventory-and-deletion-plan/pr_notes.md
- [x] T037 Update docs that point to old memberships, Telegram, or briefing browser URLs when React destinations are now preferred
- [x] T038 Regenerate React admin TypeScript contracts and verify generated files are current
- [x] T039 Run scanner tests proving no converted router references retired templates

## Phase 7: QA Docs And Validation

- [x] T040 [P] Create `.env.qa045`
- [x] T041 [P] Create `qa045.md`
- [x] T042 [P] Create `qa045_ui.md`
- [x] T043 [P] Create `qa045_user_guide.md`
- [x] T044 [P] Create `pr_notes.md`
- [x] T045 Patch validation.yml to use local-principal login and `/admin/app/channels`
- [x] T046 Run generated TypeScript contract check
- [x] T047 Run focused backend tests from quickstart
- [x] T048 Run frontend membership, channel, and App tests
- [x] T049 Run QA document validation
- [x] T050 Run `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui2-roadmap/045-channels-memberships-access-telegram-and-briefing-full-react-parity/validation.yml`
- [x] T051 Run `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui2-roadmap/045-channels-memberships-access-telegram-and-briefing-full-react-parity/validation.yml --start-processes`
- [x] T052 Inspect Playwright screenshot under output/playwright/qa045_ui

## Dependencies

- Tests T007-T015 before route conversion.
- Membership conversion T017-T021 before deleting membership template T022.
- Telegram conversion T023-T027 before deleting Telegram template T028.
- Briefing conversion T029-T033 before deleting briefing template T034.
- Cleanup T035-T039 before QA validation.
- QA document and validation tasks T040-T052 last.
