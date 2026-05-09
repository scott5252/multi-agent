# Research: Runtime Agent Communication Graph For Runs

## Decision: Use Existing Runtime Evidence First

**Rationale**: Run records, execution bundles, run steps, runtime timeline events, audit logs, gateway attempts, tool-call summaries, delivery summaries, handoffs, and artifact references already provide enough durable evidence for a useful read-only runtime graph. This avoids premature message-level persistence and leaves the deeper evidence question for Spec 068.

**Alternatives considered**:

- Add new interaction records now: rejected because Spec 067 explicitly forbids message-level persistence and Spec 068 owns the durable evidence decision.
- Infer from React UI state: rejected because production graph data must be backend-owned and durable.

## Decision: Add Admin Run Inspection Route

**Rationale**: `/admin/runs/{workflow_run_id}` already hosts timeline, replay, lineage, bundle, and export evidence with tenant-aware authorization. Adding `/admin/runs/{workflow_run_id}/agent-graph` keeps the runtime graph near the existing run inspection route family and makes curl regression coverage straightforward.

**Alternatives considered**:

- Embed graph only in operations workbench envelope: useful for UI but weaker for route-level contract tests and curl coverage.
- Add a user-facing `/runs/{id}` graph route first: deferred because Admin inspection is the safest initial surface; user-run reuse can follow only where existing channel-run contracts support it.

## Decision: Reuse AgentCommunicationGraph With Additive Runtime Evidence

**Rationale**: Spec 065 and Spec 066 already define a safe graph contract and UI. Runtime graph needs additional statuses, evidence references, and provenance fields, but the same graph/list/detail model remains valid.

**Alternatives considered**:

- Create a second runtime-only graph schema: rejected to avoid duplicate visualization contracts and UI branching.
- Overload existing fields with unstructured dictionaries: rejected because generated TypeScript and visible-detail tests need stable contracts.

## Decision: Status Precedence Is Action-First

**Rationale**: A node with both completed and failure/retry evidence should guide the reviewer to the most important action. Precedence is failed, manual-resolution-required, paused or waiting, retry-scheduled, running, succeeded or completed, skipped, queued, unavailable.

**Alternatives considered**:

- Latest event wins: rejected because a later neutral event can hide a failure.
- Severity-only ordering: rejected because waiting/manual-resolution states are operationally urgent even when not failures.

## Decision: Unmapped Evidence Becomes Graph-Level Partial State

**Rationale**: Evidence that cannot be tied to a node or edge is still useful, but synthesizing nodes would make the graph appear more precise than the platform can prove. Graph-level partial badges and summaries keep the state honest.

**Alternatives considered**:

- Create an "unmapped" node: rejected because it looks like a real runtime participant.
- Drop unmapped evidence: rejected because reviewers need to know evidence existed but could not be positioned.

## Decision: Operations Workbench Is The First UI Integration

**Rationale**: The workbench already loads `RunDebugEnvelope` with timeline, branch, gateway, tool, delivery, lineage, replay, and bundle summaries. It is the natural place to add a read-only runtime graph while preserving existing timeline panels.

**Alternatives considered**:

- Add a new navigation item: rejected because the graph is run-specific and belongs in existing run inspection.
- Replace the timeline panel: rejected because timeline remains the canonical chronological view.
