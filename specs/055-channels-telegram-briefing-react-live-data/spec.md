# Feature Specification: Channels, Telegram, Briefing React Live Data

**Feature Branch**: `codex/055-channels-telegram-briefing-react-live-data`  
**Created**: 2026-05-07  
**Status**: Draft  
**Input**: User description: "Create a feature specification for Channels, Telegram, Briefing React Live Data. Replace deterministic channel/Telegram/briefing builders with live projections from Telegram tenant config, command alias, link-token audit, linked identity, delivery attempt, webhook receipt, channel run, notification, briefing preference profile/revision/import/export, and audit services. React must show real channel readiness, real Telegram configuration state, real aliases, real identity links, real delivery diagnostics, real run status links, and real Daily Intelligence Briefing preference summaries."

## Clarifications

### Session 2026-05-07

- Q: What sources are authoritative for channel, Telegram, and briefing React projections? -> A: (autopilot) Existing Telegram config services/repositories, command alias services, link-token audit repositories, linked identity repositories, delivery/notification repositories, channel run APIs, briefing preference services, artifact metadata, and audit services are authoritative; React builders may only compose backend-owned projections or truthful empty/denied/unavailable states.
- Q: How should platform, tenant administrator, and tenant user scope be resolved? -> A: (autopilot) The backend resolves scope from the authenticated principal, local-principal/Auth0-shaped grants, requested tenant, and access-control decisions; browser state never expands scope, and all cross-tenant config, alias, identity, delivery, run, preference, import/export, and audit IDs fail closed.
- Q: What Telegram and channel details may be rendered? -> A: (autopilot) Only safe readiness labels, masked Telegram identity labels, command names, safe delivery/run summaries, timestamps, trace references, artifact references, and audit references may render; bot tokens, webhook secrets, link tokens after creation, full Telegram identifiers, private messages, raw webhook payloads, raw run payloads, and authorization headers remain absent.
- Q: Which durable actions are in scope for validation? -> A: (autopilot) Alias save/enable/disable/delete, link-token creation/revocation, webhook validation, briefing preference save/import/export, and safe delivery diagnostic refresh actions must route through existing services/repositories with idempotency, revision, denial, stale-conflict, one-time token, artifact, and audit evidence.
- Q: How will QA prove local-principal channel and briefing behavior? -> A: (autopilot) qa055 seed/setup creates real local-principal Telegram config, aliases, linked identities, link-token audits, webhook receipts, delivery attempts, notifications, channel run references, briefing preferences, imports/exports, and audit rows without external Telegram/provider calls; Playwright performs at least one visible persisted action and verifies it through backend API or redaction-safe database evidence.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Review Live Channel And Briefing State (Priority: P1)

A tenant administrator or platform operator opens the channel, Telegram, and briefing workspace and sees only authorized live readiness, configuration, alias, identity, delivery, run, notification, and briefing preference state for the active scope. Empty tenants show truthful empty or unavailable states instead of deterministic QA036 rows.

**Why this priority**: Channel and briefing screens explain whether users can receive operational notifications and Daily Intelligence Briefings. Operators must trust that readiness, aliases, identities, and preferences reflect durable platform state.

**Independent Test**: Can be tested by loading the workspace and JSON routes against an empty qa055 database and a seeded qa055 database, then comparing visible rows to persisted Telegram config, alias, identity, delivery, run, notification, and briefing preference records.

**Acceptance Scenarios**:

1. **Given** an authorized tenant administrator and an empty live tenant, **When** the administrator opens the channel workspace, **Then** Telegram config, aliases, linked identities, delivery diagnostics, run links, notifications, and briefing preference panels show truthful empty, denied, or unavailable states.
2. **Given** an authorized tenant administrator and persisted Telegram configuration, aliases, identities, delivery attempts, channel runs, notifications, and briefing preferences, **When** the administrator opens the workspace, **Then** every visible row matches an authorized live record for that tenant.
3. **Given** a platform operator, **When** the operator reviews platform-scoped channel readiness, **Then** the workspace shows only platform-authorized readiness and audit evidence.
4. **Given** a cross-tenant or unauthorized principal, **When** the principal requests channel or briefing data, **Then** the response fails closed without exposing Telegram identifiers, aliases, delivery details, run links, private preferences, or tenant labels from another tenant.

---

### User Story 2 - Inspect Redaction-Safe Delivery And Telegram Evidence (Priority: P2)

An authorized administrator inspects Telegram readiness, alias rules, linked identities, delivery diagnostics, webhook receipts, channel run links, notifications, and audit details with enough context to troubleshoot safely while sensitive Telegram identifiers, tokens, private messages, and raw payloads remain masked or absent.

**Why this priority**: Telegram and channel data can contain private user identifiers, webhook secrets, link tokens, private messages, and run references. The UI must help reviewers troubleshoot without leaking sensitive material.

