# Contract: Admin Replay And Visualization Views

The feature adds minimal server-rendered admin pages that consume the same
FastAPI schemas used by API clients. The pages are not the primary surface for
this spec, but they define how replay, lineage, and bundle data should be
visualized consistently.

## `/admin/runs`

Search and filter production run-debug evidence.

**Required controls**:

- Filter by run id, workflow id, status, failure category, time range, agent,
  tool, model selection source, notification status, and lineage relationship.
- Cursor-based pagination with bounded page size.
- Link each result to timeline, replay, lineage, bundle, and export actions
  when authorized.

**Required safety states**:

- Cross-tenant runs return safe not-found or forbidden behavior and create a
  denied inspection audit event.
- Search results never render raw prompts, memory content, tool payloads,
  secret values, credentials, or unrestricted notification destinations.

## `/admin/runs/{workflow_run_id}`

Chronological timeline detail for one run.

**Required sections**:

- Run summary with status, trace id, failure stage, safe failure reason, and
  recommended investigation category.
- Pinned version-bundle summary with workflow, contract, prompt, model, and
  tool-policy version references.
- Timeline event list sorted by sequence.
- Linked trace records for handoffs, validations, memory writes, tool usage,
  model selections, notifications, and secret access.
- Capture gaps and unavailable markers.
- Parent-child lineage summary and links to authorized related runs.

## `/admin/runs/{workflow_run_id}/replay`

Replay-style view of the run's historical evidence.

**Required behavior**:

- Render immutable events in sequence with timestamp, status after event,
  trace id, actor or system origin, safe summary, and linked trace evidence.
- Allow stepping event-by-event without triggering runtime side effects.
- Show replay checkpoints that explain when a run was accepted, started,
  waited, resumed, retried, failed, completed, or timed out.
- Mark unavailable diagnostic traces inline using CaptureGapMarker data.
- Include child-run events only when the viewer requests authorized child
  lineage.

## `/admin/runs/{workflow_run_id}/lineage`

Graph-oriented parent-child run view.

**Required behavior**:

- Render visible run nodes with run id, status, workflow reference, start/end
  times, and safe failure category.
- Render edges for parent-child, retry, resumption, and delegation
  relationships.
- Render unauthorized related runs as redacted boundary nodes with relationship
  type and no protected identifiers.
- Link each visible node to its timeline and replay views.

## `/admin/runs/{workflow_run_id}/bundle`

Pinned execution bundle and version reference view.

**Required behavior**:

- Show execution bundle id, digest, activation state at acceptance, workflow
  version, contract refs, prompt refs, model config refs, tool-policy refs,
  and migration records.
- Distinguish active-at-acceptance from latest-active-now when available.
- Never render raw workflow definitions, prompt bodies, secret values, or
  provider tokens unless a future authorized view explicitly permits it.

## `/admin/runs/{workflow_run_id}/exports`

Create and inspect redacted debug-evidence exports.

**Required behavior**:

- Allow administrators and auditors to select run-only or authorized-child
  lineage scope.
- Show included and excluded sections after redaction.
- Display export status, expiration, artifact availability, and safe failure
  reason.
- Audit create, share, download, failed, expired, and revoked actions.

## View Model Rules

- View models are generated from API/domain response schemas rather than raw
  ORM rows.
- All fields pass viewer-aware authorization and redaction before rendering.
- UI interactions never re-run workflows, call models, invoke tools, deliver
  notifications, resolve secrets, or mutate historical evidence.
- Timeline, replay, lineage, and bundle views share the same trace id and
  event ids as structured logs and metrics.
