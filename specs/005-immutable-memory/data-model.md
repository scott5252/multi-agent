# Data Model: Immutable Versioned Memory

**Feature**: Immutable Versioned Memory  
**Date**: 2026-04-24

## Overview

The memory subsystem stores immutable memory snapshots in PostgreSQL. Historical
truth is in `memory_versions`; fast runtime reads use `memory_heads`; audit
entries store metadata, hashes, and redacted summaries without raw content.
Every table is tenant-scoped, and runtime-created versions link back to pinned
execution bundles, workflow runs, run steps, and parent-child run lineage.

## Entities

### Memory Scope

Represents the ownership and current-head uniqueness boundary for one memory
key.

- `memory_scope_id`: UUID primary key
- `tenant_id`: tenant owner, nullable only where existing platform-level
  tenant semantics allow it
- `workflow_lineage_id`: stable workflow lineage id from the published workflow
  family
- `agent_key`: stable agent key within the workflow lineage
- `memory_key`: stable memory key owned by the agent
- `created_by_principal_id`: user or service principal that first created the
  scope
- `created_by_workflow_run_id`: nullable runtime run that first created the
  scope
- `created_at`: timestamp

Validation rules:

- Unique `(tenant_id, workflow_lineage_id, agent_key, memory_key)`.
- `agent_key` and `memory_key` must be non-empty and normalized before insert.
- Scope tenant must match any linked workflow run, run bundle, or run lineage.
- Scope records are not deleted while versions or audit events exist.

### Memory Version

Represents one immutable canonical JSON memory snapshot.

- `memory_version_id`: UUID primary key
- `tenant_id`: tenant owner
- `memory_scope_id`: owning scope
- `previous_memory_version_id`: nullable predecessor in the same scope
- `version_sequence`: monotonically increasing sequence starting at 1 per scope
- `content`: canonical JSONB snapshot
- `content_sha256`: SHA-256 of canonical JSON bytes
- `content_size_bytes`: canonical byte length
- `change_summary_redacted`: nullable redacted summary
- `change_reason`: nullable caller-provided reason
- `actor_principal_id`: user, service principal, or workflow actor
- `source_type`: `api`, `runtime`, `migration`, `support`
- `workflow_run_id`: nullable runtime run that created the version
- `run_step_id`: nullable runtime step that created the version
- `run_bundle_id`: nullable pinned runtime execution bundle
- `bundle_digest`: nullable pinned bundle digest
- `run_lineage_id`: nullable parent-child run lineage edge
- `idempotency_key`: nullable caller/runtime idempotency key
- `created_at`: timestamp

Validation rules:

- Existing rows cannot be updated or deleted.
- Initial version must have `previous_memory_version_id = null` and
  `version_sequence = 1`.
- Non-initial version must point to the immediately prior head in the same
  tenant and scope.
- `content_sha256` must match canonical JSON bytes.
- Runtime fields must all match the same tenant and pinned bundle when present.
- Unique `(tenant_id, memory_scope_id, version_sequence)`.
- Unique `(tenant_id, memory_scope_id, idempotency_key)` when idempotency key
  is present.

### Memory Head

Represents the current version projection for one scope.

- `memory_scope_id`: UUID primary key and foreign key to `memory_scopes`
- `tenant_id`: tenant owner
- `workflow_lineage_id`: denormalized workflow lineage id for indexed lookup
- `agent_key`: denormalized agent key
- `memory_key`: denormalized memory key
- `current_memory_version_id`: current version id
- `version_sequence`: current sequence
- `content_sha256`: hash of current version content
- `updated_by_principal_id`: actor that advanced the head
- `updated_by_workflow_run_id`: nullable runtime run that advanced the head
- `updated_at`: timestamp

Validation rules:

- Exactly one head row may exist per memory scope.
- Head version must belong to the same scope and tenant.
- Head updates occur only in the same transaction that inserts a new memory
  version and audit event.
- A head cannot point to a version marked archived-unavailable by an append-only
  archive event.

### Memory Audit Event

Represents content-free audit evidence for memory writes and reads.