**Independent Test**: Can be tested by seeding sensitive-adjacent Telegram and channel records, then verifying JSON responses, browser text, screenshots, QA docs, and artifacts expose only masked labels, safe summaries, and authorized references.

**Acceptance Scenarios**:

1. **Given** Telegram tenant config and webhook state, **When** an authorized administrator reviews readiness, **Then** the UI shows safe readiness, mode, status, and audit summaries without bot tokens, webhook secrets, or authorization headers.
2. **Given** command aliases and linked identities, **When** a reviewer opens the details, **Then** aliases, status, owner summaries, and masked identity labels appear without full Telegram IDs or private messages.
3. **Given** delivery attempts, webhook receipts, notifications, and channel run links, **When** diagnostics are viewed, **Then** the UI shows safe delivery state, timestamps, trace references, and run links without raw update payloads or unauthorized run data.
4. **Given** briefing preference profiles and revisions, **When** preferences are viewed, **Then** summaries, enabled state, delivery channel, and safe revision/import/export evidence appear without private briefing content or raw preference payloads.

---

### User Story 3 - Exercise Durable Channel And Briefing Actions (Priority: P3)

An authorized administrator performs at least one safe visible channel or briefing action and the result persists through backend services. Examples include saving a Telegram alias, creating a link token, validating webhook readiness, saving briefing preferences, importing preferences, or creating an export reference.

**Why this priority**: The live-data migration must prove that action panels are not browser-only forms or fixed success messages. Channel and briefing actions need persisted idempotency, audit, redaction, and conflict evidence.

**Independent Test**: Can be tested by performing one visible safe action in Playwright, then verifying the persisted result through the same backend API or a redaction-safe qa055 database query.

**Acceptance Scenarios**:

1. **Given** an authorized tenant administrator, **When** the administrator saves a Telegram alias or briefing preference, **Then** the mutation returns persisted result evidence and the refreshed workspace reflects the change.
2. **Given** an authorized administrator creating a link token, **When** the action succeeds, **Then** the token is shown only once, only as allowed by the backend contract, and later responses show safe audit metadata without the token value.
3. **Given** a webhook validation or briefing import/export action, **When** the action completes, **Then** the result is persisted, audited, redaction-safe, and scoped to the tenant.
4. **Given** a stale, denied, duplicate, or invalid action, **When** the administrator submits it, **Then** the system returns safe conflict, validation, denied, replayed, or unavailable evidence without fabricating success.

---

### Edge Cases

- Empty tenants return truthful empty states for Telegram config, aliases, linked identities, delivery diagnostics, webhook receipts, notifications, channel runs, and briefing preferences.
- Disabled Telegram configuration returns unavailable or not-ready state without invented aliases or deliveries.
- Link tokens are displayed only at creation time and never re-rendered from list/detail routes.
- Full Telegram identifiers, bot tokens, webhook secrets, authorization headers, private channel messages, raw update payloads, raw run payloads, raw briefing content, local paths, stack traces, and unauthorized tenant labels never render.
- Alias enable, disable, delete, duplicate, stale, and unsupported command states remain distinguishable through safe statuses.
- Delivery diagnostics are bounded when many attempts exist.
- Channel run links must pass access checks and avoid exposing unauthorized run details.
- Briefing import/export artifact references must use governed artifact metadata only.
- Cross-tenant IDs fail closed for config, aliases, identities, link-token audit, webhook receipts, deliveries, notifications, runs, preferences, imports, exports, and audits.
- Auth0-shaped principals and local-principal QA identities produce equivalent authorization outcomes for equivalent roles.
- Generated TypeScript contracts accept empty channel/briefing envelopes and reject malformed or unsafe payloads.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST replace deterministic production channel, Telegram, and briefing React data with authorized live projections from durable Telegram config, alias, identity link, link-token audit, webhook receipt, delivery attempt, channel run, notification, briefing preference, import/export, and audit records.
- **FR-002**: The system MUST return truthful empty, denied, or unavailable states when no live authorized channel or briefing records exist for the active scope.
- **FR-003**: The system MUST preserve platform, tenant administrator, tenant user, auditor, and support boundaries for all channel, Telegram, briefing, run-link, and mutation surfaces.
- **FR-004**: The system MUST expose Telegram configuration readiness only from persisted tenant config and service readiness evidence, never from fixed QA data.
- **FR-005**: The system MUST expose command aliases, alias actions, linked identities, link-token audits, and webhook validation state only from persisted records and backend service outcomes.
- **FR-006**: The system MUST expose delivery diagnostics, webhook receipts, notifications, and channel run links only from authorized persisted records and safe run references.
- **FR-007**: The system MUST expose briefing preference profile, revision, import, export, and runtime-resolution summaries only from persisted preference services and artifact references.
- **FR-008**: The system MUST keep raw bot tokens, webhook secrets, link tokens after creation, full Telegram identifiers, authorization headers, private channel messages, raw webhook payloads, raw run payloads, raw briefing content, secrets, credential values, local filesystem paths, stack traces, and unauthorized tenant labels out of React contracts, redirects, exports, screenshots, QA artifacts, logs, and docs.
- **FR-009**: The system MUST provide durable safe mutations for at least one visible channel, Telegram, or briefing action and return persisted result evidence, safe conflict details, denied states, replayed states, or unavailable states as appropriate.
- **FR-010**: The system MUST validate at least one safe channel or briefing action through Playwright and post-UI API or redaction-safe database verification before the spec is marked complete.
- **FR-011**: The system MUST update generated React TypeScript contracts so frontend code accepts live empty-state channel/briefing envelopes and rejects malformed or unsafe payloads.
- **FR-012**: The system MUST validate both Auth0-shaped backend route behavior and local-principal browser behavior for platform, tenant, and cross-tenant channel/briefing surfaces.
- **FR-013**: The system MUST update live-data scanner guardrails so former deterministic qa036 channel, Telegram, and briefing markers fail when found in production builders or React routes while remaining allowed in test-only and historical spec artifacts.
- **FR-014**: The system MUST produce QA environment, QA guide, UI walkthrough, manual QA user guide, reviewer notes, Playwright evidence, post-UI persistence evidence, and curl regression evidence for qa055.

