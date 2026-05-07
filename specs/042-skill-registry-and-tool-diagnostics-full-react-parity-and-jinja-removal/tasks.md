# Tasks: Skill Registry And Tool Diagnostics Full React Parity And Jinja Removal

**Input**: Design documents from `specs/042-skill-registry-and-tool-diagnostics-full-react-parity-and-jinja-removal/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Tests**: Required by the feature specification. Write focused backend/frontend tests before implementation where practical.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm active feature context and current skill surface inventory.

- [X] T001 Confirm `.specify/feature.json` points to `specs/042-skill-registry-and-tool-diagnostics-full-react-parity-and-jinja-removal`
- [X] T002 [P] Record current skill registry and skill diagnostics Jinja templates in `specs/042-skill-registry-and-tool-diagnostics-full-react-parity-and-jinja-removal/pr_notes.md`
- [X] T003 [P] Inspect current React skill lifecycle routes and components in `frontend/admin/src/components/skills/SkillLifecyclePage.tsx`
- [X] T004 [P] Inspect current backend skill lifecycle builders in `src/multi_agent_platform/admin/skill_lifecycle.py`
- [X] T005 [P] Inspect current Jinja browser handlers in `src/multi_agent_platform/api/routers/admin_skill_registry.py` and `src/multi_agent_platform/api/routers/admin_skill_execution.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared contracts, generated types, and route mapping that all stories depend on.

- [X] T006 [P] Add skill legacy route mapping schema to `src/multi_agent_platform/api/schemas/admin_skill_lifecycle.py`
- [X] T007 [P] Add missing safe package, version, installation, credential, smoke-test, diagnostic, and legacy-route fields to `src/multi_agent_platform/api/schemas/admin_skill_lifecycle.py`
- [X] T008 Add deterministic legacy route mapping builder to `src/multi_agent_platform/admin/skill_lifecycle.py`
- [X] T009 Add skill legacy route JSON endpoint and SPA fallback allowances in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T010 Update `scripts/frontend/generate_admin_react_types.py` and regenerate `frontend/admin/src/api/generated/reactAdminApi.ts`
- [X] T011 [P] Add contract assertions for skill legacy route mappings and safe fields in `tests/contract/test_admin_react_contract.py`
- [X] T012 [P] Add backend schema tests for skill lifecycle safe contracts in `tests/unit/api/test_admin_skill_lifecycle_schema.py`
- [X] T013 [P] Add frontend fixture coverage for legacy route mappings in `frontend/admin/src/test/skillLifecycleTestData.ts`
- [X] T014 Add React route parsing helpers for skill child routes in `frontend/admin/src/routes.tsx`

**Checkpoint**: Foundation ready - user story implementation can begin.

---

## Phase 3: User Story 1 - Manage Platform Skill Packages In React (Priority: P1) MVP

**Goal**: Platform admins can manage package, candidate, version, grant, quarantine/withdrawal, and old package URLs through React/non-Jinja paths.

**Independent Test**: Platform-admin route tests and React tests prove package workflows, legacy direct links, upload precedence, stale conflicts, and template deletion evidence.

### Tests for User Story 1

- [X] T015 [P] [US1] Add legacy package redirect tests in `tests/integration/api/test_admin_skill_registry_legacy_redirects.py`
- [X] T016 [P] [US1] Add package create/candidate/version/grant compatibility form tests in `tests/integration/api/test_admin_skill_registry_browser_flows.py`
- [X] T017 [P] [US1] Add upload-over-paste and raw-manifest redaction tests in `tests/integration/api/test_admin_skill_registry_browser_flows.py`
- [X] T018 [P] [US1] Add stale candidate publish and tenant grant conflict tests in `tests/integration/api/test_admin_skill_registry_browser_flows.py`
- [X] T019 [P] [US1] Add React package lifecycle tests in `frontend/admin/src/components/skills/SkillLifecyclePage.test.tsx`
- [X] T020 [P] [US1] Add skill template retirement scanner tests in `tests/unit/admin/test_skill_jinja_retirement.py`

### Implementation for User Story 1

- [X] T021 [US1] Extend package/candidate/version/grant summaries and actions in `src/multi_agent_platform/admin/skill_lifecycle.py`
- [X] T022 [US1] Add React package child-route view states in `frontend/admin/src/components/skills/SkillLifecyclePage.tsx`
- [X] T023 [P] [US1] Update package publication panel for create/detail/candidate/version/grant states in `frontend/admin/src/components/skills/PackagePublicationPanel.tsx`
- [X] T024 [P] [US1] Update package lifecycle panel for quarantine/withdrawal and legacy evidence in `frontend/admin/src/components/skills/PackageLifecyclePanel.tsx`
- [X] T025 [US1] Add package create, candidate, validate, publish, grant, and lifecycle API client helpers in `frontend/admin/src/api/client.ts`
- [X] T026 [US1] Convert package GET routes in `src/multi_agent_platform/api/routers/admin_skill_registry.py` to authenticated React redirects or safe non-Jinja problems
- [X] T027 [US1] Convert package form POST routes in `src/multi_agent_platform/api/routers/admin_skill_registry.py` to execute existing service behavior and redirect to React destinations
- [X] T028 [US1] Delete package-owned templates in `src/multi_agent_platform/web_admin/templates/skill_registry/package_list.html`, `src/multi_agent_platform/web_admin/templates/skill_registry/package_create.html`, `src/multi_agent_platform/web_admin/templates/skill_registry/package_candidate_form.html`, `src/multi_agent_platform/web_admin/templates/skill_registry/package_detail.html`, `src/multi_agent_platform/web_admin/templates/skill_registry/package_version_detail.html`, and `src/multi_agent_platform/web_admin/templates/skill_registry/tenant_grant_form.html`
- [X] T029 [US1] Update skill registry navigation and saved destinations in `src/multi_agent_platform/api/ui/admin_console.py`

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Manage Tenant Skill Installations In React (Priority: P2)

