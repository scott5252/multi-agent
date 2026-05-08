# Tasks: Admin UI Transitional React Label Removal

**Input**: Design documents from `specs/059-admin-ui-transitional-react-label-removal/`
**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: Required by FR-006 through FR-010 and SC-001 through SC-005. Add or update tests before each implementation slice where practical.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently.

## Phase 1: Setup

**Purpose**: Establish Spec 059 QA configuration, scanner inventory, and reviewer notes.

- [x] T001 Record the current transitional React label inventory for `src/multi_agent_platform/api/routers/admin_react.py`, `src/multi_agent_platform/api/schemas/admin_react.py`, `src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py`, `src/multi_agent_platform/admin/migration_hardening/react_migration_hardening.py`, `frontend/admin/src/App.tsx`, `frontend/admin/src/routes.tsx`, `frontend/admin/src/components/`, and `frontend/admin/src/test/` in `specs/059-admin-ui-transitional-react-label-removal/quickstart.md`
- [x] T002 [P] Create QA environment file `specs/059-admin-ui-transitional-react-label-removal/.env.qa059` for database `multi_agent_platform_qa059`
- [x] T003 [P] Create PR reviewer notes scaffold `specs/059-admin-ui-transitional-react-label-removal/pr_notes.md`
- [x] T004 [P] Inspect current generated React/admin contracts in `frontend/admin/src/api/generated/reactAdminApi.ts`
- [x] T005 [P] Record README and docs quickstart impact notes in `specs/059-admin-ui-transitional-react-label-removal/pr_notes.md`
- [x] T006 Confirm `.specify/feature.json` points at `specs/059-admin-ui-transitional-react-label-removal` and update `specs/_autopilot/remove-mock-data-roadmap/059-admin-ui-transitional-react-label-removal/status.json` if recovery notes are needed

---

## Phase 2: Foundational

**Purpose**: Shared visible-text scanner, QA seed, verifier, schema, and validation manifest foundations that block all user stories.

- [x] T007 [P] Add transitional label gate schema fields or validation helpers in `src/multi_agent_platform/api/schemas/admin_migration_hardening_react.py`
- [x] T008 [P] Add QA059 seed script `scripts/qa/seed_transitional_labels_qa059.py` for representative platform and tenant route evidence without external provider, Telegram, credential, connector, or outbound calls
- [x] T009 [P] Add QA059 verifier script `scripts/qa/verify_transitional_labels_qa059.py` for route-visible text scanning, screenshot evidence, redaction checks, and artifact report output
- [x] T010 [P] Add test fixtures for transitional label gate expectations in `tests/fixtures/transitional_labels.py`
- [x] T011 Extend visible-text scanner and allowlist helpers in `src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py`
- [x] T012 Wire transitional label gate route response or dashboard evidence in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T013 Update auth protected-surface coverage for any new Spec 059 route in `src/multi_agent_platform/auth/policy.py`
- [x] T014 Refresh generated TypeScript contracts after schema or route changes in `frontend/admin/src/api/generated/reactAdminApi.ts`
- [x] T015 [P] Add contract tests for transitional label gate schema and response invariants in `tests/contract/test_admin_transitional_label_gate_contract.py`
- [x] T016 [P] Add scanner unit tests for blocked user-visible labels and allowed implementation references in `tests/unit/admin/test_transitional_label_scanner.py`
- [x] T017 [P] Add schema tests for safe text and summary validation in `tests/unit/api/test_admin_migration_hardening_react_schema.py`

**Checkpoint**: Scanner policy, schema contracts, QA seed, and verifier foundations are ready.

---

## Phase 3: User Story 1 - Admin UI Uses Product Terminology (Priority: P1)

**Goal**: The production admin shell and representative domain pages no longer show implementation-era React labels to users.

**Independent Test**: Run backend route tests and frontend shell/component tests, then open `/admin/app` and representative pages to verify visible text uses Admin/domain terminology.

### Tests for User Story 1

- [x] T018 [P] [US1] Add backend route tests for admin shell, navigation, breadcrumbs, document title, and command/search labels in `tests/integration/test_admin_react_routes.py`
- [x] T019 [P] [US1] Add frontend shell and routing tests for product-facing Admin labels in `frontend/admin/src/App.test.tsx` and `frontend/admin/src/bootstrapContract.test.ts`
- [x] T020 [P] [US1] Add representative domain component copy tests in `frontend/admin/src/components/migrationHardening/MigrationHardeningPage.test.tsx`
- [x] T021 [P] [US1] Add visible-text scanner regression tests for production route responses in `tests/unit/admin/test_transitional_label_scanner.py`

### Implementation for User Story 1

