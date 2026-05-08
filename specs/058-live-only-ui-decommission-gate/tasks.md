# Tasks: Live-Only UI Decommission Gate

**Input**: Design documents from `specs/058-live-only-ui-decommission-gate/`
**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: Required by FR-005, FR-006, FR-007, FR-008, FR-010, FR-012, FR-014, and SC-001 through SC-005. Write or update tests before each implementation slice where practical.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently.

## Phase 1: Setup

**Purpose**: Establish Spec 058 artifacts, QA configuration, and the final live-only gate worklist.

- [X] T001 Record the current Spec 058 live-only gate inventory for `src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py`, `src/multi_agent_platform/admin/migration_hardening/react_migration_hardening.py`, `src/multi_agent_platform/api/routers/admin_react.py`, `frontend/admin/src/components/migrationHardening/LiveDataInventoryPanel.tsx`, `tests/unit/admin/test_live_data_inventory_scanner.py`, and `tests/integration/api/test_admin_live_data_inventory_routes.py` in `specs/058-live-only-ui-decommission-gate/quickstart.md`
- [X] T002 [P] Create QA environment file `specs/058-live-only-ui-decommission-gate/.env.qa058` for database `multi_agent_platform_qa058`
- [X] T003 [P] Create PR reviewer notes scaffold `specs/058-live-only-ui-decommission-gate/pr_notes.md`
- [X] T004 [P] Inspect generated React migration hardening contract coverage in `frontend/admin/src/api/generated/reactAdminApi.ts`
- [X] T005 [P] Record README and quickstart documentation impact notes in `specs/058-live-only-ui-decommission-gate/pr_notes.md`
- [X] T006 [P] Confirm `.specify/feature.json` points at `specs/058-live-only-ui-decommission-gate` and update `specs/_autopilot/remove-mock-data-roadmap/058-live-only-ui-decommission-gate/status.json` if recovery notes are needed

---

## Phase 2: Foundational

**Purpose**: Shared schema, scanner policy, QA seed, and verification foundations that block all user stories.

- [X] T007 [P] Add final live-only gate schema fields or validation helpers in `src/multi_agent_platform/api/schemas/admin_migration_hardening_react.py`
- [X] T008 [P] Add QA058 seed script `scripts/qa/seed_live_only_gate_qa058.py` for representative persisted route evidence without external provider, Telegram, credential, connector, or outbound calls
- [X] T009 [P] Add QA058 verifier script `scripts/qa/verify_live_only_gate_qa058.py` for scanner, route response, built asset, redaction, and artifact evidence
- [X] T010 [P] Add or update test fixtures for migration hardening gate expectations in `tests/fixtures/live_only_gate.py`
- [X] T011 Harden production scan roots, test-only prefixes, built-asset handling, and final allowlist policy in `src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py`
- [X] T012 Update live-data inventory route target discovery and missed-route assertions in `src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py`
- [X] T013 Wire `ci_mode` and `source_scan` query options for `/admin/app/migration/live-data-inventory.json` in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T014 Refresh generated TypeScript contracts after backend schema/route changes in `frontend/admin/src/api/generated/reactAdminApi.ts`
- [X] T015 [P] Update contract tests for final live-only gate schema and response invariants in `tests/contract/test_admin_live_data_inventory_contract.py`
- [X] T016 [P] Update scanner unit tests for final policy, built assets, generated contracts, and test-only boundaries in `tests/unit/admin/test_live_data_inventory_scanner.py`
- [X] T017 [P] Update schema tests for live-only gate safe text and summary validation in `tests/unit/api/test_admin_migration_hardening_react_schema.py`

**Checkpoint**: Final scanner policy, route target inventory, schema contracts, QA seed, and verifier foundations are ready.

---

## Phase 3: User Story 1 - Enforce Live-Only Route Contracts (Priority: P1)

**Goal**: Every production admin UI route is classified and production-reachable deterministic fixture/demo data is blocking.

**Independent Test**: Run the source/built-asset scanner and route inventory tests, then verify every production admin UI route has an allowed classification and no blocking production finding.

### Tests for User Story 1

- [X] T018 [P] [US1] Add scanner coverage for production route classifications, obsolete surface mappings, and blocking fixture markers in `tests/unit/admin/test_live_data_inventory_scanner.py`
- [X] T019 [P] [US1] Add route inventory coverage for missed production admin JSON routes in `tests/integration/api/test_admin_live_data_inventory_routes.py`
- [X] T020 [P] [US1] Add generated contract and built-asset marker coverage in `tests/contract/test_admin_live_data_inventory_contract.py`
- [X] T021 [P] [US1] Add frontend live-data inventory panel tests for final pass/warning/fail summaries in `frontend/admin/src/components/migrationHardening/LiveDataInventoryPanel.test.tsx`

