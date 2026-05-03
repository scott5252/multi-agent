# Admin Telegram UI Contract

## Route

- `GET /admin/telegram`

## Access

- Requires authenticated platform admin or tenant admin.
- Platform admins may use platform scope or select a tenant id.
- Tenant admins may only use their own tenant id.

## Page Sections

- Header: "Telegram Configuration"
- Provider readiness: token reference status, webhook secret status, production
  guardrail status, protected command readiness, last diagnostic.
- Tenant configuration form: enabled checkbox, protected command choices,
  status note, hidden revision token.
- Link token panel: issue one-time token, token expiry, safe fingerprint list.
- Linked identities: masked Telegram user/chat ids, platform identity, status,
  command readiness, revoke action.
- Diagnostics: recent safe diagnostic rows with category, status, summary,
  trace id, timestamp, and redacted metadata.
- Redaction notice: explicit statement that tokens, webhook secrets, private
  messages, raw prompts, and run results are not displayed.

## Mutations

- `POST /admin/telegram/config`: update tenant enablement with revision token.
- `POST /admin/telegram/webhook/validate`: create a local-only diagnostic.
- `POST /admin/telegram/link-tokens`: issue a one-time link token.
- `POST /admin/telegram/link-tokens/{token_audit_id}/revoke`: revoke token.
- `POST /admin/telegram/identities/{identity_id}/revoke`: revoke identity.

## Stale Conflict

If the submitted revision token does not match the current tenant config, the
page returns a conflict common state, keeps the current safe values, and does
not apply the submitted change.

## Redaction

The page must not render real bot tokens, webhook secrets, private messages,
raw prompts, run results, or raw Telegram ids. Raw link tokens are rendered only
on the immediate response after issue and never in token lists.
