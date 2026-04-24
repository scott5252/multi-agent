# Worker Runtime Protocol

**Feature**: Durable Orchestration Runtime  
**Audience**: Runtime worker implementers and reviewers

## Purpose

The worker protocol describes how background workers claim durable workflow
work, execute LangGraph runs, preserve idempotency, and recover after process
or node failure. It is an internal service contract, not a public HTTP API.

## Worker Identity

- Each worker starts with a stable `worker_id` for the process lifetime.
- Every worker operation includes `tenant_id`, `workflow_run_id`, optional
  `run_step_id`, and `trace_id`.
- Workers never infer tenant context from payload contents; tenant context is
  loaded from the durable run record.

## Claim Flow

1. Select runnable work whose run is not terminal and whose tenant has
   available concurrency budget.
2. Acquire an exclusive lease using a database transaction and row-level lock
   or atomic compare-and-set.
3. Set `lease_status=active`, `worker_id`, `claimed_at`, `expires_at`, and
   `claim_attempt`.
4. Emit a `worker_claimed` timeline and audit event.
5. Execute only while the lease remains active and owned by the worker.

Default lease expiry is 2 minutes unless workflow or tenant policy overrides
it.

## Lease Renewal

- Workers renew active leases before half of the lease window has elapsed.
- Renewal preserves the same `worker_id`, run id, step id, tenant id, and claim
  attempt.
- Renewal failure stops execution before another mutation.
- Expired leases are eligible for another worker to claim.

## LangGraph Execution

- Root run config uses `{"configurable": {"thread_id": workflow_run_id}}`.
- Child run config uses `{"configurable": {"thread_id": child_run_id}}`.
- Graphs are compiled with `AsyncPostgresSaver`.
- Worker loads the pinned runtime execution bundle before graph invocation.
- Resume uses the same bundle digest and thread id as the original run.

## Checkpoint Frequency Rules

LangGraph checkpointer persists graph state at super-step boundaries. The
runtime also records semantic checkpoint references at:

- run initialization
- worker claim and lease renewal
- handoff envelope creation and validation
- side-effect intent creation and result capture
- approval wait state and approval resume
- child-run creation and child-run completion
- retry scheduling
- terminal state

Streaming chunks and token events are not checkpoint boundaries unless they
change durable run state.

## Handoff Envelope Rules

- Sender writes an envelope with sender step, receiver key, contract digest,
  payload hash, payload ref, and trace context.
- Runtime validates against the pinned contract before receiver consumption.
- Receiver may consume only `valid` envelopes.
- Invalid envelopes follow the workflow's declared failure route, defaulting to
  failure of the affected run path.

## Side-Effect Intent Rules

- A worker must create a `planned` side-effect intent before any external tool,
  API, filesystem, email, delegated action, or object-storage mutation.
- Intent idempotency key is deterministic for tenant, run, step, bundle digest,
  operation kind, and attempt.
- Before executing, worker checks for an existing `applied` intent with the
  same key and returns the recorded result if present.
- If execution succeeds but the worker crashes before completion ack, resume
  must observe the `applied` intent and avoid repeating the external action.
- Compensation hooks execute only when declared by the pinned workflow bundle.

## Approval Wait Rules

- Approval nodes call LangGraph `interrupt()` with a JSON-serializable payload.
- Runtime persists an `ApprovalGate` record with approver policy and timeout
  behavior.
- Default timeout behavior is no automatic timeout.
- Resume uses `Command(resume=decision_payload)` with the same thread id after
  an authorized accepted decision.

## Child Run Rules

- Published subworkflows execute as child workflow runs with separate thread ids.
- Parent step records lineage before child execution begins.
- Parent waits for child result envelope according to join policy.
- Parent cancellation applies the declared child cancellation policy, defaulting
  to cascade-cancel.

## Failure Categories

- **Transient**: model timeout, network timeout, temporary storage error.
  Eligible for retry.
- **Policy**: authorization denial, quota denial, egress denial, missing
  delegated credential. Not automatically retried.
- **Contract**: invalid handoff payload or unavailable contract digest. Follow
  failure route.
- **Durability**: incompatible checkpoint or missing bundle. Mark
  recoverable_failed and require operator attention.
- **Terminal**: explicit failure, rejection route, cancellation, or exhausted
  retry budget.

## Crash Recovery Tests

Required crash injection points:

- after lease claim
- after LangGraph checkpoint write
- after side-effect intent creation
- after side-effect success before worker ack
- after approval wait state
- after child-run lineage creation
- after terminal state while stale work remains queued

Each recovery test must prove that the resumed worker uses the same bundle
digest, same thread id, same tenant id, and does not duplicate completed side
effects.
