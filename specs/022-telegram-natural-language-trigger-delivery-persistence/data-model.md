# Data Model: Telegram Natural-Language Trigger Delivery Persistence

## Telegram Command Alias

- `telegram_command_alias_id`: UUID primary key.
- `tenant_id`: Tenant that owns the alias.
- `alias_text`: Human-facing alias, for example `Morning briefing`.
- `alias_normalized`: Lower-cased, trimmed, whitespace-normalized alias used for lookup.
- `published_workflow_version_id`: Immutable workflow version identifier to start.
- `description`: Optional admin-safe note.
- `protected`: Whether a linked identity is required. Tenant workflow aliases default to protected.
- `enabled`: Whether runtime routing is allowed.
- `revision_token`: Optimistic concurrency token for admin forms.
- `created_by_principal_id`, `updated_by_principal_id`: Safe principal identifiers.
- `created_at`, `updated_at`: Lifecycle timestamps.

### Validation Rules

- `(tenant_id, alias_normalized)` is unique.
- `alias_text` must be 1 to 120 characters after trimming.
- `published_workflow_version_id` must be present.
- Runtime lookup only uses enabled aliases.

## Telegram Link Token

Existing `telegram_link_token_audits` records are used as persistent token state.

- `token_fingerprint`: SHA-256 hash of the one-time token.
- `status`: `issued`, `consumed`, `revoked`, or `expired`.
- `tenant_id`: Tenant for the future identity link.
- `issued_by_principal_id`: Platform identity that requested linking.
- `expires_at`, `issued_at`, `consumed_at`, `revoked_at`: Lifecycle timestamps.

## Telegram Identity Link

Existing `telegram_identity_links` records provide runtime identity lookup.

- `tenant_id`: Tenant context used for alias lookup.
- `platform_identity_id`: Platform identity associated with the Telegram user/chat.
- `telegram_user_id`, `telegram_chat_id`: Runtime identifiers used by the webhook, never rendered in admin views.
- `link_token_hash`: Token fingerprint used to establish the link.
- `status`: `linked`, `revoked`, `expired`, or `pending`.
- `created_at`, `expires_at`, `linked_at`, `revoked_at`: Lifecycle timestamps.

Admin-visible identity summaries continue to use masked identifiers and fingerprints.

## Telegram Update Receipt

- `telegram_update_receipt_id`: UUID primary key.
- `telegram_update_id`: Telegram `update_id`, globally unique for the bot.
- `tenant_id`: Tenant once known; null for ignored or unauthorized updates.
- `platform_identity_id`: Linked platform identity once known.
- `telegram_chat_fingerprint`: Safe chat fingerprint.
- `action_type`: `link`, `alias`, `command`, `ignored`, or `denied`.
- `response_payload`: Safe stored response replayed for duplicate updates.
- `run_id`: Created run when applicable.
- `delivery_attempt_id`: Delivery attempt when applicable.
- `trace_id`: Runtime trace ID.
- `received_at`: Receipt timestamp.

## Telegram Delivery Attempt

Existing `notification_delivery_attempts` records are reused for Bot API delivery evidence.

- `tenant_id`: Tenant owning the run and alias.
- `notification_subscription_id`: Stable synthetic UUID for the Telegram destination.
- `run_id`: Workflow run whose terminal result is delivered.
- `channel_type`: `telegram`.
- `event_type`: `terminal`.
- `payload_fingerprint`: SHA-256 fingerprint of sanitized outbound message.
- `delivery_status`: `delivered`, `retrying`, `failed`, or `suppressed`.
- `provider_message_id`: Safe provider correlation reference.
- `failure_category`: Safe failure category when delivery is not successful.
- `attempt_number`: Attempt count.
- `next_retry_at`: Backoff timestamp for transient failures.
- `trace_id`, `created_at`, `delivered_at`: Operational evidence.

## State Transitions

- Link token: `issued -> consumed`, `issued -> revoked`, or `issued -> expired`.
- Identity link: `linked -> revoked`.
- Alias: `enabled -> disabled`; updates rotate the revision token.
- Update receipt: created once and replayed for duplicates.
- Delivery attempt: one record per physical send attempt; transient failure uses `retrying` with `next_retry_at`.
