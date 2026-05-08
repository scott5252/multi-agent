# UI Contract: Usage React Live Data

## Routes

- `/admin/app/usage` serves the React usage analytics workspace.
- `/admin/app/usage/bootstrap.json` returns live dashboard data for the active
  authorized scope.
- `/admin/app/usage/events.json` returns bounded live drilldown rows for the
  active filters and rollup.
- `/admin/app/usage/exports` creates a persisted usage export request.
- `/admin/app/usage/exports/{usage_export_request_id}.json` returns persisted
  export detail for an authorized request.

## Required States

- **Live seeded state**: qa056 seeded Acme data renders persisted usage events,
  totals, trends, rollups, drilldowns, confidence states, safe attribution,
  export history, and artifact metadata.
- **Empty state**: A fresh authorized scope, including the qa056 Globex tenant,
  renders zero usage with no fake events, providers, models, workflows, prompts,
  costs, or export ids.
- **Denied state**: Cross-tenant or unauthorized filters and exports fail closed
  without forbidden tenant labels or run details.
- **Mutation persisted**: The export action creates or updates a persisted
  `usage_export_requests` row and returns status/artifact metadata from that
  row only.
- **Unavailable state**: Storage or dependency failures render a safe
  unavailable/failed result without fake artifact references.

## Redaction Contract

The browser contract must not include raw prompts, raw completions, memory
content, private run payloads, raw tool payloads, secrets, credential values,
authorization headers, provider tokens, local filesystem paths, stack traces,
or unauthorized tenant labels.

## Playwright Contract

- Playwright loads the workspace with local-principal authentication.
- The flow must render seeded live usage state and prove empty state through
  backend setup or route evidence.
- The flow must perform the visible usage export action.
- Post-UI verification confirms the export request and safe artifact metadata
  through the backend API or redaction-safe qa056 database query.