### Key Entities *(include if feature involves data)*

- **Telegram Tenant Config**: Tenant-scoped configuration, readiness, mode, webhook state, token audit summary, and safe diagnostics.
- **Command Alias**: Tenant-scoped command mapping with command text, workflow or briefing target, enabled state, revision, and audit evidence.
- **Linked Identity**: Association between a principal and a Telegram identity with masked display, status, linked/revoked timestamps, and audit summary.
- **Link Token Audit**: One-time linking token lifecycle evidence with creation, consumption, revocation, expiration, masked actor, and safe status.
- **Webhook Receipt**: Persisted Telegram update receipt with safe summary, delivery state, trace, duplicate status, and redacted metadata.
- **Delivery Attempt**: Notification or channel delivery attempt with destination summary, status, retry, latency, trace, and redacted failure summary.
- **Channel Run Link**: Safe reference from a channel request or notification to an authorized workflow run and status summary.
- **Briefing Preference Profile**: Tenant/user preference head, revisions, delivery channel choices, enabled state, import/export references, and runtime-resolution evidence.
- **Channel/Briefing Action Result**: Safe mutation outcome containing accepted, replayed, stale, validation, denied, unavailable, one-time token, artifact, revision, or audit evidence.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In an empty qa055 database, every channel, Telegram, and briefing JSON route and browser panel returns a truthful empty, denied, or unavailable state with zero deterministic aliases, identities, deliveries, notifications, webhook receipts, channel runs, preferences, imports, exports, or audit rows.
- **SC-002**: In a seeded qa055 database, channel, Telegram, and briefing JSON routes and browser panels return only persisted records authorized for the active tenant or platform scope.
- **SC-003**: A Playwright flow performs at least one visible channel, Telegram, or briefing action and a post-UI API or QA database check proves the resulting state persisted.
- **SC-004**: Auth0-shaped backend tests and local-principal Playwright tests cover platform, tenant, and cross-tenant channel/briefing access.
- **SC-005**: Redaction tests confirm bot tokens, webhook secrets, link tokens after creation, full Telegram identifiers, authorization headers, private messages, raw webhook payloads, raw run payloads, raw briefing content, secrets, local paths, stack traces, unauthorized tenant labels, and credential values are absent from React responses, screenshots, QA docs, and artifacts.
- **SC-006**: Generated TypeScript contract checks, focused backend tests, focused frontend tests, scanner tests, QA document validation, Spec QA, Playwright validation, post-UI persistence verification, and multi-agent curl validation all pass before the queue advances.

## Assumptions

- Existing Telegram config services, command alias services, link-token audit services, linked identity repositories, delivery/notification repositories, channel run APIs, briefing preference services, artifact references, and audit services remain the authoritative source for channel and briefing state.
- QA seed data may create real Telegram config, aliases, linked identities, link-token audit records, webhook receipts, delivery attempts, notifications, channel run references, briefing preferences, imports, exports, and audit rows through documented setup flows, services, repositories, public/admin APIs, or safe scripts.
- Local QA actions use local-principal identities and deterministic database rows only; they do not call Telegram, real identity providers, model providers, external tools, credentials, or outbound resources.
- Test fixtures with former qa036 markers may remain under test-only or historical spec paths but must not be imported by production routes or production projection builders.
- This spec does not remove historical specs, test fixtures, or docs solely because they contain old deterministic markers.
- The dirty worktree is intentionally preserved across specs, and no Git commit is required before or after this spec while the autopilot continues.
