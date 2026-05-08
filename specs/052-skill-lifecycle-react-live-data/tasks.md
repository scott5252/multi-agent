# Tasks: Skill Lifecycle React Live Data

**Input**: Design documents from `specs/052-skill-lifecycle-react-live-data/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Required for this live-data migration because the spec must prove empty and seeded live data, Auth0-shaped and local-principal behavior, scanner guardrails, frontend behavior, Playwright, post-UI persistence, and curl validation.

**Organization**: Tasks are grouped by user story to enable independently testable increments.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the Spec 052 validation envelope and baseline skill lifecycle work area.

- [x] T001 Reconcile `specs/_autopilot/remove-mock-data-roadmap/052-skill-lifecycle-react-live-data/validation.yml` with QA052 skill route, screenshot, and post-UI persistence expectations
- [x] T002 [P] Create QA env skeleton `specs/052-skill-lifecycle-react-live-data/.env.qa052`
- [x] T003 [P] Add reviewer notes skeleton `specs/052-skill-lifecycle-react-live-data/pr_notes.md`
- [x] T004 [P] Add QA guide skeleton `specs/052-skill-lifecycle-react-live-data/qa052.md`
- [x] T005 [P] Add UI QA guide skeleton `specs/052-skill-lifecycle-react-live-data/qa052_ui.md`
- [x] T006 [P] Add manual QA user guide skeleton `specs/052-skill-lifecycle-react-live-data/qa052_user_guide.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define shared contracts, test fixtures, repositories, and scanner boundaries before changing production behavior.

- [x] T007 [P] Add live skill lifecycle provenance and empty-state schema expectations in `tests/unit/api/test_admin_skill_lifecycle_schema.py`
- [x] T008 [P] Add empty and seeded skill lifecycle route contract expectations in `tests/contract/test_admin_react_contract.py`
- [x] T009 [P] Add live-data scanner expectations for skill lifecycle QA032 markers in `tests/unit/admin/test_live_data_inventory_scanner.py`
- [x] T010 [P] Add skill lifecycle seeded fixture factory helpers for repository-backed route tests in `tests/fixtures/skill_registry.py`
- [x] T011 Update `src/multi_agent_platform/api/schemas/admin_skill_lifecycle.py` with provenance, empty-state, nullable panel, safe detail, and safe mutation result fields
- [x] T012 Update `scripts/frontend/generate_admin_react_types.py` to emit and validate the new skill lifecycle contract fields
- [x] T013 Update `frontend/admin/src/test/skillLifecycleTestData.ts` with test-only empty and seeded fixtures matching generated contracts
- [x] T014 Update `src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py` to classify Spec 052 skill lifecycle production routes and allowed test-only fixtures

**Checkpoint**: Skill lifecycle contracts and scanner expectations are ready before user-story implementation.

---

## Phase 3: User Story 1 - Review Live Skill Lifecycle State (Priority: P1) MVP

**Goal**: Authorized users see live skill lifecycle rows or truthful empty states for packages, candidates, grants, discovery, installations, credential readiness, smoke tests, diagnostics, eligibility, lifecycle state, and audit panels.

**Independent Test**: Empty QA database returns empty/unavailable skill lifecycle panels with no QA032 domain rows; seeded QA database returns only persisted records for the active scope.

### Tests for User Story 1

- [x] T015 [P] [US1] Add unit tests for empty and seeded dashboard projections in `tests/unit/admin/test_skill_lifecycle_service.py`
- [x] T016 [P] [US1] Add integration tests for platform, tenant, Auth0-shaped, denied, empty, and seeded skill lifecycle bootstrap routes in `tests/integration/test_admin_react_routes.py`
- [x] T017 [P] [US1] Add bounded query test for live skill lifecycle dashboard projection in `tests/performance/skills/test_skill_lifecycle_queries.py`
- [x] T018 [P] [US1] Add frontend empty/seeded dashboard tests in `frontend/admin/src/components/skills/SkillLifecyclePage.test.tsx`

### Implementation for User Story 1

- [x] T019 [US1] Replace fixed dashboard aggregation in `src/multi_agent_platform/admin/skill_lifecycle.py` with async live projection entry points that accept repositories, active scope, and principal context
- [x] T020 [US1] Implement platform package and version live list projection from `SkillRegistryRepository` in `src/multi_agent_platform/admin/skill_lifecycle.py`
- [x] T021 [US1] Implement package candidate, validation, quarantine, withdrawal, and tenant grant empty/unavailable projections in `src/multi_agent_platform/admin/skill_lifecycle.py`
- [x] T022 [US1] Implement tenant discovery and installation live projections from `SkillRegistryRepository` in `src/multi_agent_platform/admin/skill_lifecycle.py`
- [x] T023 [US1] Implement credential readiness, smoke-test, connector diagnostic, binding eligibility, and audit empty/unavailable projections in `src/multi_agent_platform/admin/skill_lifecycle.py`
- [x] T024 [US1] Wire skills bootstrap, discovery, installations, diagnostics, audit, and legacy-route endpoints to live async projections in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T025 [US1] Preserve skill lifecycle route authorization surfaces in `src/multi_agent_platform/auth/policy.py`
- [x] T026 [US1] Update `frontend/admin/src/components/skills/SkillLifecyclePage.tsx` to render empty, unavailable, denied, and live provenance states without assuming fixed rows
- [x] T027 [US1] Update skill lifecycle panels in `frontend/admin/src/components/skills/PackagePublicationPanel.tsx`, `frontend/admin/src/components/skills/PackageLifecyclePanel.tsx`, `frontend/admin/src/components/skills/TenantSkillLifecyclePanel.tsx`, `frontend/admin/src/components/skills/CredentialReadinessPanel.tsx`, `frontend/admin/src/components/skills/SmokeTestPanel.tsx`, `frontend/admin/src/components/skills/ConnectorReadinessPanel.tsx`, `frontend/admin/src/components/skills/BindingAndDiagnosticsPanel.tsx`, and `frontend/admin/src/components/skills/SkillLifecycleAuditPanel.tsx`

