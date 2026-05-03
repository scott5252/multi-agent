# Tasks: User And Tenant Membership Administration

**Input**: Design documents from `/Users/scottcornell/src/my-projects/multi-agent/specs/018-user-tenant-membership-administration/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/memberships.openapi.yaml`, `contracts/admin-memberships-ui.md`, `quickstart.md`  
**Tests**: Required for admin authorization, platform-admin versus tenant-admin behavior, tenant isolation, cross-tenant denial, multi-tenant scope switching, user and tenant filters, invitation creation/replay/revocation/expiration, membership create/update/suspend/restore/remove flows, role assignment eligibility, platform role guardrails, support override boundaries, stale revision conflict handling, identity-provider reference redaction, safe flash messages, audit records, metrics where available, admin navigation, browser UI forms, screenshot-safe redaction, docs, PR review notes, testing instructions, README updates, and coverage at or above 90 percent.

**Organization**: Tasks are grouped by independently testable user stories after shared storage, policy, schema, and redaction foundations are in place.

## Phase 1: Setup

**Purpose**: Establish feature scaffolding, contract checks, and docs-test expectations.

- [X] T001 Create `src/multi_agent_platform/admin/memberships/__init__.py`
- [X] T002 [P] Add contract coverage for `specs/018-user-tenant-membership-administration/contracts/memberships.openapi.yaml` in `tests/contract/test_membership_administration_contract.py`
- [X] T003 [P] Add docs existence and README expectation tests in `tests/docs/test_membership_administration_docs.py`
- [X] T004 [P] Add migration smoke test for membership tables in `tests/integration/db/test_membership_administration_migration.py`

---

## Phase 2: Foundational Storage, Policy, Redaction, And Schemas

**Purpose**: Blocking data, schema, repository, authorization, and redaction primitives used by every story.

**Critical**: No user story implementation should start until these tasks are complete.

- [X] T005 Add SQLAlchemy invitation, membership, and audit models in `src/multi_agent_platform/db/models/user_management.py`
- [X] T006 Register membership models in `src/multi_agent_platform/db/models/__init__.py`
- [X] T007 Add additive Alembic migration in `alembic/versions/0018_user_tenant_membership_administration.py`
- [X] T008 [P] Add repository tests in `tests/unit/db/test_membership_repository.py`
- [X] T009 Implement domain models in `src/multi_agent_platform/admin/memberships/models.py`
- [X] T010 Implement email and subject redaction helpers in `src/multi_agent_platform/admin/memberships/redaction.py`
- [X] T011 [P] Add redaction tests in `tests/unit/admin/memberships/test_membership_redaction.py`
- [X] T012 Implement async repository in `src/multi_agent_platform/db/repositories/memberships.py`
- [X] T013 Add Pydantic schemas in `src/multi_agent_platform/api/schemas/memberships.py`
- [X] T014 [P] Add schema tests in `tests/unit/api/test_membership_schemas.py`
- [X] T015 Add membership protected surfaces in `src/multi_agent_platform/auth/policy.py`
- [X] T016 Update local-principal QA permission helpers in `src/multi_agent_platform/auth/local_principals.py`
- [X] T017 [P] Add policy tests in `tests/unit/auth/test_membership_policy.py`

**Checkpoint**: Storage, schemas, repository filters, redaction, and authorization are ready for user and tenant administration work.

---

## Phase 3: User Story 1 - Platform Administers Principals And Roles (Priority: P1)

**Goal**: Platform admins can list users, create idempotent invitations, link Auth0 subjects, create/revoke platform and tenant grants, suspend/reactivate principals, and inspect safe access history.

**Independent Test**: Platform admin opens `/admin/memberships`, creates an invite, links a principal, creates and revokes grants, suspends/reactivates a principal, and verifies audit-safe output.

### Tests for User Story 1

- [X] T018 [P] [US1] Add service tests for platform invitations, Auth0 linking, role grant creation/revocation, suspension/reactivation, audit records, and next-request grant refresh in `tests/unit/admin/memberships/test_membership_service.py`
- [X] T019 [P] [US1] Add API integration tests for platform membership administration in `tests/integration/api/test_admin_memberships_api.py`

### Implementation for User Story 1

- [X] T020 [US1] Implement platform membership service methods in `src/multi_agent_platform/admin/memberships/service.py`
- [X] T021 [US1] Extend auth service persisted grant/status refresh in `src/multi_agent_platform/auth/service.py`
- [X] T022 [US1] Implement admin membership API/UI router in `src/multi_agent_platform/api/routers/admin_memberships.py`
- [X] T023 [US1] Register membership router in `src/multi_agent_platform/api/main.py`

**Checkpoint**: User Story 1 platform administration is independently testable.

---

## Phase 4: User Story 2 - Tenant Administers Own Memberships (Priority: P2)

**Goal**: Tenant admins can invite and manage users in their own tenant while platform role and cross-tenant attempts fail closed.

