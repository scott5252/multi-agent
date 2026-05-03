# Feature Specification: Telegram Configuration Console

**Feature Branch**: `codex/017-telegram-configuration-console`  
**Created**: 2026-05-03  
**Status**: Draft  
**Input**: User description: "Add a server-rendered Telegram Configuration Console for platform admins and authorized tenant admins. The console must let administrators view Telegram channel readiness, configure non-secret Telegram settings through safe secret references, validate webhook configuration, manage tenant-specific Telegram enablement, inspect linked Telegram identities without exposing private chat content, issue and revoke one-time link tokens, see recent safe delivery and webhook diagnostics, and understand whether protected Telegram commands are ready for use. The feature must build on existing Spec 006 channel behavior, local-principal admin test mode, Auth0 authorization, admin shell navigation, audit/redaction helpers, secret providers, reliability retries/breakers, and existing Telegram webhook/link-token services. It must never store or display real bot tokens, webhook secrets, private messages, raw prompts, run results, or unauthorized tenant data. Include tenant isolation, role boundaries, stale form conflict recovery, redaction-safe screenshots, docs, PR review notes, testing instructions, and at least 90 percent coverage."

## Clarifications

- Q: How should local QA validate webhook and bot-token behavior without real Telegram side effects? -> A: Use safe fake secret references, local readiness probes, and simulated webhook diagnostics only; never call Telegram during validation (autopilot)
- Q: How should administrators inspect linked Telegram identities without leaking private chat data? -> A: Show tenant, platform identity, status, timestamps, and masked Telegram identifiers only; never render messages, prompts, run results, or raw chat payloads (autopilot)
- Q: How should stale form conflicts be resolved? -> A: Require revision tokens on mutable forms and return a non-destructive conflict state that asks the admin to reload current values (autopilot)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Verify Platform Telegram Readiness (Priority: P1)

Platform administrators need a console that shows whether Telegram is configured
for protected command use, which safe secret references are configured, and
whether the webhook is ready without exposing secret values or contacting
Telegram during local QA.

**Why this priority**: Without safe readiness visibility, admins cannot know
whether protected Telegram commands can be enabled for tenants.

**Independent Test**: Sign in as a platform admin, open `/admin/telegram`,
configure fake local secret references, run a webhook validation action, and
verify readiness, redaction, audit-safe diagnostics, and no real Telegram calls.

**Acceptance Scenarios**:

1. **Given** a platform admin opens the console, **When** settings include safe
   Telegram token and webhook secret references, **Then** the page shows a ready
   status using reference labels only and never displays secret values.
2. **Given** local QA fake references are configured, **When** the admin runs a
   webhook validation action, **Then** the console records a safe diagnostic
   result without sending a request to Telegram.
3. **Given** production mode is active, **When** a Telegram token or webhook
   value is not represented as a safe secret reference, **Then** readiness fails
   closed and explains the missing reference without exposing values.

---

### User Story 2 - Manage Tenant Telegram Enablement (Priority: P2)

Platform admins and tenant admins need to enable or disable Telegram for an
authorized tenant, set tenant-scoped command readiness expectations, and recover
cleanly from stale form submissions.

**Why this priority**: Tenant enablement is the boundary that prevents a global
provider configuration from becoming an implicit cross-tenant channel.

**Independent Test**: Seed two tenants, enable Telegram for Acme as a platform
admin and tenant admin, submit a stale revision, and verify Globex data remains
inaccessible to Acme.

**Acceptance Scenarios**:

1. **Given** a platform admin selected a tenant scope, **When** they enable
   Telegram for that tenant, **Then** only that tenant's enablement record is
   changed and an audit-safe record is stored.
2. **Given** an Acme tenant admin attempts to change Globex settings, **When**
   the request is submitted, **Then** the system denies the request and does not
   reveal whether Globex Telegram settings exist.
3. **Given** a revision token is stale, **When** the form is submitted, **Then**
   no update is applied and the page shows a conflict state with current safe
   values.

---

### User Story 3 - Inspect Linked Identities And Link Tokens (Priority: P3)

Authorized admins need to view linked Telegram identity summaries, issue
one-time link tokens, revoke unused or existing tokens, and understand whether
protected commands are available for linked users without exposing chat content.

