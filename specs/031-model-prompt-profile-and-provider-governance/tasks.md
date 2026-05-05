# Tasks: Model, Prompt, Profile, And Provider Governance

**Input**: Design documents from `specs/031-model-prompt-profile-and-provider-governance/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required. The feature specification mandates backend schema/service
coverage, contract and generated TypeScript drift checks, Auth0-shaped and
local-principal route coverage, tenant isolation, redaction tests, provider
secret safety tests, direct-call guardrail evidence, frontend component
coverage, Playwright evidence, QA docs, and full quality gates.

**Organization**: Tasks are grouped by user story so each story remains
independently testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and has no
  dependency on an incomplete task.
- **[Story]**: User story label from `spec.md`.
- Every task includes an exact file path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare backend, frontend, and test folders for React governance.

- [X] T001 Add backend governance schema module in `src/multi_agent_platform/api/schemas/admin_governance.py`
- [X] T002 [P] Add governance aggregation/service module in `src/multi_agent_platform/admin/governance.py`
- [X] T003 [P] Add React governance component directory in `frontend/admin/src/components/governance/`
- [X] T004 [P] Add React governance fixture file in `frontend/admin/src/test/governanceTestData.ts`
- [X] T005 [P] Add governance performance test directory in `tests/performance/governance/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define shared contracts, route protection, generated types, deterministic fixtures, and redaction guarantees.

**CRITICAL**: No user story implementation can proceed until these tasks are done.

- [X] T006 Extend `src/multi_agent_platform/api/schemas/admin_governance.py` with governance dashboard, section, provider, credential reference, probe diagnostic, prompt, preview, profile, resolution, routing, history, provenance, and mutation result models
- [X] T007 Add raw secret, resolved credential, authorization header, provider payload, raw prompt, raw completion, local path, stack trace, and unauthorized tenant label validators in `src/multi_agent_platform/api/schemas/admin_governance.py`
- [X] T008 Extend `scripts/frontend/generate_admin_react_types.py` to emit Spec 031 governance contracts and assertion helpers
- [X] T009 Regenerate `frontend/admin/src/api/generated/reactAdminApi.ts`
- [X] T010 Add Spec 031 OpenAPI and generated-contract drift checks in `tests/contract/test_admin_react_contract.py`
- [X] T011 Add governance schema redaction and validation tests in `tests/unit/api/test_admin_governance_schema.py`
- [X] T012 Add React client helpers for governance bootstrap, provider probe, credential reference, prompt preview, profile resolution, routing preview, history, and provenance requests in `frontend/admin/src/api/client.ts`
- [X] T013 Register protected React governance route/action surfaces in `src/multi_agent_platform/auth/policy.py`
- [X] T014 Add `/admin/app/governance` route constants, route wrapper, nav destination, and fallback links in `src/multi_agent_platform/api/routers/admin_react.py`

---

## Phase 3: User Story 1 - Govern Provider Setup And Health (Priority: P1) MVP

**Goal**: Platform admins can review and act on provider setup/health safely; tenant admins can only review authorized readiness.

**Independent Test**: Platform admin loads governance, inspects provider credential diagnostics, runs explicit mocked probe, and tenant admin is denied platform-only mutations while seeing authorized catalog readiness.

### Tests for User Story 1

- [X] T015 [P] [US1] Add local-principal platform governance bootstrap and provider route tests in `tests/integration/test_admin_react_routes.py`
- [X] T016 [P] [US1] Add local-principal tenant provider catalog visibility tests in `tests/integration/test_admin_react_routes.py`
- [X] T017 [P] [US1] Add Auth0-shaped governance bootstrap and provider mutation authorization tests in `tests/integration/test_admin_react_routes.py`
- [X] T018 [P] [US1] Add unauthenticated, denied, and cross-tenant governance route tests in `tests/integration/test_admin_react_routes.py`
- [X] T019 [P] [US1] Add provider summary, credential reference, probe diagnostic, local no-auth allowlist, and direct-call guardrail unit tests in `tests/unit/admin/test_governance_service.py`
- [X] T020 [P] [US1] Add provider secret safety and probe redaction schema tests in `tests/unit/api/test_admin_governance_schema.py`
- [X] T021 [P] [US1] Add React governance shell/setup tests in `frontend/admin/src/components/governance/GovernancePage.test.tsx`
- [X] T022 [P] [US1] Add React provider panel and explicit probe tests in `frontend/admin/src/components/governance/ProviderGovernancePanel.test.tsx`

