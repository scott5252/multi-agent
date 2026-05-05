# Tasks: React User And Tenant Membership Administration

**Input**: Design documents from `specs/034-react-user-and-tenant-membership-administration/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`
**Tests**: Required by FR-017, SC-003 through SC-008, and the React UI roadmap dual-auth validation policy.
**Organization**: Tasks are grouped by user story so each story remains independently testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches distinct files or does not depend on unfinished tasks.
- **[Story]**: User story label for story phases only.
- Every task names an exact file path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare Spec 034 artifacts and confirm membership administration remains additive.

- [x] T001 Verify `.specify/feature.json` points to `specs/034-react-user-and-tenant-membership-administration` and `AGENTS.md` references `specs/034-react-user-and-tenant-membership-administration/plan.md`.
- [x] T002 [P] Create the membership React component directory at `frontend/admin/src/components/memberships/`.
- [x] T003 [P] Create the membership frontend fixture file at `frontend/admin/src/test/membershipTestData.ts`.
- [x] T004 [P] Create the membership backend schema module at `src/multi_agent_platform/api/schemas/admin_membership_react.py`.
- [x] T005 [P] Create the membership React adapter/service module at `src/multi_agent_platform/admin/memberships/react_memberships.py`.
- [x] T006 [P] Create the membership performance test directory at `tests/performance/memberships/`.
- [x] T007 [P] Create the QA034 documentation placeholders in `specs/034-react-user-and-tenant-membership-administration/qa034.md`, `specs/034-react-user-and-tenant-membership-administration/qa034_ui.md`, `specs/034-react-user-and-tenant-membership-administration/.env.qa034`, `specs/034-react-user-and-tenant-membership-administration/qa034_user_guide.md`, and `specs/034-react-user-and-tenant-membership-administration/pr_notes.md`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish safe backend contracts, generated browser types, protected routes, and shared UI primitives before story work.

