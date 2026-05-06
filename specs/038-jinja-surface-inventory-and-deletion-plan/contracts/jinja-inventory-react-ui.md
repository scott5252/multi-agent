# React UI Contract: Jinja Inventory

## Route

- Browser page: `/admin/app/migration`
- JSON endpoint: `GET /admin/app/migration/jinja-inventory.json`
- Auth: existing React admin shell authentication and authorization.
- Scope: platform administrators see all groups; tenant administrators see tenant-safe groups and blocked summaries that do not reveal unauthorized tenant data.

## Required UI Behavior

- Render a "Jinja surface inventory" section after route parity and before evidence sweeps.
- Show summary counts for templates, routes, static assets, direct links, blocked items, and safe-to-delete candidates.
- Group items by planned removal spec and owner category.
- Display classification, replacement path, blocker/evidence references, and reviewer signoff state for each visible item.
- Never display absolute local filesystem paths, raw secrets, raw prompts/completions, memory contents, private channel messages, raw run payloads, raw tool payloads, stack traces, full Telegram identifiers, or unauthorized tenant labels.
- Empty state must explain that no inventory items are visible for the current scope without implying unauthorized data exists.

## Error States

- `401/403`: Use the existing React admin safe problem state.
- Dependency/scanner failure: show a safe `dependency_unavailable` state with trace id when available.
- Partial inventory: show warning counts and blocked item reasons, not raw exception details.
