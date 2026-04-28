# Runtime ModelGateway Protocol

## Purpose

Every runtime worker and test bench model call must use `ModelGateway` instead
of provider SDKs or direct provider HTTP calls. The protocol keeps model
selection, tenant visibility, credentials, retries, breakers, traces, usage,
and audit summaries consistent.

## Invocation Request

```json
{
  "tenant_id": "uuid",
  "workflow_run_id": "uuid|null",
  "test_bench_run_id": "uuid|null",
  "trace_id": "string",
  "idempotency_key": "string",
  "model_provider_entry_id": "uuid",
  "model_id": "string",
  "messages": "in-memory only",
  "parameters": {
    "temperature": 0.2,
    "max_tokens": 512
  },
  "timeout_ms": 30000,
  "caller": {
    "source": "runtime_worker|test_bench",
    "workflow_version_bundle_id": "uuid|null",
    "agent_key": "string|null",
    "step_key": "string|null"
  }
}
```

`messages` are never persisted by the gateway. Tests may assert that persisted
metadata excludes this field.

## Preflight Requirements

The gateway must verify:

- Tenant visibility for the catalog entry.
- Catalog entry is active, available, healthy, and gateway-governed.
- Governing connection is active and healthy from the latest relevant test.
- Provider model definition is still available.
- Secret references resolve through the existing secret provider.
- Local endpoint allowlist is still satisfied for local providers.
- Breaker scope allows protected work.
- Retry budget and timeout policy are available.

Failure to verify any item returns a fail-closed result.

## Invocation Result

```json
{
  "outcome": "success|failure",
  "content": "in-memory only",
  "normalized_error_category": "authorization_failure|invalid_model|timeout|rate_limit|provider_unavailable|malformed_provider_response|policy_or_visibility_denial|secret_resolution_failure|unknown_provider_failure|null",
  "usage": {
    "usage_available": true,
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30,
    "provider_model_id": "gpt-example"
  },
  "metadata": {
    "gateway_invocation_attempt_id": "uuid",
    "latency_ms": 123,
    "retry_attempts": 0,
    "breaker_scope": "model_provider:tenant:openai:connection-id:model-id",
    "safe_provider_request_id": "string|null"
  }
}
```

`content` is returned to the caller in memory and is not persisted by the
gateway.

## Retry Behavior

Retry only:

- `timeout`
- `rate_limit`
- `provider_unavailable`
- selected network failures classified as transient

Do not retry:

- `authorization_failure`
- `invalid_model`
- `malformed_provider_response`
- `policy_or_visibility_denial`
- `secret_resolution_failure`
- `unknown_provider_failure` unless explicitly classified transient by a
  future reviewed policy

## Breaker Scope

Runtime scope:

```text
model_provider:{tenant_scope}:{provider_type}:{connection_id}:{model_id}
```

Probe scope:

```text
model_provider_probe:{provider_type}:{connection_id}:{model_id}
```

Scopes must never include URLs, headers, tokens, prompts, completions, or raw
provider errors.

## Required Persisted Metadata

- Tenant id and run/test bench context when available.
- Selected catalog entry, connection, provider type, and model id.
- Latency, outcome, normalized error category, retry inputs, breaker inputs.
- Usage counts when available, or `usage_available=false`.
- Safe audit/debug trace ids.
- Sanitized provider request id only when non-secret.

## Prohibited Persisted Metadata

- Raw API keys, provider tokens, or resolved credential values.
- Raw prompts, messages, tool input payloads, or completions.
- Raw provider request or response bodies.
- Local endpoint secrets, URL userinfo, Authorization headers, or secret-like
  query parameters.
