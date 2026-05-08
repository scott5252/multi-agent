# Tasks: Governance React Live Data

**Input**: Design documents from `specs/051-governance-react-live-data/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Required for this live-data migration because the spec must prove empty and seeded live data, Auth0-shaped and local-principal behavior, scanner guardrails, frontend behavior, Playwright, post-UI persistence, and curl validation.

**Organization**: Tasks are grouped by user story to enable independently testable increments.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the Spec 051 validation envelope and baseline governance work area.

- [x] T001 Reconcile `specs/_autopilot/remove-mock-data-roadmap/051-governance-react-live-data/validation.yml` with QA051 route, screenshot, and post-UI persistence expectations
- [x] T002 [P] Create QA env skeleton `specs/051-governance-react-live-data/.env.qa051`
- [x] T003 [P] Add reviewer notes skeleton `specs/051-governance-react-live-data/pr_notes.md`
- [x] T004 [P] Add QA guide skeleton `specs/051-governance-react-live-data/qa051.md`
- [x] T005 [P] Add UI QA guide skeleton `specs/051-governance-react-live-data/qa051_ui.md`
- [x] T006 [P] Add manual QA user guide skeleton `specs/051-governance-react-live-data/qa051_user_guide.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define shared contracts, test fixtures, and scanner boundaries before changing production behavior.

- [x] T007 [P] Add live governance provenance and empty-state schema expectations in `tests/unit/api/test_admin_governance_schema.py`
- [x] T008 [P] Add empty and seeded governance route contract expectations in `tests/contract/test_admin_react_contract.py`
- [x] T009 [P] Add live-data scanner expectations for governance QA031 markers in `tests/unit/admin/test_live_data_inventory_scanner.py`
- [x] T010 [P] Add governance fixture factory helpers for repository-backed tests in `tests/fixtures/admin_console.py`
- [x] T011 Update `src/multi_agent_platform/api/schemas/admin_governance.py` with provenance, empty-state, nullable panel, and safe mutation result fields
- [x] T012 Update `scripts/frontend/generate_admin_react_types.py` to emit and validate the new governance contract fields
- [x] T013 Update `frontend/admin/src/test/governanceTestData.ts` with test-only empty and seeded governance fixtures matching generated contracts
- [x] T014 Update `src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py` to classify Spec 051 governance production routes and allowed test-only fixtures

**Checkpoint**: Governance contracts and scanner expectations are ready before user-story implementation.

---

## Phase 3: User Story 1 - Review Live Governance State (Priority: P1) MVP

**Goal**: Authorized users see live governance rows or truthful empty states for provider, prompt, profile, routing, policy, diagnostic, and provenance panels.

**Independent Test**: Empty QA database returns empty/unavailable governance panels with no QA031 domain rows; seeded QA database returns only persisted records for the active scope.

### Tests for User Story 1

- [x] T015 [P] [US1] Add unit tests for empty and seeded dashboard projections in `tests/unit/admin/test_governance_service.py`
- [x] T016 [P] [US1] Add integration tests for platform, tenant, Auth0-shaped, denied, empty, and seeded governance bootstrap routes in `tests/integration/test_admin_react_routes.py`
- [x] T017 [P] [US1] Add bounded query test for live governance dashboard projection in `tests/performance/governance/test_governance_queries.py`
- [x] T018 [P] [US1] Add frontend empty/seeded dashboard tests in `frontend/admin/src/components/governance/GovernancePage.test.tsx`

### Implementation for User Story 1

- [x] T019 [US1] Replace fixed dashboard aggregation in `src/multi_agent_platform/admin/governance.py` with async live projection entry points that accept repositories, active scope, and principal context
- [x] T020 [US1] Implement provider live list projection from `ModelProviderRepository` and safe health/test records in `src/multi_agent_platform/admin/governance.py`
- [x] T021 [US1] Implement prompt live list projection from `PromptRepository` in `src/multi_agent_platform/admin/governance.py`
- [x] T022 [US1] Implement runtime profile live list projection from `AgentProfileRepository` in `src/multi_agent_platform/admin/governance.py`
- [x] T023 [US1] Implement routing, policy history, gateway diagnostic, and provenance empty/unavailable projections in `src/multi_agent_platform/admin/governance.py`
- [x] T024 [US1] Wire governance bootstrap, providers, prompts, profiles, history, provenance, and legacy-route endpoints to live async projections in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T025 [US1] Preserve governance route authorization surfaces in `src/multi_agent_platform/auth/policy.py`
- [x] T026 [US1] Update `frontend/admin/src/components/governance/GovernancePage.tsx` to render empty, unavailable, denied, and live provenance states without assuming fixed rows
- [x] T027 [US1] Update provider, prompt, profile, routing, policy, and provenance panels in `frontend/admin/src/components/governance/ProviderGovernancePanel.tsx`, `frontend/admin/src/components/governance/PromptGovernancePanel.tsx`, `frontend/admin/src/components/governance/ProfileGovernancePanel.tsx`, `frontend/admin/src/components/governance/RoutingPreviewPanel.tsx`, `frontend/admin/src/components/governance/PolicyHistoryPanel.tsx`, and `frontend/admin/src/components/governance/ProvenancePanel.tsx`

