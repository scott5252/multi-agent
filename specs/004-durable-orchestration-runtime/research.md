# Research: Durable Orchestration Runtime

**Feature**: Durable Orchestration Runtime  
**Date**: 2026-04-24  
**Status**: Complete

## Sources Checked

- PyPI package page for `langchain` 1.2.15: https://pypi.org/project/langchain/1.2.15/
- PyPI package page for `langgraph` 1.1.9: https://pypi.org/project/langgraph/1.1.9/
- PyPI package page for `langgraph-checkpoint-postgres` 3.0.5: https://pypi.org/project/langgraph-checkpoint-postgres/3.0.5/
- LangGraph durable execution docs: https://docs.langchain.com/oss/python/langgraph/durable-execution
- LangGraph persistence docs: https://docs.langchain.com/oss/python/langgraph/persistence
- LangGraph interrupts docs: https://docs.langchain.com/oss/python/langgraph/interrupts
- LangGraph subgraphs docs: https://docs.langchain.com/oss/python/langgraph/use-subgraphs
- LangGraph checkpointer integrations docs: https://docs.langchain.com/oss/python/integrations/checkpointers
- LangGraph memory/checkpointer setup docs: https://docs.langchain.com/oss/python/langgraph/add-memory

## Latest Dependency Baseline

**Decision**: Plan implementation against `langchain==1.2.15`,
`langgraph==1.1.9`, and `langgraph-checkpoint-postgres==3.0.5` as the latest
verified PyPI versions on 2026-04-24. Update `pyproject.toml` during
implementation from the current broad `>=0.3.0` constraints to at least these
versions, and add the Postgres checkpointer package.

**Rationale**: The user explicitly requested the latest LangChain and
LangGraph. The current repository dependency lower bounds allow older 0.x
packages that predate the v1 durable execution APIs and documentation.

**Alternatives considered**: Keep broad `>=0.3.0` ranges, but that risks
installing incompatible old APIs. Pin exact versions forever, but a lower-bound
update keeps `uv` able to take compatible patches while documenting the tested
baseline.

## LangGraph Durable Execution Pattern

**Decision**: Use LangGraph graphs compiled with a durable PostgreSQL
checkpointer. Use one stable `thread_id` per workflow run and per child run.
Treat LangGraph checkpoints as graph execution state and platform runtime
tables as the authoritative business state, lease state, audit surface, and
query model.

**Rationale**: LangGraph durable execution requires persistence plus a thread
identifier, and its docs recommend deterministic and idempotent workflows with
side effects wrapped in tasks. The platform also needs tenant isolation,
leases, retention, side-effect intents, lineage, and audit records that are
outside the generic graph checkpoint shape.

**Alternatives considered**: Store all runtime state only in LangGraph
checkpoints, rejected because it weakens queryability, audit, retention, and
tenant isolation. Store only platform state without LangGraph persistence,
rejected because pause/resume, interrupts, and fault recovery would need a
custom graph replay engine.

## PostgreSQL Checkpointer

**Decision**: Use `langgraph-checkpoint-postgres` with `AsyncPostgresSaver` for
production and integration tests. Initialize checkpointer tables through an
idempotent setup path and verify schema creation through Alembic or startup
health checks.

**Rationale**: LangGraph documents Postgres as the production checkpointer
backend and exposes async checkpointer methods for async graph execution.
PostgreSQL is already the platform's transactional source of truth.

**Alternatives considered**: In-memory checkpointer, rejected for production
durability. SQLite checkpointer, rejected because the platform target is
PostgreSQL and worker leasing requires database concurrency semantics. Custom
checkpointer, rejected until an unmet requirement appears.

## Checkpoint Frequency Rules

**Decision**: Rely on LangGraph super-step checkpointing for graph state and
add platform checkpoint references at semantic runtime boundaries: run start,
worker claim, before/after handoff, before/after side-effect intent, approval
wait, approval resume, child-run start, child-run completion, retry transition,
and terminal state. Do not checkpoint every token or streaming chunk.

**Rationale**: LangGraph persists checkpoints at graph step boundaries, which
is the correct resume granularity. Platform semantic checkpoints make audit and
crash tests deterministic without overloading PostgreSQL with low-value stream
fragments.

**Alternatives considered**: Checkpoint after every emitted event, rejected due
to write amplification. Checkpoint only at run start and finish, rejected
because it cannot safely resume long-running multi-agent work.

## Worker Leasing And Recovery

**Decision**: Use PostgreSQL worker leases with exclusive active ownership per
runnable unit. Workers claim with row-level locking or atomic compare-and-set,
renew claims while executing, and release or complete claims after graph
progress. Abandoned leases become resumable after workflow or tenant claim
expiry with a 2-minute default.

**Rationale**: Worker leases must survive process failure and prevent
conflicting mutation by multiple workers. PostgreSQL gives the runtime a
durable arbitration point shared by all workers.

**Alternatives considered**: In-process locks, rejected because they do not
survive worker or node failure. External queue-only visibility timeouts,
rejected because runtime state and checkpoint state already require
PostgreSQL-coordinated transitions.

## Failure Recovery Behavior

**Decision**: On worker crash, a later worker claims expired work, loads the
same run bundle and LangGraph `thread_id`, resumes from the latest valid
checkpoint, and checks side-effect intents before any externally visible action
is repeated. Terminal runs reject stale queued work.

