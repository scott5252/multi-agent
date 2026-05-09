# Tasks: End-To-End Custom Workflow Setup Wizard And Runtime Launch

**Input**: Design artifacts from `specs/073-end-to-end-custom-workflow-setup-wizard-and-runtime-launch/`  
**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/workflow-setup-wizard-runtime-launch.md`, `quickstart.md`

## Phase 1: Setup

- [x] T001 Update AGENTS.md latest Spec Kit plan pointer and `.specify/feature.json` to specs/073-end-to-end-custom-workflow-setup-wizard-and-runtime-launch
- [x] T002 [P] Review Specs 069-072 workflow builder, prompt/profile, evidence, validation, publish, runtime, and Design Reviews surfaces
- [x] T003 [P] Review current WorkflowBuilderPage, UserRunPage, DesignReviewWorkspacePage, and Admin shell route behavior

## Phase 2: Checklist And Starter Foundations

- [x] T004 Add setup progress and three-agent starter helper in frontend/admin/src/components/workflows/workflowSetupWizard.ts
- [x] T005 Add helper tests in frontend/admin/src/components/workflows/workflowSetupWizard.test.ts
- [x] T006 Add guided setup panel component in frontend/admin/src/components/workflows/WorkflowSetupWizardPanel.tsx
- [x] T007 Add responsive setup panel styles in frontend/admin/src/styles/admin.css

## Phase 3: Workflow Builder Integration

- [x] T008 Wire setup panel into frontend/admin/src/components/workflows/WorkflowBuilderPage.tsx
- [x] T009 Add visible starter application to mutate editable document state without raw JSON editing
- [x] T010 Refresh durable builder state after successful publish so published graph and launch links become available
- [x] T011 Extend WorkflowBuilderPage tests for checklist and starter save payloads

## Phase 4: Runtime And Design Review Handoff

- [x] T012 Add workflow id query prefill in frontend/admin/src/components/userRuns/UserRunPage.tsx
- [x] T013 Add runtime prefill test in frontend/admin/src/components/userRuns/UserRunPage.test.tsx
- [x] T014 Add requested workflow bundle selection in frontend/admin/src/components/designReviews/DesignReviewWorkspacePage.tsx
- [x] T015 Add Design Reviews selection test in frontend/admin/src/components/designReviews/DesignReviewWorkspacePage.test.tsx

## Phase 5: Documentation And QA Artifacts

- [x] T016 Add Spec 073 QA guide in specs/073-end-to-end-custom-workflow-setup-wizard-and-runtime-launch/qa073.md
- [x] T017 Add Spec 073 browser-first walkthrough in specs/073-end-to-end-custom-workflow-setup-wizard-and-runtime-launch/qa073_ui.md
- [x] T018 Add Spec 073 manual user guide in specs/073-end-to-end-custom-workflow-setup-wizard-and-runtime-launch/qa073_user_guide.md
- [x] T019 Add Spec 073 QA environment in specs/073-end-to-end-custom-workflow-setup-wizard-and-runtime-launch/.env.qa073
- [x] T020 Add Spec 073 PR/reviewer notes in specs/073-end-to-end-custom-workflow-setup-wizard-and-runtime-launch/pr_notes.md
- [x] T021 Update validation manifest with desktop/mobile setup, publish, runtime, and Design Reviews journeys
- [x] T022 Record curl_testing.md coverage decision: no route family changed

## Phase 6: Validation

- [x] T023 Run focused frontend tests for workflow setup, WorkflowBuilderPage, UserRunPage, and DesignReviewWorkspacePage
- [x] T024 Run frontend typecheck
- [x] T025 Run generated React type freshness check
- [x] T026 Run Ruff check
- [x] T027 Run Ruff format check
- [x] T028 Run mypy src
- [x] T029 Run frontend build
- [x] T030 Run QA document validation
- [x] T031 Run Spec QA manifest
- [x] T032 Run Playwright UI validation
- [x] T033 Run multi-agent-curl-test for QA073
- [x] T034 Update status.json and queue.json after validation passes

## Dependencies

- T004-T007 must land before WorkflowBuilderPage integration.
- T008-T011 must land before Playwright setup journey.
- T012-T015 must land before runtime and Design Review handoff validation.
- T016-T022 must land before QA docs and manifest validation.
- T023-T034 must run after implementation and docs are complete.

## Parallel Execution Examples

- T002 and T003 can run in parallel.
- T005, T011, T013, and T015 can run as independent focused frontend tests.
- T016 through T020 can be drafted while implementation tests run.

## Implementation Strategy

1. Keep the checklist purely derived and truthful.
2. Use existing durable mutation APIs for all persistence.
3. Add a visible starter to reduce clean-tenant setup friction.
4. Use query handoff only as a prefill/selection hint.
5. Validate with browser-first QA and repository regressions.