**Checkpoint**: User Story 1 can be validated independently through backend route tests and frontend empty/seeded rendering tests.

---

## Phase 4: User Story 2 - Verify Safe Governance Details (Priority: P2)

**Goal**: Governance detail panels show redaction-safe provider diagnostics, credential readiness, prompt/profile metadata, routing policy, and run provenance without raw protected content.

**Independent Test**: Seeded records containing sensitive-adjacent references render safe summaries only; unsafe markers are rejected or summarized before reaching React.

### Tests for User Story 2

- [x] T028 [P] [US2] Add schema safety tests for unsafe governance text and route paths in `tests/unit/api/test_admin_governance_schema.py`
- [x] T029 [P] [US2] Add service tests for provider health, credential readiness, prompt history, profile resolution, routing preview, policy history, and provenance safety in `tests/unit/admin/test_governance_service.py`
- [x] T030 [P] [US2] Add route tests for safe detail endpoints and redaction behavior in `tests/integration/test_admin_react_routes.py`
- [x] T031 [P] [US2] Add frontend panel safety tests in `frontend/admin/src/components/governance/ProviderGovernancePanel.test.tsx`, `frontend/admin/src/components/governance/PromptGovernancePanel.test.tsx`, `frontend/admin/src/components/governance/ProfileGovernancePanel.test.tsx`, `frontend/admin/src/components/governance/RoutingPreviewPanel.test.tsx`, and `frontend/admin/src/components/governance/ProvenancePanel.test.tsx`

### Implementation for User Story 2

- [x] T032 [US2] Implement credential-reference readiness projection and redaction summaries in `src/multi_agent_platform/admin/governance.py`
- [x] T033 [US2] Implement safe prompt history and preview projection from prompt records and preview safety helpers in `src/multi_agent_platform/admin/governance.py`
- [x] T034 [US2] Implement runtime profile resolution projection from live profile records and active scope in `src/multi_agent_platform/admin/governance.py`
- [x] T035 [US2] Implement routing preview and policy history projection from `ModelSkillConfigRepository` and audit-safe history records in `src/multi_agent_platform/admin/governance.py`
- [x] T036 [US2] Implement run provenance lookup using safe runtime/gateway/usage/audit evidence in `src/multi_agent_platform/admin/governance.py`
- [x] T037 [US2] Update frontend detail panels to show timestamps, stale/unavailable states, redaction notices, and safe audit references in `frontend/admin/src/components/governance/ProviderGovernancePanel.tsx`, `frontend/admin/src/components/governance/PromptGovernancePanel.tsx`, `frontend/admin/src/components/governance/ProfileGovernancePanel.tsx`, `frontend/admin/src/components/governance/RoutingPreviewPanel.tsx`, `frontend/admin/src/components/governance/PolicyHistoryPanel.tsx`, and `frontend/admin/src/components/governance/ProvenancePanel.tsx`
- [x] T038 [US2] Regenerate generated TypeScript governance contracts in `frontend/admin/src/api/generated/reactAdminApi.ts`

**Checkpoint**: User Story 2 can be validated independently by seeded safe-detail API tests and frontend panel tests.

---

## Phase 5: User Story 3 - Exercise Durable Governance Actions (Priority: P3)

**Goal**: At least one safe user-visible governance action persists through backend services and is verified after UI execution.

**Independent Test**: The UI saves a prompt or profile change, the backend returns persisted revision evidence, and the saved state is visible through API/database evidence after refresh.

### Tests for User Story 3

- [x] T039 [P] [US3] Add service tests for prompt/profile save success, stale conflict, unavailable preview, and denied action behavior in `tests/unit/admin/test_governance_service.py`
- [x] T040 [P] [US3] Add integration route tests for safe prompt/profile save, preview, resolve, routing preview, platform-only probe, and credential-reference actions in `tests/integration/test_admin_react_routes.py`
- [x] T041 [P] [US3] Add frontend mutation tests in `frontend/admin/src/components/governance/GovernancePage.test.tsx`, `frontend/admin/src/components/governance/PromptGovernancePanel.test.tsx`, and `frontend/admin/src/components/governance/ProfileGovernancePanel.test.tsx`

