# Tasks: React Skill Registry And Tool Execution Lifecycle

**Input**: Design documents from `specs/032-react-skill-registry-and-tool-execution-lifecycle/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required. The feature specification mandates backend schema/service
coverage, generated TypeScript drift checks, local-principal and Auth0-shaped
route coverage, tenant isolation, redaction tests, frontend component tests,
Playwright browser lifecycle flows, QA docs, and full Spec QA evidence.

**Organization**: Tasks are grouped by user story so each story remains
independently testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and has no
  dependency on an incomplete task.
- **[Story]**: User story label from `spec.md`.
- Every task includes an exact file path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare backend, frontend, and test folders for the React skill
lifecycle workspace.

- [X] T001 Add backend skill lifecycle schema module in `src/multi_agent_platform/api/schemas/admin_skill_lifecycle.py`
- [X] T002 [P] Add skill lifecycle aggregation/service module in `src/multi_agent_platform/admin/skill_lifecycle.py`
- [X] T003 [P] Add React skill lifecycle component directory in `frontend/admin/src/components/skills/`
- [X] T004 [P] Add React skill lifecycle fixture file in `frontend/admin/src/test/skillLifecycleTestData.ts`
- [X] T005 [P] Add skill lifecycle performance test directory in `tests/performance/skills/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define shared contracts, authorization surfaces, generated types,
deterministic fixtures, safe mutations, and redaction guarantees.

**CRITICAL**: No user story implementation can proceed until these tasks are
done.

- [X] T006 Extend dashboard, section, candidate, package version, tenant grant, installation, credential option, connector readiness, gateway diagnostic, binding preview, audit record, wizard step, safe action, and mutation result models in `src/multi_agent_platform/api/schemas/admin_skill_lifecycle.py`
- [X] T007 Add raw manifest, raw credential, authorization header, provider token, private message, connector payload, raw tool output, stack trace, local path, and unauthorized tenant label validators in `src/multi_agent_platform/api/schemas/admin_skill_lifecycle.py`
- [X] T008 Extend Spec 032 skill lifecycle contract and assertion helper generation in `scripts/frontend/generate_admin_react_types.py`
- [X] T009 Regenerate generated React API types in `frontend/admin/src/api/generated/reactAdminApi.ts`
- [X] T010 Add Spec 032 OpenAPI and generated-contract drift checks in `tests/contract/test_admin_react_contract.py`
- [X] T011 Add skill lifecycle schema redaction, upload-precedence, stale-conflict, and mutation result tests in `tests/unit/api/test_admin_skill_lifecycle_schema.py`
- [X] T012 Add React client helpers for skills bootstrap, candidates, validation, publication, discovery, installations, credentials, smoke tests, diagnostics, eligibility, and audit requests in `frontend/admin/src/api/client.ts`
- [X] T013 Register protected React skill lifecycle route and mutation surfaces in `src/multi_agent_platform/auth/policy.py`
- [X] T014 Add `/admin/app/skills` route constants, route wrapper, nav destination, and fallback links in `src/multi_agent_platform/api/routers/admin_react.py`

---

## Phase 3: User Story 1 - Publish Skill Packages Safely (Priority: P1) MVP

**Goal**: Platform administrators can create package candidates, submit
manifests, validate findings, review grants, publish immutable versions, and
see quarantine/withdrawal state without unsafe payload exposure.

**Independent Test**: Platform admin loads `/admin/app/skills`, submits a
deterministic manifest fixture, validates and publishes a candidate, reviews
tenant grant impact and audit references, and confirms raw manifest text is not
echoed.

### Tests for User Story 1

- [X] T015 [P] [US1] Add local-principal platform bootstrap, manifest candidate, validation, publish, tenant grant mutation, quarantine, and withdrawal route tests in `tests/integration/test_admin_react_routes.py`
- [X] T016 [P] [US1] Add Auth0-shaped platform publication authorization, tenant grant mutation authorization, and platform-only mutation tests in `tests/integration/test_admin_react_routes.py`
- [X] T017 [P] [US1] Add unauthenticated, tenant-denied publication, stale revision, and audit-persistence failure route tests in `tests/integration/test_admin_react_routes.py`
- [X] T018 [P] [US1] Add candidate creation, upload precedence, validation findings, publish readiness, grant preview, immutable version, quarantine, withdrawal, and safe audit unit tests in `tests/unit/admin/test_skill_lifecycle_service.py`
- [X] T019 [P] [US1] Add manifest summary, validation finding, publish readiness, and unsafe payload schema tests in `tests/unit/api/test_admin_skill_lifecycle_schema.py`
- [X] T020 [P] [US1] Add React skill page shell, platform wizard, manifest upload precedence, validation blocker, and publish action tests in `frontend/admin/src/components/skills/SkillLifecyclePage.test.tsx`
- [X] T021 [P] [US1] Add React package publication panel tests in `frontend/admin/src/components/skills/PackagePublicationPanel.test.tsx`

