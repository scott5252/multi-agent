# Feature Specification: Channels, Memberships, Access, Telegram, And Briefing Full React Parity

**Feature Branch**: `codex/045-channels-memberships-access-telegram-and-briefing-full-react-parity`  
**Created**: 2026-05-07  
**Status**: Draft  
**Input**: User description: "Create a feature specification for Channels, Memberships, Access, Telegram, and Briefing Full React Parity. Specs 034 and 036 added React workspaces, but full Jinja removal requires parity for membership direct links, invitations, principal linking/provisioning, role grants, membership status changes, access history, membership audit, Telegram tenant config, aliases, webhook validation, link-token creation, linked identities, delivery diagnostics, safe run status, briefing profile save/import/export/admin summaries, access/admin support pages, and any related retained Jinja route."

## Clarifications

### Session 2026-05-07

- Q: Are support override and role-grant admin pages in scope? -> A: Yes; all admin browser pages for access and people workflows are in scope, but React must continue to use backend-owned authorization and mutation contracts. (autopilot)
- Q: How should one-time Telegram link tokens be displayed? -> A: Show link tokens only immediately after creation; retained summaries and redirects must show token metadata or redacted references only. (autopilot)
- Q: How should old membership, Telegram, and briefing browser URLs behave? -> A: Preserve old direct links through authenticated redirects to `/admin/app/memberships` or `/admin/app/channels`, carrying safe tenant, id, action, and filter context. (autopilot)
- Q: Should tenant users and tenant admins see the same React channel and membership state? -> A: No; keep backend role and tenant scope decisions authoritative, with tenant users receiving user-safe summaries and denied routes failing closed. (autopilot)
- Q: How should destructive membership actions behave after redirect parity? -> A: Keep existing backend confirmation, revision, authorization, and idempotency checks; old form-post routes may redirect after executing safe existing service behavior. (autopilot)
- Q: How should Telegram webhook validation behave? -> A: Keep mocked-safe local validation, no live Telegram calls, and no full Telegram identifiers or private messages in UI, redirects, logs, or QA artifacts. (autopilot)
- Q: Are briefing import and export routes in scope? -> A: Yes; browser routes redirect or post through retained APIs and React export/import surfaces expose artifact metadata and safe summaries only. (autopilot)
- Q: Are retained API-only routes removed? -> A: No; JSON APIs used by React remain. Only browser-rendering Jinja routes and bounded templates are retired. (autopilot)

## User Stories & Testing

### User Story 1 - Manage Memberships In React Only (Priority: P1)

A platform admin or tenant admin opens old membership links for user directory, invitations, principal links, role grants, role-grant revoke, principal status, membership status, access history, or audit and lands on the React membership workspace with safe context preserved.

**Why this priority**: Membership and access flows govern tenant boundary, role grants, and user lifecycle. They must not keep duplicate Jinja UI after React parity exists.

**Independent Test**: Request old `/admin/memberships` browser URLs and form-post routes with platform, tenant admin, tenant user, unauthorized, and cross-tenant principals; verify React redirects, retained API behavior, denied states, redaction, and no deleted template rendering.

**Acceptance Scenarios**:

1. **Given** a platform admin opens `/admin/memberships?tenant_id=...`, **When** authorization succeeds, **Then** the browser redirects to `/admin/app/memberships?tenant_id=...`.
2. **Given** a tenant admin submits an invitation, principal link, role grant, role revoke, principal status, or membership status through an old form URL, **When** the mutation is authorized, **Then** the existing backend service performs the mutation and redirects to React with safe mutation result context.
3. **Given** a tenant admin attempts a platform role assignment or cross-tenant membership change, **When** the old route or React route is used, **Then** the backend denies the request without revealing unauthorized tenant labels or subject identifiers.
4. **Given** the membership audit and access history surfaces are opened, **When** React renders data, **Then** emails, Auth0 subjects, access decisions, audit ids, and tenant labels are safe summaries only.

### User Story 2 - Manage Telegram And Channel Delivery In React Only (Priority: P1)

A platform admin or tenant admin opens old Telegram configuration, alias, webhook validation, link-token, identity, diagnostic, and delivery URLs and lands on the React channel workspace with tenant context preserved.

**Why this priority**: Telegram configuration and delivery diagnostics include sensitive identifiers and link tokens. The migration must prove one-time token behavior and redaction before deleting Jinja.

**Independent Test**: Exercise old Telegram browser GET and POST routes, retained JSON APIs, React channel mutations, link-token creation, alias actions, webhook validation, delivery diagnostics, linked identities, and run status with local-principal and Auth0-shaped tests.

**Acceptance Scenarios**:

1. **Given** an admin opens `/admin/telegram?tenant_id=...`, **When** the tenant is authorized, **Then** the browser redirects to `/admin/app/channels?tenant_id=...&panel=telegram`.
2. **Given** an admin validates a webhook, saves Telegram config, creates aliases, toggles aliases, or creates link tokens, **When** the action uses old browser form routes, **Then** the existing service behavior remains and the browser returns to React.
3. **Given** a link token is created, **When** React and QA evidence are reviewed later, **Then** the raw token appears only in the immediate creation result and never in persisted summaries, logs, screenshots, or exports.
4. **Given** delivery diagnostics, linked identities, or run status are visible, **When** a reviewer scans UI and JSON, **Then** full Telegram ids, private message text, raw webhook payloads, and raw run payloads are absent.