**Goal**: Tenant admins can discover available versions, install skills, configure credentials, review readiness, run smoke tests, preview binding eligibility, and recover from stale conflicts through React/non-Jinja paths.

**Independent Test**: Tenant-admin route tests and React tests prove installation workflows, tenant isolation, credential hygiene, smoke history, and old installation URL redirects.

### Tests for User Story 2

- [X] T030 [P] [US2] Add tenant available-version and installation redirect tests in `tests/integration/api/test_admin_skill_registry_legacy_redirects.py`
- [X] T031 [P] [US2] Add tenant install/detail/configure/smoke/eligibility browser compatibility tests in `tests/integration/api/test_admin_skill_registry_browser_flows.py`
- [X] T032 [P] [US2] Add cross-tenant installation denial and unauthorized tenant-label redaction tests in `tests/integration/api/test_admin_skill_registry_browser_flows.py`
- [X] T033 [P] [US2] Add credential reference redaction and stale revision tests in `tests/integration/api/test_admin_skill_registry_browser_flows.py`
- [X] T034 [P] [US2] Add React tenant installation lifecycle tests in `frontend/admin/src/components/skills/SkillLifecyclePage.test.tsx`

### Implementation for User Story 2

- [X] T035 [US2] Extend tenant discovery, installation, credential, readiness, smoke, binding, and audit summaries in `src/multi_agent_platform/admin/skill_lifecycle.py`
- [X] T036 [US2] Add React installation child-route view states in `frontend/admin/src/components/skills/SkillLifecyclePage.tsx`
- [X] T037 [P] [US2] Update tenant skill lifecycle panel for available versions, installation detail, and stale conflict states in `frontend/admin/src/components/skills/TenantSkillLifecyclePanel.tsx`
- [X] T038 [P] [US2] Update credential readiness panel for configure states and safe reference summaries in `frontend/admin/src/components/skills/CredentialReadinessPanel.tsx`
- [X] T039 [P] [US2] Update smoke test panel for explicit refresh and history states in `frontend/admin/src/components/skills/SmokeTestPanel.tsx`
- [X] T040 [P] [US2] Update binding panel for eligibility preview route states in `frontend/admin/src/components/skills/BindingAndDiagnosticsPanel.tsx`
- [X] T041 [US2] Convert available-version and installation GET routes in `src/multi_agent_platform/api/routers/admin_skill_registry.py` to authenticated React redirects or safe non-Jinja problems
- [X] T042 [US2] Convert install, credential, smoke, and eligibility form POST routes in `src/multi_agent_platform/api/routers/admin_skill_registry.py` to execute existing service behavior and redirect to React destinations
- [X] T043 [US2] Delete tenant installation templates in `src/multi_agent_platform/web_admin/templates/skill_registry/available_versions.html`, `src/multi_agent_platform/web_admin/templates/skill_registry/installation_list.html`, `src/multi_agent_platform/web_admin/templates/skill_registry/installation_detail.html`, and `src/multi_agent_platform/web_admin/templates/skill_registry/installation_configure.html`
- [X] T044 [US2] Delete skill registry component partials in `src/multi_agent_platform/web_admin/templates/skill_registry/components/`

**Checkpoint**: User Story 2 is independently functional and testable.

---

## Phase 5: User Story 3 - Diagnose SkillExecutionGateway Behavior In React (Priority: P3)

**Goal**: Operators and tenant admins can review and explicitly refresh safe SkillExecutionGateway diagnostics through React/non-Jinja paths.

**Independent Test**: Diagnostics route tests and React tests prove explicit mocked-safe refresh, policy enforcement, redaction, old diagnostics redirect, and diagnostics template deletion.

### Tests for User Story 3

- [X] T045 [P] [US3] Add diagnostics legacy redirect tests in `tests/integration/api/test_admin_skill_execution_legacy_redirects.py`
- [X] T046 [P] [US3] Add diagnostics explicit refresh and tool-policy redaction tests in `tests/integration/api/test_admin_skill_execution_ui.py`
- [X] T047 [P] [US3] Add React diagnostics tests in `frontend/admin/src/components/skills/SkillLifecyclePage.test.tsx`

### Implementation for User Story 3

