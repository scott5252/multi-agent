# Feature Specification: Telegram Natural-Language Trigger Delivery Persistence

**Feature Branch**: `codex/022-telegram-natural-language-trigger-delivery-persistence`  
**Created**: 2026-05-04  
**Status**: Draft  
**Input**: User description: "Add production Telegram command delivery for tenant workflows. Tenants must be able to configure aliases such as \"Morning briefing\" or \"/briefing\" that map to a published workflow version, require linked identities for protected aliases, enforce tenant Telegram configuration at runtime, persist Telegram link tokens and identity links in PostgreSQL, and send final run results back through the Telegram Bot API using safe secret references. The Daily Intelligence Briefing alias must start the published workflow when a linked user sends \"Morning briefing\" and must deliver the final briefing or partial-failure note to the same chat."

## Clarifications

### Session 2026-05-04

- Q: Should local QA perform real Telegram Bot API calls? -> A: No; use a mocked Bot API client and record deterministic delivery attempts (autopilot)
- Q: What alias matching should be used for natural-language triggers? -> A: Tenant-scoped, case-insensitive, trimmed exact alias matching after whitespace normalization (autopilot)
- Q: How are protected aliases authorized? -> A: Linked Telegram identities are required before any tenant workflow alias can start a run (autopilot)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configure Tenant Telegram Aliases (Priority: P1)

Tenant administrators configure command aliases such as `Morning briefing` and `/briefing` that point to a published workflow version. The alias list is visible in the existing Telegram admin console, stores only safe workflow identifiers and policy metadata, and can be updated without exposing bot tokens or webhook secrets.

**Why this priority**: Without tenant-managed aliases, a Telegram message cannot map to a durable published workflow version.

**Independent Test**: Create an alias through `/admin/telegram/api/aliases`, verify it appears on `/admin/telegram`, and confirm the response never includes raw Telegram secrets.

**Acceptance Scenarios**:

1. **Given** a tenant admin with Telegram configuration permissions, **When** they create the `Morning briefing` alias for a published workflow version, **Then** the alias is persisted for that tenant and appears in the alias list.
2. **Given** an existing alias and stale revision token, **When** the admin submits an update, **Then** the system rejects the write with a conflict and preserves the current alias.
3. **Given** a tenant admin from another tenant, **When** they query aliases for a tenant they do not belong to, **Then** access fails closed.

---

### User Story 2 - Trigger Published Workflows From Telegram Aliases (Priority: P1)

A linked Telegram user sends `Morning briefing` or `/briefing` to the bot. The platform verifies webhook idempotency, tenant enablement, provider readiness, linked identity status, alias policy, and then starts the configured published workflow version with the message and Telegram context.

**Why this priority**: This is the primary runtime value of the feature and closes the current gap where only `/run <workflow_id>` works.

**Independent Test**: Link a Telegram chat, configure the alias, post a Telegram update containing `Morning briefing`, and verify a run is created for the configured workflow version exactly once.

**Acceptance Scenarios**:

1. **Given** a linked Telegram identity and an enabled tenant configuration, **When** the user sends `Morning briefing`, **Then** the alias starts the configured published workflow version and returns a safe confirmation for the same update.
2. **Given** the same update is received again, **When** Telegram retries the webhook, **Then** the system replays the original response without creating another run.
3. **Given** the Telegram identity is not linked or has been revoked, **When** the user sends a protected alias, **Then** the request is rejected with a safe user-visible message.
4. **Given** tenant Telegram configuration is disabled or provider readiness is incomplete, **When** a linked user sends an alias, **Then** the workflow is not started and diagnostics record the safe denial reason.

---

### User Story 3 - Deliver Final Results To The Same Telegram Chat (Priority: P2)

When an alias-triggered run reaches a final state, the platform formats the final briefing or partial-failure note and sends it to the original Telegram chat through the Bot API boundary. Delivery attempts are persisted with safe fingerprints, retry metadata, provider correlation IDs, and no raw token or message payload leakage.

**Why this priority**: The user experience is incomplete unless Telegram receives the briefing result, and operations need durable delivery evidence.

**Independent Test**: Trigger the Daily Intelligence Briefing alias in mocked QA mode and verify the mock Bot API receives a `sendMessage` request for the same chat while a delivery attempt record is persisted.

**Acceptance Scenarios**:

1. **Given** a completed alias-triggered run, **When** final output is available, **Then** the Telegram Bot API boundary sends a message to the originating chat using the configured secret reference.
2. **Given** a partial-failure final output, **When** delivery is attempted, **Then** Telegram receives a concise partial-failure note and the attempt status remains safe for audit and diagnostics.
3. **Given** the Bot API boundary fails transiently, **When** delivery is attempted, **Then** the attempt is recorded as retrying with safe failure category and next retry timestamp.

### Edge Cases