**Independent Test**: Acme tenant admin invites and updates an Acme member, then attempts a Globex operation and platform-role assignment and receives denials.

### Tests for User Story 2

- [X] T024 [P] [US2] Add API integration tests for tenant invite, tenant grant, cross-tenant denial, and platform-role denial in `tests/integration/api/test_admin_memberships_api.py`
- [X] T025 [P] [US2] Add UI integration tests for tenant form, safe flash text, tenant scope, and navigation in `tests/integration/api/test_admin_memberships_ui.py`
- [X] T026 [P] [US2] Add UI view model tests in `tests/unit/api/test_membership_ui_models.py`

### Implementation for User Story 2

- [X] T027 [US2] Implement tenant membership guardrails and status transitions in `src/multi_agent_platform/admin/memberships/service.py`
- [X] T028 [US2] Implement membership UI view models in `src/multi_agent_platform/api/ui/memberships.py`
- [X] T029 [US2] Add Membership Administration navigation item in `src/multi_agent_platform/api/ui/admin_console.py`
- [X] T030 [US2] Implement membership template in `src/multi_agent_platform/web_admin/templates/memberships/index.html`

**Checkpoint**: User Story 2 tenant administration is independently testable through API and browser UI.

---

## Phase 5: User Story 3 - Inspect Access History And Next-Request Changes (Priority: P3)

**Goal**: Admins can inspect recent access history and persisted role/status changes affect the next protected action.

**Independent Test**: Generate access decisions, mutate role grants and principal status, re-authenticate, and verify context/history reflect current persisted state.

### Tests for User Story 3

- [X] T031 [P] [US3] Add service and repository tests for access history filtering and redacted audit summaries in `tests/unit/admin/memberships/test_membership_service.py`
- [X] T032 [P] [US3] Add auth integration tests for next-request local-principal grant and suspension behavior in `tests/unit/auth/test_service.py`

### Implementation for User Story 3

- [X] T033 [US3] Implement access history and audit listing in `src/multi_agent_platform/admin/memberships/service.py`
- [X] T034 [US3] Render access history and audit records in `src/multi_agent_platform/web_admin/templates/memberships/index.html`

**Checkpoint**: User Story 3 access history and next-request behavior are independently testable.

---

## Final Phase: Polish And Cross-Cutting Verification

**Purpose**: Complete docs, QA artifacts, README updates, task tracking, and quality gates.

- [X] T035 [P] Generate QA environment file in `specs/018-user-tenant-membership-administration/.env.qa018`
- [X] T036 [P] Generate manual QA guide in `specs/018-user-tenant-membership-administration/qa018.md`
- [X] T037 [P] Generate browser UI QA walkthrough in `specs/018-user-tenant-membership-administration/qa018_ui.md`
- [X] T038 [P] Generate non-developer manual QA user guide in `specs/018-user-tenant-membership-administration/qa018_user_guide.md`
- [X] T039 [P] Add PR review notes in `specs/018-user-tenant-membership-administration/pr-review-notes.md`
- [X] T040 [P] Add testing instructions in `specs/018-user-tenant-membership-administration/testing-instructions.md`
- [X] T041 Update `README.md` with Membership Administration admin/API/QA summary
- [X] T042 Update `docs/quickstart.md` with QA018 validation entry
- [X] T043 Run QA document validation with `.specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/018-user-tenant-membership-administration`
- [X] T044 Run API validation with `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/018-user-tenant-membership-administration/validation.yml`
- [X] T045 Run Playwright UI validation with `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/018-user-tenant-membership-administration/validation.yml --start-processes`
- [X] T046 Run quality gates `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src`, and `uv run pytest --cov=src/multi_agent_platform --cov-report=term-missing --cov-fail-under=90`
- [X] T047 Mark completed tasks in `specs/018-user-tenant-membership-administration/tasks.md`

## Dependencies

- Phase 1 must complete before Phase 2.
- Phase 2 must complete before all user stories.
- User Story 1 is the MVP and establishes platform administration.
- User Story 2 depends on foundational tenant membership scope semantics.
- User Story 3 depends on role-grant and auth refresh behavior.
- Final polish depends on all selected implementation stories.

## Parallel Execution Examples

- T002, T003, and T004 can run in parallel after T001.
- T008, T011, T014, and T017 can run in parallel while paired implementation tasks are developed.
- T018 and T019 can run in parallel once Phase 2 is complete.
- T024, T025, and T026 can run in parallel once platform service behavior exists.
- T035 through T040 can run in parallel after behavior stabilizes.

## Implementation Strategy

1. Deliver MVP platform administration by completing Phases 1-3: storage,
   redaction, policy, schemas, repository, service, router, auth refresh, and
   admin shell registration.
2. Add tenant administration and guardrails with User Story 2.
3. Add access history and next-request validation with User Story 3.
4. Complete docs, QA artifacts, Playwright validation, and quality gates.