- [x] T022 [US1] Update backend shell metadata, breadcrumbs, navigation labels, and command/search destinations in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T023 [US1] Update shared React shell titles, document title handling, route labels, and navigation copy in `frontend/admin/src/App.tsx`, `frontend/admin/src/routes.tsx`, and `frontend/admin/src/components/StatePanel.tsx`
- [x] T024 [US1] Update representative domain page headings, summaries, empty states, and error states in `frontend/admin/src/components/migrationHardening/MigrationHardeningPage.tsx`, `frontend/admin/src/components/skills/SkillLifecyclePage.tsx`, `frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx`, `frontend/admin/src/components/workbench/WorkbenchPage.tsx`, `frontend/admin/src/components/usage/UsagePage.tsx`, and `frontend/admin/src/components/channelTelegramBriefing/ChannelTelegramBriefingPage.tsx`
- [x] T025 [US1] Update frontend test data labels in `frontend/admin/src/test/shellTestData.ts`, `frontend/admin/src/test/migrationHardeningTestData.ts`, `frontend/admin/src/test/skillLifecycleTestData.ts`, `frontend/admin/src/test/governanceTestData.ts`, `frontend/admin/src/test/workflowBuilderTestData.ts`, `frontend/admin/src/test/testBenchTestData.ts`, and `frontend/admin/src/test/usageTestData.ts`
- [x] T026 [US1] Remove the remaining Spec 059 bootstrap QA marker or reclassify it as non-user-visible implementation evidence in `src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py`
- [x] T027 [US1] Run generated type refresh if backend route or schema contracts changed in `frontend/admin/src/api/generated/reactAdminApi.ts`

**Checkpoint**: User Story 1 works independently for product-facing admin terminology.

---

## Phase 4: User Story 2 - Technical Context Remains Bounded (Priority: P2)

**Goal**: Developer-only implementation context remains understandable and explicitly allowlisted while ordinary product surfaces avoid transitional labels.

**Independent Test**: Run docs, scanner, and migration evidence tests to prove allowed implementation references have rationale and user-facing docs/screenshots use Admin terminology.

### Tests for User Story 2

- [x] T028 [P] [US2] Add backend tests for migration evidence allowed implementation references in `tests/integration/api/test_admin_react_migration_inventory_routes.py`
- [x] T029 [P] [US2] Add frontend migration evidence tests for allowed implementation context in `frontend/admin/src/components/migrationHardening/LiveDataInventoryPanel.test.tsx`
- [x] T030 [P] [US2] Add docs regression coverage for QA059 terminology policy in `tests/docs/test_admin_ui_transitional_label_docs.py`
- [x] T031 [P] [US2] Add scanner tests for generated/internal/historical references in `tests/unit/admin/test_transitional_label_scanner.py`

### Implementation for User Story 2

- [x] T032 [US2] Add explicit implementation-reference allowlist and rationale data in `src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py`
- [x] T033 [US2] Update migration evidence and live-data inventory copy so platform reviewers see technical context without product-label leakage in `src/multi_agent_platform/admin/migration_hardening/react_migration_hardening.py`
- [x] T034 [US2] Update migration evidence UI rendering in `frontend/admin/src/components/migrationHardening/LiveDataInventoryPanel.tsx`
- [x] T035 [US2] Update QA059 PR notes with allowed implementation references, owner, rationale, and rollback guidance in `specs/059-admin-ui-transitional-react-label-removal/pr_notes.md`
- [x] T036 [US2] Review `README.md` and `docs/quickstart.md` for terminology impact, then update them if shared guidance changed or record the no-update rationale in `specs/059-admin-ui-transitional-react-label-removal/pr_notes.md`

**Checkpoint**: User Story 2 works independently for bounded technical context.

---

## Phase 5: User Story 3 - Transitional Label Regressions Are Prevented (Priority: P3)

**Goal**: Automated evidence blocks future production-visible transitional labels and proves screenshots use product terminology.

**Independent Test**: Run QA059 verifier, visible-text scanner tests, route tests, and Playwright screenshots; fail if banned user-visible labels appear.

### Tests for User Story 3

- [x] T037 [P] [US3] Add verifier output tests for blocked count, allowed references, and redaction safety in `tests/unit/admin/test_transitional_label_scanner.py`
- [x] T038 [P] [US3] Add integration tests for QA059 scanner route under platform, tenant, Auth0-shaped, and cross-tenant denied principals in `tests/integration/api/test_admin_transitional_label_routes.py`
- [x] T039 [P] [US3] Add frontend gate panel tests in `frontend/admin/src/components/migrationHardening/TransitionalLabelGatePanel.test.tsx`

### Implementation for User Story 3

