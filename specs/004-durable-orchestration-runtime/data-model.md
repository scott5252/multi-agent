# Data Model: Durable Orchestration Runtime

**Feature**: Durable Orchestration Runtime  
**Date**: 2026-04-24

## Overview

The runtime stores business state in platform tables and graph execution state
in LangGraph checkpoint tables. Platform tables are the query, lease, audit,
retention, and authorization surface. LangGraph checkpoints are the durable
graph state used to resume execution.

## Entities

### Runtime Execution Bundle

Represents the immutable per-run copy of the published workflow bundle.

- `run_bundle_id`: UUID primary key
- `tenant_id`: tenant owner
- `workflow_run_id`: owning run
- `published_workflow_version_id`: source version
- `bundle_digest`: SHA-256 digest of canonical bundle JSON
- `workflow_version`, `subworkflow_versions`, `contract_versions`,
  `prompt_versions`, `model_config_versions`, `tool_policy_versions`: pinned
  version maps
- `retry_policy`: default and step override retry rules
- `checkpoint_policy`: semantic checkpoint rules
- `approval_timeout_policy`: workflow-declared timeout behavior
- `child_cancellation_policy`: workflow-declared child cancellation behavior
- `compiled_graph_ref`: object or metadata reference for graph assembly
- `created_at`: timestamp

Validation rules:

- Created before any worker can claim run work.
- Immutable after creation.
- `bundle_digest` must match the canonical JSON payload.

### Workflow Run

Represents one execution of a published workflow.

- `workflow_run_id`: UUID primary key and LangGraph root `thread_id`
- `tenant_id`: tenant owner
- `scope_type`: tenant or platform scope inherited from bundle access
- `initiating_principal_id`: user or service principal that started the run
- `run_bundle_id`: pinned bundle
- `status`: `pending`, `runnable`, `running`, `paused`, `waiting_child`,
  `recoverable_failed`, `cancelling`, `cancelled`, `succeeded`, `failed`
- `current_step_id`: nullable active step pointer
- `current_checkpoint_id`: latest LangGraph checkpoint id known to platform
- `pause_reason`: nullable reason
- `terminal_reason`: nullable terminal reason
- `idempotency_key`: caller or platform-generated start key
- `trace_id`: root trace id
- `created_at`, `started_at`, `updated_at`, `finished_at`: timestamps

Validation rules:

- A run may start only from a published workflow visible to the tenant.
- A run must have exactly one runtime execution bundle.
- Terminal runs cannot be mutated by worker resume or stale queued work.

### Run Step

Represents a semantic unit of runtime progress.

- `run_step_id`: UUID primary key
- `workflow_run_id`: parent run
- `tenant_id`: tenant owner
- `step_key`: stable key from pinned bundle
- `step_type`: `agent`, `handoff`, `subworkflow`, `approval`, `tool`,
  `compensation`, `system`
- `status`: `pending`, `runnable`, `leased`, `running`, `paused`,
  `waiting_child`, `retry_scheduled`, `succeeded`, `failed`,
  `cancelled`, `compensated`
- `attempt`: current attempt number
- `max_attempts`: resolved retry budget
- `next_retry_at`: nullable timestamp
- `input_ref`, `output_ref`, `error_ref`: payload references or small JSON
- `checkpoint_before_id`, `checkpoint_after_id`: checkpoint references
- `created_at`, `updated_at`, `finished_at`: timestamps

Validation rules:

- `step_key` must exist in the pinned bundle.
- Attempts cannot exceed resolved retry budget.
- Externally visible side effects require a side-effect intent before
  execution.

### Worker Lease

Represents time-bounded worker ownership of runnable work.

- `worker_lease_id`: UUID primary key
- `tenant_id`: tenant owner
- `workflow_run_id`: associated run
- `run_step_id`: nullable specific step
- `worker_id`: claiming worker instance
- `lease_status`: `active`, `released`, `expired`, `completed`, `lost`
- `claimed_at`, `expires_at`, `last_renewed_at`, `released_at`: timestamps
- `claim_attempt`: monotonically increasing integer

