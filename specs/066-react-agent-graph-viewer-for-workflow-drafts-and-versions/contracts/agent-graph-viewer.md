# Contract: React Agent Graph Viewer

## Existing Backend Inputs

The viewer consumes the Spec 065 API routes:

- `GET /admin/workflows/drafts/{workflow_draft_id}/agent-graph`
- `GET /admin/workflows/versions/{workflow_version_bundle_id}/agent-graph`

Both return `AgentCommunicationGraph`.

## Frontend Client Helpers

### `fetchDraftAgentGraph(workflowDraftId: string): Promise<AgentCommunicationGraph>`

- Builds `/admin/workflows/drafts/{workflowDraftId}/agent-graph`.
- Sends same-origin credentials and `Accept: application/json`.
- Validates the response with the generated `assertAgentCommunicationGraph` helper.
- Throws a safe error summary from existing problem-detail handling when the response is not OK.

### `fetchVersionAgentGraph(workflowVersionBundleId: string): Promise<AgentCommunicationGraph>`

- Builds `/admin/workflows/versions/{workflowVersionBundleId}/agent-graph`.
- Sends same-origin credentials and `Accept: application/json`.
- Validates the response with the generated `assertAgentCommunicationGraph` helper.
- Throws a safe error summary from existing problem-detail handling when the response is not OK.

## Component Contract

### `AgentGraphPanel`

Inputs:

- `graph: AgentCommunicationGraph | null`
- `sourceLabel: string`
- `loading: boolean`
- `error: string | null`
- `onRetry?: () => void`

Responsibilities:

- Render a read-only graph canvas from graph nodes and edges.
- Render graph-level state and badges.
- Render selectable nodes and edges.
- Render a selected-item detail panel.
- Render keyboard-readable node and edge lists with equivalent information.
- Render loading, empty, partial, denied, not-found, and generic error states.
- Never render graph records that are not present in the backend payload.

## Test Contract

- Component tests must cover ready draft graph rendering, published graph provenance, selected node detail, selected edge detail, accessible list selection, empty state, partial state, and safe visible-copy scans.
- Page tests must cover draft and version graph fetch helper integration.
- Playwright must capture desktop and mobile graph-panel screenshots and exercise at least one selected node or edge detail state.
- Curl regression does not need new route commands unless Spec 066 changes backend route behavior; it must still pass after UI changes.
