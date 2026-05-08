# UI Contract: Operations And Run Debug React Live Data

## Primary Page

- Route: `/admin/app/operations`
- Bootstrap JSON: `/admin/app/operations.json`
- Principals: `platform-admin`, `tenant-admin-acme`, Auth0-shaped operations
  reader, and negative cross-tenant principals.
- Default range: `60m`.

## Required UI Regions

1. Header with scope, range, and generated-at freshness.
2. Summary card grid backed by live operational evidence.
3. Health/pressure panels for dependency, capacity, worker, storage, provider,
   usage, channel, and reliability evidence where authorized.
4. Likely cause panel derived from live safe symptoms.
5. Run debug panel for a live run or truthful empty/unavailable state.
6. Reliability recovery panel with retries, breakers, dead letters,
   compensation, and confirmation items.
7. Safe log timeline/table with bounded rows.
8. Export panel showing persisted export status and safe artifact reference.
9. Fallback links to related operations, reliability, governance, usage,
   Telegram/channel, skill diagnostics, and run inspection views.

## Required Interactions

- Change supported severity and subsystem filters.
- Open a run debug link for a seeded run.
- Request an export from the workbench UI.
- Refresh the workbench.
- Switch from Acme seeded tenant to Globex empty tenant.

## Empty And Denied States

- Empty tenant workbench: no incidents, no fake runs, no fake queue pressure,
  no fake delivery rows, no fake exports.
- Missing run: not found or unavailable state.
- Cross-tenant run: denied without unauthorized tenant labels.
- Export dependency unavailable: unavailable or queued state with no fake
  artifact reference.

## Redaction Rules

The UI must not render:

- raw secrets or credential values
- provider authorization headers
- raw prompts or completions
- memory contents
- raw run payloads
- private channel messages
- raw tool payloads
- raw test transcripts
- full Telegram identifiers
- storage URLs, `file:` URIs, or local filesystem paths
- stack traces
- unauthorized tenant labels

## QA057 Browser Flow

1. Sign in as `platform-admin` or `tenant-admin-acme`.
2. Open `/admin/app/operations?tenant_id=11111111-1111-1111-1111-111111111111`.
3. Confirm live seeded workbench cards and likely cause.
4. Open the seeded run debug link.
5. Click the workbench export action.
6. Confirm the export panel shows a safe artifact reference and completed or
   queued persisted state.
7. Run `scripts/qa/verify_operations_qa057.py` to prove persistence.
8. Switch to Globex and confirm truthful empty state.
