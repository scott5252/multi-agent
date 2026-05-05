# Feature Specification: React Channel, Telegram, And Briefing Preferences

**Feature Branch**: `codex/036-react-channel-telegram-and-briefing-preferences`  
**Created**: 2026-05-05  
**Status**: Draft  
**Input**: User description: "Create a feature specification for React Channel, Telegram, and Briefing Preferences. Platform admins, authorized tenant admins, and authorized tenant users need an intuitive UI for channel readiness, Telegram tenant enablement, safe secret-reference configuration, webhook validation, natural-language aliases such as `Morning briefing`, protected alias readiness, linked Telegram identities, one-time link tokens, delivery attempts, webhook diagnostics, user-facing run status links, and Daily Intelligence Briefing preference profiles. Preference profiles must cover location, timezone, news topics, VIP sender hints, workday hours, commute mode, default account references, output style, and optional scheduled briefing time. The UI must not display real bot tokens, webhook secrets, full Telegram user or chat identifiers, link tokens after creation, private messages, raw preference values in admin summaries, raw prompts, run results, or unauthorized tenant data."

## Clarifications

### Session 2026-05-05

- Q: Is user-facing run status in scope for this migration slice? A: Include safe run status links and summaries only; exclude raw run inspection, raw inputs, prompts, completions, and run results. (autopilot)
- Q: How are one-time link tokens displayed? A: Show the token value only in the immediate creation result, then replace it with masked status, expiration, consumption state, and audit evidence. (autopilot)
- Q: What alias actions are in scope? A: Include tenant-scoped alias create, edit, disable, delete, readiness refresh, and idempotent replay handling. (autopilot)
- Q: How much delivery history should the UI show? A: Show bounded recent delivery attempts and webhook receipts with safe status categories, retry context, run link eligibility, trace references, and audit references. (autopilot)
- Q: What is the preference import/export scope? A: Allow authorized users to import/export their own preference profile and tenant admins to review redacted summaries and safe artifact metadata only. (autopilot)
- Q: Does scheduled briefing time create an actual schedule? A: Treat scheduled briefing time as profile metadata until a scheduler feature exists; do not promise delivery scheduling from this UI. (autopilot)
- Q: How should webhook validation refresh work? A: Use explicit authorized validation actions that return mock-safe local evidence, readiness status, timestamp, and audit reference. (autopilot)
- Q: What can tenant administrators manage? A: Tenant administrators are limited to their tenant settings, aliases, link-token requests, masked identities, delivery diagnostics, safe preference summaries, and audit evidence. (autopilot)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Review Channel And Telegram Readiness (Priority: P1)

Platform administrators and authorized tenant administrators need one safe workspace that explains channel readiness, Telegram tenant enablement, webhook status, credential-reference readiness, linked identity coverage, and actionable next steps without exposing bot tokens, webhook secrets, private Telegram identifiers, or private messages.

**Why this priority**: Administrators must understand whether Telegram and channel delivery are ready before alias delivery, link-token creation, or briefing preferences can be trusted.

**Independent Test**: Sign in as a platform administrator and as an Acme tenant administrator, open the React channel workspace, and verify readiness cards, tenant enablement state, safe secret-reference summaries, webhook validation controls, linked identity summaries, and denied states render with no unsafe identifiers or secret values.

**Acceptance Scenarios**:

1. **Given** Telegram tenant configuration exists for Acme and Globex, **When** a platform administrator opens the channel workspace, **Then** they see platform-wide readiness and authorized tenant readiness summaries with safe labels and no raw token values.
2. **Given** an Acme tenant administrator opens the workspace, **When** the tenant scope is Acme, **Then** they see only Acme readiness, tenant enablement, linked identity summaries, webhook status, and safe remediation guidance.
3. **Given** webhook validation has not recently run, **When** an authorized administrator triggers validation, **Then** the result shows safe status, timestamp, audit reference, and next step without calling live Telegram in local QA.
4. **Given** secret references are missing, stale, or not ready, **When** readiness is rendered, **Then** the page shows safe reference labels or readiness categories without displaying secret values or provider headers.

---

### User Story 2 - Manage Aliases, Identity Links, Delivery Diagnostics, And Run Links (Priority: P2)

Tenant administrators need guided controls for natural-language Telegram aliases, protected alias readiness, one-time link-token creation, linked identity review, delivery attempt diagnostics, webhook update summaries, and user-facing run status links.

**Why this priority**: Aliases and delivery diagnostics are the operational core of Telegram-triggered workflows such as `Morning briefing`, and administrators need safe evidence when delivery fails or an identity is not linked.

**Independent Test**: In Acme tenant scope, create or update a safe alias, verify protected alias readiness, create a link token, confirm the token is visible only once with expiration guidance, review linked identities and delivery attempts, and open a safe run status link that omits private messages and run results.

