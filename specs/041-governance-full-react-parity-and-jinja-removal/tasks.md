# Tasks: Governance Full React Parity And Jinja Removal

**Input**: Design artifacts from `specs/041-governance-full-react-parity-and-jinja-removal/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`

## Phase 1: Setup

- [X] T001 Verify `.specify/feature.json` points to `specs/041-governance-full-react-parity-and-jinja-removal`
- [X] T002 [P] Review governance inventory items in `specs/038-jinja-surface-inventory-and-deletion-plan/jinja_inventory.json`
- [X] T003 [P] Confirm current governance TemplateResponse routes in `src/multi_agent_platform/api/routers/admin_model_providers.py`, `src/multi_agent_platform/api/routers/admin_prompts.py`, `src/multi_agent_platform/api/routers/admin_agent_profiles.py`, and `src/multi_agent_platform/api/routers/admin_model_skill_config.py`
- [X] T004 [P] Review existing React governance contracts and components in `src/multi_agent_platform/api/schemas/admin_governance.py`, `src/multi_agent_platform/admin/governance.py`, and `frontend/admin/src/components/governance/`

## Phase 2: Tests First

- [X] T005 [P] [US1] Extend React governance contract tests for provider list/create/edit/detail/catalog/test-results/probe/credential diagnostics in `tests/contract/test_admin_react_contract.py`
- [X] T006 [P] [US1] Add provider legacy redirect and non-Jinja route tests in `tests/integration/api/test_admin_governance_legacy_redirects.py`
- [X] T007 [P] [US1] Add provider platform-admin and tenant-admin Auth0-shaped route coverage in `tests/integration/test_admin_react_routes.py`
- [X] T008 [P] [US1] Extend provider frontend tests for create/edit/detail/catalog/test-results/probe/credential diagnostics in `frontend/admin/src/components/governance/ProviderGovernancePanel.test.tsx`
- [X] T009 [P] [US2] Extend prompt/profile contract tests for create/edit/history/detail/preview/resolve envelopes in `tests/contract/test_admin_react_contract.py`
- [X] T010 [P] [US2] Add prompt and profile legacy redirect tests in `tests/integration/api/test_admin_governance_legacy_redirects.py`
- [X] T011 [P] [US2] Extend prompt/profile frontend tests for edit/history/preview/resolve states in `frontend/admin/src/components/governance/PromptGovernancePanel.test.tsx` and `frontend/admin/src/components/governance/ProfileGovernancePanel.test.tsx`
- [X] T012 [P] [US2] Add prompt/profile redaction tests for unsafe preview and cross-tenant denied states in `tests/unit/api/test_admin_governance_redaction.py`
- [X] T013 [P] [US3] Extend routing/history/provenance contract tests in `tests/contract/test_admin_react_contract.py`
- [X] T014 [P] [US3] Add model-skill config legacy redirect tests in `tests/integration/api/test_admin_governance_legacy_redirects.py`
- [X] T015 [P] [US3] Extend routing/provenance frontend tests in `frontend/admin/src/components/governance/RoutingPreviewPanel.test.tsx` and `frontend/admin/src/components/governance/ProvenancePanel.test.tsx`
- [X] T016 [P] [US3] Add governance template/static scanner tests for deletion and retention evidence in `tests/unit/admin/test_governance_jinja_retirement.py`

## Phase 3: User Story 1 - Govern Providers Through React Only (Priority: P1)

**Goal**: Provider list/create/edit/detail/catalog/test-results/probe/credential browser journeys are React-backed and backend-authorized.

**Independent Test**: Run T005-T008 plus focused provider legacy redirect tests and verify platform-admin and tenant-admin provider governance behavior without Jinja rendering.

- [X] T017 [US1] Add provider detail/create/edit/test-results/legacy mapping schemas in `src/multi_agent_platform/api/schemas/admin_governance.py`
- [X] T018 [US1] Extend provider governance builders for create/edit/detail/catalog/test-results/probe/credential diagnostics in `src/multi_agent_platform/admin/governance.py`
- [X] T019 [US1] Add React provider detail/create/edit/test-results JSON routes and legacy mapping route in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T020 [US1] Add generated TypeScript provider governance contracts via `scripts/frontend/generate_admin_react_types.py` and `frontend/admin/src/api/generated/reactAdminApi.ts`
- [X] T021 [US1] Extend governance client helpers for provider detail/create/edit/test-results in `frontend/admin/src/api/client.ts`
- [X] T022 [US1] Extend provider React surface for create/edit/detail/catalog/test-results states in `frontend/admin/src/components/governance/ProviderGovernancePanel.tsx`
- [X] T023 [US1] Ensure provider credential diagnostics and direct-call guardrail summaries remain safe in `frontend/admin/src/components/governance/CredentialDiagnosticsPanel.tsx`
- [X] T024 [US1] Convert old model provider browser routes to React redirects or non-Jinja safe problems in `src/multi_agent_platform/api/routers/admin_model_providers.py`
- [X] T025 [US1] Update shell navigation/search provider destinations to React governance routes in `src/multi_agent_platform/api/ui/admin_console.py`