### Implementation for User Story 1

- [X] T022 [US1] Implement platform and tenant skill lifecycle bootstrap builders in `src/multi_agent_platform/admin/skill_lifecycle.py`
- [X] T023 [US1] Implement deterministic candidate creation, manifest summary, upload precedence, validation finding, publish readiness, grant preview, and platform-only tenant grant mutation builders in `src/multi_agent_platform/admin/skill_lifecycle.py`
- [X] T024 [US1] Implement immutable publication, quarantine, withdrawal, stale-conflict, and safe audit mutation result builders in `src/multi_agent_platform/admin/skill_lifecycle.py`
- [X] T025 [US1] Add `/admin/app/skills` and `/admin/app/skills/bootstrap.json` routes in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T026 [US1] Add candidate create, candidate validate, candidate publish, tenant grant mutation, package quarantine, and package withdrawal routes in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T027 [US1] Add frontend candidate, validation, publish, tenant grant, quarantine, and withdrawal request helpers in `frontend/admin/src/api/client.ts`
- [X] T028 [US1] Implement `SkillLifecyclePage` route shell in `frontend/admin/src/components/skills/SkillLifecyclePage.tsx`
- [X] T029 [US1] Implement `SkillLifecycleSectionNav` in `frontend/admin/src/components/skills/SkillLifecycleSectionNav.tsx`
- [X] T030 [US1] Implement `PackagePublicationPanel` with guided candidate and manifest controls in `frontend/admin/src/components/skills/PackagePublicationPanel.tsx`
- [X] T031 [US1] Implement `ValidationFindingsPanel` in `frontend/admin/src/components/skills/ValidationFindingsPanel.tsx`
- [X] T032 [US1] Implement `PackageLifecyclePanel` for immutable versions, platform grant form, grants, quarantine, and withdrawal evidence in `frontend/admin/src/components/skills/PackageLifecyclePanel.tsx`
- [X] T033 [US1] Route `/admin/app/skills` from `frontend/admin/src/App.tsx` and remove it from disabled fallback in `frontend/admin/src/routes.tsx`
- [X] T034 [US1] Add skill lifecycle shell, wizard, manifest, validation, publish, grant, quarantine, withdrawal, and safe evidence styles in `frontend/admin/src/styles/admin.css`

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Install And Configure Granted Skills (Priority: P2)

**Goal**: Tenant administrators can discover granted packages, install or
upgrade versions, configure authorized credential references, run explicit
smoke/readiness actions, and inspect first-party connector readiness safely.

**Independent Test**: Acme tenant admin opens discovery, sees granted packages
only, installs a package, configures authorized credential references, runs
mocked readiness checks, and verifies connector evidence is tenant-scoped and
redacted.

### Tests for User Story 2

- [X] T035 [P] [US2] Add local-principal tenant discovery, install, upgrade, credential configuration, smoke-test, connector readiness, and audit route tests in `tests/integration/test_admin_react_routes.py`
- [X] T036 [P] [US2] Add Auth0-shaped tenant discovery/install/configure authorization tests in `tests/integration/test_admin_react_routes.py`
- [X] T037 [P] [US2] Add cross-tenant package grant, unauthorized credential reference, connector degraded, and queued smoke-test denial tests in `tests/integration/test_admin_react_routes.py`
- [X] T038 [P] [US2] Add tenant discovery, installation, upgrade, credential reference picker, smoke-test queue, connector readiness, and stale conflict unit tests in `tests/unit/admin/test_skill_lifecycle_service.py`
- [X] T039 [P] [US2] Add credential option, connector readiness, smoke-test state, and unauthorized reference schema tests in `tests/unit/api/test_admin_skill_lifecycle_schema.py`
- [X] T040 [P] [US2] Add React tenant discovery, installation, credential picker, smoke-test, and connector readiness tests in `frontend/admin/src/components/skills/TenantSkillLifecyclePanel.test.tsx`
- [X] T041 [P] [US2] Add React credential and readiness panel tests in `frontend/admin/src/components/skills/CredentialReadinessPanel.test.tsx`

### Implementation for User Story 2

