# Immutable Versioned Memory

Spec `005` adds an append-only memory subsystem for agent and workflow memory.
Each accepted write creates a new canonical JSON snapshot, links it to the
previous current head, advances a separate head projection, and records
content-free audit evidence.

## Concepts

- Memory scope: `tenant_id`, `workflow_lineage_id`, `agent_key`, and
  `memory_key`.
- Memory version: immutable JSON content plus hash, sequence, lineage, actor,
  source, and optional runtime bundle/run metadata.
- Current head: the latest version for a scope, optimized for execution reads.
- Replay: returns the exact snapshot and ordered lineage up to a target version.
- Diff: compares two authorized versions from the same scope using JSON Pointer
  paths.
- Audit: stores ids, hashes, action, outcome, runtime source links, and
  redacted summaries only.

## API Flow

Create an initial version:

```bash
curl -sS -X POST http://127.0.0.1:8000/memory/versions \
  -H "X-Local-Principal: tenant-admin-acme" \
  -H "Content-Type: application/json" \
  -d '{
    "scope": {
      "workflow_lineage_id": "workflow.qa005-memory",
      "agent_key": "triage-agent",
      "memory_key": "patient-preferences"
    },
    "assert_no_current_head": true,
    "content": {"preferred_contact": "sms"},
    "change_summary_redacted": "Captured preferred contact channel"
  }'
```

Create a successor by passing the observed `memory_version_id` as
`expected_current_version_id`. If the head changed first, the API returns
`409 stale_expected_head` and leaves every prior version unchanged.

## Runtime Integration

Runtime code calls `MemoryService.get_current_head_for_runtime` and
`MemoryService.write_version_for_runtime` with `runtime-memory.v1`, tenant id,
workflow lineage id, run id, step id, pinned bundle id, bundle digest, and
optional parent-child `run_lineage_id`. The service records those links on the
created version and audit event so operators can trace a memory state back to
the pinned execution bundle that produced it.

## Debugging Paths

- API: `GET /memory/head`, `GET /memory/versions/{id}`,
  `GET /memory/scopes/{scope_id}/versions`, `GET /memory/versions/{id}/replay`,
  `POST /memory/diffs`, and `GET /memory/audit`.
- Logs: use `memory_log_context`; include ids and hashes, never raw content.
- Metrics: `multi_agent_platform_memory_actions_total`,
  `multi_agent_platform_memory_conflicts_total`, and
  `multi_agent_platform_memory_budget_denials_total`.
- Traces: use `memory_trace_attributes`; include action, outcome, ids, and
  bundle metadata only.
- Workflow timeline: runtime memory writes emit content-free timeline payloads
  with scope id, version id, and hash.

## Validation

Run:

```bash
uv run pytest --no-cov tests/unit/memory tests/unit/db/test_memory_models.py \
  tests/contract/test_memory_contract.py tests/integration/db/test_memory_migration.py \
  tests/integration/runtime/test_runtime_memory_flows.py \
  tests/integration/api/test_memory_api.py tests/performance/memory/test_memory_latency.py -q
```

For manual QA, use
[Spec 005 QA Guide](/Users/scottcornell/src/my-projects/multi-agent/specs/005-immutable-memory/qa005.md)
and
[Spec 005 Postman Collection](/Users/scottcornell/src/my-projects/multi-agent/specs/005-immutable-memory/qa005_collection.json).