**Why this priority**: Link tokens are the trust bridge between platform
identity and Telegram; administrators need safe controls and inspection.

**Independent Test**: Issue a link token, link a simulated Telegram update,
inspect the masked linked identity, revoke a link, and verify protected commands
report not-ready after revocation.

**Acceptance Scenarios**:

1. **Given** a tenant admin issues a one-time token, **When** the console
   returns it, **Then** the token is shown once with expiry and future lists show
   only a safe token fingerprint.
2. **Given** a Telegram user has linked through the existing webhook flow,
   **When** an admin inspects identities, **Then** the page shows masked
   Telegram user/chat identifiers and platform identity only.
3. **Given** an identity is revoked, **When** protected commands are checked,
   **Then** readiness for that identity is marked revoked and future commands
   are denied.

---

### User Story 4 - Review Safe Diagnostics (Priority: P4)

Operators need recent Telegram webhook and delivery diagnostic summaries that
explain readiness, ignored bad secrets, retries, suppression, and command
availability without displaying private messages, raw prompts, run results, or
provider credentials.

**Why this priority**: Diagnostics make the channel supportable after the core
configuration and linking paths are safe.

**Independent Test**: Generate simulated webhook success, duplicate update,
wrong-secret, and delivery retry summaries, then verify the console shows safe
status counts and redacted detail.

**Acceptance Scenarios**:

1. **Given** recent Telegram webhook attempts exist, **When** an admin views
   diagnostics, **Then** the console shows safe counts, timestamps, categories,
   and trace ids only.
2. **Given** delivery attempts failed or retried, **When** diagnostics are
   displayed, **Then** the console summarizes statuses and retry windows without
   rendering destination secrets or message bodies.

### Edge Cases

- Telegram provider token reference is missing.
- Webhook secret reference is missing or configured as a raw value in
  production.
- Local QA uses fake references that intentionally do not resolve to real
  Telegram credentials.
- Tenant admin requests another tenant's Telegram console.
- Platform admin uses platform scope without selecting a tenant-specific form
  target.
- A form revision token is stale.
- A one-time link token is expired, already consumed, or revoked.
- Linked identity contains numeric Telegram ids of varying length.
- Webhook update contains private message text, prompt-like text, or result-like
  text that must never be persisted or rendered.
- A wrong webhook secret is submitted and should be ignored safely.
- Diagnostics exist for multiple tenants.
- Existing Spec 006 in-memory local link state is empty after process restart.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose a server-rendered Telegram Configuration
  Console at `/admin/telegram` under the existing admin shell.
- **FR-002**: System MUST expose JSON admin APIs under `/admin/telegram/api`
  for readiness, tenant configuration, link-token issuance/revocation, linked
  identity summaries, webhook validation, and diagnostics.
- **FR-003**: Platform admins MUST be able to inspect global Telegram provider
  readiness and tenant-specific enablement for authorized tenant scopes.
- **FR-004**: Tenant admins MUST be able to inspect and mutate only their own
  tenant Telegram enablement, link tokens, linked identity summaries, and
  diagnostics.
- **FR-005**: System MUST fail closed for cross-tenant access and denied access
  without confirming unauthorized tenant data exists.
- **FR-006**: System MUST represent Telegram bot token and webhook secret
  configuration only as safe secret references or masked settings labels.
- **FR-007**: System MUST never store or display real bot tokens, webhook
  secrets, private messages, raw prompts, run results, provider credentials, or
  unauthorized tenant data in configuration records, diagnostics, audit records,
  templates, screenshots, or API responses.
- **FR-008**: Production readiness MUST require Telegram provider token and
  webhook secret configuration to use supported secret-reference prefixes.
- **FR-009**: Local and test readiness MAY accept safe fake references and MUST
  label validation as local-only when no external probe is performed.
- **FR-010**: Webhook validation MUST avoid real Telegram side effects by
  default and record only safe diagnostic summaries.
- **FR-011**: Tenant enablement updates MUST use revision tokens for stale
  conflict detection.
