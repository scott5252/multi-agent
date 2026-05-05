# UI Contract: React Usage And Cost Analytics

## Route

- React route: `/admin/app/usage`
- Bootstrap API: `GET /admin/app/usage/bootstrap.json`
- Drilldown API: `GET /admin/app/usage/events.json`
- Export creation API: `POST /admin/app/usage/exports`
- Export detail API: `GET /admin/app/usage/exports/{usage_export_request_id}.json`
- Existing fallback: `/admin/usage` remains available until Spec 037 parity
  retirement.

## Primary Layout

The first viewport is the working analytics dashboard, not a landing page.

1. Header with active scope, selected date range, last updated timestamp, and
   export action.
2. Compact filter bar for range, tenant scope when authorized, group-by,
   provider/model, and confidence status.
3. Summary card strip for total tokens, estimated cost, requests/events,
   latency, unavailable usage, and confirmed/estimated coverage.
4. Trend panel with accessible SVG chart and tabular fallback labels.
5. Rollup table with group selector, bounded rows, confidence badges, latency,
   unavailable counts, gateway/attempt/tool summaries, and drilldown actions.
6. Event drilldown panel with safe event rows and bounded result messaging.
7. Export status panel with recent export references and safe next steps.

## Interaction Contract

- Filters submit by calling the bootstrap API with query parameters; the
  browser does not derive unauthorized filter options from hidden data.
- Group changes reload dashboard data with the backend-selected grouping.
- The group selector includes all authorized Spec 016 dimensions, including
  tenant, provider, model, workflow, agent, sub-agent, prompt, execution mode,
  and principal, plus React graph/gateway/tool attribution dimensions.
- Rollup row drilldown loads `events.json` with the active filter snapshot and
  `rollup_key`.
- Export creation posts only the active safe filter snapshot and optional
  grouping context.
- Export detail refreshes status without showing raw CSV contents or storage
  paths.
- Empty, partial, unavailable, denied, and export-pending states are rendered
  from backend problem objects.

## Accessibility

- All filters have visible labels and keyboard-focus states.
- Summary cards expose metric labels and confidence status to assistive
  technologies.
- The trend chart includes text equivalents for each bucket and does not rely
  on color alone.
- Rollup and drilldown tables use proper column headings and stable row
  actions.
- Export creation returns a polite live-region update with status and audit
  reference.

## Redaction And Safe Display

The UI must never render:

- raw prompts or completions
- memory content
- private channel messages
- provider authorization headers
- provider tokens or credential values
- credential reference internals
- raw tool request/response payloads
- local filesystem paths
- unauthorized tenant labels
- unauthorized run content

The UI may render safe labels, masked ids, aggregate metrics, short safe
summaries, artifact references, checksum prefixes, status labels, and audit
references supplied by the backend.

## Error States

- **Denied**: show generic scope-safe denial copy and audit reference when
  available.
- **Empty**: keep filters visible and show next action guidance.
- **Partial**: show available metrics with partial/unavailable badges.
- **Stale pricing**: keep token counts visible and label costs as estimated or
  unavailable.
- **Export pending**: show export status and detail refresh affordance.
- **Audit unavailable**: fail closed for export or protected detail actions.

## QA Coverage

Playwright must cover:

- platform administrator dashboard with cross-tenant authorized rollups
- Acme tenant administrator dashboard with no Globex labels
- grouping changes for provider, model, workflow, agent, prompt, and gateway
  or tool attribution
- bounded event drilldown from a rollup row
- export creation and export detail status
- empty, partial, unavailable, and denied states
- redaction scan over screenshots and JSON evidence
