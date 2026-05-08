# Data Model: Channels, Telegram, Briefing React Live Data

## Telegram Tenant Config

- **Fields rendered**: tenant id/label, readiness state, delivery mode, webhook state, token audit summary, last validation summary, safe diagnostics.
- **Relationships**: Belongs to one tenant and may have aliases, linked identities, link-token audits, webhook receipts, deliveries, and audit records.
- **Validation rules**: Cross-tenant config IDs fail closed. Token references are safe labels only.

## Command Alias

- **Fields rendered**: alias id, command, target summary, enabled state, revision, last used label, authorized actions, audit reference.
- **Relationships**: Belongs to tenant config and may target briefing or workflow run launch behavior.
- **State transitions**: draft/active/disabled/deleted or equivalent service states through backend actions only.

## Linked Identity

- **Fields rendered**: identity id, masked Telegram label, linked principal summary, status, linked/revoked timestamps, audit reference.
- **Validation rules**: Full Telegram identifiers and private messages never render.

## Link Token Audit

- **Fields rendered**: token audit id, created/consumed/revoked/expired state, masked actor, expiration, one-time display flag, audit reference.
- **State transitions**: token value may appear only in creation mutation response; list/detail responses show safe audit metadata only.

## Webhook Receipt And Delivery Attempt

- **Fields rendered**: receipt or delivery id, status, duplicate state, safe destination summary, retry count, latency, trace id, failure category, audit reference.
- **Relationships**: May link to channel requests, notifications, Telegram config, aliases, identities, or workflow runs.
- **Validation rules**: Raw webhook updates, private messages, authorization headers, and stack traces never render.

## Channel Run Link

- **Fields rendered**: run id/reference, status, safe summary, tenant label, trace id, accessible link, last event label.
- **Validation rules**: Run link is visible only when the principal is authorized for that run and tenant.

## Briefing Preference Profile

- **Fields rendered**: profile id, owner/scope summary, enabled state, delivery channel, quiet hours summary, revision, import/export artifact references, runtime-resolution evidence.
- **State transitions**: preference save/import/export mutations persist through briefing preference services and produce audit/artifact evidence.
- **Validation rules**: Raw briefing content and private preference payloads never render.

## Channel/Briefing Action Result

- **Fields rendered**: status, safe summary, toast, optional one-time token, alias/config/preference/artifact summary, validation errors, stale conflict, audit reference, next-request effect.
- **States**: accepted, replayed, denied, stale, validation, unavailable, confirmation-required.
