# React UI Contract: Channels, Memberships, Access, Telegram, And Briefing Parity

## Browser Destinations

| Legacy surface | React destination | Query preservation |
| --- | --- | --- |
| `/admin/memberships` | `/admin/app/memberships` | `tenant_id`, `q`, `status`, `role`, `principal_id`, `membership_id`, `role_grant_id`, `saved_filter_id` |
| `/admin/memberships/invitations` | `/admin/app/memberships?panel=invitations` | `tenant_id`, `saved_filter_id` |
| `/admin/memberships/role-grants` | `/admin/app/memberships?panel=role-grants` | `tenant_id`, `principal_id`, `role_grant_id`, `saved_filter_id` |
| `/admin/memberships/role-grants/{role_grant_id}/revoke` | `/admin/app/memberships?panel=role-grants` | `tenant_id`, `role_grant_id` |
| `/admin/memberships/principals/{principal_identity_id}/{status_action}` | `/admin/app/memberships?panel=principals` | `tenant_id`, `principal_identity_id`, `status_action` |
| `/admin/memberships/memberships/{tenant_membership_id}/{membership_status}` | `/admin/app/memberships?panel=memberships` | `tenant_id`, `tenant_membership_id`, `membership_status` |
| `/admin/telegram` | `/admin/app/channels?panel=telegram` | `tenant_id`, `saved_filter_id` |
| `/admin/telegram/config` | `/admin/app/channels?panel=telegram` | `tenant_id` |
| `/admin/telegram/link-tokens` | `/admin/app/channels?panel=link-tokens` | `tenant_id` |
| `/admin/telegram/aliases` | `/admin/app/channels?panel=aliases` | `tenant_id`, `alias_id`, `status` |
| `/admin/briefing-preferences` | `/admin/app/channels?panel=briefing` | `tenant_id`, `saved_filter_id` |
| `/admin/briefing-preferences/export` | `/admin/app/channels?panel=briefing-export` | `tenant_id` |
| `/admin/briefing-preferences/import` | `/admin/app/channels?panel=briefing-import` | `tenant_id` |

## Retained JSON APIs

The following API families remain available:

- `/admin/memberships/api/*`
- `/admin/telegram/api/*`
- `/admin/briefing-preferences/api/*`
- `/admin/app/memberships/*`
- `/admin/app/channels/*`

## Redaction Contract

React, redirects, docs, screenshots, logs, and exports must never include:

- Raw Auth0 subjects.
- Raw invitation or link token values after immediate creation.
- Full Telegram external identifiers.
- Private channel message text.
- Raw Telegram webhook payloads.
- Private briefing preference values.
- Raw import payloads.
- Stack traces or local filesystem paths.
- Unauthorized tenant labels.

## Template Deletion Contract

The following paths must not exist after implementation:

- `src/multi_agent_platform/web_admin/templates/memberships/index.html`
- `src/multi_agent_platform/web_admin/templates/telegram/index.html`
- `src/multi_agent_platform/web_admin/templates/briefing_preferences/index.html`

Converted routers must not contain `TemplateResponse`, `Jinja2Templates`,
`workflow_ui_templates`, or the retired template filenames.