- **FR-012**: System MUST record tenant Telegram configuration state, enabled
  flag, allowed protected commands, status note, revision token, updated
  principal, and timestamps.
- **FR-013**: System MUST support issuing one-time Telegram link tokens through
  the existing channel service while storing only safe token metadata for
  console audit and listing.
- **FR-014**: System MUST support revoking pending link tokens and linked
  identities for the authorized tenant.
- **FR-015**: Linked identity inspection MUST show masked Telegram user and chat
  identifiers, tenant id, platform identity id, status, linked/revoked
  timestamps, and protected-command readiness only.
- **FR-016**: Diagnostics MUST include safe categories for webhook validation,
  webhook update handling, delivery attempts, ignored wrong-secret events,
  duplicate updates, and command readiness.
- **FR-017**: System MUST emit audit-safe metadata for readiness checks,
  enablement changes, link-token issue/revoke actions, identity revocations,
  denied access, and webhook validation.
- **FR-018**: The admin navigation registry MUST include "Telegram
  Configuration" and preserve tenant scope.
- **FR-019**: Templates MUST render redaction notices and screenshot-safe text.
- **FR-020**: Tests MUST cover authorization, platform vs tenant scope,
  tenant isolation, secret-reference validation, production guardrails, local
  fake-token QA, webhook readiness without real side effects, tenant forms,
  identity redaction, link-token flows, diagnostics, stale revision conflicts,
  audit records, metrics where available, navigation, browser UI forms, docs,
  and coverage.
- **FR-021**: Documentation MUST include README updates, quickstart validation,
  testing instructions, PR review notes, and non-developer QA guidance.
- **FR-022**: Automated test coverage for relevant code MUST meet or exceed
  the repository's 90 percent coverage threshold.

### Key Entities *(include if feature involves data)*

- **Telegram Provider Readiness**: Safe runtime view of global Telegram
  settings, secret-reference presence, production guardrails, webhook readiness,
  command readiness, and diagnostic timestamps.
- **Tenant Telegram Configuration**: Tenant-scoped enablement record with
  allowed protected commands, status note, revision token, updated principal,
  and timestamps.
- **Telegram Link Token Audit**: Safe metadata for a one-time link token,
  including tenant, issuing principal, token fingerprint, expiry, status, and
  revocation state.
- **Telegram Linked Identity Summary**: Redacted tenant-scoped identity link
  summary with platform identity, masked Telegram user/chat identifiers,
  status, linked/revoked timestamps, and command readiness.
- **Telegram Diagnostic Event**: Safe operational summary for readiness,
  webhook, delivery, and command diagnostics with category, status, trace id,
  timestamps, and redacted metadata.
- **Telegram Configuration Audit**: Audit-safe record for console actions,
  denied access, and readiness validation outcomes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Platform admin browser validation reaches `/admin/telegram` and
  captures redaction-safe screenshots showing readiness and tenant controls.
- **SC-002**: Tenant isolation tests prove an Acme tenant admin cannot read,
  mutate, or infer Globex Telegram configuration, identities, tokens, or
  diagnostics.
- **SC-003**: Production guardrail tests prove raw Telegram token and webhook
  values fail readiness while safe references pass.
- **SC-004**: Link-token tests prove issue, one-time display, simulated link,
  revoke, expiry, and safe fingerprint behavior.
- **SC-005**: Redaction tests prove rendered UI, JSON APIs, diagnostics, and
  audit metadata contain no bot token, webhook secret, private message, prompt,
  run result, or raw chat payload.
- **SC-006**: Stale revision tests prove conflicting tenant form submissions do
  not overwrite current configuration.
- **SC-007**: Relevant automated coverage remains at or above 90 percent.
- **SC-008**: Non-developer QA guide and Playwright screenshots demonstrate
  login and `/admin/telegram` target flows.

## Assumptions

- Existing Spec 006 Telegram webhook and channel service behavior remains the
  command-handling authority; this feature adds governed admin visibility and
  controls around it.
- Local QA uses static fake secret references and simulated webhook validation.
- No production Telegram registration or external Telegram API calls are
  required for this implementation.
- The first implementation stores safe console state in PostgreSQL while Spec
  006's local in-memory channel facade remains available for deterministic QA.