### Implementation for User Story 3

- [x] T042 [US3] Implement durable prompt save mutation through `PromptRepository` in `src/multi_agent_platform/admin/governance.py`
- [x] T043 [US3] Implement durable profile save mutation through `AgentProfileRepository` in `src/multi_agent_platform/admin/governance.py`
- [x] T044 [US3] Implement safe prompt preview, profile resolve, and routing preview mutation results without external provider or connector calls in `src/multi_agent_platform/admin/governance.py`
- [x] T045 [US3] Keep provider probe and credential-reference mutations platform-admin-only and mocked/local-safe for QA in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T046 [US3] Update governance API client helpers in `frontend/admin/src/api/client.ts`
- [x] T047 [US3] Wire mutation result, stale conflict, refresh, and field-error handling in `frontend/admin/src/components/governance/GovernancePage.tsx`, `frontend/admin/src/components/governance/PromptGovernancePanel.tsx`, and `frontend/admin/src/components/governance/ProfileGovernancePanel.tsx`
- [x] T048 [US3] Run `npm run --prefix frontend/admin build` to rebuild `src/multi_agent_platform/web_admin/static/react/manifest.json` and asset files under `src/multi_agent_platform/web_admin/static/react/assets/`

**Checkpoint**: User Story 3 can be validated independently by a save action, API/database persistence proof, and frontend mutation tests.

---

## Phase 6: Polish & Cross-Cutting Validation

**Purpose**: Documentation, scanners, generated contracts, and mandatory post-spec validation.

- [x] T049 [P] Finalize `specs/051-governance-react-live-data/qa051.md`
- [x] T050 [P] Finalize `specs/051-governance-react-live-data/qa051_ui.md`
- [x] T051 [P] Finalize `specs/051-governance-react-live-data/qa051_user_guide.md`
- [x] T052 [P] Finalize `specs/051-governance-react-live-data/pr_notes.md`
- [x] T053 Run `uv run python scripts/frontend/generate_admin_react_types.py --check`
- [x] T054 Run focused backend tests for `tests/unit/api/test_admin_governance_schema.py`, `tests/unit/admin/test_governance_service.py`, `tests/integration/test_admin_react_routes.py`, `tests/contract/test_admin_react_contract.py`, `tests/performance/governance/test_governance_queries.py`, and `tests/unit/admin/test_live_data_inventory_scanner.py`
- [x] T055 Run frontend governance tests for `frontend/admin/src/components/governance/*.test.tsx`, `npm run --prefix frontend/admin typecheck`, and `npm run --prefix frontend/admin build`
- [x] T056 Run QA document validation for `specs/051-governance-react-live-data`
- [x] T057 Run `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/051-governance-react-live-data/validation.yml`
- [x] T058 Run `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/051-governance-react-live-data/validation.yml --start-processes`
- [x] T059 Run post-UI API/database verification for governance save persistence and record evidence in `specs/_autopilot/remove-mock-data-roadmap/051-governance-react-live-data/status.json`
- [x] T060 Run `uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa051-after-spec`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on setup; blocks all user stories.
- **US1 (Phase 3)**: Depends on foundational tasks; MVP for truthful live/empty governance state.
- **US2 (Phase 4)**: Depends on foundational tasks and can run after US1 projection shapes are stable.
- **US3 (Phase 5)**: Depends on foundational tasks and the relevant prompt/profile projection helpers from US1/US2.
- **Polish (Phase 6)**: Depends on all selected user stories.

### Parallel Opportunities

- T002-T006 can run in parallel.
- T007-T010 can run in parallel before shared schema implementation.
- T015-T018, T028-T031, and T039-T041 can run in parallel by test file.
- Frontend panel work can run in parallel with backend projection work after generated contract shapes are known.
- Documentation tasks T049-T052 can run in parallel after implementation behavior is settled.

### Implementation Strategy

1. Complete setup and foundational contract/scanner tasks.
2. Deliver US1 first so every governance page can truthfully render empty and seeded live states.
3. Add US2 safe details and provenance without expanding mutation behavior.
4. Add US3 durable safe actions and Playwright persistence proof.
5. Run all validation gates and update status/queue only after every gate passes.

## Notes

- Production code must not return fixed QA031 governance rows.
- Test fixtures may keep QA031 markers only under test-only or historical spec paths.
- Do not commit between tasks or specs during this autopilot run; keep validated changes in the dirty worktree until the user commits at the end.