**Acceptance Scenarios**:

1. **Given** an authorized tenant administrator manages aliases, **When** they create, edit, disable, or delete a natural-language alias, **Then** the UI displays backend-owned validation, idempotency, protected readiness, and audit evidence.
2. **Given** a link token is created for Telegram identity linking, **When** the creation succeeds, **Then** the token value is shown only in the creation result and subsequent page loads show only masked token status, expiration, and audit evidence.
3. **Given** delivery attempts exist for alias-triggered runs, **When** the administrator opens diagnostics, **Then** they see bounded attempts, delivery status, safe error categories, timestamps, retry context, Bot API boundary status, and audit references without private message text.
4. **Given** a user-facing run status link is available, **When** an authorized user opens it from the React workspace, **Then** they see safe run status and next steps without raw run inputs, raw prompts, completions, private Telegram messages, or unauthorized tenant content.

---

### User Story 3 - Manage Daily Briefing Preference Profiles (Priority: P3)

Authorized tenant users need a guided Daily Intelligence Briefing preference profile screen, and administrators need safe summaries that help support users without revealing private preference values.

**Why this priority**: Preference profiles make the Daily Briefing workflow useful for end users, but private values such as VIP sender hints and account references require stricter redaction than ordinary tenant settings.

**Independent Test**: Sign in as an authorized Acme tenant user, open the briefing preferences screen, update location, timezone, topics, VIP sender hints, workday hours, commute mode, default account references, output style, and optional scheduled time, then verify tenant administrators see only safe summaries and import/export evidence.

**Acceptance Scenarios**:

1. **Given** an authorized tenant user opens their briefing preferences, **When** they save changes, **Then** the UI shows validated profile status, immutable revision evidence, runtime resolution readiness, and safe success messaging.
2. **Given** preference values include private topics, VIP hints, account references, or location data, **When** a tenant administrator reviews profile summaries, **Then** they see redacted readiness summaries instead of raw private values.
3. **Given** a user imports or exports preference data, **When** the action completes, **Then** the UI shows safe artifact metadata, row or field counts, revision evidence, and audit references without raw private preference content.
4. **Given** an optional scheduled briefing time is configured before a scheduler exists, **When** the profile is displayed, **Then** the UI labels it as profile preference evidence rather than promising delivery scheduling.

### Edge Cases

- Telegram tenant configuration is disabled while aliases or linked identities still exist.
- Secret references exist but readiness cannot be proven.
- Webhook validation is stale, failed, or unavailable.
- A tenant administrator attempts to view or mutate another tenant's aliases, link tokens, identities, diagnostics, or briefing preferences.
- A tenant user attempts to view another user's briefing profile.
- Link-token creation succeeds but the user refreshes the page.
- Alias text collides with an existing protected alias or command shortcut.
- Delivery diagnostics include retryable and non-retryable failure categories.
- A delivery attempt references a run that the current user is not authorized to inspect.
- Preference import contains invalid timezone, workday hours, commute mode, account reference, or output style.
- Audit persistence is unavailable for a protected alias, link-token, webhook validation, delivery diagnostic, or preference mutation action.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide protected React channel, Telegram, alias, delivery diagnostic, run-status, and briefing preference workspaces for authorized platform administrators, tenant administrators, and tenant users.
- **FR-002**: The system MUST preserve existing server-rendered channel, Telegram, and briefing preference fallbacks until React migration parity is explicitly proven by a later spec.
- **FR-003**: The system MUST show backend-owned channel readiness, Telegram tenant enablement, webhook status, secret-reference readiness, linked identity coverage, delivery health, and safe remediation guidance.
- **FR-004**: Platform administrators MUST be able to review authorized platform-wide and tenant-specific channel and Telegram readiness without raw secrets, full Telegram identifiers, private messages, or unauthorized tenant content.
- **FR-005**: Tenant administrators MUST see and mutate only their active tenant's Telegram settings, aliases, link-token requests, linked identity summaries, delivery diagnostics, webhook validation results, and safe preference summaries.
- **FR-006**: Tenant users MUST see and mutate only their own authorized Daily Intelligence Briefing preference profile and safe run-status links.
- **FR-007**: The system MUST provide explicit webhook validation actions that return safe status, timestamp, readiness evidence, and audit reference.
- **FR-008**: The system MUST support natural-language alias create, edit, disable, delete, readiness refresh, and protected alias validation for aliases such as `Morning briefing`.
- **FR-009**: Alias mutation results MUST show backend-owned validation, idempotency replay state, protected readiness, revision or conflict evidence, and audit references.
- **FR-010**: One-time link-token creation MUST display the token only in the immediate creation result and subsequent views MUST show only masked status, expiration, consumption state, and audit evidence.
- **FR-011**: Linked Telegram identity summaries MUST use masked labels and MUST NOT display full Telegram user ids, chat ids, usernames, or private channel messages.
- **FR-012**: Delivery attempt diagnostics MUST be bounded and MUST show safe status, attempt time, retry category, Bot API boundary status, run status link eligibility, and audit or trace references.
- **FR-013**: User-facing run status links MUST show safe progress, status, next steps, and artifact references without raw run payloads, prompts, completions, private messages, or unauthorized tenant content.
- **FR-014**: Briefing preference profiles MUST support location, timezone, news topics, VIP sender hints, workday hours, commute mode, default account references, output style, and optional scheduled briefing time.
- **FR-015**: Preference saves MUST produce immutable revision evidence, runtime resolution readiness, safe conflict handling, and audit references.
- **FR-016**: Preference admin summaries MUST redact private raw values and show only safe readiness summaries, counts, masked account references, revision metadata, and audit-safe status.
- **FR-017**: Preference import and export actions MUST use safe artifact metadata and MUST NOT render raw private preference values in admin summaries, screenshots, or QA evidence.
- **FR-018**: Empty, loading, stale, denied, dependency-unavailable, audit-unavailable, and validation-error states MUST be visible and actionable for every primary section.
- **FR-019**: Protected actions MUST fail closed when authorization, tenant scoping, revision validation, idempotency, link-token safety, secret readiness, or audit persistence cannot be proven.
- **FR-020**: The workspaces MUST be validated in both Auth0-backed production-style principal mode and `AUTH_MODE=local_principal` mode.
- **FR-021**: QA guides, screenshots, JSON evidence, and export metadata MUST exclude real bot tokens, webhook secrets, full Telegram identifiers, one-time tokens after creation, private messages, raw preference values, raw prompts, run results, raw tool payloads, local filesystem paths, fake QA secret values, and unauthorized tenant data.