**Rationale**: The spec requires resuming from durable checkpoints without
duplicating completed side effects. LangGraph pending writes and checkpoints
cover graph state, while side-effect intent records cover external reality.

**Alternatives considered**: Restart failed runs from the beginning, rejected
because long-running workflows and external actions would duplicate work.
Manual operator recovery only, rejected because the runtime must recover
automatically from normal worker failure.

## Retry Policy

**Decision**: Default transient retry budget is 3 attempts with exponential
backoff and jitter. Retry budgets are configurable by workflow or tenant.
Contract violations, authorization denials, quota denials, missing bundles,
invalid checkpoints, and non-idempotent side effects without a captured intent
are not retried automatically.

**Rationale**: Retrying transient model/tool/storage failures improves
availability, but retrying deterministic policy failures or unsafe side
effects hides errors and risks duplicate external actions.

**Alternatives considered**: Unlimited retry, rejected because it can starve
tenants and mask stuck work. No retry, rejected because model and tool calls
commonly fail transiently.

## Side-Effect Intent Capture And Compensation Hooks

**Decision**: Require a side-effect intent record before executing any external
tool, API, filesystem, email, or object-storage mutation. Intent records store
idempotency key, status, payload reference, result reference, error, and
optional compensation hook reference. Compensation runs only through declared
workflow hooks and is audited as normal runtime work.

**Rationale**: LangGraph durable execution docs call out wrapping
non-determinism and side effects so they are not repeated on resume. Intent
records let the platform reconcile effects that complete before a worker crash
acknowledges them.

**Alternatives considered**: Trust tool idempotency alone, rejected because not
all tools provide it. Automatically infer compensation, rejected because only
the workflow author knows business-safe reversal semantics.

## Handoff Envelope Storage And Contract Validation

**Decision**: Store every agent-to-agent handoff as a versioned envelope with
sender, receiver, contract digest, validation status, payload hash, payload
reference, and trace context. Validate against the pinned contract before the
receiver consumes the envelope. Invalid envelopes follow the workflow failure
route, defaulting to failure of the affected run path.

**Rationale**: Contract-first coordination is a constitution principle and the
spec requires explicit handoff contracts. Persisted envelopes are also the
debugging and replay surface for multi-agent boundaries.

**Alternatives considered**: Pass payloads directly in graph state, rejected
because it hides contract failures and makes handoff audit weak. Validate only
at publish time, rejected because runtime outputs must still satisfy contracts.

## Subworkflow Execution Semantics

**Decision**: Execute published subworkflows as separate child workflow runs,
each with its own LangGraph thread and pinned child execution bundle. The
parent step waits for the child result envelope and records lineage. Internal
agent helper subgraphs may use LangGraph per-invocation subgraph persistence,
but published subworkflows use platform child runs.

**Rationale**: LangGraph recommends per-invocation subgraph persistence for
many multi-agent cases, but this platform requires parent-child run lineage,
approval gates, cancellation policy, and independent crash recovery for
published subworkflows.

**Alternatives considered**: Inline every subworkflow into the parent graph,
rejected because lineage, cancellation, and child status become hard to audit.
Use long-lived per-thread subgraph memory by default, rejected because most
subworkflow calls should be isolated unless workflow authors opt in.

## Version Bundle Pinning

**Decision**: Clone the published workflow bundle into a per-run execution
bundle record before graph execution starts. The run bundle includes workflow,
subworkflow, contract, prompt, model configuration, tool-policy, retry,
checkpoint, approval, cancellation, and runtime compiler version metadata.

**Rationale**: The constitution requires version-pinned execution and
bundle-stable resume. A per-run bundle prevents later registry changes from
altering in-flight runs.

**Alternatives considered**: Read latest published bundle on resume, rejected
because it breaks reproducibility. Store only a pointer to the published
bundle, rejected because future migration or retirement could obscure what ran.

## Approval Wait States

**Decision**: Implement approval gates using LangGraph `interrupt()` plus a
platform `ApprovalGate` record. Resume with `Command(resume=...)` and the same
thread id after an authorized decision. Workflow-declared timeout behavior is
supported, defaulting to no automatic timeout.

**Rationale**: LangGraph interrupts are built for durable human-in-the-loop
pause/resume and save state through the checkpointer. The platform record adds
authorization, audit, timeout, and operator queryability.

**Alternatives considered**: Poll an approval table inside an active node,
rejected because it ties up workers and weakens crash behavior. Store approval
only in chat/UI state, rejected by the constitution.

## Test Strategy For Crash And Resume

**Decision**: Add deterministic crash fixtures that stop a worker after named
runtime boundaries: after claim, after checkpoint, after side-effect intent,
after side-effect completion before ack, after approval wait, and after child
run creation. Verify resumed workers reuse the same bundle, thread id, and
side-effect result.

**Rationale**: Crash recovery must be tested at the exact boundaries where
duplicate work or lost state is most likely. Unit tests cover state machines;
PostgreSQL integration tests prove the checkpointer and lease behavior.

**Alternatives considered**: Manual crash testing only, rejected because
regressions would be hard to catch. Mock-only checkpointer tests, rejected
because the feature depends on Postgres persistence and concurrency behavior.
