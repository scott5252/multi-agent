# Feature Specification: Membership And Access React Live Data

**Feature Branch**: `codex/054-membership-and-access-react-live-data`  
**Created**: 2026-05-07  
**Status**: Draft  
**Input**: User description: "Create a feature specification for Membership And Access React Live Data. Replace deterministic membership React builders with live projections from principal identity, invitation, tenant membership, role grant, access decision, support override, and membership audit repositories/services. React must show real users, masked identity details, invitations, memberships, role grants, status actions, access history, and audit records for the authorized scope. Empty states must be truthful when the tenant has no users or grants."

## Clarifications

### Session 2026-05-07

- Q: What sources are authoritative for membership and access React projections? -> A: (autopilot) MembershipService, MembershipRepository, AccessControlRepository, AuditRepository, and existing principal/role/invitation repositories are authoritative; React builders may only compose backend-owned projections from those sources or return truthful empty/denied/unavailable states.
- Q: How should platform and tenant authority be resolved? -> A: (autopilot) The backend resolves platform versus tenant scope from the authenticated principal, local-principal bootstrap permissions, requested scope, and access-control decisions; browser state never expands scope, and cross-tenant IDs fail closed.
- Q: What identity details may be rendered? -> A: (autopilot) Only masked email/contact labels, safe display names, safe actor summaries, status, role codes, revisions, timestamps, and audit references may render; raw IdP claims, full external subjects, tokens, raw audit payloads, unauthorized tenant labels, and full emails remain absent.
- Q: Which durable actions are in scope for validation? -> A: (autopilot) Invitation creation/replay, principal link/status changes, role grant creation/revocation, tenant membership status changes, and support override actions must route through existing services/repositories with idempotency, revision, denial, stale-conflict, and audit evidence.
- Q: How will QA prove local-principal membership behavior? -> A: (autopilot) qa054 seed/setup creates real local-principal membership, invitation, grant, access-decision, support-override, and audit rows without external IdP or provider calls; Playwright performs at least one visible persisted action and verifies it through backend API or redaction-safe database evidence.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Review Live Membership State (Priority: P1)

A platform operator or tenant administrator opens the membership workspace and sees only authorized live users, masked identities, invitations, memberships, role grants, access history, support override state, and membership audit records for the active scope. If no authorized rows exist, the workspace shows truthful empty, denied, or unavailable states instead of deterministic sample users or grants.

**Why this priority**: Membership and access screens govern who can use the platform. Operators must be able to trust that every row reflects durable identity and access state, not a fixed demonstration roster.

**Independent Test**: Can be tested by loading the membership workspace with an empty QA database and with QA-seeded membership records, then comparing browser and JSON responses to persisted principal, invitation, membership, grant, access decision, support override, and audit state.

**Acceptance Scenarios**:

1. **Given** an authorized tenant administrator and an empty live tenant, **When** the administrator opens the membership workspace, **Then** user, invitation, membership, role grant, access history, support override, and audit panels show truthful empty or unavailable states.
2. **Given** an authorized tenant administrator and persisted users, invitations, memberships, and role grants, **When** the administrator opens the membership workspace, **Then** every visible row matches an authorized live record for that tenant.
3. **Given** a platform operator, **When** the operator reviews platform-scoped membership and access state, **Then** the workspace shows only platform-authorized users, grants, support overrides, and audit evidence.
4. **Given** a cross-tenant or unauthorized principal, **When** the principal requests membership data, **Then** the response fails closed without exposing user names, email details, role grants, invitation metadata, access history, or audit records from another tenant.

---

### User Story 2 - Inspect Redaction-Safe Identity And Access Evidence (Priority: P2)

An authorized administrator inspects user identity, invitation, membership, role grant, access decision, support override, and audit details with enough context to make access decisions while sensitive identity, credential, token, and tenant information remains masked or absent.

**Why this priority**: Membership data is operationally sensitive. The UI must support troubleshooting and review without leaking full email addresses, external subjects, tokens, unauthorized tenant labels, support override internals, or raw audit payloads.

**Independent Test**: Can be tested by seeding sensitive-adjacent membership and access records, then verifying that JSON responses, browser text, screenshots, QA docs, and exports contain only masked labels, safe summaries, and authorized audit references.

**Acceptance Scenarios**:

