# Feature Specification: React User And Tenant Membership Administration

**Feature Branch**: `codex/034-react-user-and-tenant-membership-administration`  
**Created**: 2026-05-05  
**Status**: Draft  
**Input**: User description: "Create a feature specification for React User and Tenant Membership Administration. Platform admins need a clear user directory, invitation flow, principal linking/provisioning, platform role assignment, tenant role assignment, suspension/reactivation, grant revocation, membership status management, and access history across tenants. Tenant admins need a safer tenant-scoped view for inviting users, assigning permitted roles, revoking memberships, and viewing user status for their tenant only. The UI must avoid raw identifiers as the primary experience and must preserve safe email handling, idempotent invites, next-request role effect, tenant isolation, and audit records."

## Clarifications

### Session 2026-05-05

- Q: Which directory fields are primary for membership administration? -> A: Show display name, masked email, safe subject suffix, status, tenant labels, role labels, last access summary, and next allowed actions; keep raw IDs only in authorized detail panels (autopilot).
- Q: How should search and filters behave? -> A: Support backend-owned filters for name, masked email text, safe subject suffix, tenant, role, status, invitation state, and access decision state while failing closed for unauthorized tenant scope (autopilot).
- Q: How should invite idempotency be presented? -> A: Show replayed invitation state, original audit reference, masked email, requested roles, expiry, and next-request effect copy without creating duplicate invitation rows (autopilot).
- Q: How should role assignment be guided? -> A: Use a backend-eligible role grant wizard with separate platform and tenant scopes, tenant picker when authorized, permitted-role chips, confirmation copy, field errors, stale recovery, and safe audit result summaries (autopilot).
- Q: Which actions require confirmation? -> A: Require explicit confirmation for suspend, reactivate, remove membership, revoke grant, cross-tenant scoped changes, and principal link overwrite; cancellation must leave state unchanged (autopilot).
- Q: How much access history should be shown? -> A: Show a bounded recent timeline with safe action, tenant, decision, reason category, trace reference, timestamp, and role-source summaries, plus authorized filters for deeper review (autopilot).
- Q: How should email and subject display be masked? -> A: Use masked emails and safe subject suffixes by default; reveal full raw identifiers only in copyable detail panels when the backend marks them safe and authorized (autopilot).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Platform Administers Users And Grants (Priority: P1)

Platform administrators need a clear workspace to find users, inspect masked
identity and membership status, invite users, link or provision external
principal identities, assign platform and tenant roles, suspend or reactivate
users, revoke grants, and review safe access history across tenants.

**Why this priority**: Platform-wide user administration is the primary control
surface for production access, support operations, and incident response.

**Independent Test**: Sign in as a platform administrator, open the React
membership administration workspace, search for a user, create an invite, link
or provision a principal, grant and revoke platform and tenant roles, suspend
and reactivate a principal, and verify every result is reflected in safe audit
and access history summaries.

**Acceptance Scenarios**:

1. **Given** a platform administrator opens the membership workspace, **When**
   users, invitations, memberships, and role grants exist across tenants,
   **Then** the page shows human-friendly display names, masked emails, safe
   subject suffixes, tenant labels, role summaries, lifecycle status, and recent
   access history without making raw identifiers the primary view.
2. **Given** a platform administrator submits the same invitation twice with the
   same idempotency context, **When** the second request is processed, **Then**
   the original active invitation is returned and duplicate invitations are not
   created.
3. **Given** an invited user needs an external principal identity, **When** the
   platform administrator links or provisions the identity, **Then** the result
   displays safe subject and email summaries and never asks for or stores a user
   password.
4. **Given** platform and tenant role grants exist, **When** the platform
   administrator revokes a grant, **Then** the grant is marked revoked, the
   next protected request reflects the new role set, and audit history records
   the change safely.

---

### User Story 2 - Tenant Administers Own Memberships (Priority: P2)

Tenant administrators need a tenant-scoped workspace to invite users, assign
permitted tenant roles, revoke tenant memberships, change membership status,
and view user status for their own tenant only.

**Why this priority**: Tenant self-service reduces platform-administrator
bottlenecks while preserving tenant isolation and platform-role guardrails.

**Independent Test**: Sign in as an Acme tenant administrator, open the
membership workspace with Acme scope, invite a user, assign and revoke permitted
tenant roles, change membership status, and verify attempts to view or mutate
Globex or platform-only roles fail closed.

