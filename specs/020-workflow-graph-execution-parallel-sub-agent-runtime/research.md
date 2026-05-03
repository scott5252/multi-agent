# Research: Workflow Graph Execution And Parallel Sub-Agent Runtime

## Bundle Loading

**Decision**: Load graph execution input from the run's
`RuntimeExecutionBundleRecord` and the referenced `WorkflowVersionBundle`
summary, preferring the compiled bundle document when available and falling
back to `summary_json` graph fields.

**Rationale**: The runtime run already pins a bundle id and digest. Reading the
run bundle preserves version-pinned execution and avoids drifting to a newer
workflow revision.

**Alternatives considered**: Re-query active workflow drafts was rejected
because drafts are mutable and violate replay expectations. Reading only
channel inputs was rejected because inputs do not contain graph topology.

## Graph Planning

**Decision**: Normalize bundle documents into a `GraphExecutionPlan` with nodes
by key, inbound/outbound edges, role references, join policies, contract
schemas, and terminal nodes before any execution step mutates state.

**Rationale**: A normalized plan lets the executor validate cycles, missing
entry nodes, missing role references, and join-policy shape once, producing
safe diagnostics before partially executing an invalid graph.

**Alternatives considered**: Walking the raw bundle document directly was
rejected because it spreads validation and makes resume harder to reason about.

## Parallel Scheduling

**Decision**: Execute graph nodes in deterministic waves. A wave contains ready
role nodes whose dependencies have succeeded, plus join/terminal decisions that
can be evaluated without external calls. Role nodes in the same wave run via
`asyncio.gather`.

**Rationale**: Waves make parallelism observable, easy to test, and safe to
resume. They also align with the Daily Intelligence Briefing scout fan-out.

**Alternatives considered**: Spawning one worker lease per node was rejected
for v1 because the existing worker only leases whole runs, and per-node leases
would require more reliability and queue work.

## Role Execution Boundary

**Decision**: Define a `RoleNodeExecutor` protocol and ship a
`DeterministicRoleNodeExecutor` for QA and tests. The executor receives safe
role context, upstream summaries, and pinned metadata, then returns a safe
structured output.

**Rationale**: It lets graph orchestration land now without pretending real
Calendar/Gmail/weather/tool connectors exist. Later specs can bind ModelGateway,
tool execution, and credential resolution behind the same boundary.

**Alternatives considered**: Calling ModelGateway directly from the graph
executor was rejected because live credential resolution and tool connectors are
explicitly deferred to Specs 021 and 025.

## Join Policy Semantics

**Decision**: Implement deterministic support for:

- `all_success`: all inbound branches must succeed.
- `quorum`: at least `quorum_count` inbound branches must succeed.
- `first_success`: the first successful inbound branch unlocks downstream.
- `manual_resolution`: when automatic success criteria are not met, pause the
  run and persist approval/timeline evidence.

**Rationale**: These policies match the feature prompt and can be tested with
branch summaries without external dependencies.

**Alternatives considered**: Treating all joins as all-success was rejected
because it would not support partial failure or first-success workflows.

## Checkpoint And Resume

**Decision**: Reconstruct completed node state from existing run-step records
and skip succeeded node keys on resume. Persist checkpoint/timeline events after
each node success and before lifecycle transitions.

**Rationale**: Idempotent resume is required by the constitution. Existing
unique constraints on `(workflow_run_id, step_key, attempt)` support bounded
deduplication for v1.

**Alternatives considered**: Keeping scheduler progress only in memory was
rejected because worker crash would lose authoritative state.

## Tenant Isolation

**Decision**: A tenant-scoped run can execute only a tenant-scoped bundle with
the same tenant id, or an explicitly platform-scoped bundle that is already
pinned into the run. Cross-tenant tenant bundle references fail closed before
node execution.

**Rationale**: Tenant isolation must be enforced in the runtime, not only at
workflow authoring time.

**Alternatives considered**: Trusting the channel/API caller was rejected
because worker execution may resume long after the initial request.

## Output Storage And Redaction

**Decision**: Persist safe summaries inline and apply denylist redaction for
secret-looking keys such as secret, credential, token, prompt, response,
payload, message, raw, authorization, password, and traceback. Store only digest
or artifact references for unsafe or oversized content.

**Rationale**: Operations, audit, and run inspection surfaces can safely display
inline metadata without exposing raw model/tool/channel payloads.

**Alternatives considered**: Storing full mock payloads inline was rejected
because tests should exercise production redaction posture.

## Worker Integration

**Decision**: Keep `OrchestrationWorker.poll_once` responsible for claiming a
run and delegating execution to the graph executor. The worker returns an
execution outcome summarizing claimed, completed, paused, or failed state.

**Rationale**: The worker remains small and existing lease behavior stays in
place. The graph executor can be unit-tested without a worker process.

**Alternatives considered**: Moving graph execution into the repository was
rejected because scheduling and policy decisions belong to the runtime domain.