1. **Given** principal identities with email and external-subject metadata, **When** an authorized administrator views users, **Then** the UI shows masked identity details and safe display labels only.
2. **Given** active and historical role grants, **When** an administrator opens access details, **Then** role code, scope, status, revision, and safe actor summaries are visible without raw identity provider claims or unauthorized tenant labels.
3. **Given** access decision and membership audit records, **When** a reviewer opens history panels, **Then** the UI shows safe reasons, decisions, timestamps, actors, and trace references without raw request payloads, tokens, or stack traces.
4. **Given** support override state, **When** a platform operator reviews override evidence, **Then** the UI shows safe status, requester, approver, target scope, expiration, and audit summaries without hidden credential or raw approval payloads.

---

### User Story 3 - Exercise Durable Membership Actions (Priority: P3)

An authorized administrator performs a safe visible membership action, and the result persists through backend services. Examples include creating an invitation, changing a membership status, creating or revoking a role grant, linking a principal identity, or approving a support override.

**Why this priority**: The live-data migration must prove that action panels are not browser-only forms or fixed success messages. Safe membership actions need persisted revision, idempotency, audit, and conflict evidence.

**Independent Test**: Can be tested by performing at least one user-visible membership action in Playwright, then verifying the persisted result through a backend API first and a redaction-safe QA database query when the API cannot expose the needed evidence.

**Acceptance Scenarios**:

1. **Given** an authorized tenant administrator, **When** the administrator creates an invitation, **Then** the mutation returns persisted invitation evidence and the refreshed workspace shows the invitation with masked recipient details.
2. **Given** an authorized administrator and an existing membership, **When** the administrator changes membership status or role grants, **Then** the mutation returns persisted revision and audit evidence and the refreshed workspace reflects the change.
3. **Given** a stale, denied, or invalid access action, **When** the administrator submits it, **Then** the system returns a safe conflict, validation, denied, or unavailable result without fabricating success evidence.
4. **Given** a platform support override action, **When** a permitted operator performs the action, **Then** the outcome is persisted, audited, scoped, and visible only to authorized platform users.

---

### Edge Cases

- Empty tenants return truthful empty states for users, invitations, memberships, role grants, access history, support overrides, and audits.
- Platform scope and tenant scope may expose different action sets and must never invent rows to fill panels.
- Full email addresses, raw external subjects, raw identity provider claims, full Telegram identifiers, tokens, secrets, local paths, stack traces, and raw audit payloads never render.
- Pending, expired, accepted, replayed, revoked, suspended, removed, denied, and stale records remain distinguishable through safe statuses.
- Invitation idempotency replays show replay-safe state without creating duplicate invitation rows.
- Role grant stale revisions and unsupported role assignments return safe conflict or validation results.
- Membership status actions that would remove the actor's own required access are denied safely.
- Support override requests, approvals, expiration, and revocation remain platform-authorized and tenant-scoped.
- Access history is bounded and redaction-safe when many decisions exist.
- Cross-tenant IDs fail closed for user, invitation, membership, grant, access decision, support override, and audit routes.
- Auth0-shaped principals and local-principal QA identities produce equivalent authorization outcomes for equivalent roles.
- Generated TypeScript contracts accept empty membership envelopes and reject malformed or unsafe membership payloads.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST replace deterministic production membership and access React data with authorized live projections from durable principal identity, invitation, tenant membership, role grant, access decision, support override, and membership audit records.
- **FR-002**: The system MUST return truthful empty, denied, or unavailable states when no live authorized membership or access records exist for the active scope.
- **FR-003**: The system MUST preserve platform, tenant administrator, tenant user, auditor, and support override authorization boundaries for all membership panels and actions.
- **FR-004**: The system MUST expose user and principal identity lists only from persisted identity and membership records authorized for the active scope.
- **FR-005**: The system MUST expose invitation lists and invitation actions only from persisted invitation records, idempotency evidence, status, expiration, and safe recipient summaries.
- **FR-006**: The system MUST expose membership status and role grant lists only from persisted membership and grant records, including revision, scope, status, actor, and timestamp evidence.
- **FR-007**: The system MUST expose access history only from persisted access decision and audit records, bounded to safe summaries for the active scope.
- **FR-008**: The system MUST expose support override information only from authorized persisted override records and safe audit evidence.
- **FR-009**: The system MUST keep raw identity provider claims, full external subjects, full email addresses, full Telegram identifiers, tokens, secrets, credential values, local filesystem paths, stack traces, raw audit payloads, unauthorized tenant labels, and private channel data out of React contracts, redirects, exports, screenshots, QA artifacts, logs, and docs.
- **FR-010**: The system MUST provide durable safe mutations for at least one visible membership or access action and return persisted result evidence, safe conflict details, denied states, or unavailable states as appropriate.
- **FR-011**: The system MUST validate at least one safe membership action through Playwright and post-UI API or redaction-safe database verification before the spec is marked complete.
- **FR-012**: The system MUST update generated React TypeScript contracts so frontend code accepts live empty-state membership envelopes and rejects malformed or unsafe membership payloads.
- **FR-013**: The system MUST validate both Auth0-shaped backend route behavior and local-principal browser behavior for platform, tenant, and cross-tenant membership surfaces.
- **FR-014**: The system MUST update live-data scanner guardrails so former deterministic qa034/qa035 membership and access markers fail when found in production membership builders or React routes while remaining allowed in test-only and historical spec artifacts.
- **FR-015**: The system MUST produce QA environment, QA guide, UI walkthrough, manual QA user guide, reviewer notes, Playwright evidence, post-UI persistence evidence, and curl regression evidence for qa054.

