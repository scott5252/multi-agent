# Tasks: Publish, Launch, And Operational Verification Finish

**Input**: Design artifacts from `specs/078-publish-launch-and-operational-verification-finish/`  
**Prerequisites**: spec.md, plan.md, research.md, data-model.md, contracts/wizard-onboarding-contracts.md, quickstart.md

## Phase 1: Setup

- [x] T001 Review docs/wizard_ui.md Spec 078 prompts and constraints
- [x] T002 Review existing Console Home, workflow builder, lookups, validation, publish, Test Bench, runtime, operations, and graph surfaces relevant to this slice
- [x] T003 Confirm no new backend route family or migration is required

## Phase 2: Implementation

- [x] T004 Implement validation, publish blockers, publish confirmation, published bundle refresh, launch target links, runtime launch prefill, Design Reviews handoff, and operations or graph evidence links
- [x] T005 Reuse workflow validate action, publish action, publish readiness, user runs workspace, Design Reviews selector, operations workbench, and graph evidence routes
- [x] T006 Preserve tenant scope and backend-owned authorization/readiness boundaries
- [x] T007 Keep all screens fixed-frame and bounded for 1280 x 800
- [x] T008 Add or update styles without nested card-heavy layouts or overlapping text

## Phase 3: Tests

- [x] T009 Add or update focused tests: publish and validation component tests, handoff link tests, generated contract freshness, typecheck, build, and blocked plus happy path Playwright finish flows
- [x] T010 Add redaction and tutorial-label assertions where the slice generates or renders scenario text
- [x] T011 Add backend envelope or route assertions when admin JSON changed
- [x] T012 Run focused frontend tests for the wizard route and helpers
- [x] T013 Run frontend typecheck and build
- [x] T014 Run generated React type freshness check

## Phase 4: QA Artifacts

- [x] T015 Add QA guide specs/078-publish-launch-and-operational-verification-finish/qa078.md
- [x] T016 Add UI walkthrough specs/078-publish-launch-and-operational-verification-finish/qa078_ui.md
- [x] T017 Add QA environment specs/078-publish-launch-and-operational-verification-finish/.env.qa078
- [x] T018 Add manual user guide specs/078-publish-launch-and-operational-verification-finish/qa078_user_guide.md
- [x] T019 Add reviewer notes specs/078-publish-launch-and-operational-verification-finish/pr_notes.md
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