- [x] T008 Define redaction-safe membership enums and value objects in `src/multi_agent_platform/api/schemas/admin_membership_react.py`.
- [x] T009 Define `MembershipDashboard`, `UserDirectoryEntry`, `InvitationSummary`, `PrincipalLinkSummary`, `RoleGrantSummary`, `MembershipStatusSummary`, `AccessHistoryRecord`, `MembershipAuditRecord`, and `MembershipMutationResult` schemas in `src/multi_agent_platform/api/schemas/admin_membership_react.py`.
- [x] T010 Define invite, principal link, role grant, revoke, principal status, membership status, directory filter, access-history filter, and audit filter request schemas in `src/multi_agent_platform/api/schemas/admin_membership_react.py`.
- [x] T011 Add schema validators that reject raw passwords, authorization headers, credential values, private messages, local filesystem paths, full unsafe subjects, raw prompt/completion text, and unauthorized tenant labels in `src/multi_agent_platform/api/schemas/admin_membership_react.py`.
- [x] T012 [P] Add schema tests for safe summaries, masked emails, subject suffixes, raw identifier detail gating, stale conflicts, idempotency replay, and unsafe marker rejection in `tests/unit/api/test_admin_membership_react_schema.py`.
- [x] T013 Implement deterministic QA034 constants, safe Acme/Globex tenant labels, role choices, display names, masked emails, subject suffixes, revision tokens, and audit references in `src/multi_agent_platform/admin/memberships/react_memberships.py`.
- [x] T014 Implement backend-owned dashboard, directory, allowed scope, filter, invite form, role grant form, status action, common state, and summary-card builders in `src/multi_agent_platform/admin/memberships/react_memberships.py`.
- [x] T015 Implement backend-owned mutation builders for invitation replay, principal link/provision, role grant, grant revoke, principal suspend/reactivate, and membership status changes in `src/multi_agent_platform/admin/memberships/react_memberships.py`.
- [x] T016 Implement bounded access history and membership audit timeline builders in `src/multi_agent_platform/admin/memberships/react_memberships.py`.
- [x] T017 Implement fail-closed cross-tenant, unsupported-role, stale-revision, missing-confirmation, audit-unavailable, and directory-unavailable result builders in `src/multi_agent_platform/admin/memberships/react_memberships.py`.
- [x] T018 [P] Add service tests for platform dashboard projections, tenant dashboard projections, invite idempotency replay, role eligibility, status actions, cross-tenant denial, and redaction safety in `tests/unit/admin/memberships/test_react_membership_service.py`.
- [x] T019 [P] Add bounded query/performance tests for directory, history, and audit builders in `tests/performance/memberships/test_react_membership_queries.py`.
- [x] T020 Extend `scripts/frontend/generate_admin_react_types.py` with generated TypeScript interfaces and assert helpers for all membership React schemas and request bodies.
- [x] T021 Regenerate `frontend/admin/src/api/generated/reactAdminApi.ts` from `scripts/frontend/generate_admin_react_types.py`.
- [x] T022 Add membership API client helpers for bootstrap, invitations, principal links, role grants, grant revocation, principal status, membership status, access history, and audit timeline in `frontend/admin/src/api/client.ts`.
- [x] T023 Add protected membership React routes and mutation endpoints to `src/multi_agent_platform/api/routers/admin_react.py`.
- [x] T024 Register membership React route surfaces as authenticated protected surfaces in `src/multi_agent_platform/auth/policy.py`.
- [x] T025 Wire `/admin/app/memberships` into the React app router in `frontend/admin/src/App.tsx`.
- [x] T026 Remove `memberships` from disabled React route fallbacks while preserving `/admin/memberships` Jinja fallback handling in `frontend/admin/src/routes.tsx`.
- [x] T027 Add membership workspace styles, responsive layout rules, and stable control dimensions in `frontend/admin/src/styles/admin.css`.
- [x] T028 [P] Add contract coverage for the membership bootstrap and mutation route shapes in `tests/contract/test_admin_react_contract.py`.
- [x] T029 [P] Add integration coverage for denied, Auth0-shaped, and local-principal membership React route authorization in `tests/integration/test_admin_react_routes.py`.
- [x] T030 [P] Add membership fixture data mirroring generated schemas in `frontend/admin/src/test/membershipTestData.ts`.

**Checkpoint**: Backend contracts, generated browser types, protected routes, and shared data fixtures are ready for user-story implementation.

---

## Phase 3: User Story 1 - Platform Administers Users And Grants (Priority: P1)

**Goal**: Platform admins can search users across authorized tenants, invite users, link/provision principals, grant and revoke roles, suspend/reactivate users, and see safe mutation results.

**Independent Test**: Sign in as a platform administrator, open `/admin/app/memberships`, complete directory review, invite replay, principal link/provision, platform and tenant role grant, grant revoke, suspension, reactivation, and verify safe audit/next-request summaries.

### Tests for User Story 1

- [x] T031 [P] [US1] Add platform dashboard and directory rendering tests in `frontend/admin/src/components/memberships/MembershipPage.test.tsx`.
- [x] T032 [P] [US1] Add invite workflow tests for created and replayed invitations in `frontend/admin/src/components/memberships/InvitationPanel.test.tsx`.
- [x] T033 [P] [US1] Add principal link/provision tests for safe subject suffixes and overwrite confirmation in `frontend/admin/src/components/memberships/PrincipalLinkPanel.test.tsx`.
- [x] T034 [P] [US1] Add role grant and revoke workflow tests for platform and tenant scopes in `frontend/admin/src/components/memberships/RoleGrantPanel.test.tsx`.
- [x] T035 [P] [US1] Add principal status confirmation tests for suspend and reactivate actions in `frontend/admin/src/components/memberships/StatusActionsPanel.test.tsx`.
- [x] T036 [P] [US1] Extend platform membership mutation integration tests in `tests/integration/test_admin_react_routes.py`.

### Implementation for User Story 1

