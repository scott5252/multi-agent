# Contract: Gateway Credential Resolution

## ProviderSecretResolver Contract

### Input

- `provider_type`: `openai` or `local_openai_compatible`
- `credential_secret_reference_ids`: ordered tuple of safe secret reference ids

### Behavior

- Select the first configured reference.
- For `openai`, fail with `secret_reference_invalid` when no reference exists.
- For `local_openai_compatible`, return no credential when no reference exists.
- Resolve a selected reference through the configured `SecretProvider`.
- Treat missing, denied, and empty resolved values as `secret_reference_invalid`.

### Output

- `ResolvedProviderCredential(reference, value)` for successful resolution.
- `None` for allowed no-auth local calls.
- `SecretReferenceError` for failed or required resolution.

### Safety

- The `value` field is process-local and may only be used to populate `AdapterRequest.credential`.
- Safe diagnostics may include `reference`, never `value`.

## Provider Probe Contract

### Input

- Provider connection id.
- Platform administrator principal.
- Optional provider probe operation identity.

### Behavior

1. Load connection and first model definition.
2. Enforce platform administrator permission and rate-limit decisions.
3. Resolve credential according to provider type.
4. Invoke adapter only when credential requirements pass.
5. Append `ConnectionTestResult`.
6. Update `ConnectionHealthSnapshot`.
7. Complete provider probe operation when present.

### Credential Failure Response

- No adapter call.
- `ProviderTestSummary.outcome`: `failure`
- `ProviderTestSummary.normalized_reason`: `secret_reference_invalid`
- `safe_diagnostic_summary`: safe message such as `Provider credential reference could not be resolved`

## ModelGateway Contract

### Input

- `connection_id`
- `model_id`
- `messages`
- `GatewayInvocationContext`

### Behavior

1. Load connection.
2. Fail inactive or unhealthy connections with existing `catalog_inactive` behavior.
3. Create or recover gateway operation identity when provided.
4. Resolve credential according to provider type.
5. Invoke adapter only when credential requirements pass.
6. Record gateway attempt, physical attempt, retry/breaker summaries, and usage-safe evidence.

### Credential Failure Result

```json
{
  "outcome": "failure",
  "normalized_error_category": "secret_reference_invalid",
  "safe_audit_summary": {
    "connection_id": "<uuid>",
    "provider_type": "openai",
    "model_id": "gpt-test",
    "credential_reference_id": "qa025/openai-placeholder",
    "credential_resolution_outcome": "failed"
  }
}
```

`credential_reference_id` is omitted or null when no reference exists.

## Adapter Contract

### AdapterRequest

- `credential`: resolved credential value or `None`.

### OpenAIAdapter

- Requires `credential` to be non-empty before normal operation.
- Sends `Authorization: Bearer <resolved credential>` to `/v1/chat/completions`.
- Does not log, persist, or return the credential.

### LocalOpenAICompatibleAdapter

- Validates `base_url` against local endpoint allowlist.
- Sends no authorization header when `credential` is `None`.
- Sends `Authorization: Bearer <resolved credential>` when a credential is provided.
- Does not log, persist, or return the credential.

## Redaction Contract

The following surfaces must never contain raw resolved credential values:

- `ConnectionTestResult`
- `ConnectionHealthSnapshot`
- `GatewayInvocationAttempt`
- `GatewayOperation`
- `GatewayPhysicalAttempt`
- provider admin API responses
- provider admin web pages
- operations diagnostics
- usage records
- audit payloads
- logs
- README, quickstart, QA docs, and screenshots

Safe fields:

- provider type
- provider connection id
- model id
- safe base URL
- selected credential reference id
- normalized category
- safe diagnostic summary
- trace id
- tenant id
- operation identity

Unsafe fields:

- raw credential values
- authorization headers
- raw provider request payloads
- raw provider response bodies
- raw prompts
- raw completions
- stack traces containing provider payloads

## Test Contract

Tests must prove:

- OpenAI probe passes resolved credential into adapter.
- OpenAI gateway call passes resolved credential into adapter.
- Missing OpenAI reference fails before adapter call.
- Missing secret provider entry fails before adapter call.
- Empty secret provider value fails before adapter call.
- Local no-auth call sends no authorization header.
- Local configured credential sends the resolved authorization header.
- Raw fixture secret does not appear in persisted safe evidence.
