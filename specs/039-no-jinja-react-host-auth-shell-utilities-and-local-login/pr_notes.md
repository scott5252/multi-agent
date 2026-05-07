# PR Notes: Spec 039 No-Jinja Host/Auth/Shell

## Summary

Spec 039 converts the React admin host and local-principal login page away from server-side Jinja rendering. `/admin` now redirects to the React app, `/auth/local-login` renders non-Jinja HTML backed by `/auth/local-login.json`, and saved-filter utility pages redirect to a React route backed by `/admin/filters/{admin_area}.json`.

## Deleted

- `src/multi_agent_platform/web_admin/templates/admin_react/app.html`
- `src/multi_agent_platform/web_admin/templates/auth/local_login.html`

## Retained With Evidence

- `src/multi_agent_platform/web_admin/templates/admin_shell/*.html`
- `src/multi_agent_platform/web_admin/static/admin_shell.js`

These are retained because many domain-specific Jinja pages still extend `admin_shell/base.html`. Specs 040 through 046 own domain parity and deletion. Deleting the shared shell base in Spec 039 would break old direct links before their React replacements are validated.

## Review Focus

- Confirm admin entry routes return `X-React-Admin-Host: non-jinja`.
- Confirm local-login returns `X-Local-Login-Response: non-jinja`.
- Confirm `/admin` redirects preserve tenant query values.
- Confirm saved-filter JSON remains tenant scoped.
- Confirm no real credential, stack trace, local path, raw prompt, raw completion, raw tool payload, or unauthorized tenant label appears in responses or screenshots.

## Rollback

If the non-Jinja host fails, restore the previous host renderer from git and rebuild React assets. If local login fails, use the local-principal header in backend tests while the page is repaired. Do not restore deleted templates without also restoring route tests that prove the fallback is temporary and redaction-safe.
