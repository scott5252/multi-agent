# Data Model: Durable Agent Interaction Evidence And Replay Graph

## Runtime Interaction Evidence

Stores one safe-summary interaction event for runtime replay.

| Field | Type | Notes |
| --- | --- | --- |
| `interaction_evidence_id` | UUID | Primary key |
| `tenant_id` | UUID nullable | Tenant scope; nullable only for platform-scope runtime records |
| `workflow_run_id` | UUID | Runtime workflow run |
| `source_node_key` | string | Source workflow graph node key |
| `target_node_key` | string nullable | Target workflow graph node key when known |
| `source_run_step_id` | UUID nullable | Source run step |
| `target_run_step_id` | UUID nullable | Target run step when already created |
| `timeline_event_id` | UUID nullable | Related runtime timeline event when available |
| `interaction_kind` | string enum | `delegation`, `context_transfer`, `result_return`, `join_contribution`, `approval_pause`, `approval_resume`, `handoff`, `tool_call`, `checkpoint`, `manual_resolution`, `run_completion` |
| `status` | string enum | `recorded`, `sent`, `received`, `completed`, `paused`, `failed`, `skipped` |
| `sequence` | integer | Per-run replay ordering |
| `safe_summary` | text | Human-readable safe summary, truncated for graph display |
| `classification` | string | Safe content class such as `safe-summary` or `redacted-summary` |
| `payload_digest` | string | SHA-256 digest of original metadata/payload summary |
| `artifact_refs` | JSON array | Safe artifact IDs/references only |
| `provenance` | JSON object | Redacted structured metadata, bundle/run/worker/instrumentation hints |
| `idempotency_key` | string | Stable per interaction |
| `occurred_at` | timestamp | When interaction occurred |
| `created_at` | timestamp | Persistence timestamp |

## Constraints And Indexes

- Primary key: `interaction_evidence_id`
- Unique: `(tenant_id, workflow_run_id, idempotency_key)`
- Index: `(tenant_id, workflow_run_id, sequence)`
- Index: `(tenant_id, workflow_run_id, source_node_key, target_node_key)`
- Foreign keys: `tenant_id -> tenants`, `workflow_run_id -> runtime_workflow_runs`

## State Transitions

Interaction evidence is append-oriented. An idempotent replay returns the existing row. Existing rows are not updated during normal graph execution except by future migration-safe repair tooling, which is out of scope for Spec 068.

## Redaction Model

Sensitive structured metadata keys are redacted before persistence using runtime graph redaction helpers. The original payload is represented only by `payload_digest`. UI and API responses expose safe summaries, classifications, statuses, timestamps, IDs, and safe artifact references.

## Retention And Export

Interaction evidence follows runtime run retention and export controls. Export surfaces must treat it as safe-summary evidence and continue to exclude raw prompts, completions, provider payloads, credentials, private channel messages, memory contents, stack traces, and raw tool outputs.
