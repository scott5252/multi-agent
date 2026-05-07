# Spec 045 Reviewer Notes

## Summary

Spec 045 converts memberships, Telegram configuration, and briefing preference
browser surfaces to React-only destinations.

The retained JSON APIs remain available for React and API callers.

## Retired Jinja Surfaces

- `src/multi_agent_platform/web_admin/templates/memberships/index.html`
- `src/multi_agent_platform/web_admin/templates/telegram/index.html`
- `src/multi_agent_platform/web_admin/templates/briefing_preferences/index.html`

## Compatibility Behavior

- `/admin/memberships` redirects to `/admin/app/memberships`.
- Membership invitation, role-grant, revoke, principal-status, and membership
  status form routes execute retained service behavior and redirect to React.
- `/admin/telegram` redirects to `/admin/app/channels?panel=telegram`.
- Telegram config, webhook validation, alias, token revoke, and identity revoke
  form routes redirect to React after retained service behavior.
- Telegram link-token creation returns a non-Jinja one-time JSON response with
  the raw token and safe audit metadata.
- `/admin/briefing-preferences` redirects to `/admin/app/channels?panel=briefing`.
- Briefing save and import form routes redirect to React after retained service
  behavior.
- Old briefing export browser links redirect to React export metadata; the
  retained `/api/export` route remains available for authorized API callers.

## Redaction Notes

Raw Auth0 subjects, raw emails, full Telegram ids, private messages, raw link
tokens after creation, private preference values, raw imports, stack traces, and
unauthorized tenant labels must not appear in UI, logs, screenshots, or docs.

## Validation Notes

Focused validation covers old browser redirects, form compatibility, one-time
token behavior, tenant isolation, retained React APIs, frontend membership and
channel components, and retirement scanning.

Approve only after QA docs validation, Spec QA, and Playwright validation pass
with the QA045 React channels screenshot attached.