- [x] T040 [US3] Implement QA059 scanner summary, findings, evidence, and report writer in `scripts/qa/verify_transitional_labels_qa059.py`
- [x] T041 [US3] Implement QA059 seed setup for representative domain pages and empty/seeded route states in `scripts/qa/seed_transitional_labels_qa059.py`
- [x] T042 [US3] Add transitional label gate panel or integrate the gate summary into migration hardening UI in `frontend/admin/src/components/migrationHardening/TransitionalLabelGatePanel.tsx` and `frontend/admin/src/components/migrationHardening/MigrationHardeningPage.tsx`
- [x] T043 [US3] Update validation manifest with QA059 seed, visible-text route scans, Playwright screenshot assertions, and post-UI verifier command in `specs/_autopilot/remove-mock-data-roadmap/059-admin-ui-transitional-react-label-removal/validation.yml`
- [x] T044 [US3] Update Playwright flow to open `/admin/app`, representative domain pages, and migration evidence, then capture `qa059-admin-entry.png` and `qa059-domain-pages.png` in `specs/_autopilot/remove-mock-data-roadmap/059-admin-ui-transitional-react-label-removal/validation.yml`

**Checkpoint**: User Story 3 works independently for regression prevention and screenshot evidence.

---

## Phase 6: Polish And Validation

**Purpose**: Documentation, generated contracts/assets, validation manifest, and required post-spec validation.

- [x] T045 [P] Generate QA guide `specs/059-admin-ui-transitional-react-label-removal/qa059.md`
- [x] T046 [P] Generate UI QA guide `specs/059-admin-ui-transitional-react-label-removal/qa059_ui.md`
- [x] T047 [P] Generate user guide `specs/059-admin-ui-transitional-react-label-removal/qa059_user_guide.md`
- [x] T048 Update validation manifest `specs/_autopilot/remove-mock-data-roadmap/059-admin-ui-transitional-react-label-removal/validation.yml` for qa059 docs, seed, route scans, Playwright, post-UI verifier, and quality gates
- [x] T049 Run `uv run ruff check src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py src/multi_agent_platform/admin/migration_hardening/react_migration_hardening.py src/multi_agent_platform/api/routers/admin_react.py src/multi_agent_platform/auth/policy.py tests/unit/admin/test_transitional_label_scanner.py tests/integration/api/test_admin_transitional_label_routes.py tests/contract/test_admin_transitional_label_gate_contract.py scripts/qa/seed_transitional_labels_qa059.py scripts/qa/verify_transitional_labels_qa059.py`
- [x] T050 Run `uv run mypy src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py src/multi_agent_platform/admin/migration_hardening/react_migration_hardening.py src/multi_agent_platform/api/routers/admin_react.py scripts/qa/verify_transitional_labels_qa059.py`
- [x] T051 Run focused pytest coverage for transitional label scanner, schema, contract, route, docs, and migration dashboard tests
- [x] T052 Run `npm run --prefix frontend/admin test -- --run migrationHardening` and shell/domain frontend tests touched by Spec 059
- [x] T053 Run `npm run --prefix frontend/admin typecheck`
- [x] T054 Run `npm run --prefix frontend/admin build` and `uv run python scripts/frontend/generate_admin_react_types.py --check`
- [x] T055 Run `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/059-admin-ui-transitional-react-label-removal`
- [x] T056 Run `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/059-admin-ui-transitional-react-label-removal/validation.yml`
- [x] T057 Run `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/059-admin-ui-transitional-react-label-removal/validation.yml --start-processes`
- [x] T058 Run `uv run python scripts/qa/verify_transitional_labels_qa059.py` and record scanner, route response, screenshot, and redaction evidence in `specs/_autopilot/remove-mock-data-roadmap/059-admin-ui-transitional-react-label-removal/status.json`
- [x] T059 Run `uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa059-after-spec`
- [x] T060 Update `specs/_autopilot/remove-mock-data-roadmap/059-admin-ui-transitional-react-label-removal/status.json` and `specs/_autopilot/remove-mock-data-roadmap/queue.json` with completed implement, validation, and spec completion history before ending the roadmap

---

## Dependencies And Execution Order

### Phase Dependencies

- Phase 1 has no dependencies.
- Phase 2 depends on Phase 1 and blocks all user stories.
- User Story 1 depends on Phase 2 and is the MVP.
- User Story 2 depends on User Story 1 terminology boundaries.
- User Story 3 depends on User Stories 1 and 2 for final blocked/allowed policy.
- Phase 6 depends on all implemented user stories.

### Parallel Opportunities

- T002, T003, T004, T005, and T006 can run in parallel.
- T007, T008, T009, T010, T015, T016, and T017 can run in parallel after setup.
- Test tasks inside each user story can run in parallel because they target distinct files.
- QA docs can be drafted in parallel after validation manifest and verifier output stabilize.

## Implementation Strategy

1. Complete setup and foundational scanner/schema/QA helper work.
2. Deliver User Story 1 as the MVP and prove product-facing Admin terminology.
3. Add User Story 2 allowlist decisions for bounded implementation context.
4. Add User Story 3 regression prevention with scanner and Playwright evidence.
5. Run focused tests, full Spec QA, Playwright, post-UI verifier, and curl regression before final queue completion.
