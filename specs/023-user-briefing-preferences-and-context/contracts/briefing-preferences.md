# Contracts: Briefing Preferences

## Browser UI

`GET /admin/briefing-preferences`

- Requires authenticated principal with `briefing-preferences:read`.
- Uses tenant scope from the admin shell query parameter or the principal's
  tenant.
- Renders the user's editable profile form when tenant scoped.
- Renders safe summary rows for authorized admin users.
- Must not render raw VIP senders or raw account references in admin summary
  tables.

`POST /admin/briefing-preferences`

- Requires `briefing-preferences:write`.
- Saves the authenticated principal's own profile for the selected tenant.
- Uses `revision_token` for optimistic conflict detection.
- Redirects back to `/admin/briefing-preferences?tenant_id=...` on success.

## API

`GET /admin/briefing-preferences/api/profile?tenant_id=...&principal_id=...`

- Returns the authenticated principal's profile by default.
- Platform admins may request another principal by id for safe summary
  inspection, but raw profile reads are limited to the profile owner.

`POST /admin/briefing-preferences/api/profile`

Request:

```json
{
  "tenant_id": "11111111-1111-1111-1111-111111111111",
  "location_label": "Providence, RI",
  "timezone": "America/New_York",
  "news_topics": ["AI", "markets"],
  "vip_senders": ["sarah@example.com"],
  "workday_start": "09:00",
  "workday_end": "17:30",
  "commute_mode": "driving",
  "calendar_account_ref": "delegated:calendar:primary",
  "email_account_ref": "delegated:gmail:primary",
  "output_style": "standard",
  "scheduled_enabled": true,
  "scheduled_time": "08:00",
  "revision_token": null
}
```

Response includes the profile, revision id, revision token, content digest, and
safe summary.

`GET /admin/briefing-preferences/api/summaries?tenant_id=...`

- Returns safe summary rows for authorized admin scopes.

`GET /admin/briefing-preferences/api/export?tenant_id=...`

- Returns the authenticated principal's own JSON export document.

`POST /admin/briefing-preferences/api/import`

- Accepts a JSON export document and saves it only when tenant and principal
  ownership match the authenticated actor.

`POST /admin/briefing-preferences/api/resolve`

- Runtime/test helper for resolving the latest profile by tenant/principal.
- Returns `available=false` for missing or denied contexts without private data.

## Runtime Resolver

Input:

```json
{
  "tenant_id": "11111111-1111-1111-1111-111111111111",
  "principal_id": "tenant-admin-acme",
  "source_channel": "telegram",
  "trace_id": "trace-qa023"
}
```

Output:

```json
{
  "available": true,
  "revision_id": "33333333-3333-3333-3333-333333333333",
  "content_digest": "sha256:...",
  "preferences": {},
  "safe_summary": {}
}
```
