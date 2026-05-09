# Data Model: Model-Backed Graph Role Executor

No new PostgreSQL tables are planned. Spec 061 composes existing runtime,
configuration, gateway, usage, and artifact records with new in-process domain
models.

## RoleExecutionContext

- Existing runtime context for one graph role node.
- Fields used by Spec 061:
  - `workflow_run_id`
  - `tenant_id`
  - `trace_id`
  - `node_key`
  - `role_key`
  - `role_kind`
  - `attempt`
  - `input_summary`
  - `pinned_context`

Validation rules:

- `tenant_id` is required for model-backed execution.
- `pinned_context` must include enough safe metadata to identify output
  contract, profile reference key, model-backed execution mode, and optional
  prompt/profile/provider references.
- Raw upstream payloads are not allowed; upstream data is represented as safe
  summaries and artifact references.

## ModelBackedRolePins

- In-process resolved pin bundle for a role node.
- Fields:
  - `runtime_policy_decision_id`
  - `model_provider_key`
  - `model_id`
  - `model_routing_version_id`
  - `prompt_reference_version_id`
  - `prompt_version_id`
  - `prompt_digest`
  - `agent_profile_version_id`
  - `evaluated_version_ids`
  - `safe_reason`

Validation rules:

- All IDs must belong to the active tenant or platform-scoped governance
  records available to that tenant.
- Missing or denied pins produce fail-closed role errors.

## SafeRoleModelInput

- Redaction-safe input passed to `ModelGateway`.
- Fields:
  - system and user messages composed from safe role instructions
  - workflow and node identifiers
  - upstream safe summaries
  - artifact reference identifiers
  - output contract key and schema summary

Validation rules:

- No raw prompt body, completion body, secret, provider payload, private
  channel payload, memory content, unauthorized payload, raw external tool
  payload, filesystem path, or storage URI may appear.
- Input must be reproducible from safe metadata and pinned references.

## RoleOutputContract

- In-process structured validation rule for a role output.
- Required fields:
  - `summary`
  - `status`
  - optional `findings`
  - optional `recommendations`
  - optional `artifact_refs`
  - optional `usage`

Validation rules:

- Required fields must be present and safe-text validated.
- Unknown fields are allowed only after redaction and bounded-size checks.
- Contract-invalid output becomes a failed `RoleExecutionResult`.

## RoleExecutionResult

- Existing graph-compatible result returned to `GraphExecutionService`.
- Fields extended or populated by Spec 061:
  - `status`
  - `safe_summary`
  - `structured_output`
  - `payload_digest`
  - `error_code`

Validation rules:

- Success results must contain only safe structured output and artifact
  references.
- Failure results must include safe error categories only.
- `payload_digest` must be computed over the redaction-safe structured result
  or referenced payload metadata.

## ModelBackedRoleEvidence

- Safe metadata stored through existing runtime/gateway/usage/artifact records.
- Fields:
  - workflow run and step references
  - tenant and trace references
  - gateway operation/attempt references
  - prompt/profile/model routing references
  - usage summary
  - output digest
  - artifact reference IDs
  - policy/failure category

Validation rules:

- Evidence must be idempotent by workflow run, step, attempt, and operation
  identity.
- Evidence must never contain raw prompts, completions, credentials, provider
  headers, provider payloads, private messages, memory contents, or raw
  artifact bodies.

## State Transitions

```text
deterministic requested -> deterministic executor -> role success/failure

model-backed requested
  -> pin resolution allowed
  -> safe input built
  -> gateway invoked
  -> output contract valid
  -> artifact reference stored if needed
  -> role success

model-backed requested
  -> pin/policy/credential/tenant/redaction/contract failure
  -> role failure
```