- [x] T037 [US1] Implement `MembershipPage` orchestration, data loading, mutation state, result toasts, and section navigation in `frontend/admin/src/components/memberships/MembershipPage.tsx`.
- [x] T038 [P] [US1] Implement `MembershipSectionNav` with overview, directory, invitations, role grants, status, access history, and audit anchors in `frontend/admin/src/components/memberships/MembershipSectionNav.tsx`.
- [x] T039 [P] [US1] Implement `MembershipOverviewPanel` summary cards, scope selector, and common state messaging in `frontend/admin/src/components/memberships/MembershipOverviewPanel.tsx`.
- [x] T040 [P] [US1] Implement `UserDirectoryPanel` with backend-owned filters, human-friendly rows, status badges, role summaries, and next action buttons in `frontend/admin/src/components/memberships/UserDirectoryPanel.tsx`.
- [x] T041 [P] [US1] Implement `MaskedIdentityCell` for display name, masked email, safe subject suffix, and authorized raw detail affordance in `frontend/admin/src/components/memberships/MaskedIdentityCell.tsx`.
- [x] T042 [P] [US1] Implement `InvitationPanel` with tenant picker, eligible roles, idempotency key handling, replay state, masked result, audit reference, and next-request effect copy in `frontend/admin/src/components/memberships/InvitationPanel.tsx`.
- [x] T043 [P] [US1] Implement `PrincipalLinkPanel` with external subject suffix preview, provision/link modes, overwrite confirmation, field errors, and safe result summaries in `frontend/admin/src/components/memberships/PrincipalLinkPanel.tsx`.
- [x] T044 [P] [US1] Implement `RoleGrantPanel` with platform/tenant scope segmentation, backend-provided role chips, tenant picker, confirmation copy, stale recovery, and revoke actions in `frontend/admin/src/components/memberships/RoleGrantPanel.tsx`.
- [x] T045 [P] [US1] Implement `StatusActionsPanel` for principal suspend/reactivate and tenant membership status changes with explicit confirmations in `frontend/admin/src/components/memberships/StatusActionsPanel.tsx`.
- [x] T046 [P] [US1] Implement `MembershipMutationResultPanel` for status, toast, audit reference, field errors, stale conflict recovery, idempotency replay, confirmation-required state, and next-request effect in `frontend/admin/src/components/memberships/MembershipMutationResultPanel.tsx`.
- [x] T047 [US1] Connect platform invite, principal link, role grant, revoke, suspend, reactivate, and membership status client helpers to `MembershipPage` in `frontend/admin/src/components/memberships/MembershipPage.tsx`.
- [x] T048 [US1] Update `src/multi_agent_platform/api/routers/admin_react.py` to return platform-admin mutation builders for invitation, principal link, role grant, revoke, principal status, and membership status routes.
- [x] T049 [US1] Update `tests/integration/test_admin_react_routes.py` to assert platform mutations return masked identities, audit references, idempotency replay, and next-request effect without unsafe identifiers.

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Tenant Administers Own Memberships (Priority: P2)

**Goal**: Tenant admins can administer only their own tenant's invitations, memberships, permitted roles, and status while platform roles and cross-tenant resources fail closed.

**Independent Test**: Sign in as `tenant-admin-acme`, open `/admin/app/memberships`, invite a user, choose permitted Acme roles, revoke an Acme membership, change status, and verify Globex and platform-only actions are denied safely.

### Tests for User Story 2

- [x] T050 [P] [US2] Add tenant-scoped dashboard and directory rendering tests in `frontend/admin/src/components/memberships/TenantMembershipPage.test.tsx`.
- [x] T051 [P] [US2] Add tenant invite role eligibility tests in `frontend/admin/src/components/memberships/InvitationPanel.test.tsx`.
- [x] T052 [P] [US2] Add tenant-only role denial and cross-tenant denial tests in `frontend/admin/src/components/memberships/RoleGrantPanel.test.tsx`.
- [x] T053 [P] [US2] Add tenant membership revoke/status tests in `frontend/admin/src/components/memberships/StatusActionsPanel.test.tsx`.
- [x] T054 [P] [US2] Extend tenant authorization and cross-tenant denial integration tests in `tests/integration/test_admin_react_routes.py`.