## Phase 4: User Story 2 - Manage Prompts And Profiles Through React Only (Priority: P2)

**Goal**: Prompt and profile list/detail/create/edit/history/preview/resolve browser journeys are React-backed and redaction-safe.

**Independent Test**: Run T009-T012 and old prompt/profile direct links with authorized, unauthorized, and cross-tenant principals.

- [X] T026 [US2] Add prompt create/edit/detail/history/preview and profile create/edit/detail/history/resolve schemas in `src/multi_agent_platform/api/schemas/admin_governance.py`
- [X] T027 [US2] Extend prompt/profile governance builders for direct-link, edit, history, preview, and resolve states in `src/multi_agent_platform/admin/governance.py`
- [X] T028 [US2] Add React prompt/profile child JSON routes in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T029 [US2] Add generated TypeScript prompt/profile governance contracts via `scripts/frontend/generate_admin_react_types.py` and `frontend/admin/src/api/generated/reactAdminApi.ts`
- [X] T030 [US2] Extend governance client helpers for prompt/profile detail, save, preview, and resolve in `frontend/admin/src/api/client.ts`
- [X] T031 [US2] Extend prompt React surface for create/edit/detail/history/preview states in `frontend/admin/src/components/governance/PromptGovernancePanel.tsx` and `frontend/admin/src/components/governance/SafePromptPreviewPanel.tsx`
- [X] T032 [US2] Extend profile React surface for create/edit/detail/history/resolve states in `frontend/admin/src/components/governance/ProfileGovernancePanel.tsx` and `frontend/admin/src/components/governance/ProfileResolutionPanel.tsx`
- [X] T033 [US2] Convert old prompt browser routes to React redirects or non-Jinja safe problems in `src/multi_agent_platform/api/routers/admin_prompts.py`
- [X] T034 [US2] Convert old agent profile browser routes to React redirects or non-Jinja safe problems in `src/multi_agent_platform/api/routers/admin_agent_profiles.py`

## Phase 5: User Story 3 - Review Routing, Policy, Model-Skill Config, And Provenance Through React Only (Priority: P3)

**Goal**: Model-skill config, routing preview, policy history, and run provenance browser journeys are React-backed and side-effect safe.

**Independent Test**: Run T013-T016 and old model-skill config routes with representative tenant/query/run state.

- [X] T035 [US3] Add model-skill config history, routing preview, policy history, provenance, and legacy mapping schemas in `src/multi_agent_platform/api/schemas/admin_governance.py`
- [X] T036 [US3] Extend governance builders for model-skill config history, routing preview, policy history, provenance, and direct-call guardrail evidence in `src/multi_agent_platform/admin/governance.py`
- [X] T037 [US3] Add React routing/history/provenance child JSON routes and legacy mapping route in `src/multi_agent_platform/api/routers/admin_react.py`
- [X] T038 [US3] Extend React governance routing/history/provenance components in `frontend/admin/src/components/governance/RoutingPreviewPanel.tsx`, `frontend/admin/src/components/governance/PolicyHistoryPanel.tsx`, and `frontend/admin/src/components/governance/ProvenancePanel.tsx`
- [X] T039 [US3] Convert old model-skill config browser routes to React redirects or non-Jinja safe problems in `src/multi_agent_platform/api/routers/admin_model_skill_config.py`
- [X] T040 [US3] Update governance direct-link guidance from old URLs to React or compatibility paths in `docs/quickstart.md` and `specs/041-governance-full-react-parity-and-jinja-removal/quickstart.md`
- [X] T041 [US3] Convert legacy governance provider/prompt/profile/model-skill form posts to JSON or redirect compatibility handlers in `src/multi_agent_platform/api/routers/admin_model_providers.py`, `src/multi_agent_platform/api/routers/admin_prompts.py`, `src/multi_agent_platform/api/routers/admin_agent_profiles.py`, and `src/multi_agent_platform/api/routers/admin_model_skill_config.py`
- [X] T042 [US3] Update governance React parity and Jinja removal documentation impact in `README.md` and `docs/quickstart.md`

## Phase 6: Governance-Owned Jinja Retirement

