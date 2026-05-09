# Data Model: Runtime Agent Communication Graph For Runs

## RuntimeAgentGraphProjection

- `workflow_run_id`: Run identifier being inspected.
- `tenant_id`: Tenant scope for the run, when tenant-scoped.
- `source`: Runtime graph source.
- `state`: Ready, empty, partial, denied, not found, or error.
- `runtime_status`: Overall safe run status.
- `partial`: Whether graph evidence is incomplete or unmapped.
- `partial_reasons`: Safe reasons explaining missing or unmapped evidence.
- `provenance`: Published workflow version, execution bundle, run status, generated timestamp, and evidence counts.
- `nodes`: Runtime graph nodes derived from topology and evidence.
- `edges`: Runtime graph edges derived from topology and evidence.
- `accessibility`: Node, edge, and graph summaries for keyboard-readable alternatives.

## RuntimeGraphNode

- `node_id`: Stable graph node identifier.
- `label`: Safe node label.
- `category`: Coordinator agent, sub-agent, tool, join, approval, handoff, terminal, subworkflow, or unknown.
- `status`: Runtime status using action-first precedence.
- `summary`: Safe runtime summary for the node.
- `started_at`: Safe timestamp label or ISO timestamp when available.
- `finished_at`: Safe timestamp label or ISO timestamp when available.
- `attempt_count`: Number of observed attempts when available.
- `layout`: Existing graph layout hint.
- `badges`: Runtime status, validation, partial, or provenance badges.
- `references`: Safe runtime evidence references.
- `accessibility_label`: Keyboard-readable summary.

## RuntimeGraphEdge

- `edge_id`: Stable graph edge identifier.
- `source_node_id`: Source node identifier.
- `target_node_id`: Target node identifier.
- `label`: Safe directional edge label.
- `category`: Delegates, sends context, returns result, joins, hands off, failure route, retry, approval resume, or transition.
- `status`: Runtime edge status using action-first precedence.
- `summary`: Safe runtime communication summary.
- `badges`: Runtime status, partial, retry, or evidence badges.
- `references`: Safe evidence references.
- `accessibility_label`: Keyboard-readable summary.

## RuntimeEvidenceReference

- `reference_id`: Stable reference string for the evidence item.
- `reference_type`: Run step, timeline event, handoff, approval, gateway attempt, tool call, delivery, artifact, lineage, bundle, or graph partial evidence.
- `status`: Safe evidence status.
- `label`: Safe user-facing label.
- `summary`: Safe summary with protected content removed.
- `href`: Safe link to an existing run, timeline, replay, artifact, or operations surface when available.
- `occurred_at`: Optional safe timestamp.

## RuntimeGraphProvenance

- `workflow_run_id`: Run identifier.
- `workflow_version_bundle_id`: Published workflow version identifier when available.
- `run_bundle_id`: Pinned execution bundle identifier when available.
- `bundle_digest`: Safe digest prefix or full digest according to existing bundle patterns.
- `run_status`: Overall run status.
- `generated_at`: Projection generation timestamp.
- `evidence_counts`: Counts for run steps, timeline events, handoffs, gateway attempts, tool calls, deliveries, artifacts, and unmapped evidence.

## State Transitions

- `empty` -> `queued` or `partial` when topology exists but runtime evidence is not yet present.
- `queued` -> `running` when run steps or timeline show active work.
- `running` -> `waiting` or `paused` when approval, handoff, child wait, or manual-resolution evidence exists.
- `running` -> `retry_scheduled` when retry evidence exists.
- `running` -> `succeeded` or `completed` when terminal success evidence exists.
- `running` -> `failed` when terminal failure evidence exists.
- Any mapped state -> `partial` when required topology, bundle, or evidence mapping is incomplete.

## Validation Rules

- Cross-tenant requests must return denied or not found without graph content.
- Protected raw content must not appear in labels, summaries, references, detail panels, screenshots, or QA artifacts.
- Runtime graph records must be derived from durable records; QA seed data is the only deterministic fixture path.
- Evidence without a safe node or edge mapping must remain graph-level partial evidence.
- Missing topology must not cause fake graph nodes or edges to be created.
- Unknown statuses must render as unavailable or partial with safe labels.
