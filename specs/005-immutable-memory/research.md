# Research: Immutable Versioned Memory

**Feature**: Immutable Versioned Memory  
**Date**: 2026-04-24

## Decision: Store each memory version as a full canonical JSON snapshot

**Rationale**: The spec requires replay to any authorized version and explicit
representation of nulls and removals. Full snapshots make current-head reads,
replay, diffing, content hashing, and crash recovery deterministic without
reapplying patch chains during runtime execution.

**Alternatives considered**:

- Patch/event deltas: reduces write size but makes replay and diff correctness
  depend on every prior patch and complicates removal/null semantics.
- Mutable JSON document with audit trail: violates append-only immutability and
  makes stale-head conflict detection fragile.

## Decision: Use a separate `memory_heads` projection

**Rationale**: The immutable source of history belongs in `memory_versions`,
while current execution needs a single fast current-head lookup. A projection
row per scope allows one indexed read for runtime and one transactional update
when a new version is accepted.

**Alternatives considered**:

- `is_current` flag on versions: requires updating old version rows, which
  weakens the "versions are never updated" rule.
- Query `max(version_sequence)` for every read: preserves immutability but
  adds avoidable latency and locking complexity to hot runtime reads.

## Decision: Define scope by tenant, workflow lineage, agent, and memory key

**Rationale**: This follows the clarified requirement and lets memory survive
across runs of the same workflow lineage while still isolating tenants and
agent-owned keys. It also aligns memory with published workflow lineage rather
than individual runtime attempts.

**Alternatives considered**:

- Run-scoped memory: too narrow because future runs in the same workflow
  lineage would not see prior authorized memory.
- Tenant-wide agent memory only: too broad because unrelated workflow lineages
  could share state accidentally.

## Decision: Require expected-head optimistic concurrency

**Rationale**: Non-initial writes must prove which head they observed. The
repository locks the current head row and advances it only if the expected
version still matches. This prevents silent replacement while preserving normal
read concurrency.

**Alternatives considered**:

- Last-write-wins: violates stale-head acceptance criteria.
- Always serializable transactions: correct but heavier than required when a
  row-level head lock and unique initial-write constraints provide the needed
  guarantees.

## Decision: Use database constraints and triggers as immutability backstop

**Rationale**: Application code should never mutate memory versions, but a
PostgreSQL trigger that rejects `UPDATE` and `DELETE` on `memory_versions`
protects against future scripts, migrations, and repository mistakes.

**Alternatives considered**:

- Application-only immutability: easier to implement but provides no defense
  against out-of-band writes.
- Database role with insert-only grants: useful later, but local migrations and
  tests still benefit from an explicit trigger.

## Decision: Link memory versions to runtime run, step, bundle, and lineage

**Rationale**: The durable runtime already records pinned execution bundles and
parent-child run lineage. Memory writes need to be explainable in the same
debugging surface, so versions created during execution store `workflow_run_id`,
`run_step_id`, `run_bundle_id`, `bundle_digest`, and optional
`run_lineage_id`.

**Alternatives considered**:

- Store only actor metadata: loses the exact pinned bundle and parent-child
  context needed for replay and incident analysis.
- Store links only in audit events: makes the version record less useful and
  couples lineage reconstruction to audit retention behavior.

## Decision: Expose FastAPI memory APIs and an internal runtime protocol

**Rationale**: Reviewers and operators need current-head, history, replay, diff,
and audit APIs, while runtime execution needs a narrower facade that always
passes pinned bundle and run context. Separate contracts keep external behavior
stable and runtime safety rules explicit.

**Alternatives considered**:

- Runtime directly uses repository methods: faster to wire but bypasses policy,
  audit, and pinned-bundle checks.
- Only expose internal APIs: insufficient for reviewer replay, diff, and audit
  workflows required by the spec.

## Decision: Index by tenant plus scope, version sequence, runtime links, and audit time

**Rationale**: Access patterns are tenant-scoped current-head lookup, scope
history, lineage traversal, runtime traceability, and audit review by time or
action. Btree indexes on these dimensions cover required queries without
indexing raw memory content.

**Alternatives considered**:

- Broad GIN index on JSONB content: out of scope, increases write cost, and
  expands privacy risk for sensitive memory content.
- Minimal primary-key indexes only: would miss the current-head and history
  latency goals.

## Decision: Retain memory lineage indefinitely and mark archival state

**Rationale**: The feature assumes historical versions are retained
indefinitely unless a future retention policy changes that. Archival markers
allow cold-data workflows and operator views without deleting or mutating
history.

**Alternatives considered**:

- Hard delete old versions: violates replay, audit, and lineage requirements.
- Immediate object-storage tiering: premature for the initial transactional
  JSON snapshot scope and needs a separate encryption/retention design.