- `memory_audit_event_id`: UUID primary key
- `tenant_id`: tenant owner
- `memory_scope_id`: nullable when scope resolution failed
- `memory_version_id`: nullable version involved
- `previous_memory_version_id`: nullable predecessor for write events
- `current_memory_version_id`: nullable head observed or produced
- `workflow_lineage_id`: nullable workflow lineage id
- `agent_key`: nullable agent key
- `memory_key`: nullable memory key
- `workflow_run_id`: nullable runtime run source
- `run_step_id`: nullable runtime step source
- `run_bundle_id`: nullable pinned bundle source
- `bundle_digest`: nullable pinned bundle digest
- `run_lineage_id`: nullable parent-child lineage edge
- `actor_principal_id`: user, service principal, or workflow actor
- `action_type`: `create_version`, `get_head`, `get_version`, `list_history`,
  `replay`, `diff`, `archive_mark`
- `outcome`: `allowed`, `denied`, `not_found`, `conflict`, `invalid`
- `content_sha256`: nullable content hash for write/read target
- `base_memory_version_id`: nullable base version for diff audit events
- `compare_memory_version_id`: nullable compare version for diff audit events
- `compared_content_sha256`: nullable second hash for diff
- `change_summary_redacted`: nullable redacted summary
- `denial_reason`: nullable redacted denial/conflict reason
- `trace_id`: trace id
- `created_at`: timestamp

Validation rules:

- `payload`, summaries, and denial reasons must not contain raw memory content.
- Audit entries are append-only.
- Failed scope resolution still creates an audit event when a tenant and actor
  are known.

### Memory Diff

Represents an API result, not a persisted table in the initial implementation.

- `base_memory_version_id`: left-side version
- `compare_memory_version_id`: right-side version
- `memory_scope_id`: shared scope
- `additions`: JSON-pointer paths and values added in compare
- `removals`: JSON-pointer paths and removed value summaries
- `changes`: JSON-pointer paths with base and compare value summaries
- `content_hashes`: hashes for both versions

Validation rules:

- Both versions must be in the same tenant and memory scope.
- Identical version ids return empty additions, removals, and changes.
- Explicit removal markers are distinct from JSON null.

### Memory Replay Result

Represents an API result, not a persisted table in the initial implementation.

- `memory_scope_id`: scope replayed
- `target_memory_version_id`: target version
- `version_sequence`: target sequence
- `content`: target canonical JSON snapshot
- `content_sha256`: target content hash
- `lineage`: ordered version metadata from first version to target or a
  requested window around the target

Validation rules:

- Target version must be authorized and in the requested scope.
- Replay returns the target snapshot directly and may include lineage metadata
  for reviewer proof.

### Memory Archive Event

Represents append-only archival state linked to `memory_versions`, plus audit
evidence.

- `memory_archive_event_id`: UUID primary key
- `tenant_id`: tenant owner
- `memory_version_id`: archived version
- `archived_at`: archive marker timestamp
- `archive_reason`: redacted archive reason
- `actor_principal_id`: user, service principal, or workflow actor
- `memory_audit_event_id`: audit entry for the archive action

Validation rules:

- Archival must not update `memory_versions` content, hashes, predecessor,
  version sequence, creator metadata, or any other version column.
- Current head versions cannot be archived into an unavailable tier.
- Archive actions are tenant-scoped and audited.

## Relationships

- One Memory Scope has many Memory Versions.
- One Memory Scope has zero or one Memory Head.
- One Memory Version has zero or one previous Memory Version in the same scope.
- One Memory Version may link to one Runtime Workflow Run.
- One Memory Version may link to one Runtime Run Step.
- One Memory Version may link to one Runtime Execution Bundle.
- One Memory Version may link to one Runtime Run Lineage edge when written by a
  child or parent-child flow.
- One Memory Scope and Memory Version have many Memory Audit Events.
- One Memory Version has zero or many Memory Archive Events.

## State Transitions

### Memory Scope

```text
absent -> created
created -> active
active -> archived_scope (future policy only)
```

The initial implementation creates scopes and keeps them active.

### Memory Version

```text
created
```

Memory version content and lineage never change after `created`.

### Memory Archive Event

```text
absent -> archived_marker_recorded
```

Archival events only mark availability/review state and must not affect replay
correctness.

### Memory Head

```text
absent -> points_to_v1
points_to_vN -> points_to_vN_plus_1
```

