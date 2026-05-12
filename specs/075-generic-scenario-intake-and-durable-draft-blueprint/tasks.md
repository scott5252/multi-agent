# Tasks: Generic Scenario Intake And Durable Draft Blueprint

**Input**: Design artifacts from `specs/075-generic-scenario-intake-and-durable-draft-blueprint/`  
**Prerequisites**: spec.md, plan.md, research.md, data-model.md, contracts/wizard-onboarding-contracts.md, quickstart.md

## Phase 1: Setup

- [x] T001 Review docs/wizard_ui.md Spec 075 prompts and constraints
- [x] T002 Review existing Console Home, workflow builder, lookups, validation, publish, Test Bench, runtime, operations, and graph surfaces relevant to this slice
- [x] T003 Confirm no new backend route family or migration is required

## Phase 2: Implementation

- [x] T004 Implement scenario-neutral intake, workflow key normalization, generic editable blueprint generation, durable draft creation, revision-safe saves, and tutorial label guardrails
- [x] T005 Reuse existing workflow draft create action, full document save action, validation refresh, and generated React API contracts
- [x] T006 Preserve tenant scope and backend-owned authorization/readiness boundaries
- [x] T007 Keep all screens fixed-frame and bounded for 1280 x 800
- [x] T008 Add or update styles without nested card-heavy layouts or overlapping text

## Phase 3: Tests

- [x] T009 Add or update focused tests: workflowSetupWizard helper tests, arbitrary scenario component tests, tutorial label absence tests, typecheck, build, and clean tenant Playwright intake journey
- [x] T010 Add redaction and tutorial-label assertions where the slice generates or renders scenario text
- [x] T011 Add backend envelope or route assertions when admin JSON changed
- [x] T012 Run focused frontend tests for the wizard route and helpers
- [x] T013 Run frontend typecheck and build
- [x] T014 Run generated React type freshness check

## Phase 4: QA Artifacts

- [x] T015 Add QA guide specs/075-generic-scenario-intake-and-durable-draft-blueprint/qa075.md
- [x] T016 Add UI walkthrough specs/075-generic-scenario-intake-and-durable-draft-blueprint/qa075_ui.md
- [x] T017 Add QA environment specs/075-generic-scenario-intake-and-durable-draft-blueprint/.env.qa075
- [x] T018 Add manual user guide specs/075-generic-scenario-intake-and-durable-draft-blueprint/qa075_user_guide.md
- [x] T019 Add reviewer notes specs/075-generic-scenario-intake-and-durable-draft-blueprint/pr_notes.md
- [x] T020 Update validation manifest with real onboarding route and visible UI expectations
- [x] T021 Update curl_testing.md for the Console Home quick action and wizard SPA route smoke coverage

## Phase 5: Validation

- [x] T022 Run QA document validation
- [x] T023 Run focused Spec QA or dry-run validation where full quality gates are deferred to final roadmap gate
- [x] T024 Run Playwright UI validation or record blocker evidence for final gate repair
- [x] T025 Update per-spec status.json and queue.json phase state

## Dependencies

- T004 through T008 depend on setup review.
- T009 through T014 depend on implementation.
- T015 through T021 depend on final route and behavior decisions.
- T022 through T025 depend on QA artifacts and manifests.

## Parallel Execution Examples

- T002 and T003 can run in parallel.
- T009, T010, and T011 can run while docs are drafted.
- QA document validation can run independently once docs exist.
