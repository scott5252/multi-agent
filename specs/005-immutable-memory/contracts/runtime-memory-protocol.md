# Runtime Memory Protocol

**Feature**: Immutable Versioned Memory  
**Date**: 2026-04-24  
**Protocol Version**: `runtime-memory.v1`

This contract defines how the durable orchestration runtime reads and writes
memory safely. Runtime code uses `MemoryService`; it does not update memory
tables directly.

## Compatibility Rules

Runtime memory calls must declare `protocol_version = "runtime-memory.v1"`
either explicitly in the runtime context object or through the typed service
facade used by the orchestration runtime. Breaking changes require a new
protocol version, contract review, compatibility notes for in-flight runs, and
tests proving older pinned execution bundles continue to use their original
memory protocol behavior.

## Required Runtime Context

Every runtime memory call must include:

- `protocol_version`
- `tenant_id`
- `workflow_lineage_id`
- `agent_key`
- `memory_key`
- `workflow_run_id`
- `run_step_id`
- `run_bundle_id`
- `bundle_digest`
- `actor_principal_id` or workflow service principal
- `trace_id`
- Optional `run_lineage_id` when the call occurs inside a parent-child run
  relationship

The memory service must verify that `workflow_run_id`, `run_step_id`,
`run_bundle_id`, `bundle_digest`, and `run_lineage_id` all belong to the same
tenant and pinned execution context.

## Current Head Read

```python
await memory_service.get_current_head_for_runtime(
    tenant_id=tenant_id,
    workflow_lineage_id=workflow_lineage_id,
    agent_key=agent_key,
    memory_key=memory_key,
    workflow_run_id=workflow_run_id,
    run_step_id=run_step_id,
    run_bundle_id=run_bundle_id,
    bundle_digest=bundle_digest,
    actor_principal_id=actor_principal_id,
    trace_id=trace_id,
)
```

Success returns:

- `has_memory`
- `memory_scope_id`
- `current_memory_version_id` when present
- `version_sequence` when present
- `content_sha256` when present
- `content` only when runtime policy allows raw memory use

The service records a `get_head` audit event with no raw content.

## Initial Write

```python
await memory_service.write_version_for_runtime(
    tenant_id=tenant_id,
    workflow_lineage_id=workflow_lineage_id,
    agent_key=agent_key,
    memory_key=memory_key,
    content=canonical_json,
    assert_no_current_head=True,
    expected_current_version_id=None,
    workflow_run_id=workflow_run_id,
    run_step_id=run_step_id,
    run_bundle_id=run_bundle_id,
    bundle_digest=bundle_digest,
    run_lineage_id=run_lineage_id,
    idempotency_key=idempotency_key,
    change_reason=change_reason,
    change_summary_redacted=change_summary_redacted,
    actor_principal_id=actor_principal_id,
    trace_id=trace_id,
)
```

The call succeeds only when no current head exists for the scope. If another
runtime or API caller creates the first head first, the service returns a
conflict and the workflow node must reload current memory before retrying.

## Non-Initial Write

```python
await memory_service.write_version_for_runtime(
    tenant_id=tenant_id,
    workflow_lineage_id=workflow_lineage_id,
    agent_key=agent_key,
    memory_key=memory_key,
    content=canonical_json,
    assert_no_current_head=False,
    expected_current_version_id=observed_head_id,
    workflow_run_id=workflow_run_id,
    run_step_id=run_step_id,
    run_bundle_id=run_bundle_id,
    bundle_digest=bundle_digest,
    run_lineage_id=run_lineage_id,
    idempotency_key=idempotency_key,
    change_reason=change_reason,
    change_summary_redacted=change_summary_redacted,
    actor_principal_id=actor_principal_id,
    trace_id=trace_id,
)
```

The call succeeds only when `observed_head_id` is still the current head. A
stale expected head returns a conflict and must not be retried blindly. Runtime
nodes may reload memory and re-evaluate their intended write if the workflow
definition allows it.

## Transaction Rules

The memory repository must perform these steps in one transaction:

1. Resolve or create the memory scope.
2. Lock the current head row for non-initial writes.
3. Validate `assert_no_current_head` or `expected_current_version_id`.
4. Insert a new immutable memory version.
5. Insert or update the memory head projection.
6. Insert a content-free audit event.
7. Commit.

No domain event, queue signal, or runtime state transition may treat a memory
write as accepted until the transaction commits.

## Resume And Idempotency

Runtime memory writes should provide deterministic idempotency keys derived
from tenant id, workflow run id, run step id, bundle digest, memory scope, and
operation kind. If a worker crashes after commit but before acknowledging the
step, resume with the same idempotency key returns the already-created version
when content hash and concurrency precondition match.

If the idempotency key exists with different content or a different expected
head, the service returns a conflict and the runtime must surface a recoverable
failure rather than mutating memory.

## Parent-Child Lineage

When a child run writes memory, the runtime passes the `runtime_run_lineage`
edge connecting parent and child. The memory version stores that edge so
reviewers can trace whether a root run, child run, compensation run, manual
resume, or replay flow produced the memory state.

Parent and child runs must share tenant id. Cross-tenant lineage fails closed.

## Failure Semantics

- Missing current head for read: return explicit no-memory result.
- Missing current head for non-initial write: conflict.
- Existing head for initial write: conflict.
- Stale expected head: conflict.
- Missing or mismatched run bundle: forbidden or invalid runtime context.
- Unauthorized memory content access: forbidden and audited.
- Diff/replay of unrelated versions: invalid request and audited.

## Logging And Audit

Runtime logs, traces, and audit events may include ids, hashes, action names,
latency, outcome, and redacted summaries. They must not include raw memory JSON.
