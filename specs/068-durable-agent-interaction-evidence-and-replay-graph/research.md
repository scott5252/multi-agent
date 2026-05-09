# Research: Durable Agent Interaction Evidence And Replay Graph

## Decision: Add Minimal Durable Interaction Evidence

**Decision**: Add a new `runtime_interaction_evidence` table instead of overloading timeline events.

**Rationale**: Specs 065-067 provide topology, runtime status overlays, and safe evidence references. They still infer interaction direction from run steps and handoffs, while high-fidelity replay needs ordered source/target semantics for delegation, context transfer, result return, join contribution, approval pause/resume, and manual-resolution interactions. Generic timeline events do not enforce source/target keys, idempotency, classification, redacted metadata, or replay sequence.

**Alternatives Considered**:

- Reuse runtime timeline events only: rejected because timeline rows are broad event records and do not guarantee ordered edge-mappable interaction semantics.
- Add message-level transcripts: rejected because raw prompts, completions, memory, provider payloads, channel payloads, and tool outputs are explicitly disallowed.
- Store interaction JSON in existing run step refs: rejected because it would mix step output with cross-edge replay evidence and make idempotency/tenant queries harder.

## Decision: Repository-Level Idempotency

**Decision**: Use a unique tenant/run/idempotency key and return the existing record when the same interaction is recorded again.

**Rationale**: Worker retries and resumes can repeat graph node finalization and handoff persistence. Idempotency at the repository boundary makes the behavior stable for both direct service calls and graph execution instrumentation.

## Decision: Safe Metadata Only

**Decision**: Persist `safe_summary`, `classification`, `payload_digest`, `artifact_refs`, and redacted structured metadata. Sensitive keys in metadata are replaced by digest-only redaction objects.

**Rationale**: Interaction evidence is durable and graph-visible. It must be stricter than debug logs and cannot include raw prompts, completions, provider responses, credentials, private channel payloads, memory contents, raw tool outputs, or stack traces.

## Decision: Reuse Runtime Graph Route And Panel

**Decision**: Enrich `/admin/runs/{workflow_run_id}/agent-graph` and the existing `AgentGraphPanel` selected detail surface. Do not add another visualization route or framework.

**Rationale**: Specs 065-067 already established backend-owned graph contracts, generated TypeScript, React Flow rendering, accessible node/edge lists, and operations workbench integration.

## Decision: Additive Migration Only

**Decision**: Add only the interaction evidence table, indexes, and uniqueness constraint. Do not change existing runtime tables.

**Rationale**: The new data is additive, can be backfilled by future runtime executions, and avoids risky changes to established workflow run semantics.
