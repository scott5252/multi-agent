# Contract: Runtime Agent Communication Graph

## Backend Route

### `GET /admin/runs/{workflow_run_id}/agent-graph`

Query parameters:

- `tenant_id`: Optional tenant scope, matching existing Admin run inspection endpoints.

Authorization:

- Requires an authorized Admin principal.
- Tenant-scoped users may only inspect runs in their active tenant scope.
- Cross-tenant requests fail closed with safe problem details and no topology or evidence content.

Response:

- `200 AgentCommunicationGraph` with runtime graph source, runtime statuses, safe evidence references, provenance, and accessibility summaries.
- `403 SafeProblemDetail` for denied access.
- `404 SafeProblemDetail` when the run is not visible in the requested scope.

Required response behavior:

- `source` is `runtime_run`.
- `provenance.workflow_run_id` is the requested run identifier.
- `state` is `ready`, `empty`, or `partial` for successful responses.
- `partial` is true when topology, bundle, step, timeline, or evidence mapping is incomplete.
- Nodes and edges include runtime statuses and safe evidence references.

## Frontend Client Helper

### `fetchRunAgentGraph(workflowRunId: string, tenantId?: string | null): Promise<AgentCommunicationGraph>`

- Builds `/admin/runs/{workflowRunId}/agent-graph`.
- Includes `tenant_id` when the active tenant scope requires it.
- Sends same-origin credentials and `Accept: application/json`.
- Validates the payload with `assertAgentCommunicationGraph`.
- Throws a safe error summary using existing problem-detail handling.

## UI Contract

### `AgentGraphPanel` runtime reuse

Inputs:

- `graph: AgentCommunicationGraph | null`
- `sourceLabel: "Runtime run" | string`
- `loading: boolean`
- `error: string | null`
- `onRetry?: () => void`

Responsibilities:

- Render runtime statuses and badges without replacing timeline or branch panels.
- Render safe selected node and edge evidence details.
- Render keyboard-readable node and edge list alternatives.
- Render partial, empty, denied, and error states truthfully.
- Never synthesize nodes or evidence absent from the backend payload.

## Curl Contract

`curl_testing.md` must include:

- A success-path command for `/admin/runs/{workflow_run_id}/agent-graph`.
- A cross-tenant denied command for the same route family.
- JSON checks for `source == "runtime_run"`, requested run provenance, node or edge status coverage, accessibility summaries, and denied status.

## Test Contract

- Backend projection tests cover completed, failed/retrying, paused/manual-resolution, partial, empty, and denied runs.
- Route tests cover authorization, tenant scope, safe problem details, and no raw protected content.
- Frontend tests cover loading, ready runtime graph, selected runtime detail, partial state, denied/error state, and accessible list parity.
- Playwright validates desktop and mobile runtime graph screenshots and at least one selected failed or waiting detail state.