### Implementation for User Story 1

- [X] T022 [US1] Update final route classification data in `src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py`
- [X] T023 [US1] Remove or expire obsolete mapped legacy surface entries for completed Specs 050 through 057 in `src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py`
- [X] T024 [US1] Add built production asset scanning and safe false-positive handling in `src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py`
- [X] T025 [US1] Add production test-fixture import detection and source-path policy checks in `src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py`
- [X] T026 [US1] Update migration hardening dashboard live-data summary copy and evidence status in `src/multi_agent_platform/admin/migration_hardening/react_migration_hardening.py`
- [X] T027 [US1] Update `frontend/admin/src/components/migrationHardening/LiveDataInventoryPanel.tsx` to render final gate classifications, route counts, and blocked/warning/pass states without implying demo data
- [X] T028 [US1] Update `frontend/admin/src/test/migrationHardeningTestData.ts` with final live-only gate fixture data that remains test-only

**Checkpoint**: User Story 1 works independently for route classification and production scanner enforcement.

---

## Phase 4: User Story 2 - Prove Empty And Seeded Live Behavior (Priority: P2)

**Goal**: Route probes prove empty-state truthfulness and seeded persisted evidence for production admin UI routes using platform and tenant-shaped principals.

**Independent Test**: Run QA058 seed/verifier and route response integration tests for empty and seeded states; verify no route invents rows or leaks unauthorized tenant details.

### Tests for User Story 2

- [X] T029 [P] [US2] Add empty-database route response scan tests in `tests/integration/api/test_admin_live_data_inventory_routes.py`
- [X] T030 [P] [US2] Add seeded-database route response scan tests using QA058 fixture setup in `tests/integration/api/test_admin_live_data_inventory_routes.py`
- [X] T031 [P] [US2] Add Auth0-shaped platform and tenant route tests for live-data inventory probes in `tests/integration/test_admin_react_routes.py`
- [X] T032 [P] [US2] Add redaction and tenant isolation assertions for QA058 verifier output in `tests/unit/admin/test_live_data_inventory_scanner.py`

### Implementation for User Story 2

- [X] T033 [US2] Implement empty and seeded route probe helpers in `src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py`
- [X] T034 [US2] Implement deterministic QA058 seed setup for representative workflow, governance, skill, test bench, membership, channel, usage, and operations surfaces in `scripts/qa/seed_live_only_gate_qa058.py`
- [X] T035 [US2] Implement QA058 verifier API/database checks and safe artifact report output in `scripts/qa/verify_live_only_gate_qa058.py`
- [X] T036 [US2] Update `/admin/app/migration/live-data-inventory.json` response evidence for route response scans in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T037 [US2] Update Spec 058 validation manifest with QA058 seed, empty/seeded route checks, Playwright route classification assertions, and post-UI verifier command in `specs/_autopilot/remove-mock-data-roadmap/058-live-only-ui-decommission-gate/validation.yml`
- [X] T038 [US2] Update Playwright flow in `specs/_autopilot/remove-mock-data-roadmap/058-live-only-ui-decommission-gate/validation.yml` to open the live-data inventory UI and capture `qa058-live-data-ui-api-smoke.png`

**Checkpoint**: User Story 2 works independently for empty and seeded route-response proof.

---

## Phase 5: User Story 3 - Retire Obsolete Demo Surfaces Safely (Priority: P3)

**Goal**: Obsolete deterministic production modules are deleted, disconnected, or retained only under explicit test/QA/docs policy with rollback guidance.

**Independent Test**: Run import cleanup checks, scanner tests, docs review, and live-data inventory UI validation; verify no production route depends on obsolete deterministic builders or test fixtures.

### Tests for User Story 3

- [X] T039 [P] [US3] Add import cleanup regression coverage for obsolete deterministic builders in `tests/unit/admin/test_live_data_inventory_scanner.py`
- [X] T040 [P] [US3] Add migration dashboard route tests for deleted/disconnected surface evidence in `tests/integration/api/test_admin_react_migration_inventory_routes.py`
- [X] T041 [P] [US3] Add frontend migration hardening tests for rollback/decommission evidence in `frontend/admin/src/components/migrationHardening/RollbackAndRouteDecisionPanel.test.tsx`
- [X] T042 [P] [US3] Add docs regression coverage for QA058 guides in `tests/docs/test_live_only_ui_decommission_gate_docs.py`

### Implementation for User Story 3