Head changes are projections created by accepted writes. Historical versions
remain unchanged.

## Access Patterns

### Resolve Current Head For Runtime

Inputs: tenant id, workflow lineage id, agent key, memory key, workflow run id,
run step id, run bundle id, bundle digest.

Steps:

1. Verify the runtime run and bundle belong to the tenant and bundle digest.
2. Resolve the memory scope by natural key.
3. Return explicit no-memory result if no scope or head exists.
4. Join `memory_heads` to `memory_versions` and return authorized content.
5. Insert `memory_audit_events` with action `get_head`.

### Create Initial Version

Inputs: tenant id, scope natural key, canonical content,
`assert_no_current_head = true`, actor/runtime source, reason, redacted summary.

Steps:

1. Resolve or create `memory_scopes`.
2. Confirm no head exists for the scope.
3. Insert `memory_versions` with sequence 1 and no predecessor.
4. Insert `memory_heads` pointing to the new version.
5. Insert write audit event and commit.
6. Return 409 if a competing initial write created a head first.

### Create Non-Initial Version

Inputs: tenant id, scope, canonical content, `expected_current_version_id`,
actor/runtime source, reason, redacted summary.

Steps:

1. Resolve scope and lock its `memory_heads` row `FOR UPDATE`.
2. Compare current head to `expected_current_version_id`.
3. Insert `memory_versions` with predecessor equal to the locked head and next
   sequence.
4. Update `memory_heads` to the new version.
5. Insert write audit event and commit.
6. Return 409 if the expected head is stale.

### List History

Inputs: tenant id, scope id or natural key, cursor, limit.

Steps:

1. Resolve scope with tenant predicate.
2. Query versions ordered by `version_sequence desc`.
3. Include raw content only for callers authorized for memory content.
4. Insert content-free audit event.

### Replay To Version

Inputs: tenant id, memory version id, optional scope assertion.

Steps:

1. Fetch version with tenant predicate.
2. Verify the optional scope assertion and access policy.
3. Return the target snapshot and lineage metadata.
4. Insert replay audit event.

### Diff Versions

Inputs: tenant id, base version id, compare version id.

Steps:

1. Fetch both versions with tenant predicate.
2. Verify both belong to the same memory scope.
3. Produce JSON-pointer additions, removals, and changes.
4. Insert diff audit event with both hashes and no raw content.

## Indexes And Constraints

```text
memory_scopes:
  pk(memory_scope_id)
  unique(tenant_id, workflow_lineage_id, agent_key, memory_key)
  index(tenant_id, workflow_lineage_id, agent_key)

memory_versions:
  pk(memory_version_id)
  unique(tenant_id, memory_scope_id, version_sequence)
  unique(tenant_id, memory_scope_id, idempotency_key) where idempotency_key is not null
  index(tenant_id, memory_scope_id, created_at desc)
  index(tenant_id, previous_memory_version_id)
  index(tenant_id, workflow_run_id)
  index(tenant_id, run_bundle_id)
  index(tenant_id, run_lineage_id)

memory_archive_events:
  pk(memory_archive_event_id)
  index(tenant_id, memory_version_id, archived_at desc)
  index(tenant_id, archived_at desc)

memory_heads:
  pk(memory_scope_id)
  unique(tenant_id, workflow_lineage_id, agent_key, memory_key)
  index(tenant_id, current_memory_version_id)

memory_audit_events:
  pk(memory_audit_event_id)
  index(tenant_id, created_at desc)
  index(tenant_id, memory_scope_id, created_at desc)
  index(tenant_id, memory_version_id)
  index(tenant_id, workflow_run_id)
  index(tenant_id, run_bundle_id)
  index(tenant_id, action_type, outcome, created_at desc)
```

## Immutability Enforcement

- SQLAlchemy models expose no mutating domain methods for `MemoryVersion`.
- Repositories insert versions and never issue update/delete statements against
  `memory_versions`.
- Alembic migration adds a PostgreSQL trigger that rejects `UPDATE` and
  `DELETE` on `memory_versions`.
- Tests attempt direct ORM mutation and SQL update/delete to prove the trigger
  prevents in-place changes.
- Head projection updates are allowed because `memory_heads` is explicitly a
  mutable projection, not historical truth.