- [X] T043 Delete provider templates proven obsolete in `src/multi_agent_platform/web_admin/templates/model_providers/index.html`, `src/multi_agent_platform/web_admin/templates/model_providers/detail.html`, `src/multi_agent_platform/web_admin/templates/model_providers/edit.html`, `src/multi_agent_platform/web_admin/templates/model_providers/catalog.html`, and `src/multi_agent_platform/web_admin/templates/model_providers/test_results.html`
- [X] T044 Delete prompt templates proven obsolete in `src/multi_agent_platform/web_admin/templates/prompts/index.html`, `src/multi_agent_platform/web_admin/templates/prompts/detail.html`, `src/multi_agent_platform/web_admin/templates/prompts/edit.html`, `src/multi_agent_platform/web_admin/templates/prompts/history.html`, and `src/multi_agent_platform/web_admin/templates/prompts/preview.html`
- [X] T045 Delete agent profile templates proven obsolete in `src/multi_agent_platform/web_admin/templates/agent_profiles/index.html`, `src/multi_agent_platform/web_admin/templates/agent_profiles/detail.html`, `src/multi_agent_platform/web_admin/templates/agent_profiles/edit.html`, `src/multi_agent_platform/web_admin/templates/agent_profiles/history.html`, and `src/multi_agent_platform/web_admin/templates/agent_profiles/resolve.html`
- [X] T046 Delete model-skill config templates proven obsolete in `src/multi_agent_platform/web_admin/templates/model_skill_config/index.html`, `src/multi_agent_platform/web_admin/templates/model_skill_config/history.html`, and `src/multi_agent_platform/web_admin/templates/model_skill_config/run_provenance.html`
- [X] T047 Remove or retain with blocker evidence obsolete governance template view-model helpers in `src/multi_agent_platform/api/ui/model_providers.py`, `src/multi_agent_platform/api/ui/prompts.py`, `src/multi_agent_platform/api/ui/agent_profiles.py`, and `src/multi_agent_platform/api/ui/model_skill_config.py`
- [X] T048 Update governance Jinja inventory outcomes, retained blockers, and rollback notes in `specs/041-governance-full-react-parity-and-jinja-removal/pr_notes.md`

## Phase 7: Polish And Validation

- [X] T049 [P] Create QA guide in `specs/041-governance-full-react-parity-and-jinja-removal/qa041.md`
- [X] T050 [P] Create UI walkthrough in `specs/041-governance-full-react-parity-and-jinja-removal/qa041_ui.md`
- [X] T051 [P] Create QA environment file in `specs/041-governance-full-react-parity-and-jinja-removal/.env.qa041`
- [X] T052 [P] Create user guide in `specs/041-governance-full-react-parity-and-jinja-removal/qa041_user_guide.md`
- [X] T053 Update Spec 041 Playwright login and route steps in `specs/_autopilot/react-ui2-roadmap/041-governance-full-react-parity-and-jinja-removal/validation.yml`
- [X] T054 Run `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/041-governance-full-react-parity-and-jinja-removal`
- [X] T055 Run targeted backend tests for governance React parity, legacy redirects, no-Jinja routes, redaction, and scanner coverage
- [X] T056 Run `cd frontend/admin && npm test -- --run src/components/governance`
- [X] T057 Run `cd frontend/admin && npm run build`
- [X] T058 Run `uv run ruff check .`, `uv run ruff format --check .`, and `uv run mypy src`
- [X] T059 Run `uv run python scripts/frontend/generate_admin_react_types.py --check`
- [X] T060 Run Spec 041 validation and Playwright through `scripts/qa/run_spec_qa.py` and `scripts/qa/run_playwright_ui.py`

## Dependencies

- Setup T001-T004 must complete before tests and implementation.
- Tests T005-T016 should be added before corresponding implementation tasks.
- US1 T017-T025 establishes provider React parity and must complete before provider template deletion T041.
- US2 T026-T034 establishes prompt/profile React parity and must complete before prompt/profile template deletion T042-T043.
- US3 T035-T042 establishes routing/history/provenance parity, legacy form compatibility, and docs impact before model-skill config template deletion T046.
- Jinja retirement T043-T048 depends on passing route/scanner tests from US1-US3.
- Validation T054-T060 depends on QA artifacts T049-T053 and reviewer notes T048.

## Parallel Execution Examples

- T002, T003, and T004 can run in parallel because they inspect distinct source areas.
- T005-T016 can be drafted in parallel because each targets a distinct test or component file.
- T022-T023 can proceed after T017-T021 define provider contract shape.
- T031-T032 can proceed after T026-T030 define prompt/profile contract shape.
- T049-T052 can be prepared in parallel after implementation behavior stabilizes.

## Implementation Strategy

1. Establish tests and backend contract extensions for provider governance parity.
2. Make provider browser routes React-backed, then convert old provider browser URLs.
3. Establish prompt/profile React parity and convert old prompt/profile browser URLs.
4. Establish model-skill config, routing, history, and provenance React parity and convert old routes.
5. Delete only governance-owned templates and helpers proven unused by route tests and scanner evidence.
6. Finish QA docs, Spec QA, Playwright, and queue/status reconciliation before advancing to Spec 042.
