# Admin Usage Analytics UI Contract

## Routes

- `GET /admin/usage`: Render usage analytics dashboard.
- `POST /admin/usage/exports`: Create an audited CSV export request from the
  current filters and redirect to the export detail page.
- `GET /admin/usage/exports/{usage_export_request_id}`: Render export metadata
  and safe status.

## Dashboard Inputs

- Scope selector from the shared admin shell.
- Time range: `start`, `end`.
- Optional filters: `tenant_id`, `principal_id`, `workflow_lineage_id`,
  `workflow_version_id`, `workflow_run_id`, `workflow_run_step_id`,
  `agent_key`, `sub_agent_key`, `provider_key`, `model_id`,
  `prompt_version_id`, `execution_mode`, `usage_status`.
- Group selector: `day`, `hour`, `tenant`, `provider`, `model`, `workflow`,
  `agent`, `sub_agent`, `prompt`, `execution_mode`, `principal`.

## Dashboard Output

- Summary strip with event count, total tokens, estimated cost, confirmed event
  count, estimated event count, and unavailable event count.
- Rollup table using the active group selector.
- Event drilldown table with safe identifiers, token counts, cost estimate,
  status, latency, and recorded timestamp.
- Empty state when filters match no usage events.
- Denied state when the principal attempts unauthorized tenant scope.

## Export Behavior

- Export action uses the current safe filter snapshot.
- Platform admins can export platform scope or an explicit tenant scope.
- Tenant admins can export only their tenant scope.
- Denied export attempts render no artifact link and write audit-safe denial
  metadata.
- Export detail never renders raw prompts, completions, secrets, memory
  content, provider credentials, or unauthorized run content.

## Redaction Rules

- All displayed labels are passed through admin shell text sanitization.
- Safe attribution JSON is summarized by keys and identifiers only.
- Artifact URIs are shown only for authorized completed exports.
- Error messages use safe reason categories rather than raw exception strings.
