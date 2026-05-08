# Tasks: Live Data Inventory And Mock Guardrails

**Input**: Design documents from `/specs/048-live-data-inventory-and-mock-guardrails/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required by the spec. Write or update tests before implementation where practical.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm generated design artifacts and validation targets are present before implementation.

- [X] T001 Verify Spec 048 design artifacts in specs/048-live-data-inventory-and-mock-guardrails/plan.md, specs/048-live-data-inventory-and-mock-guardrails/research.md, specs/048-live-data-inventory-and-mock-guardrails/data-model.md, specs/048-live-data-inventory-and-mock-guardrails/quickstart.md, and specs/048-live-data-inventory-and-mock-guardrails/contracts/live-data-inventory-contract.md
- [X] T002 Verify active feature context in .specify/feature.json and queue status in specs/_autopilot/remove-mock-data-roadmap/queue.json

---

## Phase 2: Foundational Tests (Blocking Prerequisites)

**Purpose**: Add executable expectations for scanner taxonomy, route access, contracts, and UI evidence before implementation.

- [X] T003 [P] Create scanner unit tests for marker taxonomy, allowlists, production path exclusions, current roadmap findings, and CI mode in tests/unit/admin/test_live_data_inventory_scanner.py
- [X] T004 [P] Create integration route tests for local-principal, Auth0-shaped principal, cross-tenant denial, route-registry coverage against admin_react.py JSON routes, empty-state scans, seeded-state scans, and redaction safety in tests/integration/api/test_admin_live_data_inventory_routes.py
- [X] T005 [P] Create contract tests for live-data inventory schema and OpenAPI contract alignment in tests/contract/test_admin_live_data_inventory_contract.py
- [X] T006 [P] Add frontend migration evidence tests for live-data inventory rendering in frontend/admin/src/components/migrationHardening/LiveDataInventoryPanel.test.tsx

**Checkpoint**: Tests define the expected guardrail behavior and fail until implementation is complete.

---

## Phase 3: User Story 1 - Inventory Production Mock Surfaces (Priority: P1) MVP

**Goal**: Produce deletion-grade scanner output for current production mock/demo surfaces and classify each finding.

**Independent Test**: `uv run pytest --no-cov tests/unit/admin/test_live_data_inventory_scanner.py -q`

- [X] T007 [US1] Add live-data inventory enums and Pydantic response models in src/multi_agent_platform/api/schemas/admin_migration_hardening_react.py
- [X] T008 [US1] Implement marker taxonomy, source path classification, redaction-safe excerpts, and allowlist matching in src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py
- [X] T009 [US1] Implement the current roadmap finding catalog with owner spec, replacement spec, route owner, durable data source, and reachability metadata in src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py
- [X] T010 [US1] Implement production backend, frontend source, generated contract, and built asset scan helpers in src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py
- [X] T011 [US1] Implement CI mode summary logic that blocks new unallowlisted production findings while permitting mapped legacy findings in src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py
- [X] T012 [US1] Export the live-data scanner API from src/multi_agent_platform/admin/migration_hardening/__init__.py
- [X] T013 [US1] Update tests/unit/admin/test_live_data_inventory_scanner.py to assert the scanner covers all roadmap-listed production surfaces without failing on tests/ or frontend/admin/src/test markers

**Checkpoint**: Scanner inventory is usable without adding routes or UI.

---

## Phase 4: User Story 2 - Define Policy And Metadata Evidence (Priority: P2)

**Goal**: Expose live-only policy, computed metadata allowlist, route targets, and reviewer-safe evidence through backend-owned contracts.

**Independent Test**: `uv run pytest --no-cov tests/contract/test_admin_live_data_inventory_contract.py tests/integration/api/test_admin_live_data_inventory_routes.py -q`

- [X] T014 [US2] Implement live-data route target registry and missed-route coverage helpers for production /admin/app JSON endpoints in src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py
- [X] T015 [US2] Implement computed metadata allowlist entries and route response scan summaries in src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py
- [X] T016 [US2] Add build_live_data_inventory_dashboard service function in src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py
- [X] T017 [US2] Add /admin/app/migration/live-data-inventory.json endpoint with platform, tenant, and Auth0-shaped authorization behavior in src/multi_agent_platform/api/routers/admin_react.py
- [X] T018 [US2] Include live-data inventory summary in build_migration_dashboard output in src/multi_agent_platform/admin/migration_hardening/react_migration_hardening.py
- [X] T019 [US2] Update tests/integration/api/test_admin_live_data_inventory_routes.py for empty database and seeded database scan evidence paths
- [X] T020 [US2] Update tests/contract/test_admin_live_data_inventory_contract.py for schema safety, enum values, and required fields

**Checkpoint**: Backend route and contract evidence are reviewable and redaction-safe.

---

## Phase 5: User Story 3 - Block New Production Mock Regressions (Priority: P3)

**Goal**: Render reviewer evidence in the React UI and wire guardrail checks into normal validation.

**Independent Test**: `cd frontend/admin && npm test -- --run src/components/migrationHardening`

- [X] T021 [US3] Regenerate frontend admin TypeScript contracts in frontend/admin/src/api/generated/reactAdminApi.ts
- [X] T022 [US3] Add fetchLiveDataInventoryDashboard API helper in frontend/admin/src/api/client.ts
- [X] T023 [US3] Add LiveDataInventoryPanel component in frontend/admin/src/components/migrationHardening/LiveDataInventoryPanel.tsx
- [X] T024 [US3] Update MigrationHardeningPage to fetch and render live-data inventory evidence from /admin/app/migration/live-data-inventory.json in frontend/admin/src/components/migrationHardening/MigrationHardeningPage.tsx
- [X] T025 [US3] Update migration hardening test data for live-data inventory in frontend/admin/src/test/migrationHardeningTestData.ts
- [X] T026 [US3] Update frontend migration evidence tests in frontend/admin/src/components/migrationHardening/LiveDataInventoryPanel.test.tsx and frontend/admin/src/components/migrationHardening/MigrationHardeningPage.test.tsx
- [X] T027 [US3] Add reviewer-facing live-data inventory command notes in specs/048-live-data-inventory-and-mock-guardrails/pr_notes.md

**Checkpoint**: Browser reviewers can see live-data guardrail evidence.

---

## Phase 6: QA Docs And Validation

**Purpose**: Produce required QA artifacts and run the validation gates for Spec 048.

- [X] T028 Create QA environment file specs/048-live-data-inventory-and-mock-guardrails/.env.qa048
- [X] T029 Create API and quality guide specs/048-live-data-inventory-and-mock-guardrails/qa048.md
- [X] T030 Create UI walkthrough specs/048-live-data-inventory-and-mock-guardrails/qa048_ui.md
- [X] T031 Create manual QA user guide specs/048-live-data-inventory-and-mock-guardrails/qa048_user_guide.md
- [X] T032 Reconcile Playwright flow and post-UI API/database evidence in specs/_autopilot/remove-mock-data-roadmap/048-live-data-inventory-and-mock-guardrails/validation.yml
- [X] T033 Run focused backend tests for Spec 048 scanner, contract, and integration routes
- [X] T034 Run frontend migration tests, typecheck, and build
- [X] T035 Run generated TypeScript contract check with uv run python scripts/frontend/generate_admin_react_types.py --check
- [X] T036 Run QA document validation for specs/048-live-data-inventory-and-mock-guardrails
- [X] T037 Run uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/048-live-data-inventory-and-mock-guardrails/validation.yml
- [X] T038 Run uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/048-live-data-inventory-and-mock-guardrails/validation.yml --start-processes
- [X] T039 Run post-UI API/database verification for /admin/app/migration/live-data-inventory.json and save evidence in specs/_autopilot/remove-mock-data-roadmap/048-live-data-inventory-and-mock-guardrails/status.json
- [X] T040 Run uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa048-after-spec

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 has no dependencies.
- Phase 2 depends on Phase 1 and defines the failing test surface.
- Phase 3 depends on Phase 2 scanner expectations.
- Phase 4 depends on Phase 3 scanner services and schemas.
- Phase 5 depends on Phase 4 generated contracts and endpoint behavior.
- Phase 6 depends on all implementation phases.

### User Story Dependencies

- **User Story 1 (P1)**: Required MVP and blocks all later stories.
- **User Story 2 (P2)**: Depends on scanner models and service from US1.
- **User Story 3 (P3)**: Depends on backend contract and route from US2.

### Parallel Opportunities

- T003 through T006 can be drafted in parallel because they touch different test files.
- T028 through T031 can be drafted in parallel after implementation details stabilize.
- Frontend tests and focused backend tests can run independently before full QA validation.

## Implementation Strategy

1. Land scanner tests, then implement scanner models and services.
2. Add backend route and contract evidence.
3. Render the live-data inventory evidence in the migration dashboard.
4. Generate QA docs and run focused validation.
5. Run full Spec QA, Playwright, post-UI API/database verification, and curl test before marking queue state completed.