- [X] T042 [US2] Implement deterministic tenant discovery, grant visibility, package install eligibility, and version comparison builders in `src/multi_agent_platform/admin/skill_lifecycle.py`
- [X] T043 [US2] Implement tenant install, upgrade, idempotency, revision token, stale conflict, and safe mutation result builders in `src/multi_agent_platform/admin/skill_lifecycle.py`
- [X] T044 [US2] Implement authorized credential reference options, credential configuration results, and credential unavailable remediation in `src/multi_agent_platform/admin/skill_lifecycle.py`
- [X] T045 [US2] Implement explicit queued smoke-test/readiness refresh and calendar, Gmail, news, weather, and commute connector readiness builders in `src/multi_agent_platform/admin/skill_lifecycle.py`
- [X] T046 [US2] Add discovery, installation list, install/upgrade, credential configuration, and smoke-test routes in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T047 [US2] Add connector diagnostics and readiness refresh routes in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T048 [US2] Add frontend discovery, installation, credential, smoke-test, and connector readiness request helpers in `frontend/admin/src/api/client.ts`
- [X] T049 [US2] Implement `TenantSkillLifecyclePanel` for discovery, install, upgrade, and installation detail in `frontend/admin/src/components/skills/TenantSkillLifecyclePanel.tsx`
- [X] T050 [US2] Implement `CredentialReadinessPanel` with authorized reference picker in `frontend/admin/src/components/skills/CredentialReadinessPanel.tsx`
- [X] T051 [US2] Implement `ConnectorReadinessPanel` for calendar, Gmail, news, weather, and commute readiness in `frontend/admin/src/components/skills/ConnectorReadinessPanel.tsx`
- [X] T052 [US2] Implement `SmokeTestPanel` with explicit queued readiness controls in `frontend/admin/src/components/skills/SmokeTestPanel.tsx`
- [X] T053 [US2] Wire discovery, installation, credentials, smoke-test, and connector readiness panels into `frontend/admin/src/components/skills/SkillLifecyclePage.tsx`
- [X] T054 [US2] Add discovery, installation, credential, readiness, connector, queued action, and stale conflict styles in `frontend/admin/src/styles/admin.css`

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Preview Binding Eligibility And Tool Execution Readiness (Priority: P3)

**Goal**: Administrators can preview workflow/profile binding eligibility,
inspect SkillExecutionGateway diagnostics, and filter safe lifecycle audit
timeline evidence without invoking live tools or exposing raw outputs.

**Independent Test**: Tenant admin runs a deterministic binding eligibility
preview, reviews gateway diagnostics, filters audit timeline entries, and
verifies all evidence is bounded, tenant-scoped, and redacted.

### Tests for User Story 3

- [X] T055 [P] [US3] Add binding eligibility preview, SkillExecutionGateway diagnostic, and audit timeline route tests in `tests/integration/test_admin_react_routes.py`
- [X] T056 [P] [US3] Add Auth0-shaped eligibility, diagnostics, audit, and unapproved staging-probe denial tests in `tests/integration/test_admin_react_routes.py`
- [X] T057 [P] [US3] Add live-tool, live-credential, Telegram, model-provider, side-effectful connector, and cross-tenant denial tests in `tests/integration/test_admin_react_routes.py`
- [X] T058 [P] [US3] Add binding preview, gateway diagnostic, policy decision, side-effect posture, audit filter, and bounded-result unit tests in `tests/unit/admin/test_skill_lifecycle_service.py`
- [X] T059 [P] [US3] Add gateway diagnostic redaction, binding preview read-only, and audit safe diff schema tests in `tests/unit/api/test_admin_skill_lifecycle_schema.py`
- [X] T060 [P] [US3] Add bounded skill lifecycle query performance tests in `tests/performance/skills/test_skill_lifecycle_queries.py`
- [X] T061 [P] [US3] Add React binding preview and diagnostics tests in `frontend/admin/src/components/skills/BindingAndDiagnosticsPanel.test.tsx`
- [X] T062 [P] [US3] Add React audit timeline and redaction evidence tests in `frontend/admin/src/components/skills/SkillLifecycleAuditPanel.test.tsx`

### Implementation for User Story 3

- [X] T063 [US3] Implement read-only backend-owned binding context choices, eligibility decisions, missing requirements, and remediation builders in `src/multi_agent_platform/admin/skill_lifecycle.py`
- [X] T064 [US3] Implement safe SkillExecutionGateway diagnostic summaries, policy decisions, side-effect posture, outbound status, credential policy, attempt evidence references, and redaction summaries in `src/multi_agent_platform/admin/skill_lifecycle.py`
- [X] T065 [US3] Implement bounded lifecycle audit timeline filtering, safe diff summaries, authorized links, and unavailable audit states in `src/multi_agent_platform/admin/skill_lifecycle.py`
- [X] T066 [US3] Add eligibility preview, diagnostics, and audit timeline routes in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T067 [US3] Add frontend eligibility preview, diagnostics, and audit request helpers in `frontend/admin/src/api/client.ts`
- [X] T068 [US3] Implement `BindingAndDiagnosticsPanel` in `frontend/admin/src/components/skills/BindingAndDiagnosticsPanel.tsx`
- [X] T069 [US3] Implement `SkillLifecycleAuditPanel` in `frontend/admin/src/components/skills/SkillLifecycleAuditPanel.tsx`
- [X] T070 [US3] Wire binding preview, diagnostics, and audit timeline panels into `frontend/admin/src/components/skills/SkillLifecyclePage.tsx`
- [X] T071 [US3] Add binding preview, gateway diagnostics, audit timeline, filter, safe diff, and unavailable-state styles in `frontend/admin/src/styles/admin.css`

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation manifest reconciliation, QA evidence,
and final quality gates.

