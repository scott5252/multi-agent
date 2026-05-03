# Data Model: Workflow Graph Execution And Parallel Sub-Agent Runtime

## Graph Execution Plan

Represents the normalized, executable view of a published workflow bundle.

Fields:

- `workflow_version_bundle_id`: pinned published bundle id.
- `workflow_key`: safe workflow key.
- `entry_node_key`: node where execution starts.
- `nodes_by_key`: active graph nodes keyed by node key.
- `outbound_edges_by_source`: directed edges grouped by source node.
- `inbound_edges_by_target`: directed edges grouped by target node.
- `roles_by_key`: role definitions keyed by role key.
- `contracts_by_key`: JSON schema contracts keyed by contract key.
- `join_policies_by_key`: join policy definitions keyed by policy key.
- `terminal_node_keys`: terminal nodes that complete the run.

Validation rules:

- Entry node must exist and be active.
- Every edge must reference existing active nodes.
- Role nodes must reference an existing role.
- Join nodes must reference an existing join policy.
- Graph must be acyclic for v1.
- At least one terminal node must exist.

## Graph Node State

Durable runtime state for one node in one workflow run. Stored using existing
`runtime_run_steps` rows.

Fields:

- `workflow_run_id`
- `tenant_id`
- `node_key`
- `node_type`
- `role_key`
- `role_kind`
- `status`
- `attempt`
- `upstream_node_keys`
- `input_ref`
- `output_ref`
- `error_ref`
- `checkpoint_before_id`
- `checkpoint_after_id`
- `finished_at`

State transitions:

```text
pending -> running -> succeeded
pending -> running -> failed
pending -> paused
failed -> retry_scheduled -> running
running -> cancelled
```

Resume rules:

- `succeeded` node keys are reused and are not executed again.
- `failed` node keys may be retried only within the node retry budget.
- Paused manual-resolution joins resume only after durable approval state.

## Execution Wave

Transient scheduler grouping that is recorded through timeline payloads.

Fields:

- `wave_number`
- `ready_node_keys`
- `parallel_role_node_keys`
- `decision_node_keys`
- `dependency_snapshot`

Validation rules:

- A node appears in at most one wave unless it is retried after failure.
- Nodes in the same wave must not depend on each other.

## Branch Result

Safe summary of one inbound branch consumed by join policies.

Fields:

- `node_key`
- `status`
- `output_ref`
- `safe_summary`
- `error_code`
- `payload_digest`
- `completed_at`

Validation rules:

- Raw payload text is not allowed.
- Failed branches include a safe reason code and no raw exception text.

## Join Decision

Deterministic result of evaluating a join node.

Fields:

- `join_node_key`
- `join_policy_key`
- `strategy`
- `decision`: `proceed`, `wait`, `pause_manual_resolution`, or `fail`.
- `successful_branch_count`
- `failed_branch_count`
- `winning_branch_key`
- `quorum_count`
- `safe_summary`

State transitions:

```text
wait -> proceed
wait -> pause_manual_resolution
wait -> fail
pause_manual_resolution -> proceed
pause_manual_resolution -> fail
```

## Partial Failure Summary

Safe record used when graph execution cannot continue automatically.

Fields:

- `workflow_run_id`
- `join_node_key`
- `failed_node_keys`
- `successful_node_keys`
- `failure_reason_codes`
- `manual_resolution_required`
- `trace_id`

Validation rules:

- Does not include raw branch outputs, prompt text, provider payloads, or tool
  payloads.
- May be persisted in `runtime_run_steps.error_ref` and timeline payloads.

## Final Output Reference

Safe final output exposed through existing run inspection and channel result
surfaces.

Fields:

- `workflow_run_id`
- `terminal_node_key`
- `producer_node_key`
- `output_contract_key`
- `safe_summary`
- `structured_output`
- `artifact_ref`
- `payload_digest`

Validation rules:

- Inline `structured_output` is allowed only for safe fields.
- Oversized or sensitive payloads use `artifact_ref`.
