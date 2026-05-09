# Tasks: Admin Design Review Workspace

**Input**: Design documents from `specs/063-admin-design-review-workspace/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required. This feature touches React admin routing, backend-owned
envelopes, live design-review records, tenant scope, redaction, mutations, QA,
and curl coverage.

## Phase 1: Setup

- [x] T001 Create Spec 063 feature artifacts and QA placeholders
- [x] T002 Add backend workspace schemas in `src/multi_agent_platform/api/schemas/admin_design_review_workspace.py`
- [x] T003 Add backend workspace builder in `src/multi_agent_platform/admin/design_review/react_workspace.py`
- [x] T004 Add React component scaffolding under `frontend/admin/src/components/designReviews/`
- [x] T005 Add tests for backend route and React component behavior

## Phase 2: Backend Envelope

- [x] T006 Add `/admin/app/design-reviews` HTML route and `/admin/app/design-reviews/bootstrap.json` envelope route in `admin_react.py`
- [x] T007 Add design-review workspace navigation and surface policies
- [x] T008 Compose tenant-scoped session summaries, selected-session detail, revisions, rounds, verdicts, decisions, handoff, workflow options, and actions
- [x] T009 Add QA seed and verify scripts for live QA063 workspace rows

## Phase 3: React Workspace

- [x] T010 Add `DesignReviewWorkspacePage` load/error/empty/live rendering
- [x] T011 Add create-session form with safe summary, quorum policy, workflow option, and idempotency
- [x] T012 Add session list and selected-session detail panels
- [x] T013 Add round, verdict, quorum, manual decision, and handoff panels
- [x] T014 Add launch and manual-resolution actions using existing APIs
- [x] T015 Add responsive and accessible workspace styles

## Phase 4: Validation And QA

- [x] T016 Update TypeScript client helpers and tests
- [x] T017 Update `curl_testing.md` for new React workspace route coverage
- [x] T018 Complete QA docs and manual user guide
- [x] T019 Run focused backend and frontend tests
- [x] T020 Run QA document validation
- [x] T021 Run full `run_spec_qa.py` for Spec 063
- [x] T022 Run Playwright UI validation for Spec 063
- [x] T023 Run full multi-agent curl regression for Spec 063

## Dependencies

- T006 depends on T002 and T003.
- T010 depends on T004 and T006.
- T014 depends on T010-T013.
- T021-T023 depend on all implementation tasks.

## Parallel Opportunities

- T002/T003 and T004/T005 can proceed independently.
- React tests and backend tests can be developed in parallel after contracts stabilize.