### Implementation for User Story 2

- [x] T055 [US2] Update `build_membership_dashboard` tenant-scope behavior to omit unauthorized tenant choices, Globex rows, platform roles, and raw identifier detail in `src/multi_agent_platform/admin/memberships/react_memberships.py`.
- [x] T056 [US2] Update invite mutation behavior for tenant admins to accept only permitted tenant roles and return safe denial for platform role requests in `src/multi_agent_platform/admin/memberships/react_memberships.py`.
- [x] T057 [US2] Update role grant, revoke, and membership status mutation behavior for tenant admins to fail closed on cross-tenant and platform-only actions in `src/multi_agent_platform/admin/memberships/react_memberships.py`.
- [x] T058 [US2] Add tenant-admin request fixtures and safe denied fixtures to `frontend/admin/src/test/membershipTestData.ts`.
- [x] T059 [US2] Update `UserDirectoryPanel` filters to render backend-owned tenant, role, status, invitation, and access-decision choices without client-side authorization logic in `frontend/admin/src/components/memberships/UserDirectoryPanel.tsx`.
- [x] T060 [US2] Update `InvitationPanel` to hide unavailable tenant pickers and platform-only roles when metadata omits them in `frontend/admin/src/components/memberships/InvitationPanel.tsx`.
- [x] T061 [US2] Update `RoleGrantPanel` to render safe denial, stale recovery, and unsupported-role errors for tenant admins in `frontend/admin/src/components/memberships/RoleGrantPanel.tsx`.
- [x] T062 [US2] Update `StatusActionsPanel` to use backend-provided allowed actions and confirmation text for tenant membership revoke/status changes in `frontend/admin/src/components/memberships/StatusActionsPanel.tsx`.
- [x] T063 [US2] Update `src/multi_agent_platform/api/routers/admin_react.py` to route tenant-admin membership requests through tenant-scoped builders and safe problem responses.
- [x] T064 [US2] Update `tests/integration/test_admin_react_routes.py` to prove tenant admins cannot see or mutate Globex resources and cannot assign platform roles.

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Review Access History And Safe Details (Priority: P3)

**Goal**: Administrators can review bounded access history, safe detail panels, denied-action evidence, audit timelines, and next-request role-effect messaging without leaking sensitive identifiers.

**Independent Test**: Open a user detail view after allow/deny access decisions and membership changes, then verify safe timeline entries, authorized raw identifier detail only where allowed, audit references, and next-request effect summaries for Auth0-shaped and local-principal paths.

### Tests for User Story 3

- [x] T065 [P] [US3] Add access history rendering, filtering, and partial-unavailable tests in `frontend/admin/src/components/memberships/AccessHistoryPanel.test.tsx`.
- [x] T066 [P] [US3] Add audit timeline rendering and redaction tests in `frontend/admin/src/components/memberships/MembershipAuditPanel.test.tsx`.
- [x] T067 [P] [US3] Add authorized raw identifier detail tests in `frontend/admin/src/components/memberships/RawIdentifierDetailPanel.test.tsx`.
- [x] T068 [P] [US3] Add next-request role-effect and local-principal grant refresh tests in `tests/integration/test_admin_react_routes.py`.
- [x] T069 [P] [US3] Add Auth0-shaped access decision and membership effect route tests in `tests/integration/test_admin_react_routes.py`.

### Implementation for User Story 3