Validation rules:

- Only one active lease may exist for the same runnable run or step.
- Expiry comes from workflow or tenant policy, defaulting to 2 minutes.
- Lease renewal must preserve the same worker id and tenant id.

### Runtime Checkpoint Reference

Represents a platform reference to a LangGraph checkpoint.

- `runtime_checkpoint_ref_id`: UUID primary key
- `tenant_id`: tenant owner
- `workflow_run_id`: run thread id
- `run_step_id`: nullable semantic step
- `langgraph_thread_id`: root or child run id
- `langgraph_checkpoint_id`: checkpoint id
- `checkpoint_kind`: `run_start`, `superstep`, `handoff`, `side_effect`,
  `approval_wait`, `approval_resume`, `child_start`, `child_complete`,
  `terminal`
- `bundle_digest`: pinned bundle digest used for compatibility
- `created_at`: timestamp
- `retention_expires_at`: nullable timestamp for checkpoint retention

Validation rules:

- Checkpoint references must use the same bundle digest as the run.
- Checkpoint refs for checkpoints and run payload references default to 90-day
  retention unless tenant policy overrides.

### Handoff Envelope

Represents a validated or rejected transfer between agents.

- `handoff_envelope_id`: UUID primary key
- `tenant_id`: tenant owner
- `workflow_run_id`: owning run
- `sender_step_id`: producing step
- `receiver_step_key`: target step key
- `contract_id`, `contract_version`, `contract_digest`: pinned contract data
- `status`: `created`, `validating`, `valid`, `invalid`, `consumed`,
  `failed_route_applied`
- `payload_hash`: SHA-256 of canonical payload
- `payload_ref`: object-storage ref or inline JSON summary
- `validation_errors`: structured validation failure list
- `created_at`, `validated_at`, `consumed_at`: timestamps

Validation rules:

- Receiver cannot consume an envelope until status is `valid`.
- Invalid envelopes follow the workflow failure route, defaulting to affected
  run-path failure.
- Payload bodies too large for metadata must use object storage refs.

### Side-Effect Intent

Represents a planned or completed externally visible action.

- `side_effect_intent_id`: UUID primary key
- `tenant_id`: tenant owner
- `workflow_run_id`: owning run
- `run_step_id`: owning step
- `intent_kind`: `tool_call`, `http_request`, `file_write`, `email`,
  `object_storage_write`, `delegated_action`, `compensation`
- `idempotency_key`: deterministic key
- `status`: `planned`, `executing`, `applied`, `failed`, `compensating`,
  `compensated`, `cancelled`
- `tool_policy_ref`: pinned tool-policy reference
- `delegated_credential_ref`: nullable delegated credential reference
- `request_ref`, `result_ref`, `error_ref`: payload references or small JSON
- `compensation_hook_ref`: nullable workflow hook reference
- `created_at`, `executed_at`, `updated_at`: timestamps

Validation rules:

- Unique `(tenant_id, workflow_run_id, run_step_id, idempotency_key)`.
- External action cannot execute before intent status is `planned`.
- Resume must return recorded result for an `applied` intent.

### Approval Gate

Represents a durable human wait state.

- `approval_gate_id`: UUID primary key
- `tenant_id`: tenant owner
- `workflow_run_id`: owning run
- `run_step_id`: approval step
- `status`: `pending`, `approved`, `rejected`, `cancelled`, `timed_out`
- `approval_key`: stable key from pinned bundle
- `requested_action`: JSON-serializable prompt/context
- `approver_policy`: roles, users, or service principals allowed to decide
- `timeout_behavior`: workflow-declared behavior, default no automatic timeout
- `decision_id`: nullable accepted decision
- `created_at`, `decided_at`, `expires_at`: timestamps

Validation rules:

- Only one valid decision may be accepted.
- Duplicate, late, unauthorized, or conflicting decisions are rejected and
  audited.
