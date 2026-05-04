# Feature Specification: User Briefing Preferences And Context

**Feature Branch**: `codex/023-user-briefing-preferences-and-context`  
**Created**: 2026-05-04  
**Status**: Draft  
**Input**: User description: "Add tenant-scoped user briefing preferences for recurring and on-demand Daily Intelligence Briefing workflows. Linked users must be able to define location, timezone, news topics, VIP senders, workday hours, commute mode, default calendar/email account references, output style, and optional scheduled briefing time. Admins must inspect safe summaries only. Runtime workflows must resolve preferences by tenant and principal id and pass them to the orchestrator without exposing raw credentials or private data in logs."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Save My Briefing Context (Priority: P1)

A linked tenant user can create and update a Daily Intelligence Briefing
preference profile containing their location, timezone, topics, VIP sender
patterns, workday hours, commute mode, safe account references, style, and
optional scheduled briefing time.

**Why this priority**: The daily briefing workflow cannot produce useful,
personalized output unless the user's context exists before a Telegram or API
trigger arrives.

**Independent Test**: Sign in as a local tenant user, open the briefing
preferences screen, save a valid profile, reload the page, and verify the saved
values are restored without exposing raw credentials.

**Acceptance Scenarios**:

1. **Given** an authenticated Acme tenant user with no profile, **When** they save a valid preference profile, **Then** the system persists the profile for that tenant and principal and returns a new revision.
2. **Given** an authenticated Acme tenant user with an existing profile, **When** they update topics, VIP senders, and style, **Then** the previous revision remains audit-addressable and the head projection reflects only the latest values.
3. **Given** invalid workday hours, timezone, account reference, or scheduled time input, **When** the user submits the profile, **Then** the system rejects the request with field-specific validation errors and does not change the current profile.

---

### User Story 2 - Inspect Safe Admin Summaries (Priority: P2)

A tenant or platform admin can inspect briefing preference readiness and safe
summaries for users in an authorized tenant without seeing private locations,
raw VIP addresses, raw account identifiers, or credentials.

**Why this priority**: Operators need to verify readiness for Daily Intelligence
Briefing rollouts without expanding the privacy or secret exposure boundary.

**Independent Test**: Sign in as a local platform admin, open the admin briefing
preferences screen, and verify the table shows tenant-scoped status, masked
location/timezone summaries, counts, hashes, and revision metadata only.

**Acceptance Scenarios**:

1. **Given** an Acme admin and saved Acme profiles, **When** the admin opens the summary page, **Then** the page lists only Acme users unless the admin explicitly selects another authorized tenant.
2. **Given** a profile containing VIP senders and account references, **When** an admin views the summary, **Then** raw sender addresses and credential-like account values are never rendered.
3. **Given** a Globex profile, **When** an Acme tenant admin requests its principal directly, **Then** the request fails closed and records safe denial evidence.

---

### User Story 3 - Resolve Preferences At Runtime (Priority: P3)

The Telegram/channel runtime can resolve a linked user's latest preference
profile by tenant and principal id and attach a redaction-safe context payload
to a Daily Intelligence Briefing run request.

**Why this priority**: On-demand and scheduled briefing workflows need one
consistent resolver so channel triggers, cron-like schedules, and future
workflow graph execution receive identical preference context.

**Independent Test**: Create a saved profile, call the resolver with matching
tenant and principal context, and verify the returned orchestration context
contains usable preference values plus safe metadata without raw credentials.

**Acceptance Scenarios**:

1. **Given** a Telegram-linked Acme principal with a saved profile, **When** the Daily Intelligence Briefing runtime resolves preferences, **Then** it returns the latest profile for that tenant/principal and a safe summary for audit/log context.
2. **Given** no saved profile, **When** the resolver is called, **Then** it returns a typed missing-profile result so the orchestrator can request setup instead of guessing.
3. **Given** a mismatched tenant or revoked principal, **When** the resolver is called, **Then** it returns no private data and emits a safe denial audit record.

### Edge Cases

