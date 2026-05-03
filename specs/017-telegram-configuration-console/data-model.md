# Data Model: Telegram Configuration Console

## TenantTelegramConfiguration

- `telegram_tenant_config_id`: UUID primary key.
- `tenant_id`: UUID, required, unique.
- `enabled`: boolean.
- `protected_commands`: JSON list of command names such as `/run`, `/status`,
  `/approve`, `/reject`, `/resume`, `/cancel`, `/result`, `/artifacts`.
- `status_note`: safe operator note, max 500 characters, redacted if sensitive.
- `revision_token`: opaque string required on updates.
- `updated_by_principal_id`: principal id.
- `created_at`, `updated_at`: timezone-aware timestamps.

Validation:

- Tenant id is always required.
- Tenant admins may only access their own tenant id.
- Notes containing sensitive markers are replaced by safe fallback text.
- Updates require the current revision token unless the record is newly created.

## TelegramLinkTokenAudit

- `telegram_link_token_audit_id`: UUID primary key.
- `tenant_id`: UUID, required for tenant-scoped tokens.
- `issued_by_principal_id`: principal id.
- `token_fingerprint`: irreversible SHA-256 prefix or full hash; no raw token.
- `status`: `issued`, `consumed`, `revoked`, or `expired`.
- `expires_at`: timestamp.
- `issued_at`, `consumed_at`, `revoked_at`: timestamps.
- `revoked_by_principal_id`: principal id, nullable.
- `trace_id`: safe trace id.

Validation:

- Raw token is returned once by issue APIs and is never persisted.
- Revoke operations are idempotent for authorized tenants.

## TelegramLinkedIdentitySummary

- `telegram_linked_identity_summary_id`: UUID primary key.
- `tenant_id`: UUID, nullable only for platform-scoped links.
- `platform_identity_id`: platform principal linked to Telegram.
- `telegram_user_fingerprint`: irreversible fingerprint of Telegram user id.
- `telegram_chat_fingerprint`: irreversible fingerprint of Telegram chat id.
- `telegram_user_display`: masked Telegram user id.
- `telegram_chat_display`: masked Telegram chat id.
- `status`: `linked` or `revoked`.
- `linked_at`, `revoked_at`: timestamps.
- `revoked_by_principal_id`: principal id, nullable.
- `command_ready`: boolean.
- `trace_id`: safe trace id.

Validation:

- Telegram ids are masked before rendering or API response.
- Message text, raw webhook update data, prompts, and run results are not
  fields on this model.

## TelegramDiagnosticEvent

- `telegram_diagnostic_event_id`: UUID primary key.
- `tenant_id`: UUID, nullable for platform readiness diagnostics.
- `principal_id`: principal id, nullable for provider-originated summaries.
- `category`: `readiness`, `webhook_validation`, `link_token`, `identity`,
  `delivery`, `wrong_secret`, `duplicate_update`, or `access_denied`.
- `status`: `ready`, `not_ready`, `ok`, `warning`, `failed`, `denied`,
  `revoked`, or `conflict`.
- `summary`: safe text.
- `trace_id`: safe trace id.
- `redacted_metadata`: JSON dictionary containing only safe keys and values.
- `created_at`: timestamp.

Validation:

- Metadata values are sanitized and sensitive keys are dropped or replaced.
- Diagnostics are tenant-filtered for every list operation.

## Access Scope

- `scope_type`: `platform` or `tenant`.
- `tenant_id`: required for tenant scope.
- `principal_id`: current principal.
- `platform_admin`: true only for platform-admin role.

Rules:

- Platform admins can view platform readiness and any selected tenant scope.
- Tenant admins are forced to their own tenant scope.
- Cross-tenant access raises a denied error and may emit a safe diagnostic.