### Key Entities

- **Channel Readiness Dashboard**: Scope-aware page data containing channel status, Telegram tenant readiness, webhook status, secret-reference readiness, identity coverage, diagnostics summaries, and safe states.
- **Telegram Tenant Configuration**: Tenant-scoped enablement and readiness settings for Telegram delivery, webhook validation, safe secret references, and delivery boundary status.
- **Telegram Alias**: Tenant-scoped natural-language trigger with command target, protected readiness status, revision, lifecycle state, and audit evidence.
- **Link Token Result**: One-time identity linking result containing immediate token display, expiration, consumption state, masked follow-up state, and audit reference.
- **Linked Telegram Identity Summary**: Masked identity projection that connects a principal or tenant user to a Telegram identity without full user or chat identifiers.
- **Delivery Attempt Summary**: Bounded diagnostic record for Telegram delivery and webhook update handling with safe status, retry category, run link eligibility, and trace or audit references.
- **Run Status Link**: Authorized safe link or embedded summary for user-facing run status that excludes raw run content and private messages.
- **Briefing Preference Profile**: Tenant/principal-scoped preference head and immutable revision history for Daily Intelligence Briefing context and output preferences.
- **Briefing Preference Import/Export**: Audited action for portable preference metadata that uses safe artifact references and redacted summaries.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A platform administrator can identify Telegram/channel readiness, stale webhook validation, linked identity coverage, and delivery health for authorized tenants in under 90 seconds.
- **SC-002**: A tenant administrator can create or update a safe alias, validate protected readiness, and view audit evidence without seeing another tenant's settings or identities.
- **SC-003**: A one-time link token is visible only at creation and is absent from subsequent dashboard, diagnostic, screenshot, and JSON evidence captures.
- **SC-004**: Delivery diagnostics show bounded safe attempt rows and run status eligibility without private message text or raw run results.
- **SC-005**: An authorized tenant user can update a complete Daily Briefing preference profile in under 3 minutes with field-level validation and revision evidence.
- **SC-006**: Tenant administrators can support briefing users through safe summaries without raw private preference values.
- **SC-007**: Automated validation proves both Auth0-shaped principal routing and local-principal browser login for protected React channel, Telegram, and preference routes.
- **SC-008**: Redaction scans over QA JSON evidence, screenshots, and export metadata find no fake secret values, real-token markers, full Telegram identifiers, private messages, raw preference values, raw prompts, run results, local paths, or unauthorized tenant labels.

## Assumptions

- React workspaces consume existing channel, Telegram, alias, delivery, run status, and briefing preference services through explicit backend-owned contracts.
- Local QA uses deterministic fake-secret references and mock-safe Telegram delivery behavior.
- Optional scheduled briefing time is profile metadata until a scheduler is explicitly provided by another feature.
- User-facing run status links are safe status summaries, not raw run inspection pages.
- Link-token values are intentionally ephemeral and cannot be recovered after the creation result.
- Existing server-rendered pages remain available as fallbacks until Spec 037.