- [X] T043 [US3] Delete, disconnect, or document obsolete deterministic production imports discovered by the gate in `src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py`
- [X] T044 [US3] Update migration rollback and decommission evidence in `src/multi_agent_platform/admin/migration_hardening/react_migration_hardening.py`
- [X] T045 [US3] Update migration UI rollback and route decision rendering in `frontend/admin/src/components/migrationHardening/RollbackPlanPanel.tsx` and `frontend/admin/src/components/migrationHardening/MigrationParityMatrix.tsx`
- [X] T046 [US3] Update reviewer notes with delete/retain/allowlist decisions and rollback guidance in `specs/058-live-only-ui-decommission-gate/pr_notes.md`
- [X] T047 [US3] Review `README.md` and `docs/quickstart.md` for live-only gate command impact, then update them if shared guidance changed or record the no-update rationale in `specs/058-live-only-ui-decommission-gate/pr_notes.md`

**Checkpoint**: User Story 3 works independently for safe decommission and rollback review.

---

## Phase 6: Polish And Validation

**Purpose**: Documentation, generated contracts/assets, validation manifest, and required post-spec validation.

- [X] T048 [P] Generate QA guide `specs/058-live-only-ui-decommission-gate/qa058.md`
- [X] T049 [P] Generate UI QA guide `specs/058-live-only-ui-decommission-gate/qa058_ui.md`
- [X] T050 [P] Generate user guide `specs/058-live-only-ui-decommission-gate/qa058_user_guide.md`
- [X] T051 Update validation manifest `specs/_autopilot/remove-mock-data-roadmap/058-live-only-ui-decommission-gate/validation.yml` for qa058 docs, seed, route probes, Playwright, post-UI verifier, and quality gates
- [X] T052 Run `uv run ruff check src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py src/multi_agent_platform/admin/migration_hardening/react_migration_hardening.py src/multi_agent_platform/api/routers/admin_react.py src/multi_agent_platform/api/schemas/admin_migration_hardening_react.py tests/unit/admin/test_live_data_inventory_scanner.py tests/integration/api/test_admin_live_data_inventory_routes.py tests/contract/test_admin_live_data_inventory_contract.py scripts/qa/seed_live_only_gate_qa058.py scripts/qa/verify_live_only_gate_qa058.py`
- [X] T053 Run `uv run mypy src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py src/multi_agent_platform/admin/migration_hardening/react_migration_hardening.py src/multi_agent_platform/api/routers/admin_react.py`
- [X] T054 Run focused pytest coverage for live-only gate scanner, schema, contract, route, docs, and migration dashboard tests
- [X] T055 Run `npm run --prefix frontend/admin test -- --run migrationHardening` and `npm run --prefix frontend/admin typecheck`
- [X] T056 Run `npm run --prefix frontend/admin build` and `uv run python scripts/frontend/generate_admin_react_types.py --check`
- [X] T057 Run `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/058-live-only-ui-decommission-gate`
- [X] T058 Run `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/058-live-only-ui-decommission-gate/validation.yml`
- [X] T059 Run `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/058-live-only-ui-decommission-gate/validation.yml --start-processes`
- [X] T060 Run `uv run python scripts/qa/verify_live_only_gate_qa058.py` and record scanner, route response, asset, and redaction evidence in `specs/_autopilot/remove-mock-data-roadmap/058-live-only-ui-decommission-gate/status.json`
- [X] T061 Run `uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa058-after-spec`
- [X] T062 Update `specs/_autopilot/remove-mock-data-roadmap/058-live-only-ui-decommission-gate/status.json` and `specs/_autopilot/remove-mock-data-roadmap/queue.json` with completed implement, validation, and spec completion history before moving to Spec 059

---

## Dependencies And Execution Order

### Phase Dependencies

- Phase 1 has no dependencies.
- Phase 2 depends on Phase 1 and blocks all user stories.
- User Story 1 depends on Phase 2 and is the MVP.
- User Story 2 depends on User Story 1 scanner/route target classifications.
- User Story 3 depends on User Story 1 findings and User Story 2 route evidence.
- Phase 6 depends on all implemented user stories.

### Parallel Opportunities

- T002, T003, T004, T005, and T006 can run in parallel.
- T007, T008, T009, T010, T015, T016, and T017 can run in parallel after setup.
- Test tasks inside each user story can run in parallel because they target distinct files.
- Frontend migration panel tests can run in parallel with backend scanner and route tests after contract changes are known.
- QA docs can be drafted in parallel after the validation manifest and verifier command stabilize.

## Implementation Strategy

1. Complete setup and foundational scanner/schema/QA helper work.
2. Deliver User Story 1 as the MVP and prove route classification plus production scanner enforcement.
3. Add User Story 2 route-response proof for fresh and seeded QA states.
4. Add User Story 3 decommission decisions and rollback documentation.
5. Run focused tests, full Spec QA, Playwright, post-UI verifier, and curl regression before queue advancement.