### Implementation for User Story 1

- [X] T023 [US1] Implement platform and tenant governance bootstrap builders in `src/multi_agent_platform/admin/governance.py`
- [X] T024 [US1] Implement deterministic provider summaries, credential reference diagnostics, local no-auth allowlist status, and direct-call guardrail summaries in `src/multi_agent_platform/admin/governance.py`
- [X] T025 [US1] Implement explicit mocked provider probe mutation result builders in `src/multi_agent_platform/admin/governance.py`
- [X] T026 [US1] Add `/admin/app/governance` and `/admin/app/governance/bootstrap.json` routes in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T027 [US1] Add `/admin/app/governance/providers.json` route in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T028 [US1] Add `/admin/app/governance/providers/{provider_id}/probe` and credential-reference routes in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T029 [US1] Add frontend governance bootstrap and provider request helpers in `frontend/admin/src/api/client.ts`
- [X] T030 [US1] Implement `GovernancePage` section shell in `frontend/admin/src/components/governance/GovernancePage.tsx`
- [X] T031 [US1] Implement `GovernanceSectionNav` in `frontend/admin/src/components/governance/GovernanceSectionNav.tsx`
- [X] T032 [US1] Implement `ProviderGovernancePanel` in `frontend/admin/src/components/governance/ProviderGovernancePanel.tsx`
- [X] T033 [US1] Implement `CredentialDiagnosticsPanel` in `frontend/admin/src/components/governance/CredentialDiagnosticsPanel.tsx`
- [X] T034 [US1] Route `/admin/app/governance` from `frontend/admin/src/App.tsx` and remove it from disabled fallback in `frontend/admin/src/routes.tsx`
- [X] T035 [US1] Add governance setup, section navigation, provider, credential, probe, and safe diagnostic styles in `frontend/admin/src/styles/admin.css`

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Manage Prompts And Runtime Profiles Safely (Priority: P2)

**Goal**: Admins can review prompt/profile history, run safe prompt previews, and preview profile resolution without unsafe raw content.

**Independent Test**: Tenant admin opens prompt/profile fixtures, runs a safe prompt preview that blocks/summarizes unsafe text, and runs read-only profile resolution.

### Tests for User Story 2

- [X] T036 [P] [US2] Add prompt list/detail, safe draft save, and safe preview route tests in `tests/integration/test_admin_react_routes.py`
- [X] T037 [P] [US2] Add profile list/detail, safe profile save, and read-only resolution route tests in `tests/integration/test_admin_react_routes.py`
- [X] T038 [P] [US2] Add prompt grant and profile grant cross-tenant denial tests in `tests/integration/test_admin_react_routes.py`
- [X] T039 [P] [US2] Add prompt history, safe prompt save, safe preview, profile summary, safe profile save, and resolution unit tests in `tests/unit/admin/test_governance_service.py`
- [X] T040 [P] [US2] Add unsafe prompt/completion preview schema tests in `tests/unit/api/test_admin_governance_schema.py`
- [X] T041 [P] [US2] Add React prompt panel, safe draft save, and preview tests in `frontend/admin/src/components/governance/PromptGovernancePanel.test.tsx`
- [X] T042 [P] [US2] Add React profile panel, safe save, and resolver tests in `frontend/admin/src/components/governance/ProfileGovernancePanel.test.tsx`

### Implementation for User Story 2

