# UI Contract: React Channel, Telegram, And Briefing Preferences

## Routes

- React channel workspace: `/admin/app/channels`
- Bootstrap API: `GET /admin/app/channels/bootstrap.json`
- Telegram config action API: `POST /admin/app/channels/telegram/config`
- Webhook validation API: `POST /admin/app/channels/telegram/webhook/validate`
- Alias action API: `POST /admin/app/channels/telegram/aliases`
- Alias status API: `POST /admin/app/channels/telegram/aliases/{alias_id}/{action}`
- Link-token creation API: `POST /admin/app/channels/telegram/link-tokens`
- Delivery diagnostics API: `GET /admin/app/channels/telegram/deliveries.json`
- Run status API: `GET /admin/app/channels/runs/{workflow_run_id}/status.json`
- Briefing preferences API: `GET /admin/app/channels/briefing/preferences.json`
- Briefing preference save API: `POST /admin/app/channels/briefing/preferences`
- Briefing preference import API: `POST /admin/app/channels/briefing/preferences/import`
- Briefing preference export API: `POST /admin/app/channels/briefing/preferences/export`
- Existing fallbacks: `/admin/telegram`, `/admin/briefing-preferences`, and existing channel run UI routes remain available until Spec 037.

## Primary Layout

The first screen is an operational workspace, not a landing page.

1. Header with active scope, readiness status, last validation timestamp, and primary refresh action.
2. Readiness cards for channel, Telegram, webhook, secret-reference readiness, linked identities, delivery health, and preference resolver readiness.
3. Tenant Telegram configuration panel with enablement status, safe reference labels, validation action, and audit evidence.
4. Alias panel with search, bounded rows, create/edit form, disable/delete controls, protected readiness badges, and audit evidence.
5. Link-token and linked identity panel with one-time creation result, masked later state, expiration, and identity summaries.
6. Delivery diagnostics panel with bounded attempts, safe error categories, retry context, webhook receipts, and safe run status links.
7. Briefing preference profile panel for authorized users with field-level validation and profile-only scheduled time.
8. Admin-safe preference summaries and import/export evidence for authorized tenant administrators.

## Interaction Contract

- React submits only backend-owned forms and action payloads.
- The browser never computes alias eligibility, protected readiness, tenant visibility, token reuse, or preference redaction.
- Link-token value is rendered only from the immediate creation response and not from bootstrap.
- Alias create/edit/disable/delete actions require backend revision or idempotency evidence.
- Webhook validation is explicit and returns local mock-safe evidence during QA.
- Delivery diagnostics are read-only and bounded.
- Run status links show safe status summaries and cannot reveal raw run results.
- Preference profile saves return immutable revision evidence.
- Preference import/export shows safe artifact metadata and never raw private preference values in admin summaries.

## Accessibility

- Readiness cards expose status labels in text.
- Forms use visible labels, field errors, and stable focus order.
- Destructive alias actions require explicit confirmation.
- Token creation result uses a visible expiration and next-step message.
- Tables use semantic headings and bounded row counts.
- Live regions announce mutation results without exposing unsafe values.

## Redaction

The UI must never render:

- real bot token values
- webhook secrets
- full Telegram user ids, chat ids, or usernames
- one-time link tokens after creation
- private Telegram messages
- raw preference values in admin summaries
- raw prompts
- run results
- raw tool payloads
- local filesystem paths
- unauthorized tenant data

The UI may render safe labels, masked identity labels, counts, statuses, timestamps, audit references, trace references, checksum prefixes, artifact references, and backend-provided safe summaries.

## Error States

- **Denied**: show safe denial and audit reference when available.
- **Empty**: show setup guidance without exposing hidden data.
- **Stale**: show validation age and refresh action.
- **Validation error**: show safe field errors.
- **Audit unavailable**: fail closed for protected mutations.
- **Dependency unavailable**: show safe retry guidance and avoid live calls in QA.
- **Conflict**: show stale revision recovery guidance.
