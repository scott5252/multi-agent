# Contract: React Workflow Graph And Agent Role Builder

## Persistence Boundary

Spec 070 does not introduce a new public route family. It consumes the Spec 069
React workflow document save contract:

```http
POST /admin/api/react/workflows/{workflow_key}/drafts/{draft_id}/save
```

The request continues to submit a full workflow document plus revision token and
idempotency key. The response continues to return an admin mutation result and a
fresh workflow builder envelope.

## Browser Editor Contract

The React editor builds a full document payload from controlled UI sections:

- Metadata section
- Role section
- Contract section
- Topology node section
- Topology edge section
- Join policy section
- Approval gate section
- Subworkflow reference section
- Layout annotation section

Each section must be able to produce:

- Current safe document fragment.
- Dirty state relative to the loaded envelope.
- Stable collection order.
- Dependency warnings derived from currently visible references.
- Backend validation anchors from returned findings.

Client-side dependency warnings are advisory only. Backend validation remains
authoritative for persistence and publish readiness.

## Save Request Expectations

The save request must include:

- `base_revision_token`
- `idempotency_key`
- `document`
- Optional safe editor metadata already accepted by the Spec 069 contract

The `document` must preserve unrelated sections from the loaded envelope when a
single editor section changes. The UI must not drop prompt/profile references,
skill bindings, test requirements, annotations, or future unknown safe fields
while saving graph edits.

## Save Response Expectations

The UI must handle these response classes:

- Successful mutation: replace local base document with returned envelope,
  clear dirty state, show backend mutation status.
- Idempotent replay: treat returned envelope as durable success without adding
  another revision.
- Validation failure: keep safe local edits and render backend-owned findings
  by section and field path.
- Stale conflict: preserve safe local edits, show reload/recovery action, and
  avoid overwriting the newer revision.
- Authorization failure: render denied state without exposing unauthorized
  tenant labels or raw payloads.
- Oversized/unsafe payload failure: render redaction-safe findings only.

## Validation Anchors

Validation findings returned from the backend should map to these UI anchors:

- `metadata`
- `roles`
- `contracts`
- `nodes`
- `edges`
- `joins`
- `approvals`
- `subworkflows`
- `layout`
- `publish`

When a finding includes a `field_path`, the editor should show it near the
matching collection item when possible and in the validation panel otherwise.

## Graph Projection

The graph preview uses the current editable document, not only the last saved
backend graph, so users can review unsaved topology before saving. The preview
must have an equivalent keyboard-readable list projection containing:

- Node key, label, type, and role/join/approval/subworkflow reference.
- Edge key, source, target, branch label, and contract reference.
- Join key, inbound edge count, quorum behavior, timeout, and merge contract.
- Approval and subworkflow summaries.

The graph projection is display-only in this spec. Forms and lists are the
required editing controls.

## Compatibility

Existing workflow create, validate, publish, graph preview, and lower-level
workflow APIs remain supported. Existing read-only graph previews remain valid
for workflows that are not being edited.