- [X] T048 [US3] Extend skill execution diagnostic summaries and safe unavailable states in `src/multi_agent_platform/admin/skill_lifecycle.py`
- [X] T049 [US3] Convert `/admin/skill-execution/ui/diagnostics` in `src/multi_agent_platform/api/routers/admin_skill_execution.py` to authenticated React redirect or safe non-Jinja problem
- [X] T050 [US3] Ensure diagnostics API refresh remains explicit and mocked-safe in `src/multi_agent_platform/api/routers/admin_skill_execution.py`
- [X] T051 [P] [US3] Update connector readiness panel for diagnostics route states in `frontend/admin/src/components/skills/ConnectorReadinessPanel.tsx`
- [X] T052 [P] [US3] Update binding/diagnostics panel for explicit refresh results in `frontend/admin/src/components/skills/BindingAndDiagnosticsPanel.tsx`
- [X] T053 [US3] Delete `src/multi_agent_platform/web_admin/templates/skill_execution/diagnostics.html`

**Checkpoint**: User Story 3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, QA, redaction, generated assets, and final validation.

- [X] T054 [P] Update skill registry references in `README.md`
- [X] T055 [P] Update local admin quickstart guidance in `docs/quickstart.md`
- [X] T056 [P] Update admin console shell migration notes in `docs/admin-console-shell.md`
- [X] T057 [P] Update skill registry lifecycle docs in `docs/skill-registry.md` if present, otherwise update the closest existing skill registry docs under `docs/`
- [X] T058 [P] Update feature quickstart in `specs/042-skill-registry-and-tool-diagnostics-full-react-parity-and-jinja-removal/quickstart.md`
- [X] T059 Generate QA guide, UI walkthrough, `.env.qa042`, user guide, and PR notes in `specs/042-skill-registry-and-tool-diagnostics-full-react-parity-and-jinja-removal/`
- [X] T060 Reconcile `specs/_autopilot/react-ui2-roadmap/042-skill-registry-and-tool-diagnostics-full-react-parity-and-jinja-removal/validation.yml` with the final React login/route flow
- [X] T061 Run `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/042-skill-registry-and-tool-diagnostics-full-react-parity-and-jinja-removal`
- [X] T062 Run `uv run ruff check .`
- [X] T063 Run `uv run ruff format --check .`
- [X] T064 Run `uv run mypy src`
- [X] T065 Run `uv run python scripts/frontend/generate_admin_react_types.py --check`
- [X] T066 Run focused backend tests for skill registry, diagnostics, contracts, and React routes
- [X] T067 Run `cd frontend/admin && npm test -- --run src/App.test.tsx src/components/skills`
- [X] T068 Run `cd frontend/admin && npm run build`
- [X] T069 Run `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui2-roadmap/042-skill-registry-and-tool-diagnostics-full-react-parity-and-jinja-removal/validation.yml`
- [X] T070 Run `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui2-roadmap/042-skill-registry-and-tool-diagnostics-full-react-parity-and-jinja-removal/validation.yml --start-processes`
- [X] T071 Inspect `output/playwright/qa042_ui/qa042-react-ui2-smoke.png` for nonblank React skill registry evidence
- [X] T072 Update `specs/_autopilot/react-ui2-roadmap/042-skill-registry-and-tool-diagnostics-full-react-parity-and-jinja-removal/status.json` and `specs/_autopilot/react-ui2-roadmap/queue.json` after validation passes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories.
- **User Story 1 (P1)**: Depends on Foundation; can be validated independently.
- **User Story 2 (P2)**: Depends on Foundation; should preserve US1 behavior but can be implemented independently.
- **User Story 3 (P3)**: Depends on Foundation; should preserve US1/US2 behavior but can be implemented independently.
- **Polish (Phase 6)**: Depends on all desired user stories.

### Parallel Opportunities

- T002-T005 can run in parallel.
- T006, T007, T011, T012, and T013 can run in parallel after setup.
- US1 tests T015-T020 can run in parallel before US1 implementation.
- US2 tests T030-T034 can run in parallel before US2 implementation.
- US3 tests T045-T047 can run in parallel before US3 implementation.
- Frontend component tasks marked [P] can run in parallel with backend route conversions if generated contracts are stable.
- Documentation tasks T054-T058 can run in parallel after implementation shape is stable.

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete User Story 1 to prove package publication and old package route retirement.
3. Run focused US1 backend/frontend tests before moving to tenant installation or diagnostics.

### Incremental Delivery

1. Add User Story 2 for tenant installation, credentials, smoke tests, binding, and installation route retirement.
2. Add User Story 3 for SkillExecutionGateway diagnostics route retirement.
3. Complete documentation, QA docs, generated assets, full Spec QA, and Playwright before marking Spec 042 complete.

## Notes

- Do not delete global Jinja infrastructure or non-skill templates in Spec 042.
- Do not remove JSON/API routes consumed by React.
- Stop if a legacy route cannot safely redirect or return a safe non-Jinja problem.
- Stop if raw manifests, raw credentials, raw connector payloads, raw smoke transcripts, stack traces, local paths, or unauthorized tenant labels appear in React, route responses, QA docs, screenshots, logs, or reviewer notes.
