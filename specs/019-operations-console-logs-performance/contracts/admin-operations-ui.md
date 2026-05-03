# Admin Operations UI Contract

## Routes

### `GET /admin/operations`

Renders the Operations Console in the existing admin shell.

Required authorization:

- `platform_admin` with `operations:read`, or
- `auditor` with `operations:read`.

Tenant admins are denied for v1.

Query parameters:

- `trace_id`
- `tenant_id`
- `run_id`
- `component`
- `severity`
- `status`
- `dependency`
- `start`
- `end`
- `limit`

Rendered regions:

- Page title: `Operations Console`
- Redaction and retention notice.
- Summary cards for health, dependencies, capacity, DB pool, object storage,
  providers, Telegram/channel status, reliability, latency, throughput, and
  error rate.
- Filter form with the supported log filters.
- Redacted operational log table.
- Links to run inspection, reliability controls, provider tests, Telegram
  configuration, and usage analytics.
- Export action for principals with `operations:export`.

Sensitive content requirements:

- Never render raw prompts, model responses, raw channel messages, secrets,
  credentials, raw payloads, stack traces, or authorization headers.
- Render only safe labels, ids, statuses, counts, trace ids, and summaries.

### `POST /admin/operations/logs/export`

Browser form wrapper for the redacted export action.

Behavior:

- Uses the same filters as the dashboard form.
- Stores a redacted CSV artifact.
- Returns export artifact metadata as a safe response.
- Records allowed or denied inspection-access audit metadata.

## Empty And Error States

- If no logs match filters, show a non-blocking empty state.
- If dependencies are unavailable, show a degraded card rather than hiding the
  console.
- If audit persistence is unavailable, fail closed through the existing admin
  shell error flow.

## Navigation

Add "Operations Console" to the admin navigation. The item is visible only when
the current principal and scope pass the `GET:/admin/operations` surface policy.
