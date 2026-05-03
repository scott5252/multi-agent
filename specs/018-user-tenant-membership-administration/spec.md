# Feature Specification: User And Tenant Membership Administration

**Feature Branch**: `codex/018-user-tenant-membership-administration`  
**Created**: 2026-05-03  
**Status**: Draft  
**Input**: User description: "Add user and tenant membership administration. Platform admins must be able to list users, create invitations, link or provision Auth0-backed principal identities, assign platform roles, assign tenant roles, suspend or reactivate users, revoke grants, and inspect user access history across tenants. Tenant admins must be able to invite users to their own tenant, assign permitted tenant roles, revoke tenant memberships, and view user status for their tenant only. The platform must store principal metadata, invitations, memberships, and role grants, but production authentication remains Auth0-backed and the platform must not store user passwords. Local-principal mode must remain available for development and test. All role changes must take effect on the next protected action and create audit records. Require idempotent invites, safe email handling, tenant isolation, at least 90 percent coverage, docs, PR notes, testing instructions, and README updates."

## Clarifications

- Q: How should invitation email addresses be handled safely? -> A: Normalize addresses for idempotency, store the operational email only in invitation records, and render masked email text plus hashes in UI, API summaries, audit records, screenshots, and diagnostics (autopilot)
- Q: How should tenant admins be constrained when assigning roles? -> A: Tenant admins may assign or revoke only tenant-scoped `tenant_user` and `tenant_admin` roles for their own tenant; platform roles and cross-tenant grants require platform admin authority (autopilot)
- Q: How should local-principal development mode reflect role changes? -> A: Local-principal authentication continues to use catalog permissions for bootstrapping, but persisted principal identity status and role grants are merged on each protected request so admin changes are visible on the next action (autopilot)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Platform Administers Principals And Roles (Priority: P1)

Platform administrators need a single protected admin surface to list principals,
invite users, link or create Auth0-backed principal identities, assign platform
roles, assign tenant roles, revoke grants, suspend or reactivate principals, and
review access history across tenants without storing passwords.

**Why this priority**: Platform-wide user administration is the foundation for
Auth0-backed production access and support operations.

**Independent Test**: Sign in as a platform admin, open `/admin/memberships`,
create an invite, link an Auth0 subject, create and revoke platform and tenant
role grants, suspend and reactivate a principal, and verify access history and
audit-safe output.

**Acceptance Scenarios**:

1. **Given** a platform admin opens the page, **When** users and grants exist
   across tenants, **Then** the admin can see masked email summaries, principal
   identity status, tenant memberships, role grants, and recent access history.
2. **Given** an invitation is submitted twice with the same email and tenant,
   **When** the second request uses the same idempotency context, **Then** the
   original active invitation is returned without creating duplicates.
3. **Given** an Auth0 subject is provided for an invited user, **When** the
   platform admin links the subject, **Then** the principal identity is created
   or updated and passwords are never accepted or stored.
4. **Given** an active platform or tenant grant exists, **When** the platform
   admin revokes it, **Then** the grant is revoked, audit metadata is recorded,
   and the next protected request no longer receives the role.

---

### User Story 2 - Tenant Administers Own Memberships (Priority: P2)

Tenant administrators need to invite users to their own tenant, assign permitted
tenant roles, suspend or remove tenant memberships, and view user status for
their tenant without seeing or mutating other tenants.

**Why this priority**: Tenant self-service removes platform-admin bottlenecks
while preserving tenant isolation and platform-role guardrails.

**Independent Test**: Sign in as an Acme tenant admin, invite and update an
Acme member, attempt a Globex operation and a platform-role assignment, and
verify both denied requests fail closed.

**Acceptance Scenarios**:

1. **Given** a tenant admin is scoped to Acme, **When** they create an invite,
   **Then** the invitation is tenant-scoped to Acme and only permitted tenant
   roles can be requested.
2. **Given** an Acme tenant admin tries to assign `platform_admin`, **When**
   the request is submitted, **Then** the system denies the request and creates
   a safe audit record.
3. **Given** an Acme tenant admin requests Globex membership details, **When**
   the request is processed, **Then** access fails closed without confirming
   whether Globex membership exists.

---

### User Story 3 - Inspect Access History And Next-Request Changes (Priority: P3)

Admins need user access history, denied-access visibility, and confidence that
role changes affect the next protected request for Auth0 and local-principal
development flows.

**Why this priority**: Administration without explainability is unsafe in a
multi-tenant platform where role changes and denials must be auditable.

**Independent Test**: Create allow and deny decisions, change a role grant,
authenticate the affected local-principal or Auth0-backed user again, and verify
the principal context and history reflect current persisted state.

**Acceptance Scenarios**:

1. **Given** access decision records exist for a principal, **When** an admin
   opens user history, **Then** safe action, tenant, decision, reason, trace,
   and timestamp summaries are displayed.
2. **Given** a principal is suspended, **When** the same user performs a
   protected action, **Then** authorization fails before role checks.
3. **Given** a role grant is added or revoked, **When** the user's next
   protected request is authenticated, **Then** the role set reflects persisted
   active grants.

### Edge Cases