### User Story 3 - Manage Briefing Preferences In React Only (Priority: P1)

A tenant admin or user opens old briefing preference browser URLs for profile editing, save, import, export, admin summaries, and runtime resolution and lands on the React channel briefing workspace or receives retained JSON responses.

**Why this priority**: Briefing preferences can contain private preference values and import/export artifacts. Browser migration must preserve user-safe behavior without leaking raw preference payloads.

**Independent Test**: Exercise old briefing browser GET and POST routes, retained APIs, React preference routes, import/export metadata, admin summaries, tenant-user versus tenant-admin views, and Auth0-shaped principal behavior.

**Acceptance Scenarios**:

1. **Given** an authorized tenant admin opens `/admin/briefing-preferences?tenant_id=...`, **When** the route is requested, **Then** the browser redirects to `/admin/app/channels?tenant_id=...&panel=briefing`.
2. **Given** a tenant user saves preferences, imports JSON, or requests export metadata, **When** the action is authorized, **Then** backend-owned validation and revision checks execute and React receives a safe mutation result.
3. **Given** an admin summary is displayed, **When** the UI and QA artifacts are scanned, **Then** private preference values and raw import payloads are not present.
4. **Given** a cross-tenant principal requests briefing preference data, **When** old or new URLs are used, **Then** the backend fails closed without leaking whether another tenant has preferences.

### Edge Cases

- Old browser URLs include a tenant id the principal is not allowed to access.
- Old form posts omit a tenant id and the principal has no default tenant.
- Invitation, role-grant, membership, alias, token, or briefing mutation targets are stale or missing.
- A link token is created and then the page is refreshed.
- Telegram diagnostics include full external identifiers or private text in raw service data.
- Briefing import payloads contain unsupported fields or oversized content.
- A local-principal tenant user attempts platform-only membership or Telegram actions.
- React route loads with query state from old saved filters.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST redirect old membership browser GET routes to `/admin/app/memberships`, preserving safe tenant id, principal id, membership id, role-grant id, action, saved-filter id, query, and status context.
- **FR-002**: The system MUST keep retained membership JSON and mutation APIs available for React with backend-owned authorization, tenant scoping, validation, idempotency, audit, and redaction.
- **FR-003**: The system MUST prevent tenant admins from granting platform roles or mutating cross-tenant memberships through old routes or React routes.
- **FR-004**: The system MUST redirect old Telegram browser GET routes to `/admin/app/channels`, preserving safe tenant, panel, alias, identity, diagnostic, and saved-filter context.
- **FR-005**: The system MUST keep Telegram config, alias, webhook validation, link-token, identity, delivery diagnostic, and run-status APIs available for React without live Telegram calls in local or CI QA.
- **FR-006**: The system MUST expose raw link tokens only in the immediate creation response and MUST NOT persist, render, log, export, or screenshot raw token values later.
- **FR-007**: The system MUST redirect old briefing preference browser GET routes to `/admin/app/channels`, preserving safe tenant and briefing panel context.
- **FR-008**: The system MUST keep briefing profile save, import, export, summaries, and runtime resolution APIs available for React with backend-owned revision and ownership checks.
- **FR-009**: The system MUST ensure React, redirects, exports, logs, screenshots, and QA docs do not expose raw emails beyond safe labels, Auth0 subjects, full Telegram ids, private channel messages, link tokens after creation, private preference values, raw import payloads, or stack traces.
- **FR-010**: The system MUST delete only the bounded templates `memberships/index.html`, `telegram/index.html`, and `briefing_preferences/index.html` after route tests and React parity evidence pass.
- **FR-011**: The system MUST update admin shell navigation, saved-filter destinations, migration ledger notes, docs, generated TypeScript contracts, QA docs, and Playwright manifest to point to React-only destinations.

### Key Entities

- **Membership React Workspace**: The React page and JSON contracts for users, invitations, principal links, role grants, status changes, access history, and audit.
- **Channel Telegram Briefing Workspace**: The React page and JSON contracts for Telegram config, aliases, link tokens, identities, delivery diagnostics, run status, and briefing preferences.
- **Legacy Browser Redirect**: A former Jinja browser GET or form-post route that now authenticates, applies backend policy, executes retained service behavior when needed, and redirects to React.
- **Safe Mutation Result**: A bounded result containing status, safe summary, revision, audit reference, and artifact reference without raw secret or private payload values.
- **One-Time Token Result**: A creation-only response that can display the token once while all persisted summaries use token metadata or redacted references.

## Success Criteria

- **SC-001**: All old membership, Telegram, and briefing browser URLs are covered by tests that prove React redirects or safe non-Jinja responses.
- **SC-002**: React membership and channel tests cover platform, tenant admin, tenant user, unauthorized, cross-tenant, local-principal, and Auth0-shaped principal paths.
- **SC-003**: Template scanner tests prove `memberships/index.html`, `telegram/index.html`, and `briefing_preferences/index.html` are deleted and unreferenced.
- **SC-004**: Redaction sweeps find no raw Auth0 subjects, raw link tokens after creation, full Telegram ids, private messages, private preference values, raw imports, or stack traces in JSON, HTML, screenshots, logs, or docs.
- **SC-005**: QA document validation, Spec QA, full coverage gate, frontend tests, generated contract checks, and Playwright validation pass for QA045 before Spec 046 begins.
