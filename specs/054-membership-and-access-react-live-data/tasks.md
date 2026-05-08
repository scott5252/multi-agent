# Tasks: Membership And Access React Live Data

**Input**: Design documents from `specs/054-membership-and-access-react-live-data/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required by the feature spec. Include backend route/service/repository tests, generated contract checks, frontend tests, scanner tests, QA document validation, Spec QA, Playwright, post-UI persistence verification, and curl regression validation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel when executed by separate workers because it touches different files and has no dependency on incomplete tasks.
- **[Story]**: Maps task to US1, US2, or US3 from spec.md.
- No task requires staging, committing, or a clean Git worktree; validated prior-spec changes remain in the dirty worktree until the user commits.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Align contracts, validation manifests, and QA targets before implementation.

- [x] T001 Review current membership React builders, route wiring, schemas, repositories, and frontend panels in `src/multi_agent_platform/admin/memberships/react_memberships.py`, `src/multi_agent_platform/api/routers/admin_react.py`, `src/multi_agent_platform/api/schemas/admin_membership_react.py`, `src/multi_agent_platform/db/repositories/memberships.py`, and `frontend/admin/src/components/memberships/`
- [x] T002 [P] Reconcile qa054 validation commands, route hints, Playwright flow target, and post-UI persistence command in `specs/_autopilot/remove-mock-data-roadmap/054-membership-and-access-react-live-data/validation.yml`
- [x] T003 [P] Add or update qa054 seed and verifier script placeholders in `scripts/qa/seed_membership_qa054.py` and `scripts/qa/verify_membership_qa054.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core live-data and redaction foundation that all user stories depend on.

- [x] T004 [P] Extend membership React schemas with provenance, empty-state, and source metadata in `src/multi_agent_platform/api/schemas/admin_membership_react.py`
- [x] T005 [P] Add repository list/get helpers for bounded live membership projections and post-UI verification in `src/multi_agent_platform/db/repositories/memberships.py`
- [x] T006 [P] Add qa054 live membership fixtures for tests in `tests/fixtures/memberships.py`
- [x] T007 Add shared membership projection helpers for scope resolution, safe labels, role labels, empty sections, and mutation results in `src/multi_agent_platform/admin/memberships/react_memberships.py`
- [x] T008 Regenerate frontend API contracts from Pydantic schemas into `frontend/admin/src/api/generated/reactAdminApi.ts`

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Review Live Membership State (Priority: P1)

**Goal**: Authorized operators and tenant administrators see only live users, invitations, memberships, role grants, access history, support override state, and audit rows for the active scope, or truthful empty/denied/unavailable states.

**Independent Test**: Load `/admin/app/memberships/bootstrap.json` and the browser workspace against an empty qa054 database and a seeded qa054 database, then compare rows to persisted membership/access records.

### Tests for User Story 1

- [x] T009 [P] [US1] Add live empty/seeded dashboard and support-override empty/unavailable service tests in `tests/unit/admin/memberships/test_react_membership_service.py`
- [x] T010 [P] [US1] Add repository tenant/platform filtering tests in `tests/unit/db/test_membership_repository.py`
- [x] T011 [P] [US1] Add Auth0-shaped and local-principal route tests for membership bootstrap, empty state, seeded state, and cross-tenant denial in `tests/integration/test_admin_react_routes.py`
- [x] T012 [P] [US1] Add bounded query performance coverage in `tests/performance/memberships/test_react_membership_queries.py`

### Implementation for User Story 1

- [x] T013 [US1] Replace fixed dashboard rows with async service-backed live snapshot projections, including support-override empty/unavailable evidence, in `src/multi_agent_platform/admin/memberships/react_memberships.py`
- [x] T014 [US1] Wire `/admin/app/memberships/bootstrap.json` to `MembershipRepository` and `MembershipAdministrationService` in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T015 [US1] Update membership frontend empty/live provenance rendering in `frontend/admin/src/components/memberships/MembershipPage.tsx`, `frontend/admin/src/components/memberships/InvitationPanel.tsx`, `frontend/admin/src/components/memberships/RoleGrantPanel.tsx`, and `frontend/admin/src/components/memberships/StatusActionsPanel.tsx`
- [x] T016 [US1] Update frontend membership test fixtures and component tests for live empty and seeded states in `frontend/admin/src/test/membershipTestData.ts` and `frontend/admin/src/components/memberships/*.test.tsx`