- Invitation email contains mixed case or whitespace.
- Existing active invite is replayed.
- Expired, revoked, or accepted invite is replayed.
- Auth0 subject already exists for another principal.
- Principal has no Auth0 subject yet and needs placeholder provisioning.
- Tenant admin tries to assign a platform role.
- Tenant admin tries to view, invite, mutate, or revoke another tenant's user.
- Platform admin acts with no selected tenant scope.
- Principal is suspended while active role grants remain.
- Role grant is revoked immediately before the next protected request.
- Local-principal catalog role conflicts with persisted grants.
- Access history contains denied cross-tenant records.
- UI flash messages, screenshots, API responses, and audits must not reveal raw
  email addresses or Auth0 subject secrets beyond safe references.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose a server-rendered Membership Administration
  page at `/admin/memberships` under the existing admin shell.
- **FR-002**: System MUST expose JSON admin APIs under `/admin/memberships/api`
  for user listing, invitation creation, principal linking/provisioning,
  membership updates, role-grant creation and revocation, suspension and
  reactivation, and access history.
- **FR-003**: Platform admins MUST be able to list principal identities,
  invitations, memberships, role grants, and safe access history across tenants.
- **FR-004**: Tenant admins MUST be able to list and mutate only memberships,
  invitations, and role grants for their own tenant.
- **FR-005**: System MUST fail closed for cross-tenant requests and denied
  platform-role actions without confirming unauthorized tenant data exists.
- **FR-006**: System MUST support idempotent invitations using normalized email,
  target tenant, requested roles, and idempotency key when provided.
- **FR-007**: System MUST render masked email display text and safe email
  hashes in UI, API summaries, screenshots, and audit records.
- **FR-008**: System MUST store principal metadata needed for Auth0 subject
  linking, local-principal development, display name, email, and status, and
  MUST NOT store user passwords.
- **FR-009**: System MUST allow platform admins to link an Auth0 subject to an
  existing or placeholder principal identity.
- **FR-010**: System MUST allow platform admins to create, update, revoke, and
  inspect platform and tenant role grants.
- **FR-011**: System MUST allow tenant admins to create, update, revoke, and
  inspect only tenant-scoped `tenant_user` and `tenant_admin` grants in their
  own tenant.
- **FR-012**: System MUST support tenant membership status transitions for
  active, suspended, and removed memberships.
- **FR-013**: System MUST support principal suspension and reactivation, and
  suspended principals MUST be denied protected actions on the next request.
- **FR-014**: Auth0 and local-principal authentication MUST merge current
  persisted active role grants and principal status on each protected request.
- **FR-015**: Role changes MUST create audit-safe membership audit records and
  access-decision records where protected actions are allowed or denied.
- **FR-016**: Access history MUST include safe summaries of recent access
  decisions by principal and tenant scope.
- **FR-017**: The admin navigation registry MUST include "Membership
  Administration" and preserve tenant scope.
- **FR-018**: Templates MUST use screenshot-safe redaction copy and safe flash
  messages.
- **FR-019**: Tests MUST cover admin authorization, platform-admin versus
  tenant-admin behavior, tenant isolation, cross-tenant denial, multi-tenant
  scope switching, user and tenant filters, invitations, membership flows, role
  eligibility, suspension/reactivation, next-request role behavior, audit
  records, metrics where available, UI rendering, API contracts, docs, PR
  notes, testing instructions, README updates, and coverage.
- **FR-020**: Automated test coverage for relevant code MUST meet or exceed the
  repository's 90 percent coverage threshold.

### Key Entities *(include if feature involves data)*

- **Principal Identity**: Existing persisted identity with provider, external
  subject, display name, email, status, and timestamps.
- **User Invitation**: Tenant-scoped or platform-scoped invitation with masked
  email display, email hash, requested roles, status, expiry, idempotency key,
  and audit metadata.
- **Tenant Membership**: Relationship between a principal and tenant with
  status, revision token, invited email hash, and lifecycle timestamps.
- **Role Grant**: Existing platform or tenant-scoped role assignment with
  status, effective and revoked timestamps, source, and assigning principal.
- **Membership Audit Record**: Append-only safe action summary for invites,
  identity linking, membership updates, grant changes, status changes, denials,
  and stale conflicts.
- **Access History Summary**: Safe projection of recent access decisions for a
  principal or tenant.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Platform admin browser validation reaches `/admin/memberships`
  and captures screenshots showing user list, invitation form, role controls,
  status controls, and safe access history.
- **SC-002**: Tenant isolation tests prove an Acme tenant admin cannot read,
  mutate, invite into, revoke, or infer Globex memberships or users.
- **SC-003**: Idempotency tests prove duplicate active invitation replay returns
  the original invitation without a duplicate row.
- **SC-004**: Role eligibility tests prove tenant admins cannot assign
  `platform_admin` or cross-tenant grants.
- **SC-005**: Next-request tests prove added, revoked, suspended, and
  reactivated principal state is reflected by a subsequent protected action.
- **SC-006**: Redaction tests prove UI, APIs, flash messages, and audit records
  do not render raw invite email addresses except where explicitly submitted by
  an authorized admin action.
- **SC-007**: Relevant automated coverage remains at or above 90 percent.
- **SC-008**: QA guide and Playwright evidence demonstrate local login and
  direct `/admin/memberships` target flows.

## Assumptions

- Auth0 remains the production identity provider; this feature stores only
  Auth0 subject references and platform metadata.
- The first implementation sends no real email; invitation creation records
  safe state and exposes deterministic local QA evidence.
- Existing access-control tables remain the source of truth for principal
  identities and role grants.
- Local-principal mode remains deterministic for QA and merges persisted grants
  after catalog bootstrapping.