### Key Entities *(include if feature involves data)*

- **Principal Identity**: A local or external identity with safe display labels, masked contact details, provider type, status, and authorization-relevant metadata.
- **Tenant Membership**: A tenant-scoped relationship between a principal and tenant with status, source, revision, lifecycle timestamps, and actor evidence.
- **User Invitation**: A tenant-scoped invitation with masked recipient details, requested roles, status, idempotency evidence, expiration, and audit references.
- **Role Grant**: A platform or tenant-scoped role assignment with role code, principal, status, revision or timestamp evidence, effective period, and revocation evidence.
- **Access Decision Record**: A persisted authorization decision with safe principal, tenant, surface, action, decision, reason, trace, and timestamp summaries.
- **Support Override**: A platform-governed temporary access request or approval with target tenant, requester, approver, status, expiration, and audit evidence.
- **Membership Audit Record**: Append-only safe event describing invitation, membership, role grant, identity, support override, access decision, denial, or export activity.
- **Membership Action Result**: Safe mutation outcome containing accepted, replayed, stale, validation, denied, or unavailable state plus redaction-safe revision and audit references.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In an empty qa054 database, every membership JSON route and browser panel returns a truthful empty, denied, or unavailable state with zero deterministic users, invitations, memberships, grants, access decisions, support overrides, or audit rows.
- **SC-002**: In a seeded qa054 database, membership JSON routes and browser panels return only persisted records authorized for the active tenant or platform scope.
- **SC-003**: A Playwright flow performs at least one visible membership or access action and a post-UI API or QA database check proves the resulting state persisted.
- **SC-004**: Auth0-shaped backend tests and local-principal Playwright tests cover platform, tenant, and cross-tenant membership access.
- **SC-005**: Redaction tests confirm full emails, raw external subjects, raw identity provider claims, full Telegram identifiers, tokens, secrets, local paths, stack traces, raw audit payloads, unauthorized tenant labels, and private channel data are absent from React responses, screenshots, QA docs, and artifacts.
- **SC-006**: Generated TypeScript contract checks, focused backend tests, focused frontend tests, scanner tests, QA document validation, Spec QA, Playwright validation, and multi-agent curl validation all pass before the queue advances.

## Assumptions

- Existing membership services, principal identity repositories, invitation repositories, role grant repositories, access decision records, support override records, and membership audit records remain the authoritative source for membership and access state.
- QA seed data may create real principal identities, invitations, memberships, role grants, access decisions, support overrides, and audit records through documented setup flows, services, repositories, public/admin APIs, or safe scripts.
- Local QA actions use local-principal identities and deterministic data only; they do not call real identity providers, external tools, credentials, or outbound resources.
- Test fixtures with former qa034/qa035 markers may remain under test-only or historical spec paths but must not be imported by production routes or production projection builders.
- This spec does not remove historical specs, test fixtures, or docs solely because they contain old deterministic markers.
- The dirty worktree is intentionally preserved across specs, and no Git commit is required before or after this spec while the autopilot continues.