**Checkpoint**: User Story 1 can be validated independently through backend route tests and frontend empty/seeded rendering tests.

---

## Phase 4: User Story 2 - Verify Redaction-Safe Skill Details (Priority: P2)

**Goal**: Skill lifecycle detail panels show redaction-safe package, manifest, credential, smoke-test, connector, eligibility, quarantine, withdrawal, and audit evidence without raw protected content.

**Independent Test**: Seeded records containing sensitive-adjacent references render safe summaries only; unsafe markers are rejected or summarized before reaching React.

### Tests for User Story 2

- [x] T028 [P] [US2] Add schema safety tests for unsafe skill lifecycle text and route paths in `tests/unit/api/test_admin_skill_lifecycle_schema.py`
- [x] T029 [P] [US2] Add service tests for safe manifest summaries, credential readiness, smoke-test evidence, connector diagnostics, binding eligibility, quarantine, withdrawal, and audit safety in `tests/unit/admin/test_skill_lifecycle_service.py`
- [x] T030 [P] [US2] Add route tests for safe detail endpoints and redaction behavior in `tests/integration/test_admin_react_routes.py`
- [x] T031 [P] [US2] Add frontend panel safety tests in `frontend/admin/src/components/skills/PackagePublicationPanel.test.tsx`, `frontend/admin/src/components/skills/CredentialReadinessPanel.test.tsx`, `frontend/admin/src/components/skills/BindingAndDiagnosticsPanel.test.tsx`, and `frontend/admin/src/components/skills/SkillLifecycleAuditPanel.test.tsx`

### Implementation for User Story 2

- [x] T032 [US2] Implement safe manifest summary and package version detail projection in `src/multi_agent_platform/admin/skill_lifecycle.py`
- [x] T033 [US2] Implement credential-reference readiness projection and redaction summaries in `src/multi_agent_platform/admin/skill_lifecycle.py`
- [x] T034 [US2] Implement smoke-test and readiness history projection from persisted safe evidence in `src/multi_agent_platform/admin/skill_lifecycle.py`
- [x] T035 [US2] Implement connector diagnostic projection from `SkillExecutionGateway` summaries and governed diagnostic records in `src/multi_agent_platform/admin/skill_lifecycle.py`
- [x] T036 [US2] Implement binding eligibility projection from package, installation, credential, connector, and policy records in `src/multi_agent_platform/admin/skill_lifecycle.py`
- [x] T037 [US2] Implement lifecycle audit timeline projection with bounded safe audit summaries in `src/multi_agent_platform/admin/skill_lifecycle.py`
- [x] T038 [US2] Regenerate generated TypeScript skill lifecycle contracts in `frontend/admin/src/api/generated/reactAdminApi.ts`

**Checkpoint**: User Story 2 can be validated independently by seeded safe-detail API tests and frontend panel tests.

---

## Phase 5: User Story 3 - Exercise Durable Skill Lifecycle Actions (Priority: P3)

**Goal**: At least one safe user-visible skill lifecycle action persists through backend services and is verified after UI execution.

**Independent Test**: The UI saves credential metadata, refreshes readiness, validates a candidate, installs a skill, or previews eligibility; the backend returns persisted evidence and the saved state is visible through API/database evidence after refresh.

### Tests for User Story 3

- [x] T039 [P] [US3] Add service tests for candidate validation, publish, grant, install, credential save, smoke-test refresh, diagnostics, eligibility preview, stale conflict, unavailable, and denied action behavior in `tests/unit/admin/test_skill_lifecycle_service.py`
- [x] T040 [P] [US3] Add integration route tests for safe lifecycle mutations, platform-only actions, tenant-scoped actions, stale conflicts, and cross-tenant denial in `tests/integration/test_admin_react_routes.py`
- [x] T041 [P] [US3] Add frontend mutation tests in `frontend/admin/src/components/skills/SkillLifecyclePage.test.tsx`, `frontend/admin/src/components/skills/PackagePublicationPanel.test.tsx`, `frontend/admin/src/components/skills/TenantSkillLifecyclePanel.test.tsx`, and `frontend/admin/src/components/skills/CredentialReadinessPanel.test.tsx`