- Timezones must be valid IANA identifiers; ambiguous aliases and blank values are rejected.
- Workday start must be earlier than workday end and both must use 24-hour `HH:MM` format.
- Optional scheduled briefing time must be absent or a valid `HH:MM` value in the user's timezone.
- VIP sender entries may be email-like addresses or display-name hints, but stored summaries must mask raw values for admin views.
- Account references must be references such as `delegated:calendar:primary` or `secret-ref:gmail-default`, never OAuth tokens, API keys, passwords, or raw provider credentials.
- Users may disable scheduled delivery while keeping on-demand preferences.
- Existing active runs keep their pinned input context; profile updates affect only future run creation and future scheduled delivery.
- Export/import must preserve tenant/principal ownership and reject cross-tenant imports.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow authenticated tenant users to create, read, and update one active Daily Intelligence Briefing preference profile per `(tenant_id, principal_id)`.
- **FR-002**: System MUST validate location label, IANA timezone, news topics, VIP sender hints, workday hours, commute mode, default calendar account reference, default email account reference, output style, scheduled delivery toggle, and optional scheduled briefing time.
- **FR-003**: System MUST persist immutable profile revision records and a current head projection for fast runtime lookup.
- **FR-004**: System MUST record safe audit events for create, update, validation denial, admin inspection, runtime resolution, missing profile, and tenant/principal denial.
- **FR-005**: System MUST expose API schemas for saving, reading, summarizing, exporting, importing, and resolving briefing preferences.
- **FR-006**: System MUST provide a server-rendered admin/user UI at `/admin/briefing-preferences` using the existing admin shell and local-principal test mode.
- **FR-007**: System MUST ensure admins see safe summaries only: readiness status, timezone, broad location label, counts, masked/fingerprinted VIP and account references, schedule status, style, revision, and timestamps.
- **FR-008**: System MUST fail closed on cross-tenant or unauthorized principal access and MUST NOT leak whether another tenant's raw profile exists.
- **FR-009**: System MUST provide a runtime resolver that accepts tenant id, principal id, source channel, trace id, and optional workflow/run identifiers, then returns the latest preferences and safe context metadata.
- **FR-010**: System MUST pass resolved preferences to Daily Intelligence Briefing orchestration inputs without logging private values or raw credentials.
- **FR-011**: System MUST support JSON export/import for a user's own profile and reject import documents whose tenant or principal does not match the authenticated actor.
- **FR-012**: System MUST integrate with existing audit/redaction helpers and never persist raw credential values in preference fields, diagnostics, logs, or admin summaries.
- **FR-013**: System MUST include tenant isolation, redaction, validation, repository, API, UI, runtime resolver, docs, and QA fixture tests.

### Key Entities

- **BriefingPreferenceProfile**: The current head projection for one tenant/principal. Includes profile id, tenant id, principal id, revision id, safe preference fields, schedule flags, redaction metadata, and timestamps.
- **BriefingPreferenceRevision**: Immutable version of a profile update. Includes revision sequence, content digest, changed-by principal, redaction-safe audit summary, and canonical preference payload.
- **BriefingPreferenceAuditEvent**: Append-only safe event for user/admin/runtime operations.
- **BriefingPreferenceRuntimeContext**: Resolver output passed into a Daily Intelligence Briefing run with private preferences plus safe metadata and provenance.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A tenant user can save and reload a full preference profile through the browser UI in under 2 minutes during local QA.
- **SC-002**: Runtime preference lookup by tenant and principal completes in under 50 ms excluding database connection time for a single profile.
- **SC-003**: Cross-tenant API, repository, and runtime tests show zero leakage of another tenant's raw profile fields.
- **SC-004**: Admin summary and audit tests prove raw VIP sender values, raw account references, and credential-looking strings are absent from rendered HTML and safe logs.
- **SC-005**: Generated manual QA guide, API checks, Playwright screenshots, Ruff, mypy, and pytest coverage gates pass for QA023.

## Assumptions

- Daily Intelligence Briefing profile data is operational preference state, so v1 stores it in dedicated PostgreSQL tables with immutable revisions rather than only in the generic memory API. Runtime may link audit metadata to memory policy where useful.
- A principal id from existing local/Auth0 principal context is the user ownership key; Telegram-linked identities map to the same tenant/principal through existing channel identity records.
- Account fields store user-selected references only. Creating OAuth grants or delegated credentials is out of scope for this feature.
- Scheduled dispatch execution is out of scope for this feature; v1 stores schedule preferences and readiness for future scheduler integration.
- Import/export is JSON-only and scoped to the authenticated user's own profile in v1.

## Clarifications

- Q: Should briefing preferences be stored only as immutable memory or as a first-class table with immutable revisions? -> A: Use dedicated PostgreSQL tables with immutable revisions and a head projection, while preserving compatibility with the immutable memory policy through safe runtime/audit metadata. (autopilot)

## Constitution Impact

- **Durable By Default**: Preferences, revisions, and runtime resolution events persist in PostgreSQL and survive process restarts.
- **Immutable State And Memory**: Profile changes create immutable revision records and update a head projection.
- **Contract-First Agent Coordination**: API, import/export, and runtime resolver contracts are versioned in this feature.
- **Security With Practical Development Ergonomics**: Local-principal QA exercises authorization, tenant scoping, and redaction behavior.
- **Operability Is A Product Requirement**: Safe audit events and redaction metadata explain profile readiness and runtime resolution.
- **Spec-Driven Delivery**: Spec, plan, tasks, contracts, QA docs, and implementation remain traceable.
- **Test And Documentation Discipline**: Tasks include tests, QA guides, README/quickstart updates, and quality gates.
- **Tenant Isolation And Fair Scheduling**: Every profile, revision, summary, import/export, and resolver call is tenant scoped and fail-closed.
- **Version-Pinned Execution**: Runtime resolver output includes profile revision id so created runs can pin the context they used.
- **Secret Hygiene And Controlled Tool Access**: Account fields are references only; raw credentials and tokens are rejected.
- **Tiered Storage For Large Payloads**: Preference payloads are bounded JSON; large briefing artifacts remain outside this feature.
- **Human Approval Is Durable State**: No approval flow changes; future setup prompts can use existing durable wait-state semantics.