- [X] T043 [US2] Implement deterministic prompt summaries, version history, render-test readiness, safe diff summaries, safe prompt save, and preview builders in `src/multi_agent_platform/admin/governance.py`
- [X] T044 [US2] Implement deterministic runtime profile summaries, binding summaries, grants, safe profile save, and profile resolution builders in `src/multi_agent_platform/admin/governance.py`
- [X] T045 [US2] Add `/admin/app/governance/prompts.json`, prompt save, and prompt preview routes in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T046 [US2] Add `/admin/app/governance/profiles.json`, profile save, and profile resolution routes in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T047 [US2] Add frontend prompt save, prompt preview, profile save, and profile resolution request helpers in `frontend/admin/src/api/client.ts`
- [X] T048 [US2] Implement `PromptGovernancePanel` with safe draft save controls in `frontend/admin/src/components/governance/PromptGovernancePanel.tsx`
- [X] T049 [US2] Implement `SafePromptPreviewPanel` in `frontend/admin/src/components/governance/SafePromptPreviewPanel.tsx`
- [X] T050 [US2] Implement `ProfileGovernancePanel` with safe profile save controls in `frontend/admin/src/components/governance/ProfileGovernancePanel.tsx`
- [X] T051 [US2] Implement `ProfileResolutionPanel` in `frontend/admin/src/components/governance/ProfileResolutionPanel.tsx`
- [X] T052 [US2] Wire prompt/profile panels into `frontend/admin/src/components/governance/GovernancePage.tsx`
- [X] T053 [US2] Add prompt history, safe preview, profile binding, grants, and resolver styles in `frontend/admin/src/styles/admin.css`

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Preview Routing, History, And Run Provenance (Priority: P3)

**Goal**: Admins can run read-only routing previews, review policy history, and inspect run provenance through safe evidence summaries.

**Independent Test**: Tenant admin runs deterministic routing preview, filters policy history, opens run provenance, and verifies ModelGateway-only/direct-call guardrail evidence without raw payloads.

### Tests for User Story 3

- [X] T054 [P] [US3] Add read-only routing preview route tests in `tests/integration/test_admin_react_routes.py`
- [X] T055 [P] [US3] Add policy history filtering and bounded-result route tests in `tests/integration/test_admin_react_routes.py`
- [X] T056 [P] [US3] Add run provenance route and cross-tenant denial tests in `tests/integration/test_admin_react_routes.py`
- [X] T057 [P] [US3] Add routing preview, policy history, provenance, and ModelGateway-only evidence unit tests in `tests/unit/admin/test_governance_service.py`
- [X] T058 [P] [US3] Add provenance payload redaction schema tests in `tests/unit/api/test_admin_governance_schema.py`
- [X] T059 [P] [US3] Add bounded governance query performance tests in `tests/performance/governance/test_governance_queries.py`
- [X] T060 [P] [US3] Add React routing preview tests in `frontend/admin/src/components/governance/RoutingPreviewPanel.test.tsx`
- [X] T061 [P] [US3] Add React policy history and provenance tests in `frontend/admin/src/components/governance/ProvenancePanel.test.tsx`

### Implementation for User Story 3

- [X] T062 [US3] Implement deterministic routing preview, direct-call guardrail evidence, and remediation builders in `src/multi_agent_platform/admin/governance.py`
- [X] T063 [US3] Implement bounded policy history and safe diff summary builders in `src/multi_agent_platform/admin/governance.py`
- [X] T064 [US3] Implement safe run provenance builders in `src/multi_agent_platform/admin/governance.py`
- [X] T065 [US3] Add `/admin/app/governance/routing/preview` route in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T066 [US3] Add `/admin/app/governance/history.json` and provenance routes in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T067 [US3] Add frontend routing, history, and provenance request helpers in `frontend/admin/src/api/client.ts`
- [X] T068 [US3] Implement `RoutingPreviewPanel` in `frontend/admin/src/components/governance/RoutingPreviewPanel.tsx`
- [X] T069 [US3] Implement `PolicyHistoryPanel` in `frontend/admin/src/components/governance/PolicyHistoryPanel.tsx`
- [X] T070 [US3] Implement `ProvenancePanel` in `frontend/admin/src/components/governance/ProvenancePanel.tsx`
- [X] T071 [US3] Wire routing/history/provenance panels into `frontend/admin/src/components/governance/GovernancePage.tsx`
- [X] T072 [US3] Add routing preview, policy history, provenance, safe evidence, and recovery styles in `frontend/admin/src/styles/admin.css`

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation manifest reconciliation, QA evidence, and final quality gates.