- Resume uses the same LangGraph `thread_id` and the accepted decision payload.

### Approval Decision

Represents an approval, rejection, or cancellation attempt.

- `approval_decision_id`: UUID primary key
- `approval_gate_id`: gate
- `tenant_id`: tenant owner
- `principal_id`: deciding principal
- `decision`: `approve`, `reject`, `cancel`
- `decision_payload_hash`: canonical payload hash
- `decision_payload_ref`: nullable payload reference
- `accepted`: boolean
- `rejection_reason`: reason if not accepted
- `created_at`: timestamp

Validation rules:

- Accepted decision must satisfy approver policy.
- Rejected attempts remain auditable.

### Run Lineage

Represents a parent-child run relationship.

- `run_lineage_id`: UUID primary key
- `tenant_id`: tenant owner
- `parent_run_id`: parent workflow run
- `parent_step_id`: step that created child
- `child_run_id`: child workflow run
- `relationship_reason`: `subworkflow`, `compensation`, `manual_resume`,
  `replay`
- `join_policy`: parent wait and aggregation policy
- `child_cancellation_policy`: resolved policy, default cascade-cancel
- `created_at`, `resolved_at`: timestamps

Validation rules:

- Parent and child must share tenant id unless a future spec adds explicit
  cross-tenant delegation.
- Lineage is retained indefinitely by default.

### Runtime Timeline Event

Represents an append-only operator and audit timeline entry.

- `runtime_timeline_event_id`: UUID primary key
- `tenant_id`: tenant owner
- `workflow_run_id`: owning run
- `run_step_id`: nullable step
- `event_type`: start, bundle_pin, claim, renew, checkpoint, handoff,
  side_effect, approval, child_run, retry, compensation, cancel, terminal,
  retention
- `severity`: `debug`, `info`, `warning`, `error`
- `payload`: redacted structured JSON
- `trace_id`: trace id
- `created_at`: timestamp

Validation rules:

- Timeline events are append-only.
- Secret values and raw delegated credentials are never stored.

### Runtime Retention Policy

Represents tenant-specific retention rules.

- `runtime_retention_policy_id`: UUID primary key
- `tenant_id`: tenant owner
- `checkpoint_retention_days`: default 90
- `run_payload_ref_retention_days`: default 90
- `audit_retention`: default `indefinite`
- `lineage_retention`: default `indefinite`
- `created_at`, `updated_at`: timestamps

Validation rules:

- Audit and lineage retention cannot be shortened without a future explicit
  governance decision.
- Cleanup must leave audit and lineage records queryable after checkpoint and
  payload-reference expiry.

## State Transitions

### Workflow Run

```text
pending -> runnable -> running -> succeeded
pending -> runnable -> running -> failed
running -> paused -> running
running -> waiting_child -> running
running -> recoverable_failed -> runnable
running -> cancelling -> cancelled
paused -> cancelling -> cancelled
waiting_child -> cancelling -> cancelled
```

Terminal states: `succeeded`, `failed`, `cancelled`.

### Run Step

```text
pending -> runnable -> leased -> running -> succeeded
running -> retry_scheduled -> runnable
running -> paused -> running
running -> waiting_child -> running
running -> failed
running -> cancelled
failed -> compensated
```

### Worker Lease

```text
active -> completed
active -> released
active -> expired
active -> lost
expired -> active
```

### Handoff Envelope

```text
created -> validating -> valid -> consumed
created -> validating -> invalid -> failed_route_applied
```

### Side-Effect Intent

```text
planned -> executing -> applied
planned -> executing -> failed
applied -> compensating -> compensated
planned -> cancelled
```

### Approval Gate

```text
pending -> approved
pending -> rejected
pending -> cancelled
pending -> timed_out
```

## Retention

- Checkpoints and run payload references use tenant policy, defaulting to 90
  days.
- Audit events and lineage are retained indefinitely by default.
- Object-storage payload cleanup must not remove metadata needed to understand
  run history, validation status, or audit decisions.