- [X] T072 [P] Update React skill lifecycle notes in `README.md`
- [X] T073 [P] Update local validation notes in `docs/quickstart.md`
- [X] T074 [P] Create implementation reviewer notes in `specs/032-react-skill-registry-and-tool-execution-lifecycle/pr_notes.md`
- [X] T075 Generate QA API/database guide in `specs/032-react-skill-registry-and-tool-execution-lifecycle/qa032.md`
- [X] T076 Generate QA UI walkthrough in `specs/032-react-skill-registry-and-tool-execution-lifecycle/qa032_ui.md`
- [X] T077 Generate QA environment file in `specs/032-react-skill-registry-and-tool-execution-lifecycle/.env.qa032`
- [X] T078 Generate detailed manual user guide in `specs/032-react-skill-registry-and-tool-execution-lifecycle/qa032_user_guide.md`
- [X] T079 Reconcile QA032 validation commands and Playwright skill lifecycle flows in `specs/_autopilot/react-ui-roadmap/032-react-skill-registry-and-tool-execution-lifecycle/validation.yml`
- [X] T080 Run frontend build/test commands and record outcomes in `specs/032-react-skill-registry-and-tool-execution-lifecycle/pr_notes.md`
- [X] T081 Run backend quality commands and record outcomes in `specs/032-react-skill-registry-and-tool-execution-lifecycle/pr_notes.md`
- [X] T082 Run QA docs, Spec QA, Playwright validation, screenshot redaction scan, and evidence paths in `specs/032-react-skill-registry-and-tool-execution-lifecycle/pr_notes.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup and blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational and provides the publication MVP.
- **User Story 2 (Phase 4)**: Depends on Foundational and integrates with US1 while remaining testable through tenant lifecycle endpoints.
- **User Story 3 (Phase 5)**: Depends on Foundational and integrates with US1/US2 while remaining testable through eligibility, diagnostics, and audit endpoints.
- **Polish (Phase 6)**: Depends on implemented stories.

### Parallel Opportunities

- T002-T005 can run in parallel after T001 is planned.
- T010-T013 can run in parallel after T006.
- T015-T021 can run in parallel after foundational contracts exist.
- T035-T041 can run in parallel after tenant lifecycle contracts exist.
- T055-T062 can run in parallel after diagnostics and audit contracts exist.
- T072-T074 can run in parallel with QA document drafting.

## Parallel Example: User Story 1

```bash
Task: "Add platform skill lifecycle route tests in tests/integration/test_admin_react_routes.py"
Task: "Add candidate publication unit tests in tests/unit/admin/test_skill_lifecycle_service.py"
Task: "Add manifest redaction schema tests in tests/unit/api/test_admin_skill_lifecycle_schema.py"
Task: "Add React package publication panel tests in frontend/admin/src/components/skills/PackagePublicationPanel.test.tsx"
```

## Implementation Strategy

1. Complete schemas, generated contracts, route protection, deterministic service builders, and client helpers.
2. Deliver User Story 1 as the MVP platform package publication route.
3. Add User Story 2 tenant discovery, installation, credentials, smoke tests, and connector readiness.
4. Add User Story 3 binding eligibility, gateway diagnostics, and audit timeline evidence.
5. Finish QA docs, validation manifest, screenshots, and full quality evidence.

## Notes

- Do not retire or weaken existing Jinja skill registry, installation, or skill execution diagnostic routes.
- Do not call live Auth0, Telegram, model providers, credential stores, external connectors, or direct connector SDKs in local or CI QA.
- Do not render raw secrets, resolved credentials, authorization headers, provider tokens, raw manifests, private messages, memory contents, connector payloads, raw tool outputs, local paths, stack traces, or unauthorized tenant labels.
- Stop if tenant scope, package grant boundaries, credential reference authorization, connector side effects, staging-probe approval, binding preview read-only behavior, audit persistence, or redaction becomes ambiguous.