**Checkpoint**: User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Inspect Redaction-Safe Identity And Access Evidence (Priority: P2)

**Goal**: Identity, access, support override, and audit detail panels show useful safe evidence without leaking raw identity, tenant, token, path, stack trace, or audit payload data.

**Independent Test**: Seed sensitive-adjacent membership/access/audit records, then assert JSON, browser text, screenshots, QA docs, and artifacts expose only masked labels and safe summaries.

### Tests for User Story 2

- [x] T017 [P] [US2] Add schema redaction and unsafe-text rejection tests in `tests/unit/api/test_admin_membership_react_schema.py`
- [x] T018 [P] [US2] Add access-history and audit route tests in `tests/integration/test_admin_react_routes.py`
- [x] T019 [P] [US2] Add scanner guardrail tests for QA034 membership markers in `tests/unit/admin/test_live_data_inventory_scanner.py`
- [x] T020 [P] [US2] Add frontend access history, audit, and raw identifier redaction tests in `frontend/admin/src/components/memberships/AccessHistoryPanel.test.tsx`, `frontend/admin/src/components/memberships/MembershipAuditPanel.test.tsx`, and `frontend/admin/src/components/memberships/RawIdentifierDetailPanel.test.tsx`

### Implementation for User Story 2

- [x] T021 [US2] Replace fixed access-history and audit builders with live bounded projections in `src/multi_agent_platform/admin/memberships/react_memberships.py`
- [x] T022 [US2] Wire `/admin/app/memberships/access-history.json` and `/admin/app/memberships/audit.json` to live repositories/services in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T023 [US2] Update scanner production-surface rules to fail QA034 membership markers in `src/multi_agent_platform/admin/migration_hardening/live_data_inventory.py`
- [x] T024 [US2] Update membership frontend panels to render safe live evidence, empty states, and no raw identifiers in `frontend/admin/src/components/memberships/AccessHistoryPanel.tsx`, `frontend/admin/src/components/memberships/MembershipAuditPanel.tsx`, and `frontend/admin/src/components/memberships/RawIdentifierDetailPanel.tsx`

**Checkpoint**: User Stories 1 and 2 should both work independently.

---

## Phase 5: User Story 3 - Exercise Durable Membership Actions (Priority: P3)

**Goal**: At least one visible membership action persists through backend services, and mutation surfaces return persisted, replayed, stale, denied, validation, or unavailable evidence without browser-only success.

**Independent Test**: Use Playwright to create or replay a tenant invitation, then verify persisted invitation and audit evidence through backend API or redaction-safe qa054 database query.

### Tests for User Story 3

- [x] T025 [P] [US3] Add service mutation tests for invitation replay, role grant/revoke, membership status, principal status/link, and denial branches in `tests/unit/admin/memberships/test_react_membership_service.py`
- [x] T026 [P] [US3] Add React route mutation tests for accepted, replayed, denied, stale, and invalid actions in `tests/integration/test_admin_react_routes.py`
- [x] T027 [P] [US3] Add frontend mutation result tests in `frontend/admin/src/components/memberships/MembershipMutationResultPanel.test.tsx`, `frontend/admin/src/components/memberships/InvitationPanel.test.tsx`, `frontend/admin/src/components/memberships/PrincipalLinkPanel.test.tsx`, and `frontend/admin/src/components/memberships/RoleGrantPanel.test.tsx`

### Implementation for User Story 3