**Acceptance Scenarios**:

1. **Given** an Acme tenant administrator opens the workspace, **When** the
   directory loads, **Then** only Acme invitations, memberships, permitted role
   choices, and safe status summaries are shown.
2. **Given** an Acme tenant administrator creates an invitation, **When** they
   choose roles, **Then** only permitted tenant-scoped roles are available and
   the invitation shows next-request effect copy.
3. **Given** an Acme tenant administrator attempts to assign a platform role,
   **When** the request is submitted, **Then** the action is denied with a safe
   problem message and audit evidence.
4. **Given** an Acme tenant administrator attempts to inspect or mutate Globex
   membership data, **When** the request is processed, **Then** the operation
   fails closed without confirming whether the Globex resource exists.

---

### User Story 3 - Review Access History And Safe Details (Priority: P3)

Administrators need access history, denied-action evidence, safe raw identifier
detail panels, and clear next-request role-effect messaging so membership
changes are explainable without leaking sensitive identifiers.

**Why this priority**: Membership administration needs traceability and
reviewability for support, compliance, and security investigations.

**Independent Test**: Create allow and deny access decisions for a principal,
change grants or status, refresh the affected principal on the next protected
request, and verify the React workspace shows safe history, role effect,
redaction, and authorized details only.

**Acceptance Scenarios**:

1. **Given** access decision history exists for a user, **When** an authorized
   administrator opens the user detail view, **Then** safe action, tenant,
   decision, reason, trace, timestamp, and role-source summaries are shown.
2. **Given** raw principal, subject, or invitation identifiers are needed for
   support, **When** an authorized administrator opens a detail panel, **Then**
   copyable raw IDs are shown only where safe and authorized while the primary
   experience remains human-friendly.
3. **Given** a principal is suspended or reactivated, **When** the principal's
   next protected request is evaluated, **Then** authorization and role context
   reflect the current persisted state.

### Edge Cases

- Invitation email has mixed case, whitespace, or repeated submissions.
- Active, accepted, expired, and revoked invitations are replayed.
- An external subject is already linked to another principal.
- A principal has memberships in multiple tenants.
- A tenant administrator attempts a platform role assignment.
- A tenant administrator attempts cross-tenant search, detail, grant, or
  membership status changes.
- A role grant is revoked immediately before the affected user's next request.
- A principal is suspended while active role grants remain.
- Directory filters return no users.
- Search includes raw identifiers, masked emails, or safe subject suffixes.
- Audit or access history is unavailable.
- Confirmation is cancelled for suspend, remove, revoke, or reactivation.
- Local-principal catalog roles conflict with persisted role grants.
- Screenshots, exports, and audit summaries must not expose raw email addresses
  or full external subjects where only masked display is authorized.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide an additive React membership administration
  route from the existing admin shell while preserving the existing membership
  administration pages as fallbacks.
- **FR-002**: System MUST provide backend-owned JSON contracts for membership
  dashboard bootstrap, directory search, invitation creation, principal
  linking/provisioning, role grant creation, role grant revocation, principal
  status changes, tenant membership status changes, and access history.
- **FR-003**: System MUST use generated browser contracts for all membership
  response and request shapes rather than hand-maintained browser-only models.
- **FR-004**: Platform administrators MUST be able to view users, invitations,
  memberships, role grants, and access history across tenants.
- **FR-005**: Tenant administrators MUST be able to view and mutate only their
  own tenant's invitations, memberships, permitted tenant roles, and access
  history summaries.
- **FR-006**: System MUST fail closed for unauthorized, cross-tenant, stale,
  malformed, unsupported-role, unavailable-audit, and unavailable-directory
  states with safe problem details.
- **FR-007**: The primary directory experience MUST use display names, tenant
  labels, masked emails, safe subject suffixes, status badges, and role labels
  instead of raw identifiers.
- **FR-008**: Authorized detail panels MAY expose copyable raw identifiers only
  when the backend marks those identifiers safe and authorized for the current
  principal.
- **FR-009**: Invitation flows MUST normalize email addresses for idempotency,
  show masked email feedback, and make replayed invitation state explicit.
- **FR-010**: Invitation flows MUST display requested roles, expiry, status,
  audit references, and next-request effect copy.
- **FR-011**: Role grant workflows MUST present platform and tenant role choices
  according to backend eligibility rules for the active administrator.