- [x] T070 [P] [US3] Implement `AccessHistoryPanel` with bounded safe records, filters, allow/deny badges, role-source summaries, trace references, and partial unavailable state in `frontend/admin/src/components/memberships/AccessHistoryPanel.tsx`.
- [x] T071 [P] [US3] Implement `MembershipAuditPanel` with safe audit references, actor/target labels, tenant scope labels, outcomes, safe diffs, and redaction classes in `frontend/admin/src/components/memberships/MembershipAuditPanel.tsx`.
- [x] T072 [P] [US3] Implement `RawIdentifierDetailPanel` with copyable raw IDs only from backend-authorized `raw_identifier_detail` fields in `frontend/admin/src/components/memberships/RawIdentifierDetailPanel.tsx`.
- [x] T073 [US3] Add access-history and audit data loading plus filter state to `MembershipPage` in `frontend/admin/src/components/memberships/MembershipPage.tsx`.
- [x] T074 [US3] Add access-history and audit endpoints to `src/multi_agent_platform/api/routers/admin_react.py`.
- [x] T075 [US3] Update `src/multi_agent_platform/admin/memberships/react_memberships.py` to include Auth0-shaped and local-principal next-request effect examples, denied-action evidence, and bounded access history records.
- [x] T076 [US3] Update `tests/unit/admin/memberships/test_react_membership_service.py` to prove bounded access history, safe detail gating, audit unavailable states, and no raw unsafe identifiers.
- [x] T077 [US3] Update `tests/contract/test_admin_react_contract.py` to include access-history and audit contract assertions.

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation manifest, generated checks, redaction scans, and final task completion.

- [x] T078 [P] Update Spec 034 QA API/database guide in `specs/034-react-user-and-tenant-membership-administration/qa034.md`.
- [x] T079 [P] Update Spec 034 UI walkthrough in `specs/034-react-user-and-tenant-membership-administration/qa034_ui.md`.
- [x] T080 [P] Update Spec 034 local QA environment in `specs/034-react-user-and-tenant-membership-administration/.env.qa034`.
- [x] T081 [P] Update Spec 034 manual user guide in `specs/034-react-user-and-tenant-membership-administration/qa034_user_guide.md`.
- [x] T082 [P] Update Spec 034 reviewer notes in `specs/034-react-user-and-tenant-membership-administration/pr_notes.md`.
- [x] T083 Update React roadmap validation manifest for QA034 routes, curl commands, quality commands, Playwright flows, screenshots, and redaction scans in `specs/_autopilot/react-ui-roadmap/034-react-user-and-tenant-membership-administration/validation.yml`.
- [x] T084 [P] Update membership React feature notes in `README.md`.
- [x] T085 [P] Update local validation quickstart notes in `docs/quickstart.md`.
- [x] T086 Run `uv run python scripts/frontend/generate_admin_react_types.py --check` and fix drift in `scripts/frontend/generate_admin_react_types.py` or `frontend/admin/src/api/generated/reactAdminApi.ts`.
- [x] T087 Run focused backend tests with `uv run pytest --no-cov tests/unit/api/test_admin_membership_react_schema.py tests/unit/admin/memberships/test_react_membership_service.py tests/performance/memberships/test_react_membership_queries.py tests/contract/test_admin_react_contract.py tests/integration/test_admin_react_routes.py` and fix failures in the touched files.
- [x] T088 Run frontend checks with `npm run typecheck`, `npm run test`, and `npm run build` in `frontend/admin` and fix failures in `frontend/admin/src/`.
- [x] T089 Run QA document validation with `bash .specify/extensions/qa-docs/scripts/bash/validate-qa-documents.sh specs/034-react-user-and-tenant-membership-administration` and fix Spec 034 docs.
- [x] T090 Run full Spec QA with `uv run python scripts/qa/run_spec_qa.py specs/_autopilot/react-ui-roadmap/034-react-user-and-tenant-membership-administration/validation.yml` and fix active-spec failures only.
- [x] T091 Run Playwright UI validation with `uv run python scripts/qa/run_playwright_ui.py specs/_autopilot/react-ui-roadmap/034-react-user-and-tenant-membership-administration/validation.yml --start-processes` and fix active-spec failures only.
- [x] T092 Run redaction scan `rg -n "qa034-secret-value|raw email|full subject|authorization header|provider token|credential value|private message|/Users/|unauthorized tenant label|full external subject" /tmp/qa034-* output/playwright/qa034_ui || true` and remove unsafe QA034 evidence if any appears.
- [x] T093 Mark completed tasks in `specs/034-react-user-and-tenant-membership-administration/tasks.md` after implementation and validation pass.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational; MVP scope.
- **User Story 2 (Phase 4)**: Depends on Foundational and can be implemented after or alongside US1 once shared components exist.
- **User Story 3 (Phase 5)**: Depends on Foundational and can be implemented after or alongside US1/US2.
- **Polish (Phase 6)**: Depends on the desired user stories and validation artifacts.

