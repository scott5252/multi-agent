# Tasks: React Contract Provenance And Sample Route Retirement

**Input**: Design documents from `/specs/049-react-contract-provenance-and-sample-route-retirement/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required by the spec. Write or update tests before implementation where practical.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm generated design artifacts and active queue state before implementation.

- [X] T001 Verify Spec 049 design artifacts in specs/049-react-contract-provenance-and-sample-route-retirement/plan.md, specs/049-react-contract-provenance-and-sample-route-retirement/research.md, specs/049-react-contract-provenance-and-sample-route-retirement/data-model.md, specs/049-react-contract-provenance-and-sample-route-retirement/quickstart.md, and specs/049-react-contract-provenance-and-sample-route-retirement/contracts/react-contract-provenance-contract.md
- [X] T002 Verify active feature context in .specify/feature.json and queue status in specs/_autopilot/remove-mock-data-roadmap/queue.json

---

## Phase 2: Foundational Tests (Blocking Prerequisites)

**Purpose**: Add executable expectations for shared metadata, retired sample routes, generated contracts, frontend routing, and scanner guardrails before implementation.

- [X] T003 [P] Add schema tests for ReactAdminPageProvenance, ReactAdminEmptyStateMetadata, ReactAdminActionMetadata, and unsafe text rejection in tests/unit/api/test_admin_react_schema.py
- [X] T004 [P] Update admin React integration tests for production sample route retirement, Auth0-shaped behavior, local-principal behavior, bootstrap/search omission, empty QA database evidence, seeded QA database evidence, and redaction safety in tests/integration/test_admin_react_routes.py
- [X] T005 [P] Update contract tests for generated provenance metadata and retired sample route OpenAPI expectations in tests/contract/test_admin_react_contract.py
- [X] T006 [P] Update frontend App/routing tests so /admin/app/patterns renders a truthful unavailable state or relies on backend denial rather than PatternsPage in frontend/admin/src/App.test.tsx and frontend/admin/src/routes.tsx
- [X] T007 [P] Update scanner tests for retired sample route targets, production frontend marker detection, generated contract marker detection, and built asset marker detection in tests/unit/admin/test_live_data_inventory_scanner.py
- [X] T008 [P] Add frontend helper tests for generated idempotency/request metadata in frontend/admin/src/utils/adminActionMetadata.test.ts

**Checkpoint**: Tests define the expected contract, route, frontend, and scanner behavior and fail until implementation is complete.

---

## Phase 3: User Story 1 - Show Backend-Owned Provenance And Empty States (Priority: P1) MVP

**Goal**: Add shared backend-owned metadata to React admin contracts so pages can report live, computed, empty, denied, and unavailable states truthfully.

**Independent Test**: `uv run pytest --no-cov tests/unit/api/test_admin_react_schema.py tests/contract/test_admin_react_contract.py -q`

- [X] T009 [US1] Add ReactAdminSourceKind, ReactAdminPageProvenance, ReactAdminEmptyStateReason, ReactAdminEmptyStateMetadata, ReactAdminActionMetadata, and safe validators in src/multi_agent_platform/api/schemas/admin_react.py
- [X] T010 [US1] Add provenance and empty_state fields to ReactAdminShellState and action_metadata fields to ReactAdminPageAction or AdminAction as appropriate in src/multi_agent_platform/api/schemas/admin_react.py and src/multi_agent_platform/api/schemas/admin_patterns.py
- [X] T011 [US1] Add backend helper constructors for computed metadata, empty live state, denied state, and dependency unavailable provenance in src/multi_agent_platform/api/routers/admin_react.py
- [X] T012 [US1] Apply provenance and empty-state metadata to common React shell states and migration live-data inventory shell/bootstrap evidence in src/multi_agent_platform/api/routers/admin_react.py and src/multi_agent_platform/admin/migration_hardening/react_migration_hardening.py
- [X] T013 [US1] Update generated TypeScript contract generator to include the new provenance, empty-state, and action metadata schema payloads in scripts/frontend/generate_admin_react_types.py
- [X] T014 [US1] Regenerate frontend admin TypeScript contracts in frontend/admin/src/api/generated/reactAdminApi.ts
- [X] T015 [US1] Update CommonState, StatePanel, and any migration state panels to render provenance/empty-state metadata when provided without adding instructional filler in frontend/admin/src/components/states/CommonState.tsx, frontend/admin/src/components/StatePanel.tsx, and frontend/admin/src/components/migrationHardening/MigrationHardeningPage.tsx

**Checkpoint**: Shared metadata is contract-backed and visible on representative empty/unavailable states.

---

## Phase 4: User Story 2 - Retire Production Sample Patterns Route (Priority: P2)

**Goal**: Ensure production cannot navigate to or fetch sample patterns data while preserving test-only fixtures.

**Independent Test**: `uv run pytest --no-cov tests/integration/test_admin_react_routes.py tests/contract/test_admin_react_contract.py -q`

- [X] T016 [US2] Remove or explicitly deny /admin/app/patterns, /admin/app/patterns.json, /admin/app/patterns/actions/sample, and /admin/app/patterns/export production handlers in src/multi_agent_platform/api/routers/admin_react.py
- [X] T017 [US2] Remove retired sample route protected-surface entries or mark them unavailable in src/multi_agent_platform/auth/policy.py
- [X] T018 [US2] Remove PatternsSampleData, SampleRecord, SampleFormDescriptor, SampleActionRequest, and route-only sample envelope dependencies from production schema generation while preserving reusable admin form/table primitives in src/multi_agent_platform/api/schemas/admin_patterns.py and scripts/frontend/generate_admin_react_types.py
- [X] T019 [US2] Remove fetchPatternsEnvelope and requestSampleExport production client helpers in frontend/admin/src/api/client.ts
- [X] T020 [US2] Remove PatternsPage production routing from frontend/admin/src/App.tsx and remove /admin/app/patterns from frontend/admin/src/routes.tsx
- [X] T021 [US2] Remove or quarantine production PatternsPage component files under frontend/admin/src/components/patterns/ while retaining test-only fixtures under frontend/admin/src/test/
- [X] T022 [US2] Update admin React contract tests and OpenAPI assertions so retired sample routes are absent from production schema paths in tests/contract/test_admin_react_contract.py
- [X] T023 [US2] Update integration tests to assert /admin/app/patterns* no longer returns sample data in production-like configuration and that bootstrap/search omit patterns destinations in tests/integration/test_admin_react_routes.py

**Checkpoint**: Production sample route data is unreachable and test fixtures remain test-only.

---

## Phase 5: User Story 3 - Remove Frontend QA Defaults From Production Actions (Priority: P3)

**Goal**: Replace fixed QA revision/idempotency defaults in production React components with backend metadata or generated client request metadata.

**Independent Test**: `cd frontend/admin && npm test -- --run src/components src/hooks src/App.test.tsx`

- [X] T024 [US3] Add generated request metadata helpers for idempotency keys, request IDs, and safe client-side fallback markers in frontend/admin/src/utils/adminActionMetadata.ts
- [X] T025 [US3] Update workflow builder actions to use backend revisions where present and generated idempotency metadata in frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx
- [X] T026 [US3] Update governance actions to use backend-provided revisions or generated client metadata instead of fixed qa031 defaults in frontend/admin/src/components/governance/GovernancePage.tsx
- [X] T027 [US3] Update skill lifecycle actions to use backend-provided revisions or generated client metadata instead of fixed qa032 defaults in frontend/admin/src/components/skills/SkillLifecyclePage.tsx
- [X] T028 [US3] Update test bench actions and publish-gate refresh actions to use backend-provided revisions, URL metadata, or generated client metadata instead of fixed qa033 defaults in frontend/admin/src/components/testBench/TestBenchPage.tsx and frontend/admin/src/components/testBench/PublishGateEvidencePanel.tsx
- [X] T029 [US3] Update membership and principal actions to use backend-provided revisions or generated client metadata instead of fixed qa034 defaults in frontend/admin/src/components/memberships/MembershipPage.tsx, frontend/admin/src/components/memberships/RoleGrantPanel.tsx, frontend/admin/src/components/memberships/PrincipalLinkPanel.tsx, and frontend/admin/src/components/memberships/InvitationPanel.tsx
- [X] T030 [US3] Update usage export and channel/Telegram/briefing actions to use generated client metadata or backend action metadata instead of fixed qa035/qa036 defaults in frontend/admin/src/components/usage/UsagePage.tsx and frontend/admin/src/components/channelTelegramBriefing/ChannelTelegramBriefingPage.tsx
- [X] T031 [US3] Update frontend component tests and test data to assert production helpers are used while deterministic QA fixture values remain only in frontend/admin/src/test/ and *.test.* files
- [X] T032 [US3] Update Spec 048 live-data scanner allowlists and replacement mappings for Spec 049 retired routes and fixed action defaults in src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py

**Checkpoint**: Production React source no longer hardcodes fixed QA action defaults.

---

## Phase 6: QA Docs And Validation

**Purpose**: Produce required QA artifacts and run the validation gates for Spec 049.

- [X] T033 Create QA environment file specs/049-react-contract-provenance-and-sample-route-retirement/.env.qa049
- [X] T034 Create API and quality guide specs/049-react-contract-provenance-and-sample-route-retirement/qa049.md
- [X] T035 Create UI walkthrough specs/049-react-contract-provenance-and-sample-route-retirement/qa049_ui.md
- [X] T036 Create manual QA user guide specs/049-react-contract-provenance-and-sample-route-retirement/qa049_user_guide.md
- [X] T037 Create reviewer notes specs/049-react-contract-provenance-and-sample-route-retirement/pr_notes.md
- [X] T038 Reconcile Playwright flow and post-UI API/database evidence in specs/_autopilot/remove-mock-data-roadmap/049-react-contract-provenance-and-sample-route-retirement/validation.yml
- [X] T039 Run focused backend tests for Spec 049 schemas, contracts, routes, and scanner checks
- [X] T040 Run generated TypeScript contract check with uv run python scripts/frontend/generate_admin_react_types.py --check
- [X] T041 Run frontend tests, typecheck, and build
- [X] T042 Run QA document validation for specs/049-react-contract-provenance-and-sample-route-retirement
- [X] T043 Run uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/049-react-contract-provenance-and-sample-route-retirement/validation.yml
- [X] T044 Run uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/049-react-contract-provenance-and-sample-route-retirement/validation.yml --start-processes
- [X] T045 Run post-UI API/database verification for bootstrap/navigation/provenance and retired sample route behavior and save evidence in specs/_autopilot/remove-mock-data-roadmap/049-react-contract-provenance-and-sample-route-retirement/status.json
- [X] T046 Run uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa049-after-spec

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 has no dependencies.
- Phase 2 depends on Phase 1 and defines the failing test surface.
- Phase 3 depends on Phase 2 schema/contract expectations.
- Phase 4 depends on Phase 3 shared metadata and route test expectations.
- Phase 5 depends on generated contracts and route retirement from Phases 3 and 4.
- Phase 6 depends on all implementation phases.

### User Story Dependencies

- **User Story 1 (P1)**: Required MVP and blocks generated contract/frontend metadata work.
- **User Story 2 (P2)**: Depends on shared metadata but can be validated independently through route tests.
- **User Story 3 (P3)**: Depends on action metadata conventions and generated helper contracts.

### Parallel Opportunities

- T003 through T008 can be drafted in parallel because they touch different test files.
- T024 through T030 touch mostly separate frontend domain components and can be reviewed in parallel after the metadata helper lands.
- T033 through T037 can be drafted in parallel after implementation details stabilize.

## Implementation Strategy

1. Land schema, route, contract, frontend, and scanner tests first.
2. Add shared provenance and empty-state metadata.
3. Retire sample pattern production routes and frontend routing.
4. Replace fixed QA action defaults with backend/generated metadata helpers.
5. Regenerate contracts and built assets.
6. Run focused checks, full Spec QA, Playwright, post-UI API/database verification, and curl regression before marking Spec 049 complete.
