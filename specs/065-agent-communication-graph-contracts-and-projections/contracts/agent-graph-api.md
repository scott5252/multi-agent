# Contract: Agent Communication Graph API

## GET /admin/workflows/drafts/{workflow_draft_id}/agent-graph

Returns a safe Agent Communication Graph projection for the current durable
workflow draft revision.

### Success 200

```json
{
  "graph_id": "draft:aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  "source": "draft",
  "state": "ready",
  "partial": false,
  "provenance": {
    "source_type": "draft",
    "workflow_draft_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
    "workflow_version_bundle_id": null,
    "workflow_lineage_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
    "workflow_key": "design-review",
    "revision": "3",
    "source_revision_id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
    "source_digest": "sha256...",
    "scope_type": "tenant",
    "tenant_id": "11111111-1111-1111-1111-111111111111",
    "generated_at": "2026-05-09T00:00:00Z"
  },
  "nodes": [
    {
      "node_id": "node:coordinator",
      "node_key": "coordinator",
      "category": "coordinator_agent",
      "label": "Coordinator",
      "summary": "Coordinates specialist work.",
      "status": "ready",
      "role_key": "coordinator",
      "layout": {"x": 0, "y": 0},
      "references": [],
      "badges": [],
      "accessibility_label": "Coordinator agent node Coordinator is ready."
    }
  ],
  "edges": [],
  "badges": [],
  "accessibility": {
    "summary": "Agent graph has 1 node and 0 edges.",
    "node_summaries": ["Coordinator agent node Coordinator is ready."],
    "edge_summaries": []
  }
}
```

### Errors

- `401`: Missing or invalid local-principal/Auth0 context.
- `403`: Principal cannot access the draft scope.
- `404`: Draft ID is not found.

## GET /admin/workflows/versions/{workflow_version_bundle_id}/agent-graph

Returns a safe Agent Communication Graph projection for a published workflow
bundle. When a full compiled document is unavailable, returns `state:
"partial"` and `partial: true` with safe provenance and graph-level badges only.

### Success 200

Same response schema as the draft endpoint with `source: "published_version"`
and `workflow_version_bundle_id` populated in provenance.

### Errors

- `401`: Missing or invalid local-principal/Auth0 context.
- `403`: Principal cannot access the published bundle scope or sharing grant.
- `404`: Published bundle ID is not found.

## Contract Rules

- Response strings are safe for browser rendering and bounded in length.
- IDs derive from durable workflow IDs, node keys, and edge keys.
- No raw prompt, completion, memory, channel, credential, provider, stack-trace,
  local-path, or raw tool payload is returned.
- Empty graphs return `state: "empty"` and do not fabricate nodes or edges.
- Partial graphs return safe provenance and badges without guessing topology.
