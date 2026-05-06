# Tasks: Jinja Surface Inventory And Deletion Plan

**Input**: Design documents from `specs/038-jinja-surface-inventory-and-deletion-plan/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

## Phase 1: Setup

- [X] T001 Verify active feature pointer and branch in `.specify/feature.json` and `specs/_autopilot/react-ui2-roadmap/038-jinja-surface-inventory-and-deletion-plan/status.json`
- [X] T002 [P] Add Spec 038 reviewer notes skeleton in `specs/038-jinja-surface-inventory-and-deletion-plan/pr_notes.md`
- [X] T003 [P] Add generated inventory evidence placeholder in `specs/038-jinja-surface-inventory-and-deletion-plan/jinja_inventory.json`

## Phase 2: Foundational Contract And Scanner Tests

- [X] T004 [P] Add schema tests for Jinja inventory redaction, safe-to-delete validation, and repo-relative evidence in `tests/unit/api/test_admin_migration_hardening_react_schema.py`
- [X] T005 [P] Add scanner unit tests for template, static asset, TemplateResponse, Jinja2Templates, route, and docs-link discovery in `tests/unit/admin/test_jinja_inventory_scanner.py`
- [X] T006 [P] Add backend contract tests for `/admin/app/migration/jinja-inventory.json` shape and generated TypeScript inclusion in `tests/contract/test_admin_migration_jinja_inventory_contract.py`
- [X] T007 [P] Add integration tests for Auth0-shaped/local-principal allowed, denied, and tenant-scoped inventory routes in `tests/integration/api/test_admin_react_migration_inventory_routes.py`
- [X] T008 [P] Add React component tests for inventory summary, grouped rows, blocked state, and redaction-safe rendering in `frontend/admin/src/components/migrationHardening/JinjaInventoryPanel.test.tsx`

## Phase 3: User Story 1 - Review Complete Jinja Surface Inventory (Priority: P1)

**Goal**: Generate and display a complete inventory of templates, legacy assets, TemplateResponse usages, Jinja imports, route declarations, helpers, and docs/QA direct links.

**Independent Test**: Run the scanner and verify `/admin/app/migration` shows inventory counts and grouped evidence matching repository surfaces.

- [X] T009 [US1] Add Jinja inventory Pydantic enums and models in `src/multi_agent_platform/api/schemas/admin_migration_hardening_react.py`
- [X] T010 [US1] Implement deterministic scanner data structures and safe path helpers in `src/multi_agent_platform/admin/migration_hardening/jinja_inventory.py`
- [X] T011 [US1] Implement template and include discovery in `src/multi_agent_platform/admin/migration_hardening/jinja_inventory.py`
- [X] T012 [US1] Implement legacy static JavaScript/CSS asset discovery in `src/multi_agent_platform/admin/migration_hardening/jinja_inventory.py`
- [X] T013 [US1] Implement TemplateResponse, Jinja2Templates, template provider, route, and helper discovery in `src/multi_agent_platform/admin/migration_hardening/jinja_inventory.py`
- [X] T014 [US1] Implement docs/QA direct-link discovery in `src/multi_agent_platform/admin/migration_hardening/jinja_inventory.py`
- [X] T015 [US1] Export scanner builders from `src/multi_agent_platform/admin/migration_hardening/__init__.py`
- [X] T016 [US1] Write deterministic inventory evidence to `specs/038-jinja-surface-inventory-and-deletion-plan/jinja_inventory.json`

## Phase 4: User Story 2 - Classify Deletion Readiness And Replacement Path (Priority: P2)

**Goal**: Classify every inventory item with replacement path, owner category, planned removal spec, evidence references, blocker references, and reviewer signoff state.

**Independent Test**: Inspect `jinja_inventory.json` and migration dashboard rows for each classification category and planned removal spec.

- [X] T017 [US2] Add owner-category, planned-removal-spec, replacement-path, behavior, blocker, and classification mapping logic in `src/multi_agent_platform/admin/migration_hardening/jinja_inventory.py`
- [X] T018 [US2] Extend migration hardening dashboard projection with Jinja inventory summary/groups/evidence in `src/multi_agent_platform/admin/migration_hardening/react_migration_hardening.py`
- [X] T019 [US2] Add `/admin/app/migration/jinja-inventory.json` route in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T020 [US2] Add Jinja inventory models to generated React contracts in `scripts/frontend/generate_admin_react_types.py`
- [X] T021 [US2] Regenerate TypeScript contracts in `frontend/admin/src/api/generated/reactAdminApi.ts`
- [X] T022 [US2] Add client fetch helper for Jinja inventory in `frontend/admin/src/api/client.ts`

## Phase 5: User Story 3 - Prove Safe Direct-Link, Denied-State, And Redaction Coverage (Priority: P3)

**Goal**: Render the inventory in React and prove safe handling for direct links, denied states, tenant scope, redaction, and reviewer handoff.

**Independent Test**: Open `/admin/app/migration`, inspect the inventory section as platform admin and tenant admin, and confirm redaction-safe rows and blocked items.

- [X] T023 [US3] Add `JinjaInventoryPanel` React component in `frontend/admin/src/components/migrationHardening/JinjaInventoryPanel.tsx`
- [X] T024 [US3] Integrate Jinja inventory loading and panel rendering in `frontend/admin/src/components/migrationHardening/MigrationHardeningPage.tsx`
- [X] T025 [US3] Update migration hardening test data with inventory examples in `frontend/admin/src/test/migrationHardeningTestData.ts`
- [X] T026 [US3] Add inventory styling with stable table/card dimensions in `frontend/admin/src/styles/admin.css`
- [X] T027 [US3] Update migration dashboard copy to mention deletion-grade inventory in `frontend/admin/src/components/migrationHardening/MigrationSummaryHeader.tsx`

## Phase 6: Polish, QA Docs, And Validation

- [X] T028 [P] Update Spec 038 QA guide in `specs/038-jinja-surface-inventory-and-deletion-plan/qa038.md`
- [X] T029 [P] Update Spec 038 browser walkthrough in `specs/038-jinja-surface-inventory-and-deletion-plan/qa038_ui.md`
- [X] T030 [P] Add Spec 038 QA environment in `specs/038-jinja-surface-inventory-and-deletion-plan/.env.qa038`
- [X] T031 [P] Add Spec 038 user guide in `specs/038-jinja-surface-inventory-and-deletion-plan/qa038_user_guide.md`
- [X] T032 Update PR/reviewer notes in `specs/038-jinja-surface-inventory-and-deletion-plan/pr_notes.md`
- [X] T033 Run backend quality gates from `specs/_autopilot/react-ui2-roadmap/038-jinja-surface-inventory-and-deletion-plan/validation.yml`
- [X] T034 Run Playwright validation from `specs/_autopilot/react-ui2-roadmap/038-jinja-surface-inventory-and-deletion-plan/validation.yml`
- [X] T035 Update completed phase and validation evidence in `specs/_autopilot/react-ui2-roadmap/038-jinja-surface-inventory-and-deletion-plan/status.json`

## Dependencies

- Phase 1 before all implementation tasks.
- Phase 2 tests before scanner, schema, route, and React implementation.
- US1 before US2 because classification depends on scanner output.
- US2 before US3 because React consumes backend-owned contracts.
- QA docs and validation after all stories.

## Parallel Execution Examples

- T004, T005, T006, T007, and T008 touch separate test files and can be prepared independently.
- T028, T029, T030, and T031 can be drafted together after implemented behavior is known.

## Implementation Strategy

1. Build the scanner and schema first until the generated JSON proves full surface discovery.
2. Wire the protected API and generated TypeScript contracts.
3. Render the React dashboard section with safe grouped inventory.
4. Complete QA docs, run validation, and leave all Jinja files intact.
