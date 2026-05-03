# Research: Telegram Configuration Console

## Decision: Local Readiness Uses Secret References Only

Production readiness requires `telegram_provider_token_ref` and webhook secret
configuration to be expressed as secret references. Local and test modes may
use fake references so reviewers can validate redaction, forms, and diagnostics
without a real Telegram bot.

**Rationale**: This matches the existing settings guardrail that production
Telegram provider tokens must use reference-like values. The console should
explain readiness without resolving or displaying secrets.

**Alternatives considered**:

- Resolve and test real tokens from the console. Rejected because validation
  must avoid external side effects and secret exposure.
- Store bot token values in console tables. Rejected by constitution secret
  hygiene and the feature prompt.

## Decision: Webhook Validation Is A Safe Local Diagnostic

The webhook validation action records whether local configuration is internally
consistent and command handling is available. It does not register or call a
Telegram webhook.

**Rationale**: Admins need a button that proves setup shape in local QA while
avoiding real provider calls by default.

**Alternatives considered**:

- Call Telegram `setWebhook`. Rejected because it creates external side
  effects and requires real credentials.
- Omit validation. Rejected because the prompt explicitly asks admins to
  validate webhook configuration.

## Decision: Tenant Enablement Is Separate From Global Provider Readiness

Global readiness answers whether Telegram can work at all. Tenant config answers
whether a specific tenant is allowed to use protected commands.

**Rationale**: This keeps tenant isolation explicit and prevents global provider
configuration from enabling every tenant implicitly.

## Decision: Link Tokens Use Existing Channel Service Plus Safe Audit Rows

One-time link tokens are issued through existing Spec 006 `ChannelService`.
The console stores token fingerprint, tenant, issuing principal, expiry, and
status. The raw token is returned once to the issuing admin only.

**Rationale**: Existing command handling remains authoritative while the console
adds reviewable audit and revocation state.

## Decision: Identity Inspection Uses Masked Summaries

The console stores and displays masked Telegram user and chat identifiers,
platform identity id, tenant id, status, linked/revoked timestamps, and command
readiness. It does not store message text or raw webhook updates.

**Rationale**: This gives administrators enough information to support linking
without turning the console into a private chat viewer.

## Decision: Diagnostics Are Category-Based

Diagnostics use categories such as `readiness`, `webhook_validation`,
`link_token`, `identity`, `delivery`, `wrong_secret`, and `duplicate_update`
with safe status, summary, trace id, and redacted metadata.

**Rationale**: Category summaries support operations while keeping screenshots
and audit trails safe.

## Decision: Revision Tokens Handle Stale Forms

Tenant configuration forms carry a revision token. Updates with a stale token
return a conflict status and preserve the current record.

**Rationale**: This matches existing admin form patterns and avoids hidden
overwrites by two administrators.