### Implementation for User Story 3

- [x] T042 [US3] Implement durable candidate validation and publication mutations through existing skill registry services in `src/multi_agent_platform/admin/skill_lifecycle.py`
- [x] T043 [US3] Implement durable tenant grant, quarantine, and withdrawal mutations through existing skill registry services in `src/multi_agent_platform/admin/skill_lifecycle.py`
- [x] T044 [US3] Implement durable tenant installation and credential-reference mutations through existing skill registry services in `src/multi_agent_platform/admin/skill_lifecycle.py`
- [x] T045 [US3] Implement mocked-safe smoke-test refresh, connector diagnostic, and binding eligibility mutation results without external connector or provider calls in `src/multi_agent_platform/admin/skill_lifecycle.py`
- [x] T046 [US3] Wire lifecycle mutation routes to live async service-backed results in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T047 [US3] Update skill lifecycle API client helpers in `frontend/admin/src/api/client.ts`
- [x] T048 [US3] Wire mutation result, stale conflict, refresh, and field-error handling in `frontend/admin/src/components/skills/SkillLifecyclePage.tsx`, `frontend/admin/src/components/skills/PackagePublicationPanel.tsx`, `frontend/admin/src/components/skills/TenantSkillLifecyclePanel.tsx`, `frontend/admin/src/components/skills/CredentialReadinessPanel.tsx`, and `frontend/admin/src/components/skills/BindingAndDiagnosticsPanel.tsx`
- [x] T049 [US3] Run `npm run --prefix frontend/admin build` to rebuild `src/multi_agent_platform/web_admin/static/react/manifest.json` and asset files under `src/multi_agent_platform/web_admin/static/react/assets/`

**Checkpoint**: User Story 3 can be validated independently by a safe UI action, API/database persistence proof, and frontend mutation tests.

---

## Phase 6: Polish & Cross-Cutting Validation

**Purpose**: Documentation, scanners, generated contracts, and mandatory post-spec validation.

- [x] T050 [P] Finalize `specs/052-skill-lifecycle-react-live-data/qa052.md`
- [x] T051 [P] Finalize `specs/052-skill-lifecycle-react-live-data/qa052_ui.md`
- [x] T052 [P] Finalize `specs/052-skill-lifecycle-react-live-data/qa052_user_guide.md`
- [x] T053 [P] Finalize `specs/052-skill-lifecycle-react-live-data/pr_notes.md`
- [x] T054 Run `uv run python scripts/frontend/generate_admin_react_types.py --check`
- [x] T055 Run focused backend tests for `tests/unit/api/test_admin_skill_lifecycle_schema.py`, `tests/unit/admin/test_skill_lifecycle_service.py`, `tests/integration/test_admin_react_routes.py`, `tests/contract/test_admin_react_contract.py`, `tests/performance/skills/test_skill_lifecycle_queries.py`, and `tests/unit/admin/test_live_data_inventory_scanner.py`
- [x] T056 Run frontend skill lifecycle tests for `frontend/admin/src/components/skills/*.test.tsx`, `npm run --prefix frontend/admin typecheck`, and `npm run --prefix frontend/admin build`
- [x] T057 Run QA document validation for `specs/052-skill-lifecycle-react-live-data`
- [x] T058 Run `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/052-skill-lifecycle-react-live-data/validation.yml`
- [x] T059 Run `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/052-skill-lifecycle-react-live-data/validation.yml --start-processes`
- [x] T060 Run post-UI API/database verification for skill lifecycle mutation persistence and record evidence in `specs/_autopilot/remove-mock-data-roadmap/052-skill-lifecycle-react-live-data/status.json`
- [x] T061 Run `uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa052-after-spec`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on setup; blocks all user stories.
- **US1 (Phase 3)**: Depends on foundational tasks; MVP for truthful live/empty skill lifecycle state.
- **US2 (Phase 4)**: Depends on foundational tasks and can run after US1 projection shapes are stable.
- **US3 (Phase 5)**: Depends on foundational tasks and the relevant live detail projection helpers from US1/US2.
- **Polish (Phase 6)**: Depends on all selected user stories.

### Parallel Opportunities

- T002-T006 can run in parallel.
- T007-T010 can run in parallel before shared schema implementation.
- T015-T018, T028-T031, and T039-T041 can run in parallel by test file.
- Frontend panel work can run in parallel with backend projection work after generated contract shapes are known.
- Documentation tasks T050-T053 can run in parallel after implementation behavior is settled.

### Implementation Strategy

1. Complete setup and foundational contract/scanner tasks.
2. Deliver US1 first so every skill lifecycle page can truthfully render empty and seeded live states.
3. Add US2 safe details without expanding mutation behavior.
4. Add US3 durable safe actions and Playwright persistence proof.
5. Run all validation gates and update status/queue only after every gate passes.

## Notes

- Production code must not return fixed QA032 skill lifecycle rows.
- Test fixtures may keep QA032 markers only under test-only or historical spec paths.
- Do not commit between tasks or specs during this autopilot run; keep validated changes in the dirty worktree until the user commits at the end.