### User Story Dependencies

- **US1**: No story dependency after Foundational; delivers platform administration MVP.
- **US2**: Uses shared components from US1 but must remain independently testable with tenant-scoped fixtures and backend denials.
- **US3**: Uses shared identity and mutation result primitives, but history/audit panels remain independently testable.

### Parallel Opportunities

- Setup tasks T002 through T007 are parallelizable.
- Schema/service/performance/frontend fixture tests T012, T018, T019, T028, T029, and T030 can be prepared in parallel once schemas are sketched.
- US1 component tests T031 through T035 can be developed in parallel with backend integration test T036.
- US1 component implementations T038 through T046 can be implemented in parallel after `MembershipPage` contracts are stable.
- US2 tests T050 through T054 and US2 refinements T058 through T062 can be split by frontend/backend ownership.
- US3 tests T065 through T069 and panels T070 through T072 can be split safely by file.
- Documentation tasks T078 through T085 can be drafted in parallel after implementation behavior is stable.

## Parallel Example: User Story 1

```bash
Task: "Add invite workflow tests for created and replayed invitations in frontend/admin/src/components/memberships/InvitationPanel.test.tsx"
Task: "Add principal link/provision tests for safe subject suffixes and overwrite confirmation in frontend/admin/src/components/memberships/PrincipalLinkPanel.test.tsx"
Task: "Add role grant and revoke workflow tests for platform and tenant scopes in frontend/admin/src/components/memberships/RoleGrantPanel.test.tsx"
Task: "Implement MaskedIdentityCell for display name, masked email, safe subject suffix, and authorized raw detail affordance in frontend/admin/src/components/memberships/MaskedIdentityCell.tsx"
```

## Parallel Example: User Story 2

```bash
Task: "Update build_membership_dashboard tenant-scope behavior to omit unauthorized tenant choices, Globex rows, platform roles, and raw identifier detail in src/multi_agent_platform/admin/memberships/react_memberships.py"
Task: "Add tenant-scoped dashboard and directory rendering tests in frontend/admin/src/components/memberships/TenantMembershipPage.test.tsx"
Task: "Add tenant authorization and cross-tenant denial integration tests in tests/integration/test_admin_react_routes.py"
```

## Parallel Example: User Story 3

```bash
Task: "Implement AccessHistoryPanel with bounded safe records, filters, allow/deny badges, role-source summaries, trace references, and partial unavailable state in frontend/admin/src/components/memberships/AccessHistoryPanel.tsx"
Task: "Implement MembershipAuditPanel with safe audit references, actor/target labels, tenant scope labels, outcomes, safe diffs, and redaction classes in frontend/admin/src/components/memberships/MembershipAuditPanel.tsx"
Task: "Add Auth0-shaped access decision and membership effect route tests in tests/integration/test_admin_react_routes.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup and Foundational phases.
2. Implement US1 platform dashboard, directory, invite, principal link, grant, revoke, status, and mutation result flows.
3. Validate US1 with focused backend, frontend, and route tests before expanding tenant-specific behavior.

### Incremental Delivery

1. Deliver US1 for platform-wide membership administration.
2. Deliver US2 to prove tenant-scoped administration and fail-closed cross-tenant behavior.
3. Deliver US3 for access history, safe details, audit timeline, and next-request role-effect evidence.
4. Complete QA034 docs, validation manifest, full Spec QA, Playwright, and redaction scan before advancing to Spec 035.
