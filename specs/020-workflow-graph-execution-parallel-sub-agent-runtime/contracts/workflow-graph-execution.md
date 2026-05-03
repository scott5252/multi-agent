# Contract: Workflow Graph Execution

## Executor Input

```json
{
  "workflow_run_id": "uuid",
  "tenant_id": "uuid-or-null",
  "run_bundle_id": "uuid",
  "published_workflow_version_id": "uuid",
  "trace_id": "string",
  "worker_id": "string"
}
```

Rules:

- The executor MUST load the run by `workflow_run_id`.
- The executor MUST load the pinned run bundle by `run_bundle_id`.
- The executor MUST load the published workflow version referenced by the run
  bundle.
- Tenant mismatch MUST fail closed before node execution.

## Role Node Executor Boundary

```json
{
  "node_key": "calendar-scout-node",
  "role_key": "calendar-scout",
  "role_kind": "subagent",
  "workflow_run_id": "uuid",
  "tenant_id": "uuid",
  "trace_id": "trace-id",
  "attempt": 1,
  "input_summary": {
    "upstream_node_keys": ["orchestrator-intake"],
    "contract_keys": ["briefing-request"]
  },
  "pinned_context": {
    "profile_reference_key": "profile-calendar-scout",
    "skill_installation_keys": ["calendar-reader-install"]
  }
}
```

Output:

```json
{
  "status": "succeeded",
  "safe_summary": "Calendar Scout completed with deterministic QA output.",
  "structured_output": {
    "node_key": "calendar-scout-node",
    "role_key": "calendar-scout",
    "result": "safe mock output"
  },
  "payload_digest": "sha256"
}
```

Rules:

- The deterministic QA executor MUST NOT call external providers or tools.
- Future live executors MUST use the same boundary and pass ModelGateway,
  prompt/profile, memory, skill, tool-policy, and credential provenance through
  pinned context.
- Raw prompt bodies, model responses, tool payloads, credentials, and channel
  messages MUST NOT be returned inline.

## Scheduler Contract

The scheduler evaluates node readiness using:

- Entry node starts first.
- A role, approval, subworkflow, or terminal node is ready when all inbound
  source nodes have succeeded.
- A join node is ready when at least one inbound branch has reached a terminal
  branch status and the join policy can make a deterministic decision.
- Nodes already marked `succeeded` for the workflow run are skipped on resume.

The scheduler records a timeline event for each wave:

```json
{
  "event_type": "graph_wave_scheduled",
  "payload": {
    "wave_number": 2,
    "ready_node_keys": ["calendar-scout-node", "email-triage-node"],
    "parallel_role_node_count": 2
  }
}
```

## Join Policy Contract

Inputs:

```json
{
  "join_policy_key": "all-scouts-return",
  "strategy": "all_success",
  "inbound_edge_keys": ["calendar-to-join", "email-to-join"],
  "quorum_count": null,
  "failure_behavior": "manual_resolution",
  "branch_results": [
    {"node_key": "calendar-scout-node", "status": "succeeded"},
    {"node_key": "email-triage-node", "status": "failed"}
  ]
}
```

Outputs:

```json
{
  "decision": "pause_manual_resolution",
  "successful_branch_count": 1,
  "failed_branch_count": 1,
  "winning_branch_key": null,
  "safe_summary": "Join requires manual resolution because not all branches succeeded."
}
```

Rules:

- `all_success` proceeds only when all inbound branches succeeded.
- `quorum` proceeds when successful branch count is at least `quorum_count`.
- `first_success` proceeds when any inbound branch succeeded.
- `manual_resolution` pauses the run when automatic success criteria fail and
  the policy requests manual handling.

## Timeline Evidence Contract

Graph execution MUST emit safe timeline events for:

- `graph_loaded`
- `graph_wave_scheduled`
- `graph_node_started`
- `graph_node_succeeded`
- `graph_node_failed`
- `graph_join_evaluated`
- `graph_manual_resolution_required`
- `graph_checkpoint_recorded`
- `graph_final_output_persisted`
- `graph_run_succeeded`
- `graph_run_failed`

Timeline payloads MUST include safe identifiers and counts only. They MUST NOT
include raw secret values, prompts, model responses, tool payloads, channel
messages, authorization headers, or stack traces.