- [X] T073 [P] Update React governance notes in `README.md`
- [X] T074 [P] Update local validation notes in `docs/quickstart.md`
- [X] T075 [P] Create implementation reviewer notes in `specs/031-model-prompt-profile-and-provider-governance/pr_notes.md`
- [X] T076 Generate QA API/database guide in `specs/031-model-prompt-profile-and-provider-governance/qa031.md`
- [X] T077 Generate QA UI walkthrough in `specs/031-model-prompt-profile-and-provider-governance/qa031_ui.md`
- [X] T078 Generate QA environment file in `specs/031-model-prompt-profile-and-provider-governance/.env.qa031`
- [X] T079 Generate detailed manual user guide in `specs/031-model-prompt-profile-and-provider-governance/qa031_user_guide.md`
- [X] T080 Reconcile QA031 validation commands and Playwright governance flows in `specs/_autopilot/react-ui-roadmap/031-model-prompt-profile-and-provider-governance/validation.yml`
- [X] T081 Run frontend build/test commands and record outcomes in `specs/031-model-prompt-profile-and-provider-governance/pr_notes.md`
- [X] T082 Run backend quality commands and record outcomes in `specs/031-model-prompt-profile-and-provider-governance/pr_notes.md`
- [X] T083 Run QA docs, Spec QA, and Playwright validation commands and record evidence paths in `specs/031-model-prompt-profile-and-provider-governance/pr_notes.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup and blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational and provides the provider governance MVP.
- **User Story 2 (Phase 4)**: Depends on Foundational and integrates with US1 while remaining testable through prompt/profile endpoints.
- **User Story 3 (Phase 5)**: Depends on Foundational and integrates with US1/US2 while remaining testable through routing/history/provenance endpoints.
- **Polish (Phase 6)**: Depends on implemented stories.

### Parallel Opportunities

- T002-T005 can run in parallel after T001 is planned.
- T010-T013 can run in parallel after T006.
- T015-T022 can run in parallel after foundational contracts exist.
- T036-T042 can run in parallel after prompt/profile contracts exist.
- T054-T061 can run in parallel after routing/history/provenance contracts exist.
- T073-T075 can run in parallel with QA document drafting.

## Parallel Example: User Story 1

```bash
Task: "Add local-principal platform governance route tests in tests/integration/test_admin_react_routes.py"
Task: "Add provider summary and credential diagnostic unit tests in tests/unit/admin/test_governance_service.py"
Task: "Add provider secret safety tests in tests/unit/api/test_admin_governance_schema.py"
Task: "Add React provider panel tests in frontend/admin/src/components/governance/ProviderGovernancePanel.test.tsx"
```

## Implementation Strategy

1. Complete schemas, generated contracts, route protection, deterministic service builders, and client helpers.
2. Deliver User Story 1 as the MVP provider setup and health route.
3. Add User Story 2 prompt/profile governance and safe preview/resolution flows.
4. Add User Story 3 routing preview, policy history, and run provenance evidence.
5. Finish QA docs, validation manifest, screenshots, and full quality evidence.

## Notes

- Do not retire or weaken existing Jinja/model, prompt, profile, provider, or configuration routes.
- Do not call live providers, Telegram, credential stores, external connectors, or direct SDK clients in QA.
- Do not render raw secrets, resolved credentials, authorization headers, provider tokens, raw prompts, raw completions, private messages, memory, provider payloads, connector payloads, local paths, stack traces, or unauthorized tenant labels.
- Stop if tenant scope, provider mutation boundaries, credential resolution, prompt preview safety, routing preview side effects, direct-call guardrail evidence, audit persistence, or provenance redaction becomes ambiguous.
