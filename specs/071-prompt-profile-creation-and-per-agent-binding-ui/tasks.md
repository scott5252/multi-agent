# Tasks: Prompt Profile Creation And Per-Agent Binding UI

**Input**: Design artifacts from `specs/071-prompt-profile-creation-and-per-agent-binding-ui/`  
**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/prompt-profile-binding-ui.md`, `quickstart.md`

## Phase 1: Setup

- [x] T001 Update AGENTS.md latest Spec Kit plan pointer and verify `.specify/feature.json` references specs/071-prompt-profile-creation-and-per-agent-binding-ui
- [x] T002 [P] Review existing prompt/profile schemas and React workflow builder types in src/multi_agent_platform/api/schemas/prompts.py, src/multi_agent_platform/api/schemas/agent_profiles.py, src/multi_agent_platform/api/schemas/admin_workflow_builder.py, and frontend/admin/src/components/workflows/workflowDocumentEditor.ts
- [x] T003 [P] Review existing prompt/profile API routes and tenant authorization behavior in src/multi_agent_platform/api/routers/admin_prompts.py, src/multi_agent_platform/api/routers/admin_agent_profiles.py, and src/multi_agent_platform/auth/policy.py
- [x] T004 [P] Review existing governance and workflow React components in frontend/admin/src/components/governance and frontend/admin/src/components/workflows for reuse boundaries

## Phase 2: Foundational Contracts

- [x] T005 Add prompt/profile Pydantic schemas to generated React type export inputs in scripts/frontend/generate_admin_react_types.py
- [x] T006 Extend workflow builder lookup schemas with safe prompt/profile catalog contracts in src/multi_agent_platform/api/schemas/admin_workflow_builder.py
- [x] T007 Populate safe prompt/profile catalogs from existing repositories in src/multi_agent_platform/admin/workflow_builder.py
- [x] T008 Map prompt/profile validation findings to workflow builder sections in src/multi_agent_platform/admin/workflow_registry/validation.py and src/multi_agent_platform/admin/workflow_builder.py
- [x] T009 Add or update backend contract tests for generated prompt/profile contracts and workflow lookup catalogs in tests/contract/test_admin_react_contract.py and tests/contract/test_workflow_builder_contract.py
- [x] T010 Regenerate frontend TypeScript contracts in frontend/admin/src/api/generated/reactAdminApi.ts
- [x] T011 Add frontend API client helpers for prompt/profile create, draft save, validate, publish, activate, and catalog fetches in frontend/admin/src/api/client.ts

## Phase 3: User Story 1 - Create And Publish Agent Prompts (Priority: P1) MVP

**Goal**: Authorized admins can create/select prompts for workflow roles and publish prompt versions without leaking raw prompt content outside editor forms.

**Independent Test**: Create or select a prompt for a workflow role, edit variables and fixtures, validate, publish, bind, save, reload, and confirm only safe prompt references appear outside the prompt editor.

- [x] T012 [P] [US1] Add prompt binding helper tests for catalog normalization, redaction-safe summaries, and workflow reference creation in frontend/admin/src/components/workflows/workflowPromptProfileBinding.test.ts
- [x] T013 [P] [US1] Add backend prompt catalog, prompt stale conflict, idempotent replay, and role binding route tests in tests/integration/test_admin_react_routes.py
- [x] T014 [US1] Implement prompt/profile binding helper module in frontend/admin/src/components/workflows/workflowPromptProfileBinding.ts
- [x] T015 [US1] Add prompt creation, draft, variable, fixture, validation, publish, and selection controls in frontend/admin/src/components/workflows/WorkflowPromptProfileBinder.tsx
- [x] T016 [US1] Wire prompt controls into WorkflowBuilderPage state and save/revert flow in frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx
- [x] T017 [US1] Ensure raw prompt content is omitted from graph, JSON inspector, role summaries, mutation summaries, and test fixtures in frontend/admin/src/components/workflows and frontend/admin/src/test/workflowBuilderTestData.ts
- [x] T018 [US1] Add frontend tests for prompt create/select/publish/bind and raw prompt redaction boundaries in frontend/admin/src/components/workflows/WorkflowBuilderPage.test.tsx

## Phase 4: User Story 2 - Create And Activate Runtime Profiles (Priority: P2)

**Goal**: Authorized admins can create/select runtime profiles, bind published prompt versions, validate and activate profiles, and attach active profile references to workflow roles.

**Independent Test**: Starting from a role with a published prompt, create a runtime profile, bind prompt and routing hints, validate, activate, save, reload, and verify the role references the active profile version.

- [x] T019 [P] [US2] Add frontend helper tests for profile reference creation, readiness derivation, and stale profile blockers in frontend/admin/src/components/workflows/workflowPromptProfileBinding.test.ts
- [x] T020 [P] [US2] Add backend integration coverage for active/inactive profile references, profile stale conflict, idempotent replay, and cross-tenant denial in tests/integration/test_admin_react_routes.py
- [x] T021 [US2] Add profile creation, prompt reference binding, routing hint, validation, activation, and selection controls in frontend/admin/src/components/workflows/WorkflowPromptProfileBinder.tsx
- [x] T022 [US2] Add safe provider/model readiness and credential expectation fields without credential values in frontend/admin/src/components/workflows/WorkflowPromptProfileBinder.tsx
- [x] T023 [US2] Wire profile references into role `profile_reference_key` and workflow `prompt_profile_references` document state in frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx
- [x] T024 [US2] Add frontend tests for profile create/select/activate/bind and reload persistence in frontend/admin/src/components/workflows/WorkflowBuilderPage.test.tsx

## Phase 5: User Story 3 - Manage Per-Agent Bindings Across The Workflow (Priority: P3)

**Goal**: Authorized admins can scan all workflow roles, see prompt/profile readiness, reuse authorized catalog records, detect incomplete/stale bindings, and save consistent role references.

**Independent Test**: Bind distinct prompt/profile references to three roles, intentionally leave one incomplete, save, validate, reload, and verify the binding matrix and validation panel agree.

- [x] T025 [P] [US3] Add binding matrix UI tests for complete, incomplete, stale, denied, and blocked role states in frontend/admin/src/components/workflows/WorkflowBuilderPage.test.tsx
- [x] T026 [P] [US3] Add unit coverage for prompt/profile reference validation mapping in tests/unit/admin/test_workflow_builder_service.py and tests/unit/admin/test_workflow_registry_service.py
- [x] T027 [US3] Render per-agent binding matrix, role readiness badges, and section anchors in frontend/admin/src/components/workflows/WorkflowPromptProfileBinder.tsx
- [x] T028 [US3] Add validation-panel anchors and recovery labels for prompt/profile binding findings in frontend/admin/src/components/workflows/WorkflowValidationPanel.tsx
- [x] T029 [US3] Update graph/list summaries to show safe prompt/profile readiness counts without raw prompt content in frontend/admin/src/components/workflows/WorkflowGraphPanel.tsx
- [x] T030 [US3] Update WorkflowRoleEditor to link role prompt/profile reference keys to the binding section while preserving manual fallback fields in frontend/admin/src/components/workflows/WorkflowRoleEditor.tsx

## Phase 6: Security, Tenancy, And Redaction

- [x] T031 [P] Add backend tests proving unauthorized prompt/profile catalogs and cross-tenant references fail safely in tests/integration/test_admin_react_routes.py
- [x] T032 [P] Add frontend tests proving raw prompt text is absent from summaries, graph panels, JSON inspector, and screenshots fixtures in frontend/admin/src/components/workflows/WorkflowBuilderPage.test.tsx
- [x] T033 Ensure workflow builder service and validation never echo raw prompt templates, provider payloads, credential values, or unauthorized labels in src/multi_agent_platform/admin/workflow_builder.py and src/multi_agent_platform/admin/workflow_registry/validation.py
- [x] T034 Ensure prompt/profile client errors render safe problem details and no stack traces in frontend/admin/src/api/client.ts and frontend/admin/src/components/workflows/WorkflowPromptProfileBinder.tsx
- [x] T035 Add deterministic QA seed data with clean-tenant roles, prompt/profile lineages, published versions, active profiles, and blocked references in scripts/qa/seed_workflow_prompt_profile_qa071.py

## Phase 7: Documentation And QA Artifacts

- [x] T036 Add Spec 071 QA guide with deterministic setup, negative paths, redaction checks, and automated evidence in specs/071-prompt-profile-creation-and-per-agent-binding-ui/qa071.md
- [x] T037 Add Spec 071 browser-first UI walkthrough in specs/071-prompt-profile-creation-and-per-agent-binding-ui/qa071_ui.md
- [x] T038 Add Spec 071 manual user guide in specs/071-prompt-profile-creation-and-per-agent-binding-ui/qa071_user_guide.md
- [x] T039 Add Spec 071 QA environment file in specs/071-prompt-profile-creation-and-per-agent-binding-ui/.env.qa071
- [x] T040 Add Spec 071 PR/reviewer notes and README.md/docs/quickstart.md impact review in specs/071-prompt-profile-creation-and-per-agent-binding-ui/pr_notes.md
- [x] T041 Update validation manifest with QA seed and desktop/mobile prompt/profile binding journeys in specs/_autopilot/workflow-setup-roadmap/071-prompt-profile-creation-and-per-agent-binding-ui/validation.yml
- [x] T042 Review curl_testing.md and update route coverage if prompt/profile or workflow setup route families changed
- [x] T043 Update specs/_autopilot/workflow-setup-roadmap/071-prompt-profile-creation-and-per-agent-binding-ui/status.json with implementation artifact summary and curl coverage decision

## Phase 8: Validation

- [x] T044 Run focused backend tests for workflow builder, prompt/profile contracts, validation mapping, and tenant denial
- [x] T045 Run focused frontend workflow tests and frontend typecheck
- [x] T046 Run uv run python scripts/frontend/generate_admin_react_types.py --check
- [x] T047 Run uv run ruff check .
- [x] T048 Run uv run ruff format --check .
- [x] T049 Run uv run mypy src
- [x] T050 Run cd frontend/admin && npm run build
- [x] T051 Run bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/071-prompt-profile-creation-and-per-agent-binding-ui
- [x] T052 Run uv run python scripts/qa/run_spec_qa.py specs/_autopilot/workflow-setup-roadmap/071-prompt-profile-creation-and-per-agent-binding-ui/validation.yml
- [x] T053 Run uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/workflow-setup-roadmap/071-prompt-profile-creation-and-per-agent-binding-ui/validation.yml --start-processes
- [x] T054 Run uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa071-after-spec
- [x] T055 Update specs/_autopilot/workflow-setup-roadmap/071-prompt-profile-creation-and-per-agent-binding-ui/status.json and specs/_autopilot/workflow-setup-roadmap/queue.json after all validation passes

## Dependencies

- Phase 1 must complete before implementation edits.
- Phase 2 contract work blocks frontend API helpers and generated types.
- User Story 1 prompt binding is the MVP and blocks profile activation binding.
- User Story 2 builds on published prompt references from User Story 1.
- User Story 3 builds on the prompt/profile binding state from User Stories 1 and 2.
- Security/redaction tasks must complete before QA screenshots and docs.
- Validation must run only after QA docs, validation manifest, and seed data are complete.

## Parallel Execution Examples

- T002, T003, and T004 can run in parallel during setup.
- T012 and T013 can run in parallel before US1 implementation.
- T019 and T020 can run in parallel before US2 implementation.
- T025 and T026 can run in parallel before US3 implementation.
- T036, T037, T038, T039, and T040 can be drafted in parallel once implementation behavior is stable.

## Implementation Strategy

1. Deliver generated contracts and safe backend prompt/profile catalogs first.
2. Deliver prompt create/select/publish and role binding as the MVP.
3. Add profile create/select/activate and active profile role binding.
4. Add matrix readiness, validation recovery, and safe summaries across graph/role surfaces.
5. Finish docs, Playwright, curl coverage review, and full validation before Spec 072.