- [x] T028 [US3] Migrate invitation, principal link/status, role grant/revoke, and tenant membership status mutation builders to existing durable membership services in `src/multi_agent_platform/admin/memberships/react_memberships.py`
- [x] T029 [US3] Wire membership mutation endpoints to live repository/service dependencies and safe error mapping in `src/multi_agent_platform/api/routers/admin_react.py`
- [x] T030 [US3] Ensure frontend membership forms submit backend-owned actions and refresh persisted results in `frontend/admin/src/components/memberships/InvitationPanel.tsx`, `frontend/admin/src/components/memberships/PrincipalLinkPanel.tsx`, `frontend/admin/src/components/memberships/RoleGrantPanel.tsx`, and `frontend/admin/src/components/memberships/StatusActionsPanel.tsx`
- [x] T031 [US3] Implement qa054 Playwright seed and post-UI persistence verification in `scripts/qa/seed_membership_qa054.py`, `scripts/qa/verify_membership_qa054.py`, and `specs/_autopilot/remove-mock-data-roadmap/054-membership-and-access-react-live-data/validation.yml`

**Checkpoint**: All user stories should now be independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, QA artifacts, contract generation, and required validation.

- [x] T032 [P] Generate qa054 QA guide, UI walkthrough, environment file, manual user guide, and reviewer notes in `specs/054-membership-and-access-react-live-data/qa054.md`, `specs/054-membership-and-access-react-live-data/qa054_ui.md`, `specs/054-membership-and-access-react-live-data/.env.qa054`, `specs/054-membership-and-access-react-live-data/qa054_user_guide.md`, and `specs/054-membership-and-access-react-live-data/pr_notes.md`
- [x] T033 [P] Update membership live-data contracts and quickstart after implementation in `specs/054-membership-and-access-react-live-data/contracts/` and `specs/054-membership-and-access-react-live-data/quickstart.md`
- [x] T034 Run Ruff, mypy-targeted checks where applicable, focused pytest, frontend tests, and build commands from `specs/054-membership-and-access-react-live-data/quickstart.md`
- [x] T035 Run QA document validation with `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/054-membership-and-access-react-live-data`
- [x] T036 Run Spec QA with `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/remove-mock-data-roadmap/054-membership-and-access-react-live-data/validation.yml`
- [x] T037 Run Playwright UI validation with `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/remove-mock-data-roadmap/054-membership-and-access-react-live-data/validation.yml --start-processes`
- [x] T038 Run post-UI persistence verification with `uv run python scripts/qa/verify_membership_qa054.py`
- [x] T039 Run multi-agent curl regression with `uv run python .agents/skills/multi-agent-curl-test/scripts/run_curl_test.py --output-dir .data/curl_test_runs/qa054-after-spec`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories.
- **User Stories (Phase 3-5)**: Depend on Foundational completion. Execute sequentially for the autopilot, but each story remains independently testable.
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational; no dependency on US2 or US3.
- **User Story 2 (P2)**: Can start after Foundational; uses the same live snapshot foundation as US1.
- **User Story 3 (P3)**: Can start after Foundational; mutation UI benefits from US1 refresh behavior and US2 redaction checks.

### Parallel Opportunities

- T002 and T003 can run in parallel after T001 review.
- T004, T005, and T006 can run in parallel before T007 integration.
- US1 tests T009-T012 can be drafted in parallel.
- US2 tests T017-T020 can be drafted in parallel.
- US3 tests T025-T027 can be drafted in parallel.
- Documentation T032 and contract/quickstart update T033 can proceed once implementation behavior is stable.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup and Foundational tasks.
2. Replace bootstrap/dashboard fixed data with live repository-backed projections.
3. Validate empty database, seeded database, and cross-tenant denial for `/admin/app/memberships/bootstrap.json`.

### Incremental Delivery

1. Add US1 live dashboard and truthful empty state.
2. Add US2 redaction-safe access history and audit timeline.
3. Add US3 durable membership actions and post-UI persistence verification.
4. Run full qa054 validation and curl regression before advancing to Spec 055.
