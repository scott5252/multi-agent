# Tasks: Design Reviewer Template, Test Bench, And Publish Gates

**Input**: Design documents from `specs/064-design-reviewer-template-test-bench-and-publish-gates/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required. This feature touches workflow templates, publish gates,
Agent Test Bench evidence, admin authorization, tenant scope, React Admin,
QA docs, Playwright, and curl coverage.

## Phase 1: Setup

- [x] T001 Create Spec 064 feature artifacts and QA placeholders in `specs/064-design-reviewer-template-test-bench-and-publish-gates/`
- [x] T002 [P] Add template API schema contracts in `src/multi_agent_platform/api/schemas/design_review.py`
- [x] T003 [P] Add template state schema contracts in `src/multi_agent_platform/api/schemas/admin_design_review_workspace.py`
- [x] T004 [P] Add focused template service test skeleton in `tests/unit/admin/design_review/test_design_review_template.py`
- [x] T005 [P] Add focused API integration test skeleton in `tests/integration/api/test_admin_design_review_template_api.py`

## Phase 2: Foundational

- [x] T006 Implement Design Reviewer Council workflow draft builder in `src/multi_agent_platform/admin/design_review/template.py`
- [x] T007 Implement required Test Bench suite/case/evidence orchestration in `src/multi_agent_platform/admin/design_review/template.py`
- [x] T008 Implement current-revision publish-gate evaluation and stale evidence detection in `src/multi_agent_platform/admin/design_review/template.py`
- [x] T009 Add template install authorization surface in `src/multi_agent_platform/auth/policy.py`
- [x] T010 Extend live-data inventory and guardrails for template route coverage in `src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py`

## Phase 3: User Story 1 - Install Council Template With Evidence (Priority: P1)

**Goal**: Authorized admins can explicitly install or reuse the council template and required evidence.

**Independent Test**: Run backend service and API tests that install the template twice and verify idempotent workflow/evidence reuse.

- [x] T011 [P] [US1] Test idempotent template install and evidence creation in `tests/unit/admin/design_review/test_design_review_template.py`
- [x] T012 [P] [US1] Test install API success and replay in `tests/integration/api/test_admin_design_review_template_api.py`
- [x] T013 [US1] Add `POST /admin/design-reviews/templates/council/install` in `src/multi_agent_platform/api/routers/admin_design_review.py`
- [x] T014 [US1] Record safe audit events for install and replay in `src/multi_agent_platform/api/routers/admin_design_review.py`
- [x] T015 [US1] Wire template setup state into `src/multi_agent_platform/admin/design_review/react_workspace.py`

## Phase 4: User Story 2 - Enforce Current Publish Evidence (Priority: P2)

**Goal**: Publish readiness is blocked unless the current workflow draft revision has passing required evidence.

**Independent Test**: Run tests that create current evidence, evaluate ready state, save a newer draft revision, and verify stale blocking state.

- [x] T016 [P] [US2] Test publish gate ready and stale evidence behavior in `tests/unit/admin/design_review/test_design_review_template.py`
- [x] T017 [P] [US2] Test failed and cross-tenant evidence denial in `tests/integration/api/test_admin_design_review_template_api.py`
- [x] T018 [US2] Ensure workflow draft document carries required Test Bench evidence references in `src/multi_agent_platform/admin/design_review/template.py`
- [x] T019 [US2] Add safe publish-gate status to Admin workspace bootstrap response in `src/multi_agent_platform/admin/design_review/react_workspace.py`

## Phase 5: User Story 3 - Prove Scenario Outcomes And Denials (Priority: P3)

**Goal**: QA proves the required scenario matrix, cross-tenant denial, redaction, and live Admin states.

**Independent Test**: Run QA064 seed/verify scripts and Playwright validation.

- [x] T020 [P] [US3] Add QA seed script in `scripts/qa/seed_design_review_template_qa064.py`
- [x] T021 [P] [US3] Add QA verify script in `scripts/qa/verify_design_review_template_qa064.py`
- [x] T022 [P] [US3] Extend React workspace component tests in `frontend/admin/src/components/designReviews/DesignReviewWorkspacePage.test.tsx`
- [x] T023 [US3] Add template setup panel and install interaction in `frontend/admin/src/components/designReviews/DesignReviewWorkspacePage.tsx`
- [x] T024 [US3] Add responsive template setup styles in `frontend/admin/src/styles/admin.css`
- [x] T025 [US3] Update `specs/_autopilot/scenario-enhancement-roadmap/064-design-reviewer-template-test-bench-and-publish-gates/validation.yml` for QA064 setup and Playwright expectations

## Phase 6: Polish & Validation

- [x] T026 Update `curl_testing.md` for template install, replay, workspace bootstrap, and cross-tenant denial coverage
- [x] T027 Complete `qa064.md`, `qa064_ui.md`, `.env.qa064`, `qa064_user_guide.md`, and `pr_notes.md`
- [x] T028 Run focused backend tests for template, publish gate, and Admin API
- [x] T029 Run focused frontend tests, typecheck, and React build
- [x] T030 Run QA document validation for Spec 064
- [x] T031 Run full `run_spec_qa.py` for Spec 064
- [x] T032 Run Playwright UI validation for Spec 064
- [x] T033 Run full multi-agent curl regression for Spec 064
- [x] T034 Update Spec 064 status and roadmap queue completion files

## Dependencies

- T006-T010 depend on T002-T005.
- T013 depends on T006-T009.
- T015 depends on T003 and T013.
- T018-T019 depend on T007-T008.
- T020-T025 depend on T013-T019.
- T026-T034 depend on all implementation tasks.

## Parallel Opportunities

- T002-T005 can proceed independently after setup.
- T011/T012 and T016/T017 can be developed while the service stabilizes.
- T020/T021 and T022 can proceed independently after API contracts stabilize.

## Implementation Strategy

Deliver P1 first with a backend install action and durable required evidence.
Then add current-revision publish-gate enforcement, Admin workspace state, QA
matrix verification, Playwright coverage, curl regression updates, and final
roadmap bookkeeping.
