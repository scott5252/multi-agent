# Contract: Model-Backed Role Executor

This is an internal runtime contract, not a public HTTP API.

## Executor Selection

```text
select_role_executor(context) -> RoleNodeExecutor
```

Rules:

- Deterministic mode always selects `DeterministicRoleNodeExecutor`.
- Model-backed mode selects `ModelBackedRoleNodeExecutor` only when tenant id,
  run id, step id, role key, output contract key, and governed pins are
  available.
- Missing or denied model-backed prerequisites produce a failed
  `RoleExecutionResult`; they must not invoke `ModelGateway`.

## ModelBackedRoleNodeExecutor.execute

Input:

```json
{
  "workflow_run_id": "uuid",
  "tenant_id": "uuid",
  "trace_id": "trace",
  "node_key": "reviewer-ux",
  "role_key": "ux-reviewer",
  "role_kind": "agent",
  "attempt": 0,
  "input_summary": {
    "upstream_node_keys": ["lead-designer"],
    "upstream_outputs": {
      "lead-designer": {
        "safe_summary": "Safe design proposal summary.",
        "artifact_refs": ["artifact-ref"]
      }
    }
  },
  "pinned_context": {
    "execution_mode": "model_gateway",
    "profile_reference_key": "ux-reviewer-profile",
    "output_contract_key": "design-reviewer-verdict-v1"
  }
}
```

Success output:

```json
{
  "status": "succeeded",
  "safe_summary": "ux-reviewer completed with model-backed output.",
  "structured_output": {
    "summary": "Safe reviewer summary.",
    "status": "approved",
    "findings": [],
    "artifact_refs": [],
    "usage": {
      "total_tokens": 42,
      "usage_available": "available"
    },
    "provenance": {
      "model_id": "gpt-safe-fixture",
      "prompt_version_id": "uuid",
      "model_routing_version_id": "uuid"
    }
  },
  "payload_digest": "sha256:..."
}
```

Failure output:

```json
{
  "status": "failed",
  "safe_summary": "ux-reviewer failed before provider invocation.",
  "structured_output": {
    "error_code": "model_policy_denied",
    "safe_reason": "model-backed role execution denied by policy"
  },
  "payload_digest": "sha256:...",
  "error_code": "model_policy_denied"
}
```

## Failure Codes

- `model_execution_mode_disabled`
- `model_pin_resolution_failed`
- `model_policy_denied`
- `model_credential_unavailable`
- `model_gateway_failed`
- `model_output_contract_invalid`
- `model_output_redaction_failed`
- `model_output_artifact_failed`
- `model_tenant_scope_denied`

## Redaction Rules

The executor must reject or redact:

- raw prompt bodies
- raw completions
- secrets and credential values
- provider authorization headers
- raw provider request or response bodies
- private channel payloads
- memory contents
- unauthorized run payloads
- raw external tool payloads
- local filesystem paths and storage URIs

## Idempotency

Gateway operation identity:

```text
runtime:{workflow_run_id}:step:{run_step_id}:node:{node_key}:attempt:{attempt}
```

Repeated execution with the same operation identity must reuse gateway
operation recovery behavior and must not duplicate authoritative provider usage
evidence.