- **FR-012**: Destructive or access-changing actions, including suspend,
  remove, revoke, and reactivation, MUST require explicit confirmation.
- **FR-013**: Membership and grant mutation results MUST show backend-owned
  status, audit reference, stale conflict recovery, idempotency replay, and
  next-request effect summaries.
- **FR-014**: Access history MUST show bounded, safe access decision summaries
  by user and tenant scope.
- **FR-015**: Directory filtering MUST support name, masked email text, safe
  subject suffix, tenant, role, and status filters without exposing
  unauthorized tenant data.
- **FR-016**: Empty, loading, denied, validation error, stale conflict,
  unavailable dependency, partial-data, and unexpected-error states MUST be
  represented as reusable safe UI states.
- **FR-017**: All membership route and mutation surfaces MUST be validated with
  both Auth0-shaped production principals and local-principal QA principals.
- **FR-018**: Local validation MUST avoid live Auth0 calls, real email delivery,
  external provider calls, and real credential resolution.
- **FR-019**: Membership screenshots, JSON evidence, audit records, and QA
  artifacts MUST NOT include raw email addresses, full external subjects,
  passwords, authorization headers, private channel messages, raw prompts,
  credential values, local paths, or unauthorized tenant labels.
- **FR-020**: Documentation MUST include QA API/database guide, UI walkthrough,
  manual user guide, reviewer notes, README updates, quickstart updates, and a
  validation manifest with Playwright screenshot flows.

### Key Entities *(include if feature involves data)*

- **Membership Dashboard**: Backend-owned route bootstrap containing scope,
  summary metrics, directory filters, form metadata, safe role eligibility, and
  first-page directory data.
- **User Directory Entry**: Safe projection of a principal with display name,
  masked email, safe subject suffix, status, tenant memberships, role labels,
  and available actions.
- **Invitation Summary**: Safe invitation projection with masked email, tenant
  scope, requested roles, status, expiry, replay state, audit reference, and
  next-request copy.
- **Principal Link Summary**: Safe outcome of linking or provisioning an
  external principal identity, including subject suffix and audit reference.
- **Role Grant Summary**: Platform or tenant role assignment with scope, role,
  status, eligibility, effect timing, revoke action, and audit metadata.
- **Membership Status Summary**: Tenant membership lifecycle state with active,
  suspended, removed, stale, and unavailable projections.
- **Access History Record**: Bounded safe access-decision summary with action,
  decision, tenant scope, reason category, trace reference, and timestamp.
- **Membership Mutation Result**: Backend-owned mutation response containing
  status, summary, field errors, confirmation state, stale conflicts,
  idempotency replay, audit reference, and safe next-step actions.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Platform administrator validation can complete directory review,
  invitation creation, principal linking/provisioning, role grant, role revoke,
  suspension, reactivation, and access history review from the React workspace.
- **SC-002**: Tenant administrator validation can invite, assign permitted
  tenant roles, revoke tenant membership, and inspect tenant-scoped user status
  without seeing cross-tenant data.
- **SC-003**: Automated tests prove invitation idempotency returns the original
  active invitation for repeated submissions.
- **SC-004**: Automated tests prove tenant administrators cannot assign
  platform roles or mutate another tenant's users, grants, invitations, or
  memberships.
- **SC-005**: Automated tests prove added, revoked, suspended, and reactivated
  access state is reflected on the next protected action for Auth0-shaped and
  local-principal principals.
- **SC-006**: Redaction tests prove React contracts, screenshots, audit
  records, and QA artifacts do not expose raw email addresses, full external
  subjects, passwords, authorization headers, credential values, local paths,
  or unauthorized tenant labels.
- **SC-007**: Playwright validation captures denied, platform, tenant, invite,
  role grant, revoke, status, access history, and cross-tenant denial evidence.
- **SC-008**: Relevant automated coverage remains at or above the repository's
  required threshold.

## Assumptions

- Existing membership domain services, repositories, policies, redaction
  helpers, and server-rendered pages remain authoritative and available.
- Production authentication remains Auth0-backed; this feature does not store
  passwords or perform real Auth0 provisioning in local QA.
- Local-principal mode remains deterministic for development and validation.
- Invitation creation records safe local evidence and does not send real email
  during QA034.
- Role and status changes take effect on the affected user's next protected
  request.