- Telegram sends a webhook update without a message body or text.
- The webhook secret is wrong; the update is ignored without revealing configuration.
- A link token is expired, already consumed, or revoked.
- A linked identity exists in channel persistence but the admin summary has been revoked.
- Alias text differs only by case or duplicate whitespace.
- Two tenants configure the same alias text for different workflow versions.
- A tenant disables Telegram after a user has linked an identity.
- Bot API delivery succeeds but the provider returns no message ID.
- Final result contains raw secrets, long payloads, prompt bodies, or sensitive provider data.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST persist Telegram alias configuration per tenant with alias text, normalized alias key, published workflow version identifier, protected flag, enabled flag, revision token, and audit-safe update metadata.
- **FR-002**: System MUST provide API and server-rendered admin controls to list, create, update, and disable tenant Telegram aliases from `/admin/telegram`.
- **FR-003**: System MUST enforce tenant authorization for all alias reads and writes; cross-tenant alias access MUST fail closed.
- **FR-004**: System MUST persist Telegram link tokens and consumed linked identity records in PostgreSQL so a restart does not invalidate issued tokens or linked chats.
- **FR-005**: System MUST hash or mask link tokens, Telegram user identifiers, and chat identifiers in admin-visible and diagnostic records.
- **FR-006**: System MUST match natural-language aliases by tenant-scoped normalized exact match after trimming, whitespace normalization, and case folding.
- **FR-007**: System MUST require an active linked Telegram identity before any protected tenant alias can start a workflow run.
- **FR-008**: System MUST enforce tenant Telegram configuration readiness at runtime before starting an alias-triggered run.
- **FR-009**: System MUST persist Telegram update idempotency so duplicate webhook deliveries replay the original response without creating duplicate runs or duplicate final deliveries.
- **FR-010**: System MUST start the configured published workflow version with safe Telegram context and the original user text when a linked user sends an enabled alias.
- **FR-011**: System MUST support the Daily Intelligence Briefing alias where `Morning briefing` starts the published briefing workflow.
- **FR-012**: System MUST format final Telegram delivery text as either the final briefing summary or a concise partial-failure note without raw secrets, prompt bodies, credential values, or unbounded payloads.
- **FR-013**: System MUST send final alias-triggered results through a Telegram Bot API client boundary that receives only safe secret references from runtime configuration.
- **FR-014**: System MUST persist Telegram delivery attempts with tenant, run, chat destination fingerprint, provider correlation reference, delivery status, attempt number, retry timestamp, safe failure category, and trace ID.
- **FR-015**: System MUST keep local and CI validation deterministic by using a mocked Telegram Bot API client.
- **FR-016**: System MUST record redaction-safe diagnostics for alias routing, access denials, duplicate updates, runtime configuration failures, and delivery attempts.

### Key Entities *(include if feature involves data)*

- **Telegram Command Alias**: Tenant-scoped mapping from user text to a published workflow version with protected/enabled policy and revision metadata.
- **Telegram Link Token**: One-time token audit record with tenant, issuer, hash, status, expiration, consumption, revocation, and trace metadata.
- **Telegram Identity Link**: Persistent link from tenant and platform identity to Telegram user/chat identifiers, plus link status and lifecycle timestamps.
- **Telegram Update Receipt**: Idempotency record keyed by Telegram update ID with safe stored response and trace metadata.
- **Telegram Delivery Attempt**: Persisted outbound message attempt for a run result with safe destination fingerprint, status, retry/backoff, and provider correlation reference.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A tenant admin can create a `Morning briefing` alias and see it on `/admin/telegram` in under 30 seconds during local QA.
- **SC-002**: A linked Telegram update containing `Morning briefing` creates exactly one workflow run after three duplicate webhook submissions.
- **SC-003**: Local QA records a mocked `sendMessage` delivery attempt to the originating chat within two seconds of a deterministic alias-triggered completion.
- **SC-004**: Cross-tenant alias access, unlinked identity access, revoked identity access, and disabled-tenant runtime access each return safe denials and create no workflow runs.
- **SC-005**: Admin pages, API responses, diagnostics, and delivery attempts contain no raw bot token, webhook secret, link token, full Telegram user ID, full chat ID, prompt body, or credential value.

## Assumptions

- Existing Auth0/local-principal authorization, tenant scoping, Telegram configuration, channel facade, runtime run creation, audit/redaction helpers, and server-rendered admin shell are reused.
- The v1 alias router starts published workflow versions through the existing channel run facade and uses deterministic mocked completion for local Daily Intelligence Briefing QA.
- Real external Telegram delivery is behind a Bot API client boundary and is not exercised in local QA or CI.
- Alias matching is exact after normalization; fuzzy natural-language interpretation is out of scope for this feature.
- Workflow graph execution, real tool execution, and final briefing synthesis are handled by adjacent specs 020 and 021.
